from __future__ import annotations

import shlex
import uuid
from dataclasses import dataclass, field

from bot.texts import node as texts
from bot.texts.translations import t

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


async def _ensure_docker(session: RemoteSession, progress: ProgressCallback, lang: str) -> None:
    check = await session.run("command -v docker")
    if check.exit_status == 0:
        await session.run_checked(
            "systemctl enable --now docker 2>/dev/null || service docker start",
            t(lang, "err_docker_start"),
        )
    else:
        await progress(texts.progress_installing_docker(lang))
        await session.run(
            "command -v curl >/dev/null 2>&1 || "
            "(apt-get update -y && apt-get install -y curl) || "
            "(yum install -y curl) || (dnf install -y curl)"
        )
        await session.run_checked(
            "curl -fsSL https://get.docker.com | sh",
            t(lang, "err_docker_install"),
            timeout=900,
        )
        await session.run_checked(
            "systemctl enable --now docker",
            t(lang, "err_docker_after_install"),
        )

    compose_check = await session.run("docker compose version")
    if compose_check.exit_status != 0:
        await progress(texts.progress_installing_compose(lang))
        await session.run_checked(
            "(apt-get update -y && apt-get install -y docker-compose-plugin) || "
            "(yum install -y docker-compose-plugin) || "
            "(dnf install -y docker-compose-plugin)",
            t(lang, "err_compose_install"),
        )


async def install_marzban_node(
    target: SSHTarget,
    cert_pem: str,
    progress: ProgressCallback,
    lang: str,
) -> NodeInstallResult:
    await progress(texts.progress_connecting(lang))
    session = await RemoteSession.connect(target)
    try:
        await progress(texts.progress_checking_docker(lang))
        await _ensure_docker(session, progress, lang)

        await progress(texts.progress_uploading_marzban(lang))
        await session.deploy_file(cert_pem, MARZBAN_CERT_FILENAME, MARZBAN_DIR, mode="600")
        await session.deploy_file(MARZBAN_COMPOSE, "docker-compose.yml", MARZBAN_DIR, mode="644")

        await progress(texts.progress_launching(lang, "marzban-node"))
        await session.run_checked(
            f"cd {shlex.quote(MARZBAN_DIR)} && docker compose up -d --force-recreate",
            t(lang, "err_marzban_up"),
            timeout=300,
        )

        status = await session.run("docker ps --filter name=marzban-node --format '{{.Status}}'")
        container_status = (status.stdout or "").strip() or "?"

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
    lang: str,
) -> NodeInstallResult:
    await progress(texts.progress_connecting(lang))
    session = await RemoteSession.connect(target)
    try:
        await progress(texts.progress_checking_docker(lang))
        await _ensure_docker(session, progress, lang)

        certs_dir = f"{PASARGUARD_DIR}/certs"
        await session.run_checked(f"mkdir -p {shlex.quote(certs_dir)}", t(lang, "err_mkdir"))

        await progress(texts.progress_generating_pasarguard_cert(lang))
        cert_check = await session.run(f"test -f {shlex.quote(certs_dir)}/ssl_cert.pem")
        if cert_check.exit_status != 0:
            await session.run_checked(
                "openssl req -x509 -newkey rsa:2048 -nodes -days 3650 "
                f"-keyout {shlex.quote(certs_dir)}/ssl_key.pem "
                f"-out {shlex.quote(certs_dir)}/ssl_cert.pem "
                f'-subj "/CN={target.host}" '
                f'-addext "subjectAltName=IP:{target.host}"',
                t(lang, "err_cert_gen"),
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

        await progress(texts.progress_uploading_pasarguard(lang))
        await session.deploy_file(PASARGUARD_COMPOSE, "docker-compose.yml", PASARGUARD_DIR, mode="644")
        await session.deploy_file(env_content, ".env", PASARGUARD_DIR, mode="600")

        await progress(texts.progress_launching(lang, "pg-node"))
        await session.run_checked(
            f"cd {shlex.quote(PASARGUARD_DIR)} && docker compose up -d --force-recreate",
            t(lang, "err_pasarguard_up"),
            timeout=300,
        )

        status = await session.run("docker ps --filter name=pg-node --format '{{.Status}}'")
        container_status = (status.stdout or "").strip() or "?"

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
