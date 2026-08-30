from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.texts.panel import panel_list_label
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


def panel_dashboard_keyboard(lang: str, panel_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t(lang, "btn_panel_stats"), callback_data=f"pdash:stats:{panel_id}")
    builder.button(text=t(lang, "btn_panel_users"), callback_data=f"pdash:users:{panel_id}")
    builder.button(text=t(lang, "btn_panel_remove"), callback_data=f"pdash:rmask:{panel_id}")
    builder.button(text=t(lang, "btn_panel_list"), callback_data="pdash:list")
    builder.adjust(1, 1, 1, 1)
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
