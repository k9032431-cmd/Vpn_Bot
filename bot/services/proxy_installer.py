from __future__ import annotations

import shlex
from dataclasses import dataclass

from bot.texts import proxy as texts
from bot.texts.translations import t

from .node_installer import ensure_docker
from .ssh_client import NodeInstallError, ProgressCallback, RemoteSession, SSHTarget

__all__ = ["ProxyInstallResult", "install_telegram_proxy"]

# mtg (https://github.com/9seconds/mtg) -- a single-binary MTProto proxy.
# Picked over the original Telegram MTProxy for this bot's purposes because
# it needs no fetched proxy-secret/proxy-multi.conf dance with Telegram's
# own config servers, just one container and a config file.
MTG_IMAGE = "nineseconds/mtg:2"
MTG_CONTAINER = "mtg"
MTG_DIR = "/opt/mtg"
MTG_PUBLIC_PORT = 443
MTG_INTERNAL_PORT = 3128
# A real, popular HTTPS site to disguise FakeTLS traffic as -- mtg bakes
# this into the generated secret itself (an "ee..."-prefixed secret), so a
# DPI box inspecting the TLS handshake sees what looks like a normal visit
# to this domain instead of anything proxy-shaped.
FAKE_TLS_DOMAIN = "www.google.com"


@dataclass
class ProxyInstallResult:
    host: str
    port: int
    secret: str
    link: str


async def install_telegram_proxy(target: SSHTarget, progress: ProgressCallback, lang: str) -> ProxyInstallResult:
    await progress(texts.progress_connecting(lang))
    session = await RemoteSession.connect(target)
    try:
        await progress(texts.progress_checking_docker(lang))
        await ensure_docker(session, progress, lang)

        await progress(texts.progress_generating_secret(lang))
        secret_result = await session.run_checked(
            f"docker run --rm {MTG_IMAGE} generate-secret --hex {shlex.quote(FAKE_TLS_DOMAIN)}",
            t(lang, "err_proxy_secret"),
            timeout=120,
        )
        secret = (secret_result.stdout or "").strip()
        if not secret:
            raise NodeInstallError(t(lang, "err_proxy_secret"))

        # bind-to is the container's own internal port -- the public port
        # the user actually connects to is just a host-side docker -p
        # mapping onto it, kept deliberately separate from what's inside
        # the config so a redeploy never has to touch this file's content.
        config_toml = f'secret = "{secret}"\nbind-to = "0.0.0.0:{MTG_INTERNAL_PORT}"\n'
        await session.deploy_file(config_toml, "config.toml", MTG_DIR, mode="600")

        await progress(texts.progress_launching(lang))
        # Clears out a previous run of this same installer so re-running it
        # on a server that already has mtg on it redeploys cleanly instead
        # of failing on "container name already in use" -- ignored if no
        # such container exists yet.
        await session.run(f"docker rm -f {MTG_CONTAINER}")
        await session.run_checked(
            f"docker run -d --name {MTG_CONTAINER} --restart unless-stopped "
            f"-v {shlex.quote(MTG_DIR)}/config.toml:/config.toml "
            f"-p {MTG_PUBLIC_PORT}:{MTG_INTERNAL_PORT} {MTG_IMAGE}",
            t(lang, "err_proxy_run"),
        )

        status = await session.run(f"docker ps --filter name={MTG_CONTAINER} --format '{{{{.Status}}}}'")
        container_status = (status.stdout or "").strip()
        if not container_status:
            raise NodeInstallError(t(lang, "err_proxy_not_running"))

        link = f"https://t.me/proxy?server={target.host}&port={MTG_PUBLIC_PORT}&secret={secret}"
        return ProxyInstallResult(host=target.host, port=MTG_PUBLIC_PORT, secret=secret, link=link)
    finally:
        await session.close()
