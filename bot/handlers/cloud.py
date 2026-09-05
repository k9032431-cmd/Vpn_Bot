from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.cloud import (
    account_dashboard_keyboard,
    account_list_keyboard,
    account_remove_confirm_keyboard,
    cloud_cancel_keyboard,
    cloud_error_keyboard,
    create_cancel_keyboard,
    create_confirm_keyboard,
    create_pick_keyboard,
    provider_list_keyboard,
    provider_soon_keyboard,
    server_delete_confirm_keyboard,
    server_detail_keyboard,
    servers_list_keyboard,
)
from bot.services.cloud_store import cloud_store
from bot.services.upcloud_api import (
    UpCloudAPIError,
    upcloud_create_server,
    upcloud_delete_server,
    upcloud_get_account,
    upcloud_get_server,
    upcloud_list_plans,
    upcloud_list_servers,
    upcloud_list_templates,
    upcloud_list_zones,
    upcloud_login,
    upcloud_restart_server,
    upcloud_start_server,
    upcloud_stop_server,
)
from bot.states.cloud_setup import CloudServerCreateStates, CloudSetupStates
from bot.texts import cloud as texts
from bot.texts.cloud import ACTIVE_PROVIDERS, PROVIDERS

router = Router(name="cloud")

HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-.]{0,251}[a-zA-Z0-9])?$")


async def _login(provider: str, username: str, password: str):
    if provider == "upcloud":
        return await upcloud_login(username, password)
    raise UpCloudAPIError("bad_response")


async def _show_provider_list(callback: CallbackQuery, lang: str) -> None:
    await callback.message.edit_text(texts.provider_list_text(lang), reply_markup=provider_list_keyboard(lang))


async def _show_account_list(callback: CallbackQuery, lang: str, provider: str) -> None:
    accounts = await cloud_store.list(callback.from_user.id, provider)
    await callback.message.edit_text(
        texts.account_list_text(lang, provider, accounts),
        reply_markup=account_list_keyboard(lang, provider, accounts),
    )


async def _show_servers(callback: CallbackQuery, lang: str, account: dict) -> None:
    try:
        servers = await upcloud_list_servers(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.servers_header_text(lang, account, bool(servers)),
        reply_markup=servers_list_keyboard(lang, account["id"], servers),
    )


# --- Provider list & account connect ---


@router.callback_query(F.data == "menu:cloud_vps")
async def cb_cloud_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await _show_provider_list(callback, lang)
    await callback.answer()


