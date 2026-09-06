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
    azure_create_auth_method_keyboard,
    azure_create_cancel_keyboard,
    azure_create_confirm_keyboard,
    azure_password_mode_keyboard,
    azure_port_cancel_keyboard,
    azure_port_delete_confirm_keyboard,
    azure_port_protocol_keyboard,
    azure_ports_list_keyboard,
    azure_vm_delete_confirm_keyboard,
    azure_vm_detail_keyboard,
    azure_vm_reimage_confirm_keyboard,
    azure_vms_list_keyboard,
    azure_zone_keyboard,
    back_to_server_keyboard,
    backup_create_confirm_keyboard,
    backup_delete_confirm_keyboard,
    backup_detail_keyboard,
    backup_restore_confirm_keyboard,
    backups_list_keyboard,
    cloud_cancel_keyboard,
    cloud_error_keyboard,
    create_auth_method_keyboard,
    create_cancel_keyboard,
    create_confirm_keyboard,
    ip_add_confirm_keyboard,
    ip_remove_confirm_keyboard,
    ips_list_keyboard,
    must_stop_keyboard,
    paginated_pick_keyboard,
    plan_confirm_keyboard,
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
from bot.services.azure_api import (
    AzureAPIError,
    AzureCredentials,
    ImageInfo,
    azure_add_port_rule,
    azure_capacity_restricted_skus,
    azure_create_vm,
    azure_delete_port_rule,
    azure_delete_vm,
    azure_get_account,
    azure_get_hourly_price,
    azure_get_vm,
    azure_list_available_sizes,
    azure_list_images,
    azure_list_locations,
    azure_list_port_rules,
    azure_list_vms,
    azure_login,
    azure_reimage_vm,
    azure_restart_vm,
    azure_start_vm,
    azure_stop_vm,
    generate_azure_password,
    is_valid_azure_username,
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
    AzurePortStates,
    AzureSetupStates,
    AzureVMCreateStates,
    CloudDiskStates,
    CloudPlanChangeStates,
    CloudServerCreateStates,
    CloudSetupStates,
)
from bot.texts import cloud as texts
from bot.texts.cloud import ACTIVE_PROVIDERS, PROVIDERS

router = Router(name="cloud")

HOSTNAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9\-.]{0,251}[a-zA-Z0-9])?$")
SSH_PUBLIC_KEY_PREFIXES = ("ssh-rsa ", "ssh-ed25519 ", "ssh-dss ", "ecdsa-sha2-")
AZURE_VM_NAME_RE = re.compile(r"^(?!\d+$)[a-zA-Z0-9]([a-zA-Z0-9-]{0,62}[a-zA-Z0-9])?$")


def _is_valid_ssh_public_key(value: str) -> bool:
    return value.startswith(SSH_PUBLIC_KEY_PREFIXES)


def _azure_creds(account: dict) -> AzureCredentials:
    return AzureCredentials(
        tenant_id=account["tenant_id"],
        client_id=account["client_id"],
        client_secret=account["client_secret"],
        subscription_id=account["subscription_id"],
    )


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


async def _require_stopped(callback: CallbackQuery, lang: str, account_id: str, server, must_stop_text: str) -> bool:
    """Gates an action that needs a stopped server. Returns True if it's
    stopped and the caller can proceed. Otherwise shows the right screen —
    a "stop it first" prompt normally, or a wait-only screen when UpCloud
    itself has the server in 'maintenance' (where the Stop button would
    just fail with the same error) — and returns False."""
    if server.state == "stopped":
        return True
    if server.state == "maintenance":
        await callback.message.edit_text(
            texts.server_in_maintenance_text(lang), reply_markup=back_to_server_keyboard(lang, account_id, server.uuid)
        )
    else:
        await callback.message.edit_text(must_stop_text, reply_markup=must_stop_keyboard(lang, account_id, server.uuid))
    return False


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
    if provider == "azure":
        await state.set_state(AzureSetupStates.waiting_tenant_id)
        await callback.message.edit_text(
            texts.azure_step_tenant_text(lang), reply_markup=cloud_cancel_keyboard(lang)
        )
        await callback.answer()
        return
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


