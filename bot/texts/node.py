from __future__ import annotations

import html

from .premium_emoji import e

NODE_TITLES = {"marzban": "Marzban Node", "pasarguard": "PasarGuard"}
NODE_EMOJI = {"marzban": ("marzban", "⚡"), "pasarguard": ("pasarguard", "🛡")}


def _node_header(node_type: str) -> str:
    key, fallback = NODE_EMOJI[node_type]
    return f"{e(key, fallback)} <b>{NODE_TITLES[node_type]}</b>"


def node_menu_text() -> str:
    return f"{e('node', '🖥')} <b>Node</b>\n<i>Какую ноду разворачиваем?</i>"


def node_cancelled_text() -> str:
    return f"{e('node', '🖥')} <b>Node</b>\n<i>Установка отменена.</i>"


def step_ip_text(node_type: str) -> str:
    return (
        f"{_node_header(node_type)}\n<i>Шаг 1 из 3</i>\n\n"
        f"{e('globe', '🌍')} Пришлите IP-адрес или домен сервера."
    )


def invalid_host_text() -> str:
    return "Похоже, это не IP-адрес и не домен. Попробуйте ещё раз — например: <code>203.0.113.10</code>"


def step_ssh_user_text(node_type: str) -> str:
    return (
        f"{_node_header(node_type)}\n<i>Шаг 2 из 3</i>\n\n"
        "Кто главный на сервере? Укажите SSH-пользователя или нажмите «root».\n"
        "<i>Обычный sudo-пользователь тоже подойдёт — бот сам разберётся с правами.</i>"
    )


def invalid_ssh_user_text() -> str:
    return "Имя пользователя может содержать только буквы, цифры, «_» и «-». Попробуйте ещё раз."


def step_password_text(node_type: str, username: str) -> str:
    return (
        f"{_node_header(node_type)}\n<i>Шаг 3 из 3</i>\n\n"
        f"Пароль от <b>{html.escape(username)}</b>, пожалуйста.\n\n"
        f"{e('warning', '⚠️')} <i>Сообщение с паролем удалится сразу после отправки — "
        "он нужен только для подключения и нигде не сохраняется.</i>"
    )


def empty_password_text() -> str:
    return "Пароль не может быть пустым. Отправьте его ещё раз."


def ask_cert_text() -> str:
    return (
        f"{e('key', '🔑')} Остался сертификат клиента из панели Marzban "
        "(его выдают при добавлении ноды).\n"
        "<i>Пришлите файлом (.pem / .crt) или просто текстом.</i>"
    )


def invalid_cert_text() -> str:
    return (
        "Это не похоже на сертификат в формате PEM — он должен начинаться с "
        "<code>-----BEGIN CERTIFICATE-----</code>. Пришлите ещё раз."
    )


def confirmation_text(node_type: str, host: str, ssh_user: str) -> str:
    return (
        f"{_node_header(node_type)}\n\n"
        f"Сервер: <code>{html.escape(host)}</code>\n"
        f"Пользователь: <code>{html.escape(ssh_user)}</code>\n\n"
        "Всё готово — начинаем установку?"
    )


def installing_started_text() -> str:
    return f"{e('launch', '🚀')} Начинаю установку..."


def error_text(reason: str) -> str:
    return f"{e('error', '❌')} Не получилось установить ноду.\n\n{reason}"


def unexpected_error_text(reason: str) -> str:
    return f"{e('error', '❌')} Непредвиденная ошибка: {html.escape(reason)}"


def result_text(
    node_type: str,
    host: str,
    directory: str,
    container_status: str,
    extra: dict,
) -> str:
    lines = [
        f"{e('success', '✅')} {_node_header(node_type)} готова на <code>{html.escape(host)}</code>",
        f"Папка: <code>{directory}</code>",
        f"Статус: <code>{html.escape(container_status)}</code>",
    ]
    if node_type == "pasarguard":
        lines += [
            "",
            "Добавьте ноду в панели PasarGuard:",
            f"Порт <code>{extra['port']}</code> · API_KEY <code>{html.escape(extra['api_key'])}</code>",
            "",
            "Сертификат ноды:",
            f"<pre>{html.escape(extra['cert'])}</pre>",
        ]
    return "\n".join(lines)


# --- Прогресс установки (сообщения, которые бот присылает по ходу) ---


def progress_connecting() -> str:
    return f"{e('connect', '🔌')} Захожу на сервер..."


def progress_checking_docker() -> str:
    return f"{e('docker', '🐳')} Проверяю Docker..."


def progress_installing_docker() -> str:
    return f"{e('docker', '🐳')} Docker не найден — ставлю (пара минут)..."


def progress_installing_compose() -> str:
    return f"{e('docker', '🐳')} Добавляю плагин docker compose..."


def progress_uploading_marzban() -> str:
    return f"{e('files', '📁')} Загружаю сертификат и конфигурацию..."


def progress_generating_pasarguard_cert() -> str:
    return f"{e('key', '🔑')} Готовлю сертификат ноды..."


def progress_uploading_pasarguard() -> str:
    return f"{e('files', '📁')} Настраиваю docker-compose и .env..."


def progress_launching(container_name: str) -> str:
    return f"{e('launch', '🚀')} Запускаю контейнер {container_name}..."
