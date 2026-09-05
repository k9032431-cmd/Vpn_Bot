from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.cloud import (
    PAGE_SIZE,
    account_dashboard_keyboard,
    account_list_keyboard,
    account_remove_confirm_keyboard,
    backup_create_confirm_keyboard,
    backup_delete_confirm_keyboard,
    backup_detail_keyboard,
    backup_restore_confirm_keyboard,
    backups_list_keyboard,
    cloud_cancel_keyboard,
    cloud_error_keyboard,
    create_cancel_keyboard,
    create_confirm_keyboard,
    ip_add_confirm_keyboard,
    ip_remove_confirm_keyboard,
    ips_list_keyboard,
    paginated_pick_keyboard,
    plan_confirm_keyboard,
    plan_must_stop_keyboard,
    provider_list_keyboard,
    provider_soon_keyboard,
    server_delete_confirm_keyboard,
    server_detail_keyboard,
    servers_list_keyboard,
    storage_attach_confirm_keyboard,
    storage_delete_confirm_keyboard,
    storage_detach_confirm_keyboard,
    storage_detail_keyboard,
    storage_list_keyboard,
    storage_resize_confirm_keyboard,
    storage_wizard_cancel_keyboard,
)
from bot.services.cloud_store import cloud_store
from bot.services.upcloud_api import (
    UpCloudAPIError,
    storage_tier_for_plan,
    upcloud_add_ip,
    upcloud_attach_storage,
    upcloud_create_backup,
    upcloud_create_server,
    upcloud_delete_server,
    upcloud_delete_storage,
    upcloud_detach_storage,
    upcloud_get_account,
    upcloud_get_server,
    upcloud_list_backups,
    upcloud_list_plans,
    upcloud_list_servers,
    upcloud_list_templates,
    upcloud_list_zones,
    upcloud_login,
    upcloud_modify_server,
    upcloud_remove_ip,
    upcloud_resize_storage,
    upcloud_restart_server,
    upcloud_restore_backup,
    upcloud_start_server,
    upcloud_stop_server,
)
from bot.states.cloud_setup import (
    CloudDiskStates,
    CloudPlanChangeStates,
    CloudServerCreateStates,
    CloudSetupStates,
)
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


async def _get_account(callback: CallbackQuery, lang: str, account_id: str) -> dict | None:
    account = await cloud_store.get(callback.from_user.id, account_id)
    if not account:
        await _show_provider_list(callback, lang)
        await callback.answer()
    return account


async def _redisplay_server(callback: CallbackQuery, lang: str, account_id: str, server_uuid: str) -> None:
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.server_detail_text(lang, server), reply_markup=server_detail_keyboard(lang, account_id, server)
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
        await status_message.edit_text(
            texts.login_error_text(lang, str(exc), data["provider"]), reply_markup=cloud_error_keyboard(lang)
        )
        return
    except Exception:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, "bad_response", data["provider"]), reply_markup=cloud_error_keyboard(lang)
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
#
# Zones/plans/templates are all "pick one from a possibly-long catalog"
# screens with the identical shape: fetch the full list once, stash it in
# FSM state, then page through it 10-at-a-time. The page itself is never
# stored — each ◀️/▶️ tap just re-renders the same stashed list at the
# requested page, so there's nothing to go stale.


def _zone_options(zones: list[dict]) -> list[tuple[str, str]]:
    return [(f"{z['description']} ({z['id']})", f"ccreate:zone:{i}") for i, z in enumerate(zones)]


def _plan_options(plans: list[dict]) -> list[tuple[str, str]]:
    return [
        (f"{p['name']} ({p['core_number']} CPU / {p['memory_amount']} MB)", f"ccreate:plan:{i}")
        for i, p in enumerate(plans)
    ]


def _template_options(templates: list[dict]) -> list[tuple[str, str]]:
    return [(tpl["title"], f"ccreate:tmpl:{i}") for i, tpl in enumerate(templates)]


