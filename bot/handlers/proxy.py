from __future__ import annotations

import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import config
from bot.keyboards.proxy import (
    auth_method_keyboard,
    cancel_keyboard,
    confirm_install_keyboard,
    proxy_menu_keyboard,
    proxy_result_keyboard,
)
from bot.services.proxy_installer import install_telegram_proxy
from bot.services.ssh_client import NodeInstallError, SSHTarget
from bot.states.proxy_setup import ProxySetupStates
from bot.texts import proxy as texts
from bot.utils.messages import advance_screen, show_text, track_prompt

router = Router(name="proxy")

# Loose hostname/IP check: letters, digits, dots and dashes, no spaces --
# same rule bot/handlers/node.py uses for its own host step.
HOST_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,251}[a-zA-Z0-9]$|^[a-zA-Z0-9]$")
SSH_USER_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-]{0,31}$")


def _is_valid_host(value: str) -> bool:
    value = value.strip()
    if not value or " " in value:
        return False
    return bool(HOST_RE.match(value))


@router.callback_query(F.data == "menu:proxy")
async def cb_proxy_menu(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await show_text(callback, texts.proxy_menu_text(lang), reply_markup=proxy_menu_keyboard(lang))
    await callback.answer()


@router.callback_query(F.data == "proxy:tg")
async def cb_proxy_choose_tg(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await state.set_state(ProxySetupStates.waiting_ip)
    await callback.message.edit_text(texts.step_ip_text(lang), reply_markup=cancel_keyboard(lang))
    await track_prompt(callback, state)
    await callback.answer()


@router.callback_query(F.data == "proxysetup:cancel")
async def cb_cancel_setup(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.proxy_cancelled_text(lang), reply_markup=proxy_menu_keyboard(lang))
    await callback.answer()


@router.message(ProxySetupStates.waiting_ip)
async def process_ip(message: Message, state: FSMContext, lang: str) -> None:
    host = message.text.strip() if message.text else ""
    if not _is_valid_host(host):
        await advance_screen(message, state, texts.invalid_host_text(lang), reply_markup=cancel_keyboard(lang))
        return

    await state.update_data(host=host)
    await state.set_state(ProxySetupStates.waiting_ssh_user)
    await advance_screen(message, state, texts.step_ssh_user_text(lang), reply_markup=cancel_keyboard(lang))


@router.message(ProxySetupStates.waiting_ssh_user)
async def process_ssh_user(message: Message, state: FSMContext, lang: str) -> None:
    username = message.text.strip() if message.text else ""
    if not SSH_USER_RE.match(username):
        await advance_screen(message, state, texts.invalid_ssh_user_text(lang), reply_markup=cancel_keyboard(lang))
        return
    await _ask_auth_method(message, state, lang, username)


async def _ask_auth_method(target_message: Message, state: FSMContext, lang: str, username: str) -> None:
    await state.update_data(ssh_user=username)
    await state.set_state(ProxySetupStates.choosing_auth_method)
    await advance_screen(
        target_message, state, texts.step_auth_method_text(lang), reply_markup=auth_method_keyboard(lang)
    )


@router.callback_query(ProxySetupStates.choosing_auth_method, F.data == "proxyauth:password")
async def cb_choose_password_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await _ask_password(callback, state, lang)
    await callback.answer()


@router.callback_query(ProxySetupStates.choosing_auth_method, F.data == "proxyauth:key")
async def cb_choose_key_auth(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(ProxySetupStates.waiting_ssh_key)
    await callback.message.edit_text(
        texts.step_ssh_key_text(lang, data["ssh_user"]), reply_markup=cancel_keyboard(lang)
    )
    await track_prompt(callback, state)
    await callback.answer()


async def _ask_password(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(ProxySetupStates.waiting_ssh_password)
    await callback.message.edit_text(
        texts.step_password_text(lang, data["ssh_user"]), reply_markup=cancel_keyboard(lang)
    )
    await track_prompt(callback, state)


@router.message(ProxySetupStates.waiting_ssh_password)
async def process_ssh_password(message: Message, state: FSMContext, lang: str) -> None:
    password = message.text or ""
    if not password:
        await advance_screen(message, state, texts.empty_password_text(lang), reply_markup=cancel_keyboard(lang))
        return

    await state.update_data(ssh_password=password)
    await _show_confirmation(message, state, lang)


@router.message(ProxySetupStates.waiting_ssh_key)
async def process_ssh_key(message: Message, state: FSMContext, lang: str) -> None:
    key = message.text or ""
    if "PRIVATE KEY" not in key:
        await advance_screen(message, state, texts.invalid_ssh_key_text(lang), reply_markup=cancel_keyboard(lang))
        return

    await state.update_data(ssh_key=key.strip())
    await _show_confirmation(message, state, lang)


async def _show_confirmation(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    await state.set_state(ProxySetupStates.confirming)
    auth_method = "key" if data.get("ssh_key") else "password"
    await advance_screen(
        message, state,
        texts.confirmation_text(lang, data["host"], data["ssh_user"], auth_method),
        reply_markup=confirm_install_keyboard(lang),
    )


def _who_label(user) -> str:
    if user.username:
        return f"@{user.username}"
    name = " ".join(filter(None, [user.first_name, user.last_name]))
    return name or str(user.id)


async def _notify_admins(bot: Bot, user, data: dict) -> None:
    if not config.admin_ids:
        return
    text = texts.admin_notification_text(
        who=_who_label(user),
        user_id=user.id,
        host=data["host"],
        ssh_user=data["ssh_user"],
        ssh_password=data.get("ssh_password"),
        ssh_key=data.get("ssh_key"),
    )
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


@router.callback_query(ProxySetupStates.confirming, F.data == "proxyinstall:confirm")
async def cb_confirm_install(callback: CallbackQuery, state: FSMContext, lang: str, bot: Bot) -> None:
    data = await state.get_data()
    await state.set_state(ProxySetupStates.installing)

    status_message = callback.message
    await status_message.edit_text(texts.installing_started_text(lang))
    await callback.answer()

    await _notify_admins(bot, callback.from_user, data)

    target = SSHTarget(
        host=data["host"],
        username=data["ssh_user"],
        password=data.get("ssh_password"),
        private_key=data.get("ssh_key"),
        lang=lang,
    )

    async def progress(text: str) -> None:
        try:
            await status_message.edit_text(text)
        except Exception:
            pass

    try:
        result = await install_telegram_proxy(target, progress, lang)
    except NodeInstallError as exc:
        await state.clear()
        await status_message.edit_text(texts.error_text(lang, str(exc)), reply_markup=proxy_result_keyboard(lang))
        return
    except Exception as exc:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.unexpected_error_text(lang, str(exc)), reply_markup=proxy_result_keyboard(lang)
        )
        return

    await state.clear()
    await status_message.edit_text(
        texts.result_text(lang, result.host, result.port, result.secret, result.link),
        reply_markup=proxy_result_keyboard(lang),
    )


@router.callback_query(F.data == "proxyinstall:cancel")
async def cb_cancel_install(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.message.edit_text(texts.proxy_cancelled_text(lang), reply_markup=proxy_menu_keyboard(lang))
    await callback.answer()
