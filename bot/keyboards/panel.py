from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.panel import (
    admin_list_label,
    host_list_label,
    inbound_list_label,
    node_list_label,
    panel_list_label,
)
from bot.texts.translations import t


def panel_list_keyboard(lang: str, panels: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for panel in panels:
        builder.button(text=panel_list_label(lang, panel), callback_data=f"pview:{panel['id']}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_add"), callback_data="padd:menu")
    rows.append(1)
    builder.button(text=t(lang, "btn_back"), callback_data="menu:back")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_add_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_marzban"), callback_data="padd:marzban")
    builder.button(text=t(lang, "btn_panel_pasarguard"), callback_data="padd:pasarguard")
    builder.button(text=t(lang, "btn_panel_3xui"), callback_data="padd:3xui")
    builder.button(text=t(lang, "btn_back"), callback_data="pdash:list")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def panel_cancel_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data="panelsetup:cancel")
    return builder.as_markup()


def panel_error_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_menu"), callback_data="menu:panel")
    builder.button(text=t(lang, "btn_main_menu"), callback_data="menu:back")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_dashboard_keyboard(lang: str, panel_id: str, panel_type: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_stats"), callback_data=f"pdash:stats:{panel_id}")
    builder.button(text=t(lang, "btn_panel_users"), callback_data=f"pdash:users:{panel_id}")
    rows = [1, 1]
    if panel_type in ("marzban", "pasarguard"):
        builder.button(text=t(lang, "btn_panel_nodes"), callback_data=f"pdash:nodes:{panel_id}")
        builder.button(text=t(lang, "btn_panel_core"), callback_data=f"pdash:core:{panel_id}")
        builder.button(text=t(lang, "btn_panel_admins"), callback_data=f"pdash:admins:{panel_id}")
        builder.button(text=t(lang, "btn_panel_hosts"), callback_data=f"pdash:hosts:{panel_id}")
        rows.extend([1, 1, 1, 1])
    elif panel_type == "3xui":
        builder.button(text=t(lang, "btn_panel_inbounds"), callback_data=f"pdash:inbounds:{panel_id}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_remove"), callback_data=f"pdash:rmask:{panel_id}")
    builder.button(text=t(lang, "btn_panel_list"), callback_data="pdash:list")
    rows.extend([1, 1])
    builder.adjust(*rows)
    return builder.as_markup()


def panel_dashboard_back_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    builder.button(text=t(lang, "btn_panel_list"), callback_data="pdash:list")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_remove_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_remove_confirm"), callback_data=f"pdash:rmcnf:{panel_id}")
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_nodes_keyboard(lang: str, panel_id: str, nodes: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for node in nodes:
        builder.button(text=node_list_label(node), callback_data=f"pnode:view:{panel_id}:{node.id}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_node_add"), callback_data=f"pnode:new:{panel_id}")
    rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_node_cancel_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pnode:cancel:{panel_id}")
    return builder.as_markup()


def panel_node_create_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_node_create_confirm"), callback_data=f"pnode:createcnf:{panel_id}")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pnode:cancel:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_node_detail_keyboard(lang: str, panel_id: str, node_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_node_reconnect"), callback_data=f"pnode:reconnect:{panel_id}:{node_id}")
    builder.button(text=t(lang, "btn_panel_node_delete"), callback_data=f"pnode:delask:{panel_id}:{node_id}")
    builder.button(text=t(lang, "btn_panel_nodes"), callback_data=f"pdash:nodes:{panel_id}")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def panel_node_delete_confirm_keyboard(lang: str, panel_id: str, node_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_node_delete_confirm"), callback_data=f"pnode:delcnf:{panel_id}:{node_id}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pnode:view:{panel_id}:{node_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_core_menu_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_core_view"), callback_data=f"pcore:view:{panel_id}")
    builder.button(text=t(lang, "btn_panel_core_edit"), callback_data=f"pcore:editstart:{panel_id}")
    builder.button(text=t(lang, "btn_panel_core_restart"), callback_data=f"pcore:restartask:{panel_id}")
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()


def panel_core_back_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_core"), callback_data=f"pdash:core:{panel_id}")
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_core_cancel_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pcore:cancel:{panel_id}")
    return builder.as_markup()


def panel_core_edit_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_core_apply"), callback_data=f"pcore:editcnf:{panel_id}")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pcore:cancel:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_core_restart_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_core_restart_confirm"), callback_data=f"pcore:restartcnf:{panel_id}")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pdash:core:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_admins_keyboard(lang: str, panel_id: str, admins: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for admin in admins:
        builder.button(text=admin_list_label(admin), callback_data=f"padmin:view:{panel_id}:{admin.username}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_admin_add"), callback_data=f"padmin:new:{panel_id}")
    rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_admin_cancel_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"padmin:cancel:{panel_id}")
    return builder.as_markup()