@router.message(AzureSetupStates.waiting_tenant_id)
async def process_azure_tenant(message: Message, state: FSMContext, lang: str) -> None:
    value = message.text.strip() if message.text else ""
    if not value:
        await message.answer(texts.azure_empty_field_text(lang), reply_markup=cloud_cancel_keyboard(lang))
        return
    await state.update_data(tenant_id=value)
    await state.set_state(AzureSetupStates.waiting_client_id)
    await message.answer(texts.azure_step_client_id_text(lang), reply_markup=cloud_cancel_keyboard(lang))


@router.message(AzureSetupStates.waiting_client_id)
async def process_azure_client_id(message: Message, state: FSMContext, lang: str) -> None:
    value = message.text.strip() if message.text else ""
    if not value:
        await message.answer(texts.azure_empty_field_text(lang), reply_markup=cloud_cancel_keyboard(lang))
        return
    await state.update_data(client_id=value)
    await state.set_state(AzureSetupStates.waiting_client_secret)
    await message.answer(texts.azure_step_client_secret_text(lang), reply_markup=cloud_cancel_keyboard(lang))


@router.message(AzureSetupStates.waiting_client_secret)
async def process_azure_client_secret(message: Message, state: FSMContext, lang: str) -> None:
    value = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass
    if not value:
        await message.answer(texts.azure_empty_field_text(lang), reply_markup=cloud_cancel_keyboard(lang))
        return
    await state.update_data(client_secret=value)
    await state.set_state(AzureSetupStates.waiting_subscription_id)
    await message.answer(texts.azure_step_subscription_text(lang), reply_markup=cloud_cancel_keyboard(lang))


@router.message(AzureSetupStates.waiting_subscription_id)
async def process_azure_subscription(message: Message, state: FSMContext, lang: str) -> None:
    value = message.text.strip() if message.text else ""
    if not value:
        await message.answer(texts.azure_empty_field_text(lang), reply_markup=cloud_cancel_keyboard(lang))
        return

    data = await state.update_data(subscription_id=value)
    await state.set_state(AzureSetupStates.connecting)
    status_message = await message.answer(texts.connecting_text(lang))

    creds = AzureCredentials(
        tenant_id=data["tenant_id"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        subscription_id=value,
    )
    try:
        await azure_login(creds)
    except AzureAPIError as exc:
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, str(exc), "azure"), reply_markup=cloud_error_keyboard(lang)
        )
        return
    except Exception:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.login_error_text(lang, "bad_response", "azure"), reply_markup=cloud_error_keyboard(lang)
        )
        return

    account_id = await cloud_store.add(
        message.from_user.id,
        "azure",
        tenant_id=data["tenant_id"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        subscription_id=value,
    )
    await state.clear()
    await status_message.edit_text(
        texts.connected_text(lang, "azure"),
        reply_markup=account_dashboard_keyboard(lang, account_id, "azure"),
    )


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

    account_id = await cloud_store.add(
        message.from_user.id, data["provider"], username=data["username"], password=password
    )
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
    if account["provider"] == "azure":
        try:
            info = await azure_get_account(_azure_creds(account))
        except AzureAPIError as exc:
            await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
            return
        await callback.message.edit_text(
            texts.azure_account_dashboard_text(lang, account, info),
            reply_markup=account_dashboard_keyboard(lang, account_id, "azure"),
        )
        return
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
    if account["provider"] == "azure":
        await _show_azure_vms(callback, lang, account, account_id)
        return
    await _show_servers(callback, lang, account)


async def _show_azure_vms(callback: CallbackQuery, lang: str, account: dict, account_id: str) -> None:
    try:
        vms = await azure_list_vms(_azure_creds(account))
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.azure_vms_header_text(lang, account, bool(vms)),
        reply_markup=azure_vms_list_keyboard(lang, account_id, vms),
    )


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

    if not await _require_stopped(callback, lang, account_id, server, texts.delete_must_stop_text(lang)):
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

    await state.update_data(hostname=hostname)
    await state.set_state(CloudServerCreateStates.choosing_auth_method)
    await message.answer(
        texts.create_choose_auth_method_text(lang), reply_markup=create_auth_method_keyboard(lang)
    )


@router.callback_query(F.data == "ccreate:auth:password", CloudServerCreateStates.choosing_auth_method)
async def cb_create_choose_password_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(ssh_public_key=None)
    await _show_create_confirmation(callback.message, state, lang)
    await callback.answer()


