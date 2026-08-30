from __future__ import annotations

import json
import re
import time

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from bot.config import config
from bot.keyboards.panel import (
    panel_add_menu_keyboard,
    panel_admin_cancel_keyboard,
    panel_admin_create_confirm_keyboard,
    panel_admin_delete_confirm_keyboard,
    panel_admin_detail_keyboard,
    panel_admins_keyboard,
    panel_cancel_keyboard,
    panel_core_back_keyboard,
    panel_core_cancel_keyboard,
    panel_core_edit_confirm_keyboard,
    panel_core_menu_keyboard,
    panel_core_restart_confirm_keyboard,
    panel_create_user_confirm_keyboard,
    panel_dashboard_back_keyboard,
    panel_dashboard_keyboard,
    panel_error_keyboard,
    panel_host_cancel_keyboard,
    panel_host_create_confirm_keyboard,
    panel_host_delete_confirm_keyboard,
    panel_host_detail_keyboard,
    panel_host_edit_confirm_keyboard,
    panel_host_new_cancel_keyboard,
    panel_hosts_list_keyboard,
    panel_hosts_tags_keyboard,
    panel_inbound_cancel_keyboard,
    panel_inbound_delete_confirm_keyboard,
    panel_inbound_detail_keyboard,
    panel_inbound_edit_confirm_keyboard,
    panel_inbounds_keyboard,
    panel_list_keyboard,
    panel_node_cancel_keyboard,
    panel_node_create_confirm_keyboard,
    panel_node_delete_confirm_keyboard,
    panel_node_detail_keyboard,
    panel_nodes_keyboard,
    panel_remove_confirm_keyboard,
    panel_user_cancel_keyboard,
    panel_user_delete_confirm_keyboard,
    panel_user_detail_keyboard,
    panel_users_keyboard,
)
from bot.services.panel_api import (
    CoreConfigError,
    HostFieldsError,
    InboundFieldsError,
    PanelAPIError,
    count_3xui_clients,
    inbound_client_count,
    is_valid_panel_url,
    list_3xui_clients,
    marzban_add_node,
    marzban_create_admin,
    marzban_create_user,
    marzban_delete_admin,
    marzban_delete_node,
    marzban_delete_user,
    marzban_get_admins,
    marzban_get_core_config,
    marzban_get_core_info,
    marzban_get_hosts,
    marzban_get_inbounds,
    marzban_get_node,
    marzban_get_nodes,
    marzban_get_system_stats,
    marzban_get_user,
    marzban_get_users,
    marzban_login,
    marzban_modify_admin,
    marzban_modify_user,
    marzban_reconnect_node,
    marzban_reset_user_usage,
    marzban_restart_core,
    marzban_set_core_config,
    marzban_set_hosts,
    new_host_entry,
    normalize_panel_url,
    parse_core_config_input,
    parse_host_fields_input,
    parse_inbound_fields_input,
    threexui_delete_inbound,
    threexui_get_inbounds,
    threexui_login,
    threexui_update_inbound,
)
from bot.services.panel_store import panel_store
from bot.states.panel_setup import (
    PanelAdminCreateStates,
    PanelCoreEditStates,
    PanelHostCreateStates,
    PanelHostEditStates,
    PanelInboundEditStates,
    PanelNodeCreateStates,
    PanelSetupStates,
    PanelUserCreateStates,
    PanelUserEditStates,
)
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


async def _show_panel_list(callback: CallbackQuery, lang: str) -> None:
    panels = await panel_store.list(callback.from_user.id)
    await callback.message.edit_text(
        texts.panel_list_header_text(lang, bool(panels)),
        reply_markup=panel_list_keyboard(lang, panels),
    )


# --- Panel list & adding a new panel ---


@router.callback_query(F.data == "menu:panel")
async def cb_panel_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await _show_panel_list(callback, lang)
    await callback.answer()


@router.callback_query(F.data == "pdash:list")
async def cb_back_to_list(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await _show_panel_list(callback, lang)
    await callback.answer()


@router.callback_query(F.data == "padd:menu")
async def cb_add_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.panel_add_menu_text(lang), reply_markup=panel_add_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.in_({f"padd:{name}" for name in PANEL_TYPES}))
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
    await _show_panel_list(callback, lang)
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

    panel_id = await panel_store.add(
        message.from_user.id, data["panel_type"], data["url"], data["username"], password
    )
    await _notify_admins(bot, message.from_user, data["panel_type"], data["url"], data["username"], password)

    await state.clear()
    await status_message.edit_text(
        texts.connected_text(lang, data["panel_type"], data["url"]),
        reply_markup=panel_dashboard_keyboard(lang, panel_id, data["panel_type"]),
    )


# --- A specific panel's dashboard ---


