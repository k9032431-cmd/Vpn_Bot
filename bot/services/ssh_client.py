from __future__ import annotations

import asyncio
import shlex
import uuid
from dataclasses import dataclass
from typing import Awaitable, Callable

import asyncssh

from bot.texts.translations import t

ProgressCallback = Callable[[str], Awaitable[None]]

CONNECT_TIMEOUT = 20
COMMAND_TIMEOUT = 600


class NodeInstallError(Exception):
    """Raised when the remote node installation cannot proceed."""


@dataclass
class SSHTarget:
    host: str
    username: str
    password: str
    port: int = 22
    lang: str = "ru"


class RemoteSession:
    """Wraps an asyncssh connection and transparently elevates every
    command with sudo when the login user is not root.

    Cloud images (Azure included) almost never allow direct root SSH
    login, so every command here is routed through ``sudo -S`` with the
    SSH password piped over stdin when passwordless sudo isn't already
    configured. This lets the installer work the same way regardless of
    how the target server is set up.
    """

    def __init__(self, conn: asyncssh.SSHClientConnection, target: SSHTarget) -> None:
        self._conn = conn
        self._target = target
        self._sudo_mode = "root"  # "root" | "nopasswd" | "password"

    @classmethod
    async def connect(cls, target: SSHTarget) -> "RemoteSession":
        try:
            conn = await asyncio.wait_for(
                asyncssh.connect(
                    target.host,
                    port=target.port,
                    username=target.username,
                    password=target.password,
                    known_hosts=None,
                ),
                timeout=CONNECT_TIMEOUT,
            )
        except asyncio.TimeoutError as exc:
            raise NodeInstallError(t(target.lang, "err_ssh_timeout")) from exc
        except asyncssh.PermissionDenied as exc:
            raise NodeInstallError(t(target.lang, "err_ssh_auth")) from exc
        except (OSError, asyncssh.Error) as exc:
            raise NodeInstallError(t(target.lang, "err_ssh_connect", error=str(exc))) from exc

        session = cls(conn, target)
        session._sudo_mode = await session._detect_sudo_mode()
        return session

    async def _detect_sudo_mode(self) -> str:
        whoami = await self._conn.run("whoami", check=False)
        current_user = (whoami.stdout or "").strip()
        if current_user == "root":
            return "root"

        passwordless = await self._conn.run("sudo -n true", check=False)
        if passwordless.exit_status == 0:
            return "nopasswd"

        probe = await self._conn.run(
            "sudo -S -p '' true",
            input=self._target.password + "\n",
            check=False,
        )
        if probe.exit_status == 0:
            return "password"

        raise NodeInstallError(
            t(self._target.lang, "err_sudo_denied", user=self._target.username)
        )

    async def run(self, command: str, timeout: int = COMMAND_TIMEOUT) -> asyncssh.SSHCompletedProcess:
        wrapped = f"bash -c {shlex.quote(command)}"
        if self._sudo_mode == "root":
            return await asyncio.wait_for(self._conn.run(wrapped, check=False), timeout=timeout)
        if self._sudo_mode == "nopasswd":
            return await asyncio.wait_for(
                self._conn.run(f"sudo -n {wrapped}", check=False), timeout=timeout
            )
        return await asyncio.wait_for(
            self._conn.run(
                f"sudo -S -p '' {wrapped}",
                input=self._target.password + "\n",
                check=False,
            ),
            timeout=timeout,
        )

    async def run_checked(
        self, command: str, error_hint: str, timeout: int = COMMAND_TIMEOUT
    ) -> asyncssh.SSHCompletedProcess:
        result = await self.run(command, timeout=timeout)
        if result.exit_status != 0:
            details = (result.stderr or result.stdout or "").strip()
            details = details[-800:] if details else t(self._target.lang, "err_no_details")
            raise NodeInstallError(f"{error_hint}\n\n<code>{details}</code>")
        return result

    async def _write_to_home(self, filename: str, content: str) -> str:
        """Writes content into the login user's own home directory over
        SFTP (no elevated privileges needed there), returning the path."""
        home_result = await self._conn.run("echo $HOME", check=False)
        home = (home_result.stdout or "").strip() or "/tmp"
        tmp_path = f"{home}/.arsicloudbot_{uuid.uuid4().hex}_{filename}"
        async with self._conn.start_sftp_client() as sftp:
            async with sftp.open(tmp_path, "w") as f:
                await f.write(content)
        return tmp_path

    async def deploy_file(self, content: str, filename: str, target_dir: str, mode: str = "600") -> None:
        """Uploads ``content`` as ``filename`` inside ``target_dir`` on the
        remote server, creating the directory (with sudo, if needed) since
        it commonly lives under /var/lib or /opt where the login user has
        no write access."""
        tmp_path = await self._write_to_home(filename, content)
        remote_path = f"{target_dir.rstrip('/')}/{filename}"
        try:
            # `mv` is a rename when source/target share a filesystem, so it
            # keeps the login user as owner even when run under sudo — chown
            # explicitly afterwards so the deployed file ends up root-owned.
            await self.run_checked(
                f"mkdir -p {shlex.quote(target_dir)} && "
                f"mv {shlex.quote(tmp_path)} {shlex.quote(remote_path)} && "
                f"chown root:root {shlex.quote(remote_path)} && "
                f"chmod {mode} {shlex.quote(remote_path)}",
                t(self._target.lang, "err_write_file", filename=filename),
            )
        finally:
            await self.run(f"rm -f {shlex.quote(tmp_path)}")

    async def close(self) -> None:
        self._conn.close()
        try:
            await self._conn.wait_closed()
        except Exception:
            pass