@router.callback_query(F.data == "ccreate:auth:key", CloudServerCreateStates.choosing_auth_method)
async def cb_create_choose_key_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(CloudServerCreateStates.waiting_ssh_key)
    await callback.message.edit_text(
        texts.create_waiting_ssh_key_text(lang), reply_markup=create_cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(CloudServerCreateStates.waiting_ssh_key)
async def process_ssh_public_key(message: Message, state: FSMContext, lang: str) -> None:
    public_key = message.text.strip() if message.text else ""
    if not _is_valid_ssh_public_key(public_key):
        await message.answer(texts.create_invalid_ssh_key_text(lang), reply_markup=create_cancel_keyboard(lang))
        return

    await state.update_data(ssh_public_key=public_key)
    await _show_create_confirmation(message, state, lang)


async def _show_create_confirmation(target_message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(CloudServerCreateStates.confirming)
    auth_method = "key" if data.get("ssh_public_key") else "password"
    await target_message.answer(
        texts.create_confirm_text(lang, data["hostname"], data["zone"], data["plan"], data["template_title"], auth_method),
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

    ssh_public_key = data.get("ssh_public_key")
    try:
        server = await upcloud_create_server(
            account["username"],
            account["password"],
            zone=data["zone"],
            hostname=data["hostname"],
            title=data["hostname"],
            plan=data["plan"],
            template_uuid=data["template_uuid"],
            ssh_public_key=ssh_public_key,
        )
    except UpCloudAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    await state.clear()
    await callback.message.edit_text(
        texts.create_success_text(lang, server, ssh_key_used=bool(ssh_public_key)),
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

    if not await _require_stopped(callback, lang, account_id, server, texts.plan_must_stop_text(lang)):
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
        server = await upcloud_get_server(account["username"], account["password"], server_uuid)
    except UpCloudAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    if not await _require_stopped(callback, lang, account_id, server, texts.restore_must_stop_text(lang)):
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


# --- Azure: VM detail & actions ---


@router.callback_query(F.data.startswith("azvm:view:"))
async def cb_azure_vm_view(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    try:
        vm = await azure_get_vm(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.azure_vm_detail_text(lang, vm), reply_markup=azure_vm_detail_keyboard(lang, account_id, vm)
    )


async def _run_azure_vm_action(callback: CallbackQuery, lang: str, action, account_id: str, vm_name: str) -> None:
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer(texts.azure_vm_action_ok_text(lang))
    creds = _azure_creds(account)
    try:
        await action(creds, vm_name)
        vm = await azure_get_vm(creds, vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.azure_vm_detail_text(lang, vm), reply_markup=azure_vm_detail_keyboard(lang, account_id, vm)
    )


@router.callback_query(F.data.startswith("azvm:start:"))
async def cb_azure_vm_start(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    await _run_azure_vm_action(callback, lang, azure_start_vm, account_id, vm_name)


@router.callback_query(F.data.startswith("azvm:stop:"))
async def cb_azure_vm_stop(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    await _run_azure_vm_action(callback, lang, azure_stop_vm, account_id, vm_name)


@router.callback_query(F.data.startswith("azvm:restart:"))
async def cb_azure_vm_restart(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    await _run_azure_vm_action(callback, lang, azure_restart_vm, account_id, vm_name)


@router.callback_query(F.data.startswith("azvm:delask:"))
async def cb_azure_vm_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        vm = await azure_get_vm(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    await callback.message.edit_text(
        texts.azure_vm_delete_confirm_text(lang, vm),
        reply_markup=azure_vm_delete_confirm_keyboard(lang, account_id, vm_name),
    )


@router.callback_query(F.data.startswith("azvm:del:"))
async def cb_azure_vm_delete(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    try:
        await azure_delete_vm(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.azure_vm_deleted_text(lang), reply_markup=None)
    await _show_azure_vms(callback, lang, account, account_id)


# --- Azure: VM creation ---


def _azure_location_options(locations: list[dict]) -> list[tuple[str, str]]:
    return [
        (texts.azure_location_display(loc["name"], loc["display_name"]), f"azcreate:loc:{i}")
        for i, loc in enumerate(locations)
    ]


def _azure_format_memory(memory_mb: int) -> str:
    if memory_mb and memory_mb % 1024 == 0:
        return f"{memory_mb // 1024} GB"
    return f"{memory_mb} MB"


def _azure_size_options(sizes: list[dict]) -> list[tuple[str, str]]:
    options = []
    for i, s in enumerate(sizes):
        label = f"{s['name']} ({s['cores']} CPU / {_azure_format_memory(s['memory_mb'])})"
        price = s.get("price")
        if price is not None:
            label += f" — ~${price:.4f}/hr"
        options.append((label, f"azcreate:size:{i}"))
    return options


def _azure_image_options(images: list[dict]) -> list[tuple[str, str]]:
    return [(img["title"], f"azcreate:img:{i}") for i, img in enumerate(images)]


@router.callback_query(F.data.startswith("azvm:add:"))
async def cb_azure_vm_add(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    account_id = callback.data.split(":", 2)[2]
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    try:
        locations = await azure_list_locations(_azure_creds(account))
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    await state.clear()
    location_dicts = [{"name": loc.name, "display_name": loc.display_name} for loc in locations]
    await state.update_data(account_id=account_id, locations=location_dicts)
    await state.set_state(AzureVMCreateStates.choosing_location)
    await _render_create_page(
        callback, lang, texts.azure_create_choose_location_text, _azure_location_options(location_dicts),
        0, "azcreate:locpage", "azcreate:cancel",
    )


@router.callback_query(F.data.startswith("azcreate:locpage:"), AzureVMCreateStates.choosing_location)
async def cb_azure_create_location_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(
        callback, lang, texts.azure_create_choose_location_text, _azure_location_options(data["locations"]),
        page, "azcreate:locpage", "azcreate:cancel",
    )


@router.callback_query(F.data == "azcreate:cancel", AzureVMCreateStates)
async def cb_azure_create_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account_id = data.get("account_id")
    await state.clear()
    account = await cloud_store.get(callback.from_user.id, account_id) if account_id else None
    await callback.answer()
    if not account:
        await _show_provider_list(callback, lang)
        return
    await _show_azure_vms(callback, lang, account, account_id)


@router.callback_query(F.data.startswith("azcreate:loc:"), AzureVMCreateStates.choosing_location)
async def cb_azure_create_pick_location(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    location = data["locations"][index]
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        sizes = await azure_list_available_sizes(_azure_creds(account), location["name"])
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return

    size_dicts = []
    for s in sizes:
        price = await azure_get_hourly_price(s.name, location["name"])
        size_dicts.append({"name": s.name, "cores": s.cores, "memory_mb": s.memory_mb, "price": price, "zones": s.zones})
    await state.update_data(location=location["name"], location_display=location["display_name"], sizes=size_dicts)
    await state.set_state(AzureVMCreateStates.choosing_size)
    await _render_create_page(
        callback, lang, texts.azure_create_choose_size_text, _azure_size_options(size_dicts),
        0, "azcreate:sizepage", "azcreate:cancel",
    )


@router.callback_query(F.data.startswith("azcreate:sizepage:"), AzureVMCreateStates.choosing_size)
async def cb_azure_create_size_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(
        callback, lang, texts.azure_create_choose_size_text, _azure_size_options(data["sizes"]),
        page, "azcreate:sizepage", "azcreate:cancel",
    )


async def _show_azure_image_step(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    images = azure_list_images()
    image_dicts = [
        {"key": img.key, "title": img.title, "publisher": img.publisher, "offer": img.offer, "sku": img.sku, "version": img.version}
        for img in images
    ]
    await state.update_data(images=image_dicts)
    await state.set_state(AzureVMCreateStates.choosing_image)
    await _render_create_page(
        callback, lang, texts.azure_create_choose_image_text, _azure_image_options(image_dicts),
        0, "azcreate:imgpage", "azcreate:cancel",
    )


@router.callback_query(F.data.startswith("azcreate:size:"), AzureVMCreateStates.choosing_size)
async def cb_azure_create_pick_size(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    size = data["sizes"][index]
    await state.update_data(vm_size=size["name"])
    await callback.answer()

    zones = size.get("zones") or []
    if zones:
        # Azure Availability Zones are per-region *and* per-size — the same
        # location can support zones for one size but not another, exactly
        # like the zone dropdown on the Azure Portal only appears when the
        # chosen size actually supports it there.
        await state.set_state(AzureVMCreateStates.choosing_zone)
        await callback.message.edit_text(
            texts.azure_create_choose_zone_text(lang), reply_markup=azure_zone_keyboard(lang, zones)
        )
        return

    await state.update_data(zone=None)
    await _show_azure_image_step(callback, state, lang)


@router.callback_query(F.data.startswith("azcreate:zone:"), AzureVMCreateStates.choosing_zone)
async def cb_azure_create_pick_zone(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    raw = callback.data.split(":", 2)[2]
    zone = None if raw == "none" else raw
    await state.update_data(zone=zone)
    await callback.answer()
    await _show_azure_image_step(callback, state, lang)


@router.callback_query(F.data.startswith("azcreate:imgpage:"), AzureVMCreateStates.choosing_image)
async def cb_azure_create_image_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    page = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    await callback.answer()
    await _render_create_page(
        callback, lang, texts.azure_create_choose_image_text, _azure_image_options(data["images"]),
        page, "azcreate:imgpage", "azcreate:cancel",
    )


@router.callback_query(F.data.startswith("azcreate:img:"), AzureVMCreateStates.choosing_image)
async def cb_azure_create_pick_image(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    index = int(callback.data.split(":", 2)[2])
    data = await state.get_data()
    image = data["images"][index]
    await state.update_data(image_key=image["key"])
    await state.set_state(AzureVMCreateStates.waiting_hostname)
    await callback.message.edit_text(
        texts.azure_create_waiting_hostname_text(lang), reply_markup=azure_create_cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(AzureVMCreateStates.waiting_hostname)
async def process_azure_hostname(message: Message, state: FSMContext, lang: str) -> None:
    hostname = message.text.strip() if message.text else ""
    if not hostname or not AZURE_VM_NAME_RE.match(hostname) or len(hostname) > 64:
        await message.answer(texts.azure_create_invalid_hostname_text(lang), reply_markup=azure_create_cancel_keyboard(lang))
        return

    await state.update_data(hostname=hostname)
    await state.set_state(AzureVMCreateStates.waiting_username)
    await message.answer(
        texts.azure_create_waiting_username_text(lang), reply_markup=azure_create_cancel_keyboard(lang)
    )


@router.message(AzureVMCreateStates.waiting_username)
async def process_azure_username(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    if not is_valid_azure_username(username):
        await message.answer(texts.azure_create_invalid_username_text(lang), reply_markup=azure_create_cancel_keyboard(lang))
        return

    await state.update_data(admin_username=username)
    await state.set_state(AzureVMCreateStates.choosing_auth_method)
    await message.answer(
        texts.azure_create_choose_auth_method_text(lang), reply_markup=azure_create_auth_method_keyboard(lang)
    )


@router.callback_query(F.data == "azcreate:auth:password", AzureVMCreateStates.choosing_auth_method)
async def cb_azure_create_choose_password_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(ssh_public_key=None)
    await state.set_state(AzureVMCreateStates.choosing_password_mode)
    await callback.message.edit_text(
        texts.azure_create_choose_password_mode_text(lang), reply_markup=azure_password_mode_keyboard(lang)
    )
    await callback.answer()


@router.callback_query(F.data == "azcreate:pwmode:generate", AzureVMCreateStates.choosing_password_mode)
async def cb_azure_create_password_generate(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(custom_password=None)
    await _show_azure_create_confirmation(callback.message, state, lang)
    await callback.answer()


@router.callback_query(F.data == "azcreate:pwmode:custom", AzureVMCreateStates.choosing_password_mode)
async def cb_azure_create_password_custom(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(AzureVMCreateStates.waiting_custom_password)
    await callback.message.edit_text(
        texts.azure_create_waiting_custom_password_text(lang), reply_markup=azure_create_cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(AzureVMCreateStates.waiting_custom_password)
async def process_azure_custom_password(message: Message, state: FSMContext, lang: str) -> None:
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if not (12 <= len(password) <= 72):
        await message.answer(
            texts.azure_create_invalid_custom_password_text(lang), reply_markup=azure_create_cancel_keyboard(lang)
        )
        return

    await state.update_data(custom_password=password)
    await _show_azure_create_confirmation(message, state, lang)


@router.callback_query(F.data == "azcreate:auth:key", AzureVMCreateStates.choosing_auth_method)
async def cb_azure_create_choose_key_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(AzureVMCreateStates.waiting_ssh_key)
    await callback.message.edit_text(
        texts.azure_create_waiting_ssh_key_text(lang), reply_markup=azure_create_cancel_keyboard(lang)
    )
    await callback.answer()


@router.message(AzureVMCreateStates.waiting_ssh_key)
async def process_azure_ssh_public_key(message: Message, state: FSMContext, lang: str) -> None:
    public_key = message.text.strip() if message.text else ""
    if not _is_valid_ssh_public_key(public_key):
        await message.answer(texts.azure_create_invalid_ssh_key_text(lang), reply_markup=azure_create_cancel_keyboard(lang))
        return

    await state.update_data(ssh_public_key=public_key)
    await _show_azure_create_confirmation(message, state, lang)


async def _show_azure_create_confirmation(target_message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(AzureVMCreateStates.confirming)
    image = next(img for img in data["images"] if img["key"] == data["image_key"])
    auth_method = "key" if data.get("ssh_public_key") else "password"
    await target_message.answer(
        texts.azure_create_confirm_text(
            lang, data["hostname"], data["location_display"], data["vm_size"], image["title"],
            data["admin_username"], auth_method, zone=data.get("zone"),
        ),
        reply_markup=azure_create_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "azcreate:confirm", AzureVMCreateStates.confirming)
async def cb_azure_create_confirm(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()

    status_message = callback.message
    await status_message.edit_text(texts.azure_progress_text(lang, "resource_group"))

    async def progress(step: str) -> None:
        try:
            await status_message.edit_text(texts.azure_progress_text(lang, step))
        except Exception:
            pass

    image_dict = next(img for img in data["images"] if img["key"] == data["image_key"])
    image = ImageInfo(
        key=image_dict["key"], title=image_dict["title"], publisher=image_dict["publisher"],
        offer=image_dict["offer"], sku=image_dict["sku"], version=image_dict["version"],
    )
    ssh_public_key = data.get("ssh_public_key")
    if ssh_public_key:
        admin_password = None
    else:
        admin_password = data.get("custom_password") or generate_azure_password()

    try:
        vm = await azure_create_vm(
            _azure_creds(account),
            location=data["location"],
            vm_size=data["vm_size"],
            image=image,
            vm_name=data["hostname"],
            admin_username=data["admin_username"],
            admin_password=admin_password,
            ssh_public_key=ssh_public_key,
            zone=data.get("zone"),
            progress=progress,
        )
    except AzureAPIError as exc:
        reason = str(exc)
        failed_skus = azure_capacity_restricted_skus(reason) if reason.startswith("detail:") else []
        remaining_sizes = [s for s in data["sizes"] if s["name"] not in failed_skus]
        if failed_skus and remaining_sizes:
            await state.update_data(sizes=remaining_sizes)
            await state.set_state(AzureVMCreateStates.choosing_size)
            failed_size = failed_skus[0]
            await _render_create_page(
                callback,
                lang,
                lambda l, p, tp, _size=failed_size: texts.azure_create_size_capacity_error_text(l, _size, p, tp),
                _azure_size_options(remaining_sizes),
                0, "azcreate:sizepage", "azcreate:cancel",
            )
            return
        await state.clear()
        await status_message.edit_text(texts.action_error_text(lang, reason), reply_markup=cloud_error_keyboard(lang))
        return

    await state.clear()
    await status_message.edit_text(
        texts.azure_create_success_text(lang, vm, ssh_key_used=bool(ssh_public_key)),
        reply_markup=azure_vm_detail_keyboard(lang, data["account_id"], vm),
    )


# --- Azure: reimage (reinstall OS) ---


@router.callback_query(F.data.startswith("azvm:reimageask:"))
async def cb_azure_vm_reimage_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        vm = await azure_get_vm(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.answer()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.answer()
    await callback.message.edit_text(
        texts.azure_vm_reimage_confirm_text(lang, vm),
        reply_markup=azure_vm_reimage_confirm_keyboard(lang, account_id, vm_name),
    )


@router.callback_query(F.data.startswith("azvm:reimage:"))
async def cb_azure_vm_reimage(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer(texts.azure_vm_reimage_ok_text(lang))
    creds = _azure_creds(account)
    try:
        await azure_reimage_vm(creds, vm_name)
        vm = await azure_get_vm(creds, vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.azure_vm_detail_text(lang, vm), reply_markup=azure_vm_detail_keyboard(lang, account_id, vm)
    )


# --- Azure: ports / firewall management ---


async def _show_azure_ports(callback: CallbackQuery, lang: str, account: dict, account_id: str, vm_name: str) -> None:
    try:
        vm = await azure_get_vm(_azure_creds(account), vm_name)
        rules = await azure_list_port_rules(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(
        texts.azure_ports_header_text(lang, vm, bool(rules)),
        reply_markup=azure_ports_list_keyboard(lang, account_id, vm_name, rules),
    )


@router.callback_query(F.data.startswith("azports:list:"))
async def cb_azure_ports_list(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    await _show_azure_ports(callback, lang, account, account_id, vm_name)


@router.callback_query(F.data.startswith("azports:add:"))
async def cb_azure_port_add_ask(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await state.clear()
    await state.update_data(account_id=account_id, vm_name=vm_name)
    await state.set_state(AzurePortStates.waiting_port)
    await callback.answer()
    await callback.message.edit_text(
        texts.azure_step_port_number_text(lang), reply_markup=azure_port_cancel_keyboard(lang, account_id, vm_name)
    )


@router.callback_query(F.data.startswith("azports:cancel:"), AzurePortStates)
async def cb_azure_port_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    _, _, account_id, vm_name = callback.data.split(":", 3)
    await state.clear()
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    await callback.answer()
    await _show_azure_ports(callback, lang, account, account_id, vm_name)


@router.message(AzurePortStates.waiting_port)
async def process_azure_port_number(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    raw = message.text.strip() if message.text else ""
    if not raw.isdigit() or not (1 <= int(raw) <= 65535):
        await message.answer(
            texts.azure_invalid_port_number_text(lang),
            reply_markup=azure_port_cancel_keyboard(lang, data["account_id"], data["vm_name"]),
        )
        return
    await state.update_data(port=raw)
    await state.set_state(AzurePortStates.choosing_protocol)
    await message.answer(
        texts.azure_choose_protocol_text(lang, raw),
        reply_markup=azure_port_protocol_keyboard(lang, data["account_id"], data["vm_name"]),
    )


@router.callback_query(F.data.startswith("azports:proto:"), AzurePortStates.choosing_protocol)
async def cb_azure_port_protocol(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    protocol_raw = callback.data.split(":", 2)[2]
    protocol = "Tcp" if protocol_raw == "tcp" else "Udp"
    data = await state.get_data()
    account = await cloud_store.get(callback.from_user.id, data["account_id"])
    if not account:
        await state.clear()
        await _show_provider_list(callback, lang)
        await callback.answer()
        return
    await callback.answer()
    try:
        rule = await azure_add_port_rule(_azure_creds(account), data["vm_name"], data["port"], protocol)
    except AzureAPIError as exc:
        await state.clear()
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await state.clear()
    await callback.message.edit_text(texts.azure_port_added_text(lang, rule), reply_markup=None)
    await _show_azure_ports(callback, lang, account, data["account_id"], data["vm_name"])


async def _resolve_port_rule(callback: CallbackQuery, lang: str, account: dict, vm_name: str, index: int):
    try:
        rules = await azure_list_port_rules(_azure_creds(account), vm_name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        raise _ResolveFailed from exc
    if index >= len(rules):
        return None
    return rules[index]


@router.callback_query(F.data.startswith("azports:delask:"))
async def cb_azure_port_delete_ask(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        rule = await _resolve_port_rule(callback, lang, account, vm_name, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if rule is None:
        await _show_azure_ports(callback, lang, account, account_id, vm_name)
        return
    await callback.message.edit_text(
        texts.azure_port_delete_confirm_text(lang, rule),
        reply_markup=azure_port_delete_confirm_keyboard(lang, account_id, vm_name, index),
    )


@router.callback_query(F.data.startswith("azports:del:"))
async def cb_azure_port_delete(callback: CallbackQuery, lang: str) -> None:
    _, _, account_id, vm_name, index_raw = callback.data.split(":", 4)
    index = int(index_raw)
    account = await _get_account(callback, lang, account_id)
    if not account:
        return
    try:
        rule = await _resolve_port_rule(callback, lang, account, vm_name, index)
    except _ResolveFailed:
        await callback.answer()
        return
    await callback.answer()
    if rule is None:
        await _show_azure_ports(callback, lang, account, account_id, vm_name)
        return
    try:
        await azure_delete_port_rule(_azure_creds(account), vm_name, rule.name)
    except AzureAPIError as exc:
        await callback.message.edit_text(texts.action_error_text(lang, str(exc)), reply_markup=cloud_error_keyboard(lang))
        return
    await callback.message.edit_text(texts.azure_port_deleted_text(lang), reply_markup=None)
    await _show_azure_ports(callback, lang, account, account_id, vm_name)
