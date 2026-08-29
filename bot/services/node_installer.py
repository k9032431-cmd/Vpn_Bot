from __future__ import annotations

import shlex
import uuid
from dataclasses import dataclass, field

from .ssh_client import NodeInstallError, ProgressCallback, RemoteSession, SSHTarget

__all__ = [
    "NodeInstallError",
    "NodeInstallResult",
    "install_marzban_node",
    "install_pasarguard_node",
]

MARZBAN_DIR = "/var/lib/marzban-node"
MARZBAN_CERT_FILENAME = "ssl_client_cert.pem"
MARZBAN_COMPOSE = """services:
  marzban-node:
    image: gozargah/marzban-node:latest
    container_name: marzban-node
    restart: always
    network_mode: host
    environment:
      SSL_CLIENT_CERT_FILE: "/var/lib/marzban-node/ssl_client_cert.pem"
      SERVICE_PROTOCOL: "rest"
    volumes:
      - /var/lib/marzban-node:/var/lib/marzban-node
"""

PASARGUARD_DIR = "/var/lib/pg-node"
PASARGUARD_PORT = 62050
PASARGUARD_COMPOSE = """services:
  node:
    image: pasarguard/node:latest
    container_name: pg-node
    restart: always
    network_mode: host
    cap_add:
      - NET_ADMIN
    env_file: .env
    volumes:
      - /var/lib/pg-node:/var/lib/pg-node
"""


@dataclass
class NodeInstallResult:
    node_type: str
    host: str
    directory: str
    container_status: str
    extra: dict = field(default_factory=dict)


async def _ensure_docker(session: RemoteSession, progress: ProgressCallback) -> None:
    check = await session.run("command -v docker")
    if check.exit_status == 0:
        await session.run_checked(
            "systemctl enable --now docker 2>/dev/null || service docker start",
            "Docker установлен на сервере, но не удалось его запустить.",
        )
    else:
        await progress("🐳 Docker не найден на сервере, устанавливаю (может занять пару минут)...")
        await session.run(
            "command -v curl >/dev/null 2>&1 || "
            "(apt-get update -y && apt-get install -y curl) || "
            "(yum install -y curl) || (dnf install -y curl)"
        )
        await session.run_checked(
            "curl -fsSL https://get.docker.com | sh",
            "Не удалось установить Docker автоматически. Установите его вручную и повторите попытку.",
            timeout=900,
        )
        await session.run_checked(
            "systemctl enable --now docker",
            "Docker установлен, но не удалось его запустить.",
        )

    compose_check = await session.run("docker compose version")
    if compose_check.exit_status != 0:
        await progress("🔧 Устанавливаю плагин docker compose...")
        await session.run_checked(
            "(apt-get update -y && apt-get install -y docker-compose-plugin) || "
            "(yum install -y docker-compose-plugin) || "
            "(dnf install -y docker-compose-plugin)",
            "Не удалось установить docker compose plugin.",
        )


async def install_marzban_node(
    target: SSHTarget,
    cert_pem: str,
    progress: ProgressCallback,
) -> NodeInstallResult:
    await progress("🔌 Подключаюсь по SSH...")
    session = await RemoteSession.connect(target)
    try:
        await progress("🐳 Проверяю Docker...")
        await _ensure_docker(session, progress)

        await progress("📁 Загружаю сертификат панели и конфигурацию на сервер...")
        await session.deploy_file(cert_pem, MARZBAN_CERT_FILENAME, MARZBAN_DIR, mode="600")
        await session.deploy_file(MARZBAN_COMPOSE, "docker-compose.yml", MARZBAN_DIR, mode="644")

        await progress("🚀 Запускаю контейнер marzban-node...")
        await session.run_checked(
            f"cd {shlex.quote(MARZBAN_DIR)} && docker compose up -d --force-recreate",
            "Не удалось запустить контейнер marzban-node.",
            timeout=300,
        )

        status = await session.run("docker ps --filter name=marzban-node --format '{{.Status}}'")
        container_status = (status.stdout or "").strip() or "неизвестно"

        return NodeInstallResult(
            node_type="marzban",
            host=target.host,
            directory=MARZBAN_DIR,
            container_status=container_status,
        )
    finally:
        await session.close()


async def install_pasarguard_node(
    target: SSHTarget,
    progress: ProgressCallback,
) -> NodeInstallResult:
    await progress("🔌 Подключаюсь по SSH...")
    session = await RemoteSession.connect(target)
    try:
        await progress("🐳 Проверяю Docker...")
        await _ensure_docker(session, progress)

        certs_dir = f"{PASARGUARD_DIR}/certs"
        await session.run_checked(
            f"mkdir -p {shlex.quote(certs_dir)}", "Не удалось создать директорию ноды."
        )

        await progress("🔑 Проверяю/генерирую сертификат ноды...")
        cert_check = await session.run(f"test -f {shlex.quote(certs_dir)}/ssl_cert.pem")
        if cert_check.exit_status != 0:
            await session.run_checked(
                "openssl req -x509 -newkey rsa:2048 -nodes -days 3650 "
                f"-keyout {shlex.quote(certs_dir)}/ssl_key.pem "
                f"-out {shlex.quote(certs_dir)}/ssl_cert.pem "
                f'-subj "/CN={target.host}" '
                f'-addext "subjectAltName=IP:{target.host}"',
                "Не удалось сгенерировать сертификат ноды.",
            )

        # Reuse an existing API_KEY across redeploys so the panel <-> node
        # binding doesn't break every time this installer is re-run.
        existing_env = await session.run(f"cat {shlex.quote(PASARGUARD_DIR)}/.env 2>/dev/null")
        api_key = None
        if existing_env.exit_status == 0:
            for line in (existing_env.stdout or "").splitlines():
                if line.strip().startswith("API_KEY"):
                    _, _, value = line.partition("=")
                    value = value.strip()
                    if value:
                        api_key = value
                    break
        api_key = api_key or str(uuid.uuid4())

        env_content = (
            "SERVICE_PORT = {port}\n"
            'NODE_HOST = "0.0.0.0"\n'
            "SSL_CERT_FILE = {certs_dir}/ssl_cert.pem\n"
            "SSL_KEY_FILE = {certs_dir}/ssl_key.pem\n"
            "API_KEY = {api_key}\n"
        ).format(port=PASARGUARD_PORT, certs_dir=certs_dir, api_key=api_key)

        await progress("📁 Настраиваю docker-compose и .env...")
        await session.deploy_file(PASARGUARD_COMPOSE, "docker-compose.yml", PASARGUARD_DIR, mode="644")
        await session.deploy_file(env_content, ".env", PASARGUARD_DIR, mode="600")

        await progress("🚀 Запускаю контейнер pg-node...")
        await session.run_checked(
            f"cd {shlex.quote(PASARGUARD_DIR)} && docker compose up -d --force-recreate",
            "Не удалось запустить контейнер pg-node.",
            timeout=300,
        )

        status = await session.run("docker ps --filter name=pg-node --format '{{.Status}}'")
        container_status = (status.stdout or "").strip() or "неизвестно"

        cert_result = await session.run(f"cat {shlex.quote(certs_dir)}/ssl_cert.pem")
        node_cert = (cert_result.stdout or "").strip()

        return NodeInstallResult(
            node_type="pasarguard",
            host=target.host,
            directory=PASARGUARD_DIR,
            container_status=container_status,
            extra={"api_key": api_key, "port": PASARGUARD_PORT, "cert": node_cert},
        )
    finally:
        await session.close()