async def _render_create_page(
    callback: CallbackQuery,
    lang: str,
    header_fn,
    options: list[tuple[str, str]],
    page: int,
    nav_prefix: str,
    cancel_callback: str = "ccreate:cancel",
) -> None:
    total_pages = max(1, -(-len(options) // PAGE_SIZE))
    page = max(0, min(page, total_pages - 1))
    await callback.message.edit_text(
        header_fn(lang, page, total_pages),
        reply_markup=paginated_pick_keyboard(lang, options, page, nav_prefix, cancel_callback),
    )


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
    zone_dicts = [{"id": z.id, "description": z.description} for z in zones]
    await state.update_data(account_id=account_id, zones=zone_dicts)
    await state.set_state(CloudServerCreateStates.choosing_zone)
    await _render_create_page(callback, lang, texts.create_choose_zone_text, _zone_options(zone_dicts), 0, "ccreate:zonepage")


@router.callback_query(F.data.startswith("ccreate:zonepage:"), CloudServerCreateStates.choosing_zone)
async def cb_create_zone_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(callback, lang, texts.create_choose_zone_text, _zone_options(data["zones"]), page, "ccreate:zonepage")


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

    plan_dicts = [{"name": p.name, "core_number": p.core_number, "memory_amount": p.memory_amount} for p in plans]
    await state.update_data(zone=zone["id"], plans=plan_dicts)
    await state.set_state(CloudServerCreateStates.choosing_plan)
    await _render_create_page(callback, lang, texts.create_choose_plan_text, _plan_options(plan_dicts), 0, "ccreate:planpage")


@router.callback_query(F.data.startswith("ccreate:planpage:"), CloudServerCreateStates.choosing_plan)
async def cb_create_plan_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(callback, lang, texts.create_choose_plan_text, _plan_options(data["plans"]), page, "ccreate:planpage")


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

    template_dicts = [{"uuid": tpl.uuid, "title": tpl.title} for tpl in templates]
    await state.update_data(plan=plan["name"], templates=template_dicts)
    await state.set_state(CloudServerCreateStates.choosing_template)
    await _render_create_page(
        callback, lang, texts.create_choose_template_text, _template_options(template_dicts), 0, "ccreate:tmplpage"
    )


@router.callback_query(F.data.startswith("ccreate:tmplpage:"), CloudServerCreateStates.choosing_template)
async def cb_create_template_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(
        callback, lang, texts.create_choose_template_text, _template_options(data["templates"]), page, "ccreate:tmplpage"
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


# --- Plan change ---


@router.callback_query(F.data.startswith("cplan:start:"))
async def cb_plan_start(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    if server.state != "stopped":
        await callback.message.edit_text(
            texts.plan_must_stop_text(lang), reply_markup=plan_must_stop_keyboard(lang, account_id, server_uuid)
        )
        return

    try:
        plans = await upcloud_list_plans(account["username"], account["password"])
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    plan_names = [p.name for p in plans]
    await state.clear()
    await state.update_data(account_id=account_id, server_uuid=server_uuid, current_plan=server.plan, plans=plan_names)
    await state.set_state(CloudPlanChangeStates.choosing_plan)
    options = [(name, f"cplan:pick:{i}") for i, name in enumerate(plan_names)]
    await _render_create_page(
        callback,
        lang,
        lambda plan_lang, page, total: texts.plan_choose_text(plan_lang, server.plan, page, total),
        options,
        0,
        "cplan:page",
        "cplan:cancel",
    )


@router.callback_query(F.data.startswith("cplan:page:"), CloudPlanChangeStates.choosing_plan)
async def cb_plan_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    options = [(name, f"cplan:pick:{i}") for i, name in enumerate(data["plans"])]
    await _render_create_page(
        callback,
        lang,
        lambda plan_lang, p, total: texts.plan_choose_text(plan_lang, data["current_plan"], p, total),
        options,
        page,
        "cplan:page",
        "cplan:cancel",
    )


@router.callback_query(F.data == "cplan:cancel", CloudPlanChangeStates)
async def cb_plan_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.answer()
    await _redisplay_server(callback, lang, data["account_id"], data["server_uuid"])


@router.callback_query(F.data.startswith("cplan:pick:"), CloudPlanChangeStates.choosing_plan)
async def cb_plan_pick(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    new_plan = data["plans"][index]
    await state.update_data(new_plan=new_plan)
    await state.set_state(CloudPlanChangeStates.confirming)
    await callback.message.edit_text(
        texts.plan_confirm_text(lang, data["current_plan"], new_plan), reply_markup=plan_confirm_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "cplan:confirm", CloudPlanChangeStates.confirming)
async def cb_plan_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account = await _get_account(callback, lang, data["account_id"])
    if not account:
        await state.clear()
        return
    await callback.answer()
    try:
        server = await upcloud_modify_server(
            account["username"], account["password"], data["server_uuid"], plan=data["new_plan"]
        )
    except UpCloudAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await state.clear()
    await callback.message.edit_text(
        f"{texts.plan_changed_text(lang)}\n\n{texts.server_detail_text(lang, server)}",
        reply_markup=server_detail_keyboard(lang, data["account_id"], server),
    )


# --- Storage / disks ---


async def _show_storage_list(callback: CallbackQuery, lang: str, account: dict, account_id: str, server_uuid: str) -> None:
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.storage_header_text(lang, server, bool(server.storage_devices)),
        reply_markup=storage_list_keyboard(lang, account_id, server_uuid, server.storage_devices),
    )


@router.callback_query(F.data.startswith("csto:list:"))
async def cb_storage_list(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    await _show_storage_list(callback, lang, account, account_id, server_uuid)


@router.callback_query(F.data.startswith("csto:view:"))
async def cb_storage_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    if index >= len(server.storage_devices):
        await callback.answer()
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    storage = server.storage_devices[index]
    await callback.answer()
    await callback.message.edit_text(
        texts.storage_detail_text(lang, storage),
        reply_markup=storage_detail_keyboard(lang, account_id, server_uuid, index),
    )


class _ResolveFailed(Exception):
    """Raised by the _resolve_* helpers once they've already rendered an
    error message on a failed API call — callers just stop on catching it."""


async def _resolve_storage(callback: CallbackQuery, lang: str, account: dict, server_uuid: str, index: int):
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        raise _ResolveFailed from exc
    if index >= len(server.storage_devices):
        return None
    return server.storage_devices[index]


@router.callback_query(F.data.startswith("csto:add:"))
async def cb_storage_add(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await state.clear()
    await state.update_data(account_id=account_id, server_uuid=server_uuid, server_plan=server.plan)
    await state.set_state(CloudDiskStates.waiting_size)
    await callback.answer()
    await callback.message.edit_text(
        texts.storage_waiting_size_text(lang), reply_markup=storage_wizard_cancel_keyboard(lang, "csto:cancel_attach")
    )


@router.callback_query(F.data == "csto:cancel_attach", CloudDiskStates)
async def cb_storage_add_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.answer()
    account = await _get_account(callback, lang, data["account_id"])
    if not account:
        return
    await _show_storage_list(callback, lang, account, data["account_id"], data["server_uuid"])


@router.message(CloudDiskStates.waiting_size)
async def process_disk_size(message: Message, state: FSMContext, lang: str) -> None:
    raw = message.text.strip() if message.text else ""
    if not raw.isdigit() or not (10 <= int(raw) <= 4096):
        await message.answer(
            texts.storage_invalid_size_text(lang), reply_markup=storage_wizard_cancel_keyboard(lang, "csto:cancel_attach")
        )
        return
    await state.update_data(size=int(raw))
    await state.set_state(CloudDiskStates.confirming_attach)
    await message.answer(texts.storage_confirm_attach_text(lang, int(raw)), reply_markup=storage_attach_confirm_keyboard(lang))


@router.callback_query(F.data == "csto:confirm_attach", CloudDiskStates.confirming_attach)
async def cb_storage_attach_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account = await _get_account(callback, lang, data["account_id"])
    if not account:
        await state.clear()
        return
    await callback.answer()
    try:
        server = await upcloud_attach_storage(
            account["username"],
            account["password"],
            data["server_uuid"],
            title=f"disk-{data['size']}gb",
            size=data["size"],
            tier=storage_tier_for_plan(data["server_plan"]),
        )
    except UpCloudAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await state.clear()
    await callback.message.edit_text(
        texts.storage_attached_text(lang),
        reply_markup=storage_list_keyboard(lang, data["account_id"], data["server_uuid"], server.storage_devices),
    )


@router.callback_query(F.data.startswith("csto:rsz:"))
async def cb_storage_resize_ask(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    if storage is None:
        await callback.answer()
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return

    await state.clear()
    await state.update_data(
        account_id=account_id,
        server_uuid=server_uuid,
        index=index,
        storage_uuid=storage.uuid,
        storage_title=storage.title,
        current_size=storage.size,
    )
    await state.set_state(CloudDiskStates.waiting_resize_size)
    await callback.answer()
    await callback.message.edit_text(
        texts.storage_waiting_resize_text(lang, storage.size),
        reply_markup=storage_wizard_cancel_keyboard(lang, "csto:cancel_resize"),
    )


@router.callback_query(F.data == "csto:cancel_resize", CloudDiskStates)
async def cb_storage_resize_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.clear()
    await callback.answer()
    account_id, server_uuid, index = data["account_id"], data["server_uuid"], data["index"]
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        return
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    await callback.message.edit_text(
        texts.storage_detail_text(lang, storage), reply_markup=storage_detail_keyboard(lang, account_id, server_uuid, index)
    )


@router.message(CloudDiskStates.waiting_resize_size)
async def process_disk_resize(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    raw = message.text.strip() if message.text else ""
    if not raw.isdigit() or not (data["current_size"] < int(raw) <= 10240):
        await message.answer(
            texts.storage_invalid_size_text(lang), reply_markup=storage_wizard_cancel_keyboard(lang, "csto:cancel_resize")
        )
        return
    await state.update_data(new_size=int(raw))
    await state.set_state(CloudDiskStates.confirming_resize)
    await message.answer(
        texts.storage_confirm_resize_text(lang, data["storage_title"], data["current_size"], int(raw)),
        reply_markup=storage_resize_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "csto:confirm_resize", CloudDiskStates.confirming_resize)
async def cb_storage_resize_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account = await _get_account(callback, lang, data["account_id"])
    if not account:
        await state.clear()
        return
    await callback.answer()
    try:
        await upcloud_resize_storage(account["username"], account["password"], data["storage_uuid"], data["new_size"])
    except UpCloudAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    account_id, server_uuid, index = data["account_id"], data["server_uuid"], data["index"]
    await state.clear()
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        return
    await callback.message.edit_text(
        texts.storage_resized_text(lang),
        reply_markup=storage_detail_keyboard(lang, account_id, server_uuid, index)
        if storage
        else storage_list_keyboard(lang, account_id, server_uuid, []),
    )


@router.callback_query(F.data.startswith("csto:dt:"))
async def cb_storage_detach_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    await callback.message.edit_text(
        texts.storage_detach_confirm_text(lang, storage),
        reply_markup=storage_detach_confirm_keyboard(lang, account_id, server_uuid, index),
    )


@router.callback_query(F.data.startswith("csto:dtc:"))
async def cb_storage_detach(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    try:
        await upcloud_detach_storage(account["username"], account["password"], server_uuid, storage.uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.storage_detached_text(lang), reply_markup=None)
    await _show_storage_list(callback, lang, account, account_id, server_uuid)


@router.callback_query(F.data.startswith("csto:del:"))
async def cb_storage_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    await callback.message.edit_text(
        texts.storage_delete_confirm_text(lang, storage),
        reply_markup=storage_delete_confirm_keyboard(lang, account_id, server_uuid, index),
    )


@router.callback_query(F.data.startswith("csto:delc:"))
async def cb_storage_delete(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    try:
        await upcloud_delete_storage(account["username"], account["password"], storage.uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.storage_deleted_text(lang), reply_markup=None)
    await _show_storage_list(callback, lang, account, account_id, server_uuid)


# --- Backups ---


async def _show_backups(callback: CallbackQuery, lang: str, account: dict, account_id: str, server_uuid: str, index: int, storage) -> None:
    try:
        backups = await upcloud_list_backups(account["username"], account["password"], storage.uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.backups_header_text(lang, storage, bool(backups)),
        reply_markup=backups_list_keyboard(lang, account_id, server_uuid, index, backups),
    )


@router.callback_query(F.data.startswith("cbak:list:"))
async def cb_backups_list(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)


@router.callback_query(F.data.startswith("cbak:mk:"))
async def cb_backup_create_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    await callback.message.edit_text(
        texts.backup_create_confirm_text(lang, storage),
        reply_markup=backup_create_confirm_keyboard(lang, account_id, server_uuid, index),
    )


@router.callback_query(F.data.startswith("cbak:mkc:"))
async def cb_backup_create(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    try:
        await upcloud_create_backup(account["username"], account["password"], storage.uuid, title=f"{storage.title}-backup")
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.backup_created_text(lang), reply_markup=None)
    await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)


async def _resolve_backup(callback: CallbackQuery, lang: str, account: dict, storage_uuid: str, backup_index: int):
    try:
        backups = await upcloud_list_backups(account["username"], account["password"], storage_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        raise _ResolveFailed from exc
    if backup_index >= len(backups):
        return None
    return backups[backup_index]


async def _resolve_storage_and_backup(callback: CallbackQuery, lang: str, account: dict, server_uuid: str, index: int, backup_index: int):
    """Resolves both levels for a backup-scoped callback; returns (storage, backup),
    with either possibly None if the list moved (e.g. deleted from elsewhere)."""
    storage = await _resolve_storage(callback, lang, account, server_uuid, index)
    if storage is None:
        return None, None
    backup = await _resolve_backup(callback, lang, account, storage.uuid, backup_index)
    return storage, backup


@router.callback_query(F.data.startswith("cbak:view:"))
async def cb_backup_view(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw, backup_index_raw = callback.data.split(":", 5)
    index, backup_index = int(index_raw), int(backup_index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage, backup = await _resolve_storage_and_backup(callback, lang, account, server_uuid, index, backup_index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    if backup is None:
        await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)
        return
    await callback.message.edit_text(
        texts.backup_detail_text(lang, backup),
        reply_markup=backup_detail_keyboard(lang, account_id, server_uuid, index, backup_index),
    )


@router.callback_query(F.data.startswith("cbak:rs:"))
async def cb_backup_restore_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw, backup_index_raw = callback.data.split(":", 5)
    index, backup_index = int(index_raw), int(backup_index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage, backup = await _resolve_storage_and_backup(callback, lang, account, server_uuid, index, backup_index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    if backup is None:
        await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)
        return
    await callback.message.edit_text(
        texts.backup_restore_confirm_text(lang, backup),
        reply_markup=backup_restore_confirm_keyboard(lang, account_id, server_uuid, index, backup_index),
    )


@router.callback_query(F.data.startswith("cbak:rsc:"))
async def cb_backup_restore(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw, backup_index_raw = callback.data.split(":", 5)
    index, backup_index = int(index_raw), int(backup_index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage, backup = await _resolve_storage_and_backup(callback, lang, account, server_uuid, index, backup_index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    if backup is None:
        await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)
        return
    try:
        await upcloud_restore_backup(account["username"], account["password"], backup.uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.backup_restored_text(lang), reply_markup=None)
    await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)


@router.callback_query(F.data.startswith("cbak:dl:"))
async def cb_backup_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw, backup_index_raw = callback.data.split(":", 5)
    index, backup_index = int(index_raw), int(backup_index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage, backup = await _resolve_storage_and_backup(callback, lang, account, server_uuid, index, backup_index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    if backup is None:
        await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)
        return
    await callback.message.edit_text(
        texts.backup_delete_confirm_text(lang, backup),
        reply_markup=backup_delete_confirm_keyboard(lang, account_id, server_uuid, index, backup_index),
    )


@router.callback_query(F.data.startswith("cbak:dlc:"))
async def cb_backup_delete(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw, backup_index_raw = callback.data.split(":", 5)
    index, backup_index = int(index_raw), int(backup_index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        storage, backup = await _resolve_storage_and_backup(callback, lang, account, server_uuid, index, backup_index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if storage is None:
        await _show_storage_list(callback, lang, account, account_id, server_uuid)
        return
    if backup is None:
        await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)
        return
    try:
        await upcloud_delete_storage(account["username"], account["password"], backup.uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.backup_deleted_text(lang), reply_markup=None)
    await _show_backups(callback, lang, account, account_id, server_uuid, index, storage)


# --- IP addresses ---


async def _show_ips(callback: CallbackQuery, lang: str, account: dict, account_id: str, server_uuid: str) -> None:
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    public_ips = [ip for ip in server.ip_addresses if ip.access == "public"]
    await callback.message.edit_text(
        texts.ips_header_text(lang, server, bool(public_ips)),
        reply_markup=ips_list_keyboard(lang, account_id, server_uuid, public_ips),
    )


@router.callback_query(F.data.startswith("cip:list:"))
async def cb_ips_list(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    await _show_ips(callback, lang, account, account_id, server_uuid)


@router.callback_query(F.data.startswith("cip:add:"))
async def cb_ip_add_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    await callback.message.edit_text(
        texts.ip_add_confirm_text(lang, server), reply_markup=ip_add_confirm_keyboard(lang, account_id, server_uuid)
    )


@router.callback_query(F.data.startswith("cip:addc:"))
async def cb_ip_add(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    try:
        ip = await upcloud_add_ip(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.ip_added_text(lang, ip.address), reply_markup=None)
    await _show_ips(callback, lang, account, account_id, server_uuid)


async def _resolve_public_ip(account: dict, server_uuid: str, index: int):
    server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    public_ips = [ip for ip in server.ip_addresses if ip.access == "public"]
    if index >= len(public_ips):
        return None, server
    return public_ips[index], server


@router.callback_query(F.data.startswith("cip:rm:"))
async def cb_ip_remove_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        ip, server = await _resolve_public_ip(account, server_uuid, index)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    if ip is None:
        await _show_ips(callback, lang, account, account_id, server_uuid)
        return
    await callback.message.edit_text(
        texts.ip_remove_confirm_text(lang, server, ip.address),
        reply_markup=ip_remove_confirm_keyboard(lang, account_id, server_uuid, index),
    )


@router.callback_query(F.data.startswith("cip:rmc:"))
async def cb_ip_remove(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, server_uuid, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        ip, _server = await _resolve_public_ip(account, server_uuid, index)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    if ip is None:
        await _show_ips(callback, lang, account, account_id, server_uuid)
        return
    try:
        await upcloud_remove_ip(account["username"], account["password"], ip.address)
    except UpCloudAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.ip_removed_text(lang), reply_markup=None)
    await _show_ips(callback, lang, account, account_id, server_uuid)