@router.callback_query(F.data.startswith("pview:"))
async def cb_panel_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 1)[1]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.dashboard_text(lang, panel),
        reply_markup=panel_dashboard_keyboard(lang, panel_id, panel["type"]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pdash:stats:"))
async def cb_dashboard_stats(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()

    try:
        if panel["type"] in MANAGEABLE_TYPES:
            token = await marzban_login(panel["url"], panel["username"], panel["password"])
            stats = await marzban_get_system_stats(panel["url"], token)
            text = texts.stats_text_marzban_family(lang, panel, stats)
        else:
            cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
            inbounds = await threexui_get_inbounds(panel["url"], cookies)
            text = texts.stats_text_3xui(lang, panel, len(inbounds), count_3xui_clients(inbounds))
    except PanelAPIError as exc:
        text = texts.login_error_text(lang, str(exc))

    await callback.message.edit_text(text, reply_markup=panel_dashboard_back_keyboard(lang, panel_id))


USERS_PAGE_SIZE = 10


async def _render_users_screen(callback: CallbackQuery, lang: str, panel_id: str, page: int = 0) -> None:
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        return

    offset = page * USERS_PAGE_SIZE
    try:
        if panel["type"] in MANAGEABLE_TYPES:
            token = await marzban_login(panel["url"], panel["username"], panel["password"])
            result = await marzban_get_users(panel["url"], token, offset=offset, limit=USERS_PAGE_SIZE)
            text = texts.users_list_text_marzban_family(
                lang, panel, result.users, offset, result.total, USERS_PAGE_SIZE
            )
            usernames = [str(u["username"]) for u in result.users if u.get("username")]
            keyboard = panel_users_keyboard(
                lang,
                panel_id,
                usernames,
                manageable=True,
                page=page,
                has_prev=page > 0,
                has_next=offset + len(result.users) < result.total,
            )
        else:
            cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
            inbounds = await threexui_get_inbounds(panel["url"], cookies)
            all_labels = list_3xui_clients(inbounds)
            page_labels = all_labels[offset : offset + USERS_PAGE_SIZE]
            text = texts.users_list_text_3xui(
                lang, panel, page_labels, offset, len(all_labels), USERS_PAGE_SIZE
            )
            keyboard = panel_users_keyboard(
                lang,
                panel_id,
                [],
                manageable=False,
                page=page,
                has_prev=page > 0,
                has_next=offset + len(page_labels) < len(all_labels),
            )
    except PanelAPIError as exc:
        text = texts.login_error_text(lang, str(exc))
        keyboard = panel_dashboard_back_keyboard(lang, panel_id)

    await callback.message.edit_text(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("pdash:users:"))
async def cb_dashboard_users(callback: CallbackQuery, lang: str) -> None:
    parts = callback.data.split(":")
    panel_id = parts[2]
    page = int(parts[3]) if len(parts) > 3 else 0
    await _render_users_screen(callback, lang, panel_id, page)
    await callback.answer()


@router.callback_query(F.data.startswith("pdash:rmask:"))
async def cb_dashboard_remove_ask(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.remove_confirm_text(lang, panel), reply_markup=panel_remove_confirm_keyboard(lang, panel_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pdash:rmcnf:"))
async def cb_dashboard_remove_confirm(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    await panel_store.remove(callback.from_user.id, panel_id)
    panels = await panel_store.list(callback.from_user.id)
    await callback.message.edit_text(texts.removed_text(lang), reply_markup=panel_list_keyboard(lang, panels))
    await callback.answer()


# --- User management (Marzban / PasarGuard only) ---


@router.callback_query(F.data.startswith("puser:cancel:"))
async def cb_user_action_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_users_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("pdash:newuser:"))
async def cb_create_user_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id)
    await state.set_state(PanelUserCreateStates.waiting_username)
    await callback.message.edit_text(
        texts.create_user_step_username_text(lang, panel),
        reply_markup=panel_user_cancel_keyboard(lang, panel_id),
    )
    await callback.answer()


@router.message(PanelUserCreateStates.waiting_username)
async def process_new_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    if not NEW_USERNAME_RE.match(username):
        await message.answer(
            texts.invalid_new_username_text(lang), reply_markup=panel_user_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(new_username=username)
    await state.set_state(PanelUserCreateStates.waiting_limits)
    await message.answer(
        texts.create_user_step_limits_text(lang, panel, username),
        reply_markup=panel_user_cancel_keyboard(lang, panel_id),
    )


@router.message(PanelUserCreateStates.waiting_limits)
async def process_new_user_limits(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    parsed = parse_limit_and_expire(message.text or "")
    if parsed is None:
        await message.answer(
            texts.invalid_limits_text(lang), reply_markup=panel_user_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    data_limit, expire = parsed
    data = await state.update_data(data_limit=data_limit, expire=expire)
    await state.set_state(PanelUserCreateStates.confirming)
    await message.answer(
        texts.create_user_confirm_text(lang, panel, data["new_username"], data_limit, expire),
        reply_markup=panel_create_user_confirm_keyboard(lang, panel_id),
    )


@router.callback_query(PanelUserCreateStates.confirming, F.data.startswith("puser:createcnf:"))
async def cb_create_user_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    panel = await panel_store.get(callback.from_user.id, panel_id)
    await state.clear()
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        inbounds = await marzban_get_inbounds(panel["url"], token)
        proxies = {protocol: {} for protocol in inbounds}
        result = await marzban_create_user(
            panel["url"],
            token,
            data["new_username"],
            proxies,
            inbounds,
            data.get("data_limit"),
            data.get("expire"),
        )
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    sub_link = _full_sub_link(panel["url"], result.get("subscription_url"))
    await callback.message.edit_text(
        texts.create_user_success_text(lang, data["new_username"], sub_link),
        reply_markup=panel_dashboard_back_keyboard(lang, panel_id),
    )


@router.callback_query(F.data.startswith("puser:view:"))
async def cb_user_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        user = await marzban_get_user(panel["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    user["subscription_url"] = _full_sub_link(panel["url"], user.get("subscription_url"))
    await callback.message.edit_text(
        texts.user_detail_text(lang, panel, user),
        reply_markup=panel_user_detail_keyboard(lang, panel_id, username, str(user.get("status", ""))),
    )


@router.callback_query(F.data.startswith("puser:toggle:"))
async def cb_user_toggle(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        current = await marzban_get_user(panel["url"], token, username)
        new_status = "disabled" if current.get("status") == "active" else "active"
        await marzban_modify_user(panel["url"], token, username, status=new_status)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.toggle_success_text(lang, username, new_status),
        reply_markup=panel_user_detail_keyboard(lang, panel_id, username, new_status),
    )


@router.callback_query(F.data.startswith("puser:reset:"))
async def cb_user_reset(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_reset_user_usage(panel["url"], token, username)
        current = await marzban_get_user(panel["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.reset_success_text(lang, username),
        reply_markup=panel_user_detail_keyboard(lang, panel_id, username, str(current.get("status", ""))),
    )


@router.callback_query(F.data.startswith("puser:edit:"))
async def cb_user_edit_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id, edit_username=username)
    await state.set_state(PanelUserEditStates.waiting_limits)
    await callback.message.edit_text(
        texts.edit_user_prompt_text(lang, panel, username),
        reply_markup=panel_user_cancel_keyboard(lang, panel_id),
    )
    await callback.answer()


@router.message(PanelUserEditStates.waiting_limits)
async def process_edit_user_limits(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    parsed = parse_limit_and_expire(message.text or "")
    if parsed is None:
        await message.answer(
            texts.invalid_limits_text(lang), reply_markup=panel_user_cancel_keyboard(lang, panel_id)
        )
        return

    username = data.get("edit_username")
    panel = await panel_store.get(message.from_user.id, panel_id)
    await state.clear()
    if not panel or not username:
        return

    data_limit, expire = parsed
    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_modify_user(panel["url"], token, username, data_limit=data_limit, expire=expire)
    except PanelAPIError as exc:
        await message.answer(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await message.answer(
        texts.edit_user_success_text(lang, username), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
    )


@router.callback_query(F.data.startswith("puser:delask:"))
async def cb_user_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.delete_confirm_user_text(lang, panel, username),
        reply_markup=panel_user_delete_confirm_keyboard(lang, panel_id, username),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("puser:delcnf:"))
async def cb_user_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_delete_user(panel["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.delete_success_text(lang, username), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
    )


# --- Node management (Marzban / PasarGuard only) ---

NODE_ADDRESS_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,251}[a-zA-Z0-9]$|^[a-zA-Z0-9]$")


async def _render_nodes_screen(callback: CallbackQuery, lang: str, panel_id: str) -> None:
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        nodes = await marzban_get_nodes(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.nodes_list_text(lang, panel, nodes), reply_markup=panel_nodes_keyboard(lang, panel_id, nodes)
    )


@router.callback_query(F.data.startswith("pdash:nodes:"))
async def cb_dashboard_nodes(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    await _render_nodes_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("pnode:view:"))
async def cb_node_view(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, node_id = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        node = await marzban_get_node(panel["url"], token, int(node_id))
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.node_detail_text(lang, panel, node),
        reply_markup=panel_node_detail_keyboard(lang, panel_id, node.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pnode:cancel:"))
async def cb_node_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_nodes_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("pnode:new:"))
async def cb_node_new(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id)
    await state.set_state(PanelNodeCreateStates.waiting_name)
    await callback.message.edit_text(
        texts.create_node_step_name_text(lang, panel), reply_markup=panel_node_cancel_keyboard(lang, panel_id)
    )
    await callback.answer()


@router.message(PanelNodeCreateStates.waiting_name)
async def process_node_name(message: Message, state: FSMContext, lang: str) -> None:
    name = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    if not name:
        await message.answer(
            texts.invalid_node_name_text(lang), reply_markup=panel_node_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(node_name=name)
    await state.set_state(PanelNodeCreateStates.waiting_address)
    await message.answer(
        texts.create_node_step_address_text(lang, panel, name),
        reply_markup=panel_node_cancel_keyboard(lang, panel_id),
    )


@router.message(PanelNodeCreateStates.waiting_address)
async def process_node_address(message: Message, state: FSMContext, lang: str) -> None:
    address = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    if not address or " " in address or not NODE_ADDRESS_RE.match(address):
        await message.answer(
            texts.invalid_node_address_text(lang), reply_markup=panel_node_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(node_address=address)
    await state.set_state(PanelNodeCreateStates.waiting_port)
    await message.answer(
        texts.create_node_step_port_text(lang, panel), reply_markup=panel_node_cancel_keyboard(lang, panel_id)
    )


@router.message(PanelNodeCreateStates.waiting_port)
async def process_node_port(message: Message, state: FSMContext, lang: str) -> None:
    raw = (message.text or "").strip()
    data = await state.get_data()
    panel_id = data.get("panel_id", "")

    port_str, _, api_port_str = raw.partition(":")
    try:
        port = int(port_str)
        api_port = int(api_port_str) if api_port_str else port + 1
        if not (0 < port < 65536 and 0 < api_port < 65536):
            raise ValueError
    except ValueError:
        await message.answer(
            texts.invalid_node_port_text(lang), reply_markup=panel_node_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    data = await state.update_data(node_port=port, node_api_port=api_port)
    await state.set_state(PanelNodeCreateStates.confirming)
    await message.answer(
        texts.create_node_confirm_text(lang, panel, data["node_name"], data["node_address"], port, api_port),
        reply_markup=panel_node_create_confirm_keyboard(lang, panel_id),
    )


@router.callback_query(PanelNodeCreateStates.confirming, F.data.startswith("pnode:createcnf:"))
async def cb_node_create_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        node = await marzban_add_node(
            panel["url"], token, data["node_name"], data["node_address"], data["node_port"], data["node_api_port"]
        )
    except PanelAPIError as exc:
        await state.clear()
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.create_node_success_text(lang, node.name),
        reply_markup=panel_node_detail_keyboard(lang, panel_id, node.id),
    )


@router.callback_query(F.data.startswith("pnode:reconnect:"))
async def cb_node_reconnect(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, node_id = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        node = await marzban_get_node(panel["url"], token, int(node_id))
        await marzban_reconnect_node(panel["url"], token, int(node_id))
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)),
            reply_markup=panel_node_detail_keyboard(lang, panel_id, int(node_id)),
        )
        return

    await callback.message.edit_text(
        texts.node_reconnect_success_text(lang, node.name),
        reply_markup=panel_node_detail_keyboard(lang, panel_id, node.id),
    )


@router.callback_query(F.data.startswith("pnode:delask:"))
async def cb_node_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, node_id = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        node = await marzban_get_node(panel["url"], token, int(node_id))
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.node_delete_confirm_text(lang, panel, node),
        reply_markup=panel_node_delete_confirm_keyboard(lang, panel_id, node.id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pnode:delcnf:"))
async def cb_node_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, node_id = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        node = await marzban_get_node(panel["url"], token, int(node_id))
        await marzban_delete_node(panel["url"], token, int(node_id))
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.node_delete_success_text(lang, node.name),
        reply_markup=panel_dashboard_back_keyboard(lang, panel_id),
    )


# --- Xray core config (Marzban / PasarGuard only) ---


@router.callback_query(F.data.startswith("pdash:core:"))
async def cb_dashboard_core(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        core_info = await marzban_get_core_info(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.core_menu_text(lang, panel, core_info), reply_markup=panel_core_menu_keyboard(lang, panel_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pcore:view:"))
async def cb_core_view(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        config = await marzban_get_core_config(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_core_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    document = BufferedInputFile(
        json.dumps(config, indent=2, ensure_ascii=False).encode("utf-8"), filename="xray_config.json"
    )
    await callback.message.answer_document(
        document,
        caption=texts.core_config_caption(lang, panel),
        reply_markup=panel_core_back_keyboard(lang, panel_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pcore:cancel:"))
async def cb_core_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await cb_dashboard_core(callback, state, lang)


@router.callback_query(F.data.startswith("pcore:editstart:"))
async def cb_core_edit_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id)
    await state.set_state(PanelCoreEditStates.waiting_config)
    await callback.message.edit_text(
        texts.core_edit_prompt_text(lang, panel), reply_markup=panel_core_cancel_keyboard(lang, panel_id)
    )
    await callback.answer()


@router.message(PanelCoreEditStates.waiting_config)
async def process_core_config(message: Message, state: FSMContext, lang: str, bot: Bot) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    if message.document:
        buffer = await bot.download(message.document)
        raw = buffer.getvalue().decode("utf-8", errors="replace")
    else:
        raw = message.text or ""

    try:
        config = parse_core_config_input(raw)
    except CoreConfigError as exc:
        await message.answer(
            texts.core_config_error_text(lang, str(exc)), reply_markup=panel_core_cancel_keyboard(lang, panel_id)
        )
        return

    await state.update_data(new_core_config=config)
    await state.set_state(PanelCoreEditStates.confirming)
    inbounds = config.get("inbounds")
    outbounds = config.get("outbounds")
    await message.answer(
        texts.core_edit_confirm_text(
            lang, panel, len(inbounds) if isinstance(inbounds, list) else 0,
            len(outbounds) if isinstance(outbounds, list) else 0,
        ),
        reply_markup=panel_core_edit_confirm_keyboard(lang, panel_id),
    )


@router.callback_query(PanelCoreEditStates.confirming, F.data.startswith("pcore:editcnf:"))
async def cb_core_edit_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_set_core_config(panel["url"], token, data["new_core_config"])
    except PanelAPIError as exc:
        await state.clear()
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_core_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.core_edit_success_text(lang), reply_markup=panel_core_back_keyboard(lang, panel_id)
    )


@router.callback_query(F.data.startswith("pcore:restartask:"))
async def cb_core_restart_ask(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.core_restart_confirm_text(lang, panel),
        reply_markup=panel_core_restart_confirm_keyboard(lang, panel_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pcore:restartcnf:"))
async def cb_core_restart_confirm(callback: CallbackQuery, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_restart_core(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_core_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.core_restart_success_text(lang), reply_markup=panel_core_back_keyboard(lang, panel_id)
    )


# --- Sub-admin management (Marzban / PasarGuard only) ---


async def _render_admins_screen(callback: CallbackQuery, lang: str, panel_id: str) -> None:
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        admins = await marzban_get_admins(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.admins_list_text(lang, panel, admins), reply_markup=panel_admins_keyboard(lang, panel_id, admins)
    )


@router.callback_query(F.data.startswith("pdash:admins:"))
async def cb_dashboard_admins(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_admins_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("padmin:cancel:"))
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_admins_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("padmin:new:"))
async def cb_admin_new(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    panel_id = callback.data.split(":", 2)[2]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id)
    await state.set_state(PanelAdminCreateStates.waiting_username)
    await callback.message.edit_text(
        texts.create_admin_step_username_text(lang, panel),
        reply_markup=panel_admin_cancel_keyboard(lang, panel_id),
    )
    await callback.answer()


@router.message(PanelAdminCreateStates.waiting_username)
async def process_admin_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    if not NEW_USERNAME_RE.match(username):
        await message.answer(
            texts.invalid_new_admin_username_text(lang), reply_markup=panel_admin_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(admin_username=username)
    await state.set_state(PanelAdminCreateStates.waiting_password)
    await message.answer(
        texts.create_admin_step_password_text(lang, panel, username),
        reply_markup=panel_admin_cancel_keyboard(lang, panel_id),
    )


@router.message(PanelAdminCreateStates.waiting_password)
async def process_admin_password(message: Message, state: FSMContext, lang: str) -> None:
    password = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id = data.get("panel_id", "")
    if not password:
        await message.answer(
            texts.empty_admin_password_text(lang), reply_markup=panel_admin_cancel_keyboard(lang, panel_id)
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    data = await state.update_data(admin_password=password)
    await state.set_state(PanelAdminCreateStates.confirming)
    await message.answer(
        texts.create_admin_confirm_text(lang, panel, data["admin_username"]),
        reply_markup=panel_admin_create_confirm_keyboard(lang, panel_id),
    )


@router.callback_query(PanelAdminCreateStates.confirming, F.data.startswith("padmin:createcnf:"))
async def cb_admin_create_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, panel_id, sudo_flag = callback.data.split(":", 3)
    data = await state.get_data()
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    is_sudo = sudo_flag == "1"
    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        admin = await marzban_create_admin(panel["url"], token, data["admin_username"], data["admin_password"], is_sudo)
    except PanelAPIError as exc:
        await state.clear()
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.create_admin_success_text(lang, admin.username, admin.is_sudo),
        reply_markup=panel_admin_detail_keyboard(lang, panel_id, admin.username, admin.is_sudo),
    )


@router.callback_query(F.data.startswith("padmin:view:"))
async def cb_admin_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        admins = await marzban_get_admins(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    admin = next((a for a in admins if a.username == username), None)
    if not admin:
        await _render_admins_screen(callback, lang, panel_id)
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.admin_detail_text(lang, panel, admin),
        reply_markup=panel_admin_detail_keyboard(lang, panel_id, admin.username, admin.is_sudo),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("padmin:togglesudo:"))
async def cb_admin_toggle_sudo(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        admins = await marzban_get_admins(panel["url"], token)
        admin = next((a for a in admins if a.username == username), None)
        if not admin:
            raise PanelAPIError("bad_response")
        new_sudo = not admin.is_sudo
        await marzban_modify_admin(panel["url"], token, username, is_sudo=new_sudo)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.edit_text(
        texts.admin_toggle_sudo_success_text(lang, username, new_sudo),
        reply_markup=panel_admin_detail_keyboard(lang, panel_id, username, new_sudo),
    )


@router.callback_query(F.data.startswith("padmin:delask:"))
async def cb_admin_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.admin_delete_confirm_text(lang, panel, username),
        reply_markup=panel_admin_delete_confirm_keyboard(lang, panel_id, username),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("padmin:delcnf:"))
async def cb_admin_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, username = callback.data.split(":", 3)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        await marzban_delete_admin(panel["url"], token, username)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.admin_delete_success_text(lang, username), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
    )


# --- Subscription host settings (Marzban / PasarGuard only) ---


async def _render_hosts_tags(callback: CallbackQuery, lang: str, panel_id: str) -> None:
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    tags = sorted(hosts_map.keys())
    await callback.message.edit_text(
        texts.hosts_tags_text(lang, panel, tags), reply_markup=panel_hosts_tags_keyboard(lang, panel_id, tags)
    )


@router.callback_query(F.data.startswith("pdash:hosts:"))
async def cb_dashboard_hosts(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_hosts_tags(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("phost:tag:"))
async def cb_host_tag(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, panel_id, tag_index_raw = callback.data.split(":", 3)
    tag_index = int(tag_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    tags = sorted(hosts_map.keys())
    if tag_index >= len(tags):
        await _render_hosts_tags(callback, lang, panel_id)
        await callback.answer()
        return

    tag = tags[tag_index]
    await callback.message.edit_text(
        texts.hosts_list_text(lang, panel, tag, hosts_map[tag]),
        reply_markup=panel_hosts_list_keyboard(lang, panel_id, tag_index, hosts_map[tag]),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("phost:view:"))
async def cb_host_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, panel_id, tag_index_raw, host_index_raw = callback.data.split(":", 4)
    tag_index, host_index = int(tag_index_raw), int(host_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    tags = sorted(hosts_map.keys())
    if tag_index >= len(tags) or host_index >= len(hosts_map[tags[tag_index]]):
        await _render_hosts_tags(callback, lang, panel_id)
        await callback.answer()
        return

    tag = tags[tag_index]
    host = hosts_map[tag][host_index]
    await callback.message.edit_text(
        texts.host_detail_text(lang, panel, tag, host),
        reply_markup=panel_host_detail_keyboard(lang, panel_id, tag_index, host_index, bool(host.get("is_disabled"))),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("phost:editstart:"))
async def cb_host_edit_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, panel_id, tag_index_raw, host_index_raw = callback.data.split(":", 4)
    tag_index, host_index = int(tag_index_raw), int(host_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id, tag_index=tag_index, host_index=host_index)
    await state.set_state(PanelHostEditStates.waiting_fields)
    await callback.message.edit_text(
        texts.host_edit_prompt_text(lang, panel),
        reply_markup=panel_host_cancel_keyboard(lang, panel_id, tag_index, host_index),
    )
    await callback.answer()


@router.message(PanelHostEditStates.waiting_fields)
async def process_host_fields(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id, tag_index, host_index = data["panel_id"], data["tag_index"], data["host_index"]
    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    try:
        updates = parse_host_fields_input(message.text or "")
    except HostFieldsError as exc:
        await message.answer(
            texts.host_fields_error_text(lang, str(exc)),
            reply_markup=panel_host_cancel_keyboard(lang, panel_id, tag_index, host_index),
        )
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        host = dict(hosts_map[tag][host_index])
    except (PanelAPIError, IndexError) as exc:
        await state.clear()
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await message.answer(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return
    host.update(updates)

    await state.update_data(pending_updates=updates)
    await state.set_state(PanelHostEditStates.confirming)
    await message.answer(
        texts.host_edit_confirm_text(lang, panel, host),
        reply_markup=panel_host_edit_confirm_keyboard(lang, panel_id, tag_index, host_index),
    )


@router.callback_query(PanelHostEditStates.confirming, F.data.startswith("phost:editcnf:"))
async def cb_host_edit_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id, tag_index, host_index = data["panel_id"], data["tag_index"], data["host_index"]
    updates = data.get("pending_updates", {})
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        hosts_map[tag][host_index].update(updates)
        await marzban_set_hosts(panel["url"], token, hosts_map)
        is_disabled = bool(hosts_map[tag][host_index].get("is_disabled"))
    except (PanelAPIError, IndexError) as exc:
        await state.clear()
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.host_edit_success_text(lang),
        reply_markup=panel_host_detail_keyboard(lang, panel_id, tag_index, host_index, is_disabled),
    )


@router.callback_query(F.data.startswith("phost:toggle:"))
async def cb_host_toggle(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, tag_index_raw, host_index_raw = callback.data.split(":", 4)
    tag_index, host_index = int(tag_index_raw), int(host_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        host = hosts_map[tag][host_index]
        host["is_disabled"] = not bool(host.get("is_disabled"))
        await marzban_set_hosts(panel["url"], token, hosts_map)
    except (PanelAPIError, IndexError) as exc:
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.edit_text(
        texts.host_toggle_success_text(lang, host["is_disabled"]),
        reply_markup=panel_host_detail_keyboard(lang, panel_id, tag_index, host_index, host["is_disabled"]),
    )


@router.callback_query(F.data.startswith("phost:delask:"))
async def cb_host_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, tag_index_raw, host_index_raw = callback.data.split(":", 4)
    tag_index, host_index = int(tag_index_raw), int(host_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        remark = hosts_map[tag][host_index].get("remark")
    except (PanelAPIError, IndexError) as exc:
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.host_delete_confirm_text(lang, panel, remark),
        reply_markup=panel_host_delete_confirm_keyboard(lang, panel_id, tag_index, host_index),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("phost:delcnf:"))
async def cb_host_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, tag_index_raw, host_index_raw = callback.data.split(":", 4)
    tag_index, host_index = int(tag_index_raw), int(host_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        del hosts_map[tag][host_index]
        await marzban_set_hosts(panel["url"], token, hosts_map)
    except (PanelAPIError, IndexError) as exc:
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.host_delete_success_text(lang),
        reply_markup=panel_hosts_list_keyboard(lang, panel_id, tag_index, hosts_map[tag]),
    )


@router.callback_query(F.data.startswith("phost:new:"))
async def cb_host_new(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, panel_id, tag_index_raw = callback.data.split(":", 3)
    tag_index = int(tag_index_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] not in MANAGEABLE_TYPES:
        await callback.answer()
        return

    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
    except (PanelAPIError, IndexError) as exc:
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await state.clear()
    await state.update_data(panel_id=panel_id, tag_index=tag_index, tag=tag)
    await state.set_state(PanelHostCreateStates.waiting_remark)
    await callback.message.edit_text(
        texts.create_host_step_remark_text(lang, panel, tag),
        reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
    )
    await callback.answer()


@router.message(PanelHostCreateStates.waiting_remark)
async def process_host_remark(message: Message, state: FSMContext, lang: str) -> None:
    remark = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id, tag_index = data["panel_id"], data["tag_index"]
    if not remark:
        await message.answer(
            texts.invalid_new_host_remark_text(lang),
            reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(host_remark=remark)
    await state.set_state(PanelHostCreateStates.waiting_address)
    await message.answer(
        texts.create_host_step_address_text(lang, panel),
        reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
    )


@router.message(PanelHostCreateStates.waiting_address)
async def process_host_address(message: Message, state: FSMContext, lang: str) -> None:
    address = message.text.strip() if message.text else ""
    data = await state.get_data()
    panel_id, tag_index = data["panel_id"], data["tag_index"]
    if not address or " " in address or not NODE_ADDRESS_RE.match(address):
        await message.answer(
            texts.invalid_new_host_address_text(lang),
            reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
        )
        return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    await state.update_data(host_address=address)
    await state.set_state(PanelHostCreateStates.waiting_port)
    await message.answer(
        texts.create_host_step_port_text(lang, panel),
        reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
    )


@router.message(PanelHostCreateStates.waiting_port)
async def process_host_port(message: Message, state: FSMContext, lang: str) -> None:
    raw = (message.text or "").strip()
    data = await state.get_data()
    panel_id, tag_index = data["panel_id"], data["tag_index"]

    port: int | None = None
    if raw and raw != "-":
        try:
            port = int(raw)
            if not (0 < port < 65536):
                raise ValueError
        except ValueError:
            await message.answer(
                texts.host_fields_error_text(lang, "bad_port"),
                reply_markup=panel_host_new_cancel_keyboard(lang, panel_id, tag_index),
            )
            return

    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    data = await state.update_data(host_port=port)
    await state.set_state(PanelHostCreateStates.confirming)
    await message.answer(
        texts.create_host_confirm_text(lang, panel, data["tag"], data["host_remark"], data["host_address"], port),
        reply_markup=panel_host_create_confirm_keyboard(lang, panel_id, tag_index),
    )


@router.callback_query(PanelHostCreateStates.confirming, F.data.startswith("phost:newcnf:"))
async def cb_host_create_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id, tag_index = data["panel_id"], data["tag_index"]
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    new_host = new_host_entry(data["host_remark"], data["host_address"], data.get("host_port"))
    try:
        token = await marzban_login(panel["url"], panel["username"], panel["password"])
        hosts_map = await marzban_get_hosts(panel["url"], token)
        tag = sorted(hosts_map.keys())[tag_index]
        hosts_map[tag].append(new_host)
        await marzban_set_hosts(panel["url"], token, hosts_map)
    except (PanelAPIError, IndexError) as exc:
        await state.clear()
        reason = str(exc) if isinstance(exc, PanelAPIError) else "bad_response"
        await callback.message.edit_text(
            texts.action_error_text(lang, reason), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.create_host_success_text(lang, new_host["remark"]),
        reply_markup=panel_hosts_list_keyboard(lang, panel_id, tag_index, hosts_map[tag]),
    )


# --- Inbound management (3X-UI only) ---
#
# Creating a brand-new inbound isn't offered here: a working, secure
# inbound needs protocol-specific settings (VLESS/VMess/Trojan client
# fields, TLS or REALITY key material, ...) that are best generated and
# reviewed in the panel's own UI rather than guessed at over chat. Editing
# an existing inbound's remark/port, enabling/disabling it, and deleting
# it are all safe, protocol-agnostic operations that don't require
# touching its settings/streamSettings at all.


def _find_inbound(inbounds: list[dict], inbound_id: int) -> dict | None:
    return next((ib for ib in inbounds if ib.get("id") == inbound_id), None)


async def _render_inbounds_screen(callback: CallbackQuery, lang: str, panel_id: str) -> None:
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await _show_panel_list(callback, lang)
        return

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    clients_by_id = {ib.get("id"): inbound_client_count(ib) for ib in inbounds}
    await callback.message.edit_text(
        texts.inbounds_list_text(lang, panel, inbounds),
        reply_markup=panel_inbounds_keyboard(lang, panel_id, inbounds, clients_by_id),
    )


@router.callback_query(F.data.startswith("pdash:inbounds:"))
async def cb_dashboard_inbounds(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    panel_id = callback.data.split(":", 2)[2]
    await _render_inbounds_screen(callback, lang, panel_id)
    await callback.answer()


@router.callback_query(F.data.startswith("pinb:view:"))
async def cb_inbound_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, panel_id, inbound_id_raw = callback.data.split(":", 3)
    inbound_id = int(inbound_id_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    inbound = _find_inbound(inbounds, inbound_id)
    if not inbound:
        await _render_inbounds_screen(callback, lang, panel_id)
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.inbound_detail_text(lang, panel, inbound, inbound_client_count(inbound)),
        reply_markup=panel_inbound_detail_keyboard(lang, panel_id, inbound_id, bool(inbound.get("enable", True))),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pinb:editstart:"))
async def cb_inbound_edit_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, panel_id, inbound_id_raw = callback.data.split(":", 3)
    inbound_id = int(inbound_id_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel or panel["type"] != "3xui":
        await callback.answer()
        return
    await state.clear()
    await state.update_data(panel_id=panel_id, inbound_id=inbound_id)
    await state.set_state(PanelInboundEditStates.waiting_fields)
    await callback.message.edit_text(
        texts.inbound_edit_prompt_text(lang, panel),
        reply_markup=panel_inbound_cancel_keyboard(lang, panel_id, inbound_id),
    )
    await callback.answer()


@router.message(PanelInboundEditStates.waiting_fields)
async def process_inbound_fields(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id, inbound_id = data["panel_id"], data["inbound_id"]
    panel = await panel_store.get(message.from_user.id, panel_id)
    if not panel:
        await state.clear()
        return

    try:
        updates = parse_inbound_fields_input(message.text or "")
    except InboundFieldsError as exc:
        await message.answer(
            texts.inbound_fields_error_text(lang, str(exc)),
            reply_markup=panel_inbound_cancel_keyboard(lang, panel_id, inbound_id),
        )
        return

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
    except PanelAPIError as exc:
        await state.clear()
        await message.answer(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    inbound = _find_inbound(inbounds, inbound_id)
    if not inbound:
        await state.clear()
        await message.answer(
            texts.action_error_text(lang, "bad_response"),
            reply_markup=panel_dashboard_back_keyboard(lang, panel_id),
        )
        return
    inbound = dict(inbound)
    inbound.update(updates)

    await state.update_data(pending_updates=updates)
    await state.set_state(PanelInboundEditStates.confirming)
    await message.answer(
        texts.inbound_edit_confirm_text(lang, panel, inbound),
        reply_markup=panel_inbound_edit_confirm_keyboard(lang, panel_id, inbound_id),
    )


@router.callback_query(PanelInboundEditStates.confirming, F.data.startswith("pinb:editcnf:"))
async def cb_inbound_edit_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    panel_id, inbound_id = data["panel_id"], data["inbound_id"]
    updates = data.get("pending_updates", {})
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await state.clear()
        await callback.answer()
        return
    await callback.answer()

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
        inbound = _find_inbound(inbounds, inbound_id)
        if not inbound:
            raise PanelAPIError("bad_response")
        inbound = dict(inbound)
        inbound.update(updates)
        await threexui_update_inbound(panel["url"], cookies, inbound)
    except PanelAPIError as exc:
        await state.clear()
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await state.clear()
    await callback.message.edit_text(
        texts.inbound_edit_success_text(lang),
        reply_markup=panel_inbound_detail_keyboard(lang, panel_id, inbound_id, bool(inbound.get("enable", True))),
    )


@router.callback_query(F.data.startswith("pinb:toggle:"))
async def cb_inbound_toggle(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, inbound_id_raw = callback.data.split(":", 3)
    inbound_id = int(inbound_id_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
        inbound = _find_inbound(inbounds, inbound_id)
        if not inbound:
            raise PanelAPIError("bad_response")
        inbound = dict(inbound)
        inbound["enable"] = not bool(inbound.get("enable", True))
        await threexui_update_inbound(panel["url"], cookies, inbound)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.edit_text(
        texts.inbound_toggle_success_text(lang, inbound["enable"]),
        reply_markup=panel_inbound_detail_keyboard(lang, panel_id, inbound_id, inbound["enable"]),
    )


@router.callback_query(F.data.startswith("pinb:delask:"))
async def cb_inbound_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, inbound_id_raw = callback.data.split(":", 3)
    inbound_id = int(inbound_id_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        inbounds = await threexui_get_inbounds(panel["url"], cookies)
        inbound = _find_inbound(inbounds, inbound_id)
        remark = str(inbound.get("remark") or f"#{inbound_id}") if inbound else f"#{inbound_id}"
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.inbound_delete_confirm_text(lang, panel, remark),
        reply_markup=panel_inbound_delete_confirm_keyboard(lang, panel_id, inbound_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pinb:delcnf:"))
async def cb_inbound_delete_confirm(callback: CallbackQuery, lang: str) -> None:
    _, _, panel_id, inbound_id_raw = callback.data.split(":", 3)
    inbound_id = int(inbound_id_raw)
    panel = await panel_store.get(callback.from_user.id, panel_id)
    if not panel:
        await callback.answer()
        return
    await callback.answer()

    try:
        cookies = await threexui_login(panel["url"], panel["username"], panel["password"])
        await threexui_delete_inbound(panel["url"], cookies, inbound_id)
    except PanelAPIError as exc:
        await callback.message.edit_text(
            texts.action_error_text(lang, str(exc)), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
        )
        return

    await callback.message.edit_text(
        texts.inbound_delete_success_text(lang), reply_markup=panel_dashboard_back_keyboard(lang, panel_id)
    )