@router.callback_query(F.data.in_({f"cprov:{name}" for name in PROVIDERS}))
async def cb_choose_provider(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    provider = callback.data.split(":", 1)[1]
    await state.clear()
    if provider not in ACTIVE_PROVIDERS:
        await callback.message.edit_text(texts.provider_soon_text(lang), reply_markup=provider_soon_keyboard(lang))
        await callback.answer()
        return
    await _show_account_list(callback, lang, provider)
    await callback.answer()


@router.callback_query(F.data.in_({f"cadd:{name}" for name in ACTIVE_PROVIDERS}))
async def cb_add_account(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    provider = callback.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(provider=provider)
    await state.set_state(CloudSetupStates.waiting_username)
    await callback.message.edit_text(
        texts.step_username_text(lang, provider), reply_markup=cloud_cancel_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "csetup:cancel")
async def cb_cancel_setup(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.clear()
    provider = data.get("provider", "upcloud")
    await _show_account_list(callback, lang, provider)
    await callback.answer()


@router.message(CloudSetupStates.waiting_username)
async def process_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    if not username:
        await message.answer(texts.step_username_text(lang, (await state.get_data())["provider"]))
        return
    await state.update_data(username=username)
    await state.set_state(CloudSetupStates.waiting_password)
    await message.answer(texts.step_password_text(lang), reply_markup=cloud_cancel_keyboard(lang))


@router.message(CloudSetupStates.waiting_password)
async def process_password(message: Message, state: FSMContext, lang: str) -> None:
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if not password:
        await message.answer(texts.empty_password_text(lang), reply_markup=cloud_cancel_keyboard(lang))
        return

    data = await state.update_data(password=password)
    await state.set_state(CloudSetupStates.connecting)
    status_message = await message.answer(texts.connecting_text(lang))

    try:
        await _login(data["provider"], data["username"], password)
    except UpCloudAPIError as exc:
        await state.clear()
        await status_message.edit_text(texts.login_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    except Exception:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, "bad_response"), reply_markup=cloud_error_keyboard(lang)
        )
        return

    account_id = await cloud_store.add(message.from_user.id, data["provider"], data["username"], password)
    await state.clear()
    await status_message.edit_text(
        texts.connected_text(lang, data["provider"]),
        reply_markup=account_dashboard_keyboard(lang, account_id, data["provider"]),
    )


# --- Account dashboard ---


@router.callback_query(F.data.startswith("cview:"))
async def cb_view_account(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    account_id = callback.data.split(":", 1)[1]
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        info = await upcloud_get_account(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.account_dashboard_text(lang, account, info.credits),
        reply_markup=account_dashboard_keyboard(lang, account_id, account["provider"]),
    )


@router.callback_query(F.data.startswith("cacc:rmask:"))
async def cb_remove_account_ask(callback: CallbackQuery, lang: str) -> None:
    account_id = callback.data.split(":", 2)[2]
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.message.edit_text(
        texts.account_remove_confirm_text(lang, account),
        reply_markup=account_remove_confirm_keyboard(lang, account_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cacc:rm:"))
async def cb_remove_account(callback: CallbackQuery, lang: str) -> None:
    account_id = callback.data.split(":", 2)[2]
    await cloud_store.remove(callback.from_user.id, account_id)
    await callback.message.edit_text(texts.account_removed_text(lang), reply_markup=provider_list_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("cacc:servers:"))
async def cb_account_servers(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    account_id = callback.data.split(":", 2)[2]
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    await _show_servers(callback, lang, account)


# --- Server detail & actions ---


@router.callback_query(F.data.startswith("csrv:view:"))
async def cb_server_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.server_detail_text(lang, server), reply_markup=server_detail_keyboard(lang, account_id, server)
    )


async def _run_server_action(callback: CallbackQuery, lang: str, action, account_id: str, server_uuid: str) -> None:
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer(texts.server_action_ok_text(lang))
    try:
        server = await action(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.server_detail_text(lang, server), reply_markup=server_detail_keyboard(lang, account_id, server)
    )


@router.callback_query(F.data.startswith("csrv:start:"))
async def cb_server_start(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    await _run_server_action(callback, lang, upcloud_start_server, account_id, server_uuid)


@router.callback_query(F.data.startswith("csrv:stop:"))
async def cb_server_stop(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    await _run_server_action(callback, lang, upcloud_stop_server, account_id, server_uuid)


@router.callback_query(F.data.startswith("csrv:restart:"))
async def cb_server_restart(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    await _run_server_action(callback, lang, upcloud_restart_server, account_id, server_uuid)


@router.callback_query(F.data.startswith("csrv:delask:"))
async def cb_server_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.server_delete_confirm_text(lang, server),
        reply_markup=server_delete_confirm_keyboard(lang, account_id, server_uuid),
    )


@router.callback_query(F.data.startswith("csrv:del:"))
async def cb_server_delete(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        await upcloud_delete_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.server_deleted_text(lang), reply_markup=None)
    await _show_servers(callback, lang, account)


# --- Server creation ---


@router.callback_query(F.data.startswith("csrv:add:"))
async def cb_server_add(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    account_id = callback.data.split(":", 2)[2]
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        zones = await upcloud_list_zones(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    await state.clear()
    await state.update_data(account_id=account_id, zones=[{"id": z.id, "description": z.description} for z in zones])
    await state.set_state(CloudServerCreateStates.choosing_zone)
    options = [(f"{z.description} ({z.id})", f"ccreate:zone:{i}") for i, z in enumerate(zones)]
    await callback.message.edit_text(texts.create_choose_zone_text(lang), reply_markup=create_pick_keyboard(lang, options))


@router.callback_query(F.data == "ccreate:cancel", CloudServerCreateStates)
async def cb_create_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account_id = data.get("account_id")
    await state.clear()
    account = await cloud_store.get(callback.from_user.id, account_id) if account_id else None
    await callback.answer()
    if not account:
        await _show_provider_list(callback, lang)
        return
    await _show_servers(callback, lang, account)


@router.callback_query(F.data.startswith("ccreate:zone:"), CloudServerCreateStates.choosing_zone)
async def cb_create_pick_zone(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    zone = data["zones"][index]
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        plans = await upcloud_list_plans(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    await state.update_data(
        zone=zone["id"],
        plans=[{"name": p.name, "core_number": p.core_number, "memory_amount": p.memory_amount} for p in plans],
    )
    await state.set_state(CloudServerCreateStates.choosing_plan)
    options = [
        (f"{p.name} ({p.core_number} CPU / {p.memory_amount} MB)", f"ccreate:plan:{i}")
        for i, p in enumerate(plans)
    ]
    await callback.message.edit_text(texts.create_choose_plan_text(lang), reply_markup=create_pick_keyboard(lang, options))


@router.callback_query(F.data.startswith("ccreate:plan:"), CloudServerCreateStates.choosing_plan)
async def cb_create_pick_plan(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    plan = data["plans"][index]
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        templates = await upcloud_list_templates(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    # UpCloud's public template catalog can be long — show the most common
    # ones first, capped so the keyboard stays on one screen.
    templates = templates[:20]
    await state.update_data(
        plan=plan["name"],
        templates=[{"uuid": tpl.uuid, "title": tpl.title} for tpl in templates],
    )
    await state.set_state(CloudServerCreateStates.choosing_template)
    options = [(tpl.title, f"ccreate:tmpl:{i}") for i, tpl in enumerate(templates)]
    await callback.message.edit_text(
        texts.create_choose_template_text(lang), reply_markup=create_pick_keyboard(lang, options)
    )


@router.callback_query(F.data.startswith("ccreate:tmpl:"), CloudServerCreateStates.choosing_template)
async def cb_create_pick_template(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    template = data["templates"][index]
    await state.update_data(template_uuid=template["uuid"], template_title=template["title"])
    await state.set_state(CloudServerCreateStates.waiting_hostname)
    await callback.message.edit_text(texts.create_waiting_hostname_text(lang), reply_markup=create_cancel_keyboard(lang))
    await callback.answer()


@router.message(CloudServerCreateStates.waiting_hostname)
async def process_hostname(message: Message, state: FSMContext, lang: str) -> None:
    hostname = message.text.strip() if message.text else ""
    if not hostname or not HOSTNAME_RE.match(hostname) or len(hostname) > 253:
        await message.answer(texts.create_invalid_hostname_text(lang), reply_markup=create_cancel_keyboard(lang))
        return

    data = await state.update_data(hostname=hostname)
    await state.set_state(CloudServerCreateStates.confirming)
    await message.answer(
        texts.create_confirm_text(lang, hostname, data["zone"], data["plan"], data["template_title"]),
        reply_markup=create_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "ccreate:confirm", CloudServerCreateStates.confirming)
async def cb_create_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    await callback.message.edit_text(texts.creating_text(lang))

    try:
        server = await upcloud_create_server(
            account["username"],
            account["password"],
            zone=data["zone"],
            hostname=data["hostname"],
            title=data["hostname"],
            plan=data["plan"],
            template_uuid=data["template_uuid"],
        )
    except UpCloudAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    await state.clear()
    await callback.message.edit_text(
        texts.create_success_text(lang, server),
        reply_markup=server_detail_keyboard(lang, data["account_id"], server),
    )
