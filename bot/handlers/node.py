from __future__ import annotations

import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.node import (
    cancel_keyboard,
    confirm_install_keyboard,
    node_menu_keyboard,
    node_result_keyboard,
    ssh_user_keyboard,
)
from bot.services.node_installer import install_marzban_node, install_pasarguard_node
from bot.services.ssh_client import NodeInstallError, SSHTarget
from bot.states.node_setup import NodeSetupStates
from bot.texts import node as texts

router = Router(name="node")

# Loose hostname/IP check: letters, digits, dots and dashes, no spaces.
HOST_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,251}[a-zA-Z0-9]$|^[a-zA-Z0-9]$")
SSH_USER_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-]{0,31}$")


def _is_valid_host(value: str) -> bool:
    value = value.strip()
    if not value or " " in value:
        return False
    return bool(HOST_RE.match(value))


@router.callback_query(F.data == "menu:node")
async def cb_node_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(texts.node_menu_text(), reply_markup=node_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.in_({"node:marzban", "node:pasarguard"}))
async def cb_node_choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    node_type = callback.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(node_type=node_type)
    await state.set_state(NodeSetupStates.waiting_ip)
    await callback.message.edit_text(texts.step_ip_text(node_type), reply_markup=cancel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "nodesetup:cancel")
async def cb_cancel_setup(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(texts.node_cancelled_text(), reply_markup=node_menu_keyboard())
    await callback.answer()


@router.message(NodeSetupStates.waiting_ip)
async def process_ip(message: Message, state: FSMContext) -> None:
    host = message.text.strip() if message.text else ""
    if not _is_valid_host(host):
        await message.answer(texts.invalid_host_text(), reply_markup=cancel_keyboard())
        return

    data = await state.update_data(host=host)
    await state.set_state(NodeSetupStates.waiting_ssh_user)
    await message.answer(
        texts.step_ssh_user_text(data["node_type"]), reply_markup=ssh_user_keyboard()
    )


@router.callback_query(NodeSetupStates.waiting_ssh_user, F.data == "sshuser:root")
async def process_ssh_user_root(callback: CallbackQuery, state: FSMContext) -> None:
    await _ask_password(callback.message, state, "root")
    await callback.answer()


@router.message(NodeSetupStates.waiting_ssh_user)
async def process_ssh_user(message: Message, state: FSMContext) -> None:
    username = message.text.strip() if message.text else ""
    if not SSH_USER_RE.match(username):
        await message.answer(texts.invalid_ssh_user_text(), reply_markup=cancel_keyboard())
        return
    await _ask_password(message, state, username)


async def _ask_password(target_message: Message, state: FSMContext, username: str) -> None:
    data = await state.update_data(ssh_user=username)
    await state.set_state(NodeSetupStates.waiting_ssh_password)
    await target_message.answer(
        texts.step_password_text(data["node_type"], username), reply_markup=cancel_keyboard()
    )


@router.message(NodeSetupStates.waiting_ssh_password)
async def process_ssh_password(message: Message, state: FSMContext) -> None:
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if not password:
        await message.answer(texts.empty_password_text(), reply_markup=cancel_keyboard())
        return

    await state.update_data(ssh_password=password)
    data = await state.get_data()

    if data["node_type"] == "marzban":
        await state.set_state(NodeSetupStates.waiting_cert)
        await message.answer(texts.ask_cert_text(), reply_markup=cancel_keyboard())
    else:
        await _show_confirmation(message, state)


@router.message(NodeSetupStates.waiting_cert, F.document)
async def process_cert_document(message: Message, state: FSMContext, bot: Bot) -> None:
    file = await bot.get_file(message.document.file_id)
    buffer = await bot.download_file(file.file_path)
    content = buffer.read().decode("utf-8", errors="ignore")
    await _handle_cert_content(message, state, content)


@router.message(NodeSetupStates.waiting_cert, F.text)
async def process_cert_text(message: Message, state: FSMContext) -> None:
    await _handle_cert_content(message, state, message.text or "")


async def _handle_cert_content(message: Message, state: FSMContext, content: str) -> None:
    content = content.strip()
    if "BEGIN CERTIFICATE" not in content:
        await message.answer(texts.invalid_cert_text(), reply_markup=cancel_keyboard())
        return
    await state.update_data(cert_pem=content)
    await _show_confirmation(message, state)


async def _show_confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(NodeSetupStates.confirming)
    await message.answer(
        texts.confirmation_text(data["node_type"], data["host"], data["ssh_user"]),
        reply_markup=confirm_install_keyboard(),
    )


@router.callback_query(NodeSetupStates.confirming, F.data == "nodeinstall:confirm")
async def cb_confirm_install(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(NodeSetupStates.installing)

    status_message = callback.message
    await status_message.edit_text(texts.installing_started_text())
    await callback.answer()

    target = SSHTarget(host=data["host"], username=data["ssh_user"], password=data["ssh_password"])

    async def progress(text: str) -> None:
        try:
            await status_message.edit_text(text)
        except Exception:
            pass

    try:
        if data["node_type"] == "marzban":
            result = await install_marzban_node(target, data["cert_pem"], progress)
        else:
            result = await install_pasarguard_node(target, progress)
    except NodeInstallError as exc:
        await state.clear()
        await status_message.edit_text(
            texts.error_text(str(exc)), reply_markup=node_result_keyboard()
        )
        return
    except Exception as exc:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            texts.unexpected_error_text(str(exc)), reply_markup=node_result_keyboard()
        )
        return

    await state.clear()
    await status_message.edit_text(
        texts.result_text(
            result.node_type, result.host, result.directory, result.container_status, result.extra
        ),
        reply_markup=node_result_keyboard(),
    )


@router.callback_query(F.data == "nodeinstall:cancel")
async def cb_cancel_install(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(texts.node_cancelled_text(), reply_markup=node_menu_keyboard())
    await callback.answer()