def panel_admin_create_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_admin_create_normal"), callback_data=f"padmin:createcnf:{panel_id}:0")
    builder.button(text=t(lang, "btn_panel_admin_create_sudo"), callback_data=f"padmin:createcnf:{panel_id}:1")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"padmin:cancel:{panel_id}")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def panel_admin_detail_keyboard(lang: str, panel_id: str, username: str, is_sudo: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_key = "btn_panel_admin_toggle_sudo_off" if is_sudo else "btn_panel_admin_toggle_sudo_on"
    builder.button(text=t(lang, toggle_key), callback_data=f"padmin:togglesudo:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_admin_delete"), callback_data=f"padmin:delask:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_admins"), callback_data=f"pdash:admins:{panel_id}")
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def panel_admin_delete_confirm_keyboard(lang: str, panel_id: str, username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_admin_delete_confirm"), callback_data=f"padmin:delcnf:{panel_id}:{username}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"padmin:view:{panel_id}:{username}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_hosts_tags_keyboard(lang: str, panel_id: str, tags: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, tag in enumerate(tags):
        builder.button(text=f"📡 {tag}", callback_data=f"phost:tag:{panel_id}:{i}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_hosts_list_keyboard(lang: str, panel_id: str, tag_index: int, hosts: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for i, host in enumerate(hosts):
        builder.button(text=host_list_label(host), callback_data=f"phost:view:{panel_id}:{tag_index}:{i}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_host_add"), callback_data=f"phost:new:{panel_id}:{tag_index}")
    rows.append(1)
    builder.button(text=t(lang, "btn_panel_hosts"), callback_data=f"pdash:hosts:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_host_detail_keyboard(
    lang: str, panel_id: str, tag_index: int, host_index: int, is_disabled: bool
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_key = "btn_panel_host_toggle_on" if is_disabled else "btn_panel_host_toggle_off"
    builder.button(
        text=t(lang, "btn_panel_host_edit"), callback_data=f"phost:editstart:{panel_id}:{tag_index}:{host_index}"
    )
    builder.button(text=t(lang, toggle_key), callback_data=f"phost:toggle:{panel_id}:{tag_index}:{host_index}")
    builder.button(
        text=t(lang, "btn_panel_host_delete"), callback_data=f"phost:delask:{panel_id}:{tag_index}:{host_index}"
    )
    builder.button(text=t(lang, "btn_panel_hosts_list"), callback_data=f"phost:tag:{panel_id}:{tag_index}")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def panel_host_cancel_keyboard(lang: str, panel_id: str, tag_index: int, host_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"phost:view:{panel_id}:{tag_index}:{host_index}")
    return builder.as_markup()


def panel_host_edit_confirm_keyboard(
    lang: str, panel_id: str, tag_index: int, host_index: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_host_apply"), callback_data=f"phost:editcnf:{panel_id}:{tag_index}:{host_index}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"phost:view:{panel_id}:{tag_index}:{host_index}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_host_delete_confirm_keyboard(
    lang: str, panel_id: str, tag_index: int, host_index: int
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_host_delete_confirm"),
        callback_data=f"phost:delcnf:{panel_id}:{tag_index}:{host_index}",
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"phost:view:{panel_id}:{tag_index}:{host_index}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_host_new_cancel_keyboard(lang: str, panel_id: str, tag_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"phost:tag:{panel_id}:{tag_index}")
    return builder.as_markup()


def panel_host_create_confirm_keyboard(lang: str, panel_id: str, tag_index: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_host_create_confirm"), callback_data=f"phost:newcnf:{panel_id}:{tag_index}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"phost:tag:{panel_id}:{tag_index}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_inbounds_keyboard(
    lang: str, panel_id: str, inbounds: list[dict], clients_by_id: dict[int, int]
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    for inbound in inbounds:
        inbound_id = inbound.get("id")
        clients = clients_by_id.get(inbound_id, 0)
        builder.button(text=inbound_list_label(inbound, clients), callback_data=f"pinb:view:{panel_id}:{inbound_id}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_inbound_detail_keyboard(lang: str, panel_id: str, inbound_id: int, enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_key = "btn_panel_inbound_toggle_off" if enabled else "btn_panel_inbound_toggle_on"
    builder.button(
        text=t(lang, "btn_panel_inbound_edit"), callback_data=f"pinb:editstart:{panel_id}:{inbound_id}"
    )
    builder.button(text=t(lang, toggle_key), callback_data=f"pinb:toggle:{panel_id}:{inbound_id}")
    builder.button(
        text=t(lang, "btn_panel_inbound_delete"), callback_data=f"pinb:delask:{panel_id}:{inbound_id}"
    )
    builder.button(text=t(lang, "btn_panel_inbounds_list"), callback_data=f"pdash:inbounds:{panel_id}")
    builder.adjust(2, 1, 1)
    return builder.as_markup()


def panel_inbound_cancel_keyboard(lang: str, panel_id: str, inbound_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pinb:view:{panel_id}:{inbound_id}")
    return builder.as_markup()


def panel_inbound_edit_confirm_keyboard(lang: str, panel_id: str, inbound_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_inbound_apply"), callback_data=f"pinb:editcnf:{panel_id}:{inbound_id}")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pinb:view:{panel_id}:{inbound_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_inbound_delete_confirm_keyboard(lang: str, panel_id: str, inbound_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_inbound_delete_confirm"), callback_data=f"pinb:delcnf:{panel_id}:{inbound_id}"
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"pinb:view:{panel_id}:{inbound_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_users_keyboard(
    lang: str,
    panel_id: str,
    usernames: list[str],
    manageable: bool,
    page: int = 0,
    has_prev: bool = False,
    has_next: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    rows: list[int] = []
    if manageable:
        for name in usernames:
            builder.button(text=f"👤 {name}", callback_data=f"puser:view:{panel_id}:{name}")
            rows.append(1)

    nav_buttons = 0
    if has_prev:
        builder.button(text="◀️", callback_data=f"pdash:users:{panel_id}:{page - 1}")
        nav_buttons += 1
    if has_next:
        builder.button(text="▶️", callback_data=f"pdash:users:{panel_id}:{page + 1}")
        nav_buttons += 1
    if nav_buttons:
        rows.append(nav_buttons)

    if manageable:
        builder.button(text=t(lang, "btn_panel_create_user"), callback_data=f"pdash:newuser:{panel_id}")
        rows.append(1)
    builder.button(text=t(lang, "btn_panel_dashboard"), callback_data=f"pview:{panel_id}")
    rows.append(1)
    builder.adjust(*rows)
    return builder.as_markup()


def panel_user_cancel_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"puser:cancel:{panel_id}")
    return builder.as_markup()


def panel_create_user_confirm_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_create_confirm"), callback_data=f"puser:createcnf:{panel_id}")
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"puser:cancel:{panel_id}")
    builder.adjust(1, 1)
    return builder.as_markup()


def panel_user_detail_keyboard(lang: str, panel_id: str, username: str, status: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    toggle_key = "btn_panel_user_disable" if status == "active" else "btn_panel_user_enable"
    builder.button(text=t(lang, toggle_key), callback_data=f"puser:toggle:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_user_reset"), callback_data=f"puser:reset:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_user_edit"), callback_data=f"puser:edit:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_user_delete"), callback_data=f"puser:delask:{panel_id}:{username}")
    builder.button(text=t(lang, "btn_panel_users"), callback_data=f"pdash:users:{panel_id}")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def panel_user_delete_confirm_keyboard(lang: str, panel_id: str, username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn_panel_user_delete_confirm"),
        callback_data=f"puser:delcnf:{panel_id}:{username}",
    )
    builder.button(text=t(lang, "btn_cancel"), callback_data=f"puser:view:{panel_id}:{username}")
    builder.adjust(1, 1)
    return builder.as_markup()
