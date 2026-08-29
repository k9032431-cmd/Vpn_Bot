from __future__ import annotations

import html
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
from bot.services.node_installer import (
    NodeInstallResult,
    install_marzban_node,
    install_pasarguard_node,
)
from bot.services.ssh_client import NodeInstallError, SSHTarget
from bot.states.node_setup import NodeSetupStates

router = Router(name="node")

# Loose hostname/IP check: letters, digits, dots and dashes, no spaces.
HOST_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9.\-]{0,251}[a-zA-Z0-9]$|^[a-zA-Z0-9]$")
SSH_USER_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-]{0,31}$")

NODE_TITLES = {"marzban": "Marzban Node", "pasarguard": "PasarGuard"}


def _is_valid_host(value: str) -> bool:
    value = value.strip()
    if not value or " " in value:
        return False
    return bool(HOST_RE.match(value))


@router.callback_query(F.data == "menu:node")
async def cb_node_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🖥 <b>Node</b>\n\nВыберите тип ноды, которую нужно установить на сервер:",
        reply_markup=node_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.in_({"node:marzban", "node:pasarguard"}))
async def cb_node_choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    node_type = callback.data.split(":", 1)[1]
    await state.clear()
    await state.update_data(node_type=node_type)
    await state.set_state(NodeSetupStates.waiting_ip)
    await callback.message.edit_text(
        f"🖥 <b>{NODE_TITLES[node_type]}</b>\n\n"
        "Шаг 1/3. Отправьте IP-адрес (или домен) сервера, на котором нужно установить ноду.",
        reply_markup=cancel_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "nodesetup:cancel")
async def cb_cancel_setup(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🖥 <b>Node</b>\n\nУстановка отменена. Выберите тип ноды:",
        reply_markup=node_menu_keyboard(),
    )
    await callback.answer()


@router.message(NodeSetupStates.waiting_ip)
async def process_ip(message: Message, state: FSMContext) -> None:
    host = message.text.strip() if message.text else ""
    if not _is_valid_host(host):
        await message.answer(
            "Не похоже на корректный IP-адрес или домен. Попробуйте ещё раз, например: 203.0.113.10",
            reply_markup=cancel_keyboard(),
        )
        return

    data = await state.update_data(host=host)
    await state.set_state(NodeSetupStates.waiting_ssh_user)
    await message.answer(
        f"🖥 <b>{NODE_TITLES[data['node_type']]}</b>\n\n"
        "Шаг 2/3. Укажите SSH-пользователя для входа на сервер (или нажмите «root»). "
        "Пользователь может быть обычным sudo-пользователем — это нормально, например, "
        "для серверов Azure бот сам подставит sudo, где нужно.",
        reply_markup=ssh_user_keyboard(),
    )


@router.callback_query(NodeSetupStates.waiting_ssh_user, F.data == "sshuser:root")
async def process_ssh_user_root(callback: CallbackQuery, state: FSMContext) -> None:
    await _ask_password(callback.message, state, "root")
    await callback.answer()


@router.message(NodeSetupStates.waiting_ssh_user)
async def process_ssh_user(message: Message, state: FSMContext) -> None:
    username = message.text.strip() if message.text else ""
    if not SSH_USER_RE.match(username):
        await message.answer(
            "Некорректное имя пользователя. Используйте буквы, цифры, «_» и «-».",
            reply_markup=cancel_keyboard(),
        )
        return
    await _ask_password(message, state, username)


async def _ask_password(target_message: Message, state: FSMContext, username: str) -> None:
    await state.update_data(ssh_user=username)
    await state.set_state(NodeSetupStates.waiting_ssh_password)
    await target_message.answer(
        f"Шаг 3/3. Отправьте пароль SSH-пользователя <b>{html.escape(username)}</b>.\n\n"
        "⚠️ Сообщение с паролем будет автоматически удалено сразу после получения. "
        "Пароль используется только для подключения и нигде не сохраняется.",
        reply_markup=cancel_keyboard(),
    )


@router.message(NodeSetupStates.waiting_ssh_password)
async def process_ssh_password(message: Message, state: FSMContext) -> None:
    password = message.text or ""
    try:
        await message.delete()
    except Exception:
        pass

    if not password:
        await message.answer(
            "Пароль не может быть пустым. Отправьте его ещё раз.", reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(ssh_password=password)
    data = await state.get_data()

    if data["node_type"] == "marzban":
        await state.set_state(NodeSetupStates.waiting_cert)
        await message.answer(
            "Отправьте сертификат клиента, который выдаёт панель Marzban при добавлении ноды "
            "(файлом <code>.pem</code>/<code>.crt</code> или текстом, начинающимся с "
            "<code>-----BEGIN CERTIFICATE-----</code>).",
            reply_markup=cancel_keyboard(),
        )
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
        await message.answer(
            "Это не похоже на сертификат в формате PEM. Убедитесь, что он содержит "
            "<code>-----BEGIN CERTIFICATE-----</code>, и отправьте снова.",
            reply_markup=cancel_keyboard(),
        )
        return
    await state.update_data(cert_pem=content)
    await _show_confirmation(message, state)


async def _show_confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(NodeSetupStates.confirming)
    await message.answer(
        f"🖥 <b>{NODE_TITLES[data['node_type']]}</b>\n\n"
        f"IP/домен: <code>{html.escape(data['host'])}</code>\n"
        f"SSH-пользователь: <code>{html.escape(data['ssh_user'])}</code>\n\n"
        "Начать установку? Бот подключится по SSH и настроит ноду автоматически "
        "(через sudo, если пользователь не root).",
        reply_markup=confirm_install_keyboard(),
    )


@router.callback_query(NodeSetupStates.confirming, F.data == "nodeinstall:confirm")
async def cb_confirm_install(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(NodeSetupStates.installing)

    status_message = callback.message
    await status_message.edit_text("⏳ Начинаю установку...")
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
            f"❌ Установка не удалась:\n\n{exc}",
            reply_markup=node_result_keyboard(),
        )
        return
    except Exception as exc:  # noqa: BLE001 - surface unexpected errors to the user
        await state.clear()
        await status_message.edit_text(
            f"❌ Непредвиденная ошибка при установке: {html.escape(str(exc))}",
            reply_markup=node_result_keyboard(),
        )
        return

    await state.clear()
    await status_message.edit_text(_format_result(result), reply_markup=node_result_keyboard())


@router.callback_query(F.data == "nodeinstall:cancel")
async def cb_cancel_install(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🖥 <b>Node</b>\n\nУстановка отменена. Выберите тип ноды:",
        reply_markup=node_menu_keyboard(),
    )
    await callback.answer()


def _format_result(result: NodeInstallResult) -> str:
    lines = [
        f"✅ <b>{NODE_TITLES[result.node_type]}</b> установлена на <code>{html.escape(result.host)}</code>",
        f"Директория: <code>{result.directory}</code>",
        f"Статус контейнера: <code>{html.escape(result.container_status)}</code>",
    ]
    if result.node_type == "pasarguard":
        lines += [
            "",
            "Добавьте эту ноду в панели PasarGuard со следующими данными:",
            f"Порт: <code>{result.extra['port']}</code>",
            f"API_KEY: <code>{html.escape(result.extra['api_key'])}</code>",
            "",
            "Сертификат ноды (вставьте в панель при добавлении):",
            f"<pre>{html.escape(result.extra['cert'])}</pre>",
        ]
    return "\n".join(lines)
