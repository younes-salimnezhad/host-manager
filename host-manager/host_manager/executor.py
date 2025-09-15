from __future__ import annotations

import getpass
import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple

from fabric import Connection
from invoke import UnexpectedExit

from .logging_setup import get_logger


logger = get_logger(__name__)


@dataclass
class SSHConfig:
    host: str
    user: str
    port: int = 22
    key: Optional[str] = None
    password: Optional[str] = None


class CommandError(RuntimeError):
    pass


class Executor:
    def __init__(self, local: bool = True, ssh: Optional[SSHConfig] = None, dry_run: bool = False):
        self.local = local
        self.ssh = ssh
        self.dry_run = dry_run
        self._conn: Optional[Connection] = None

    def _ensure_conn(self) -> Connection:
        if self._conn is not None:
            return self._conn
        if self.local:
            raise RuntimeError("Local executor does not use SSH")
        if not self.ssh:
            raise RuntimeError("SSH configuration is required for remote mode")
        connect_kwargs = {}
        if self.ssh.key:
            connect_kwargs["key_filename"] = [self.ssh.key]
        if self.ssh.password:
            connect_kwargs["password"] = self.ssh.password
        self._conn = Connection(
            host=self.ssh.host,
            user=self.ssh.user,
            port=self.ssh.port,
            connect_kwargs=connect_kwargs,
        )
        return self._conn

    def run(self, command: str, sudo: bool = False, env: Optional[dict] = None, cwd: Optional[str] = None) -> Tuple[int, str, str]:
        full_cmd = command
        if env:
            exports = " ".join(f"{k}={shlex.quote(str(v))}" for k, v in env.items())
            full_cmd = f"{exports} {full_cmd}"
        if cwd:
            full_cmd = f"cd {shlex.quote(cwd)} && {full_cmd}"
        if sudo:
            full_cmd = f"sudo -H bash -lc {shlex.quote(full_cmd)}"
        else:
            full_cmd = f"bash -lc {shlex.quote(full_cmd)}"

        logger.debug(f"EXEC {'(dry-run) ' if self.dry_run else ''}{full_cmd}")
        if self.dry_run:
            return 0, "", ""

        if self.local:
            proc = subprocess.Popen(
                full_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            out, err = proc.communicate()
            return proc.returncode, out, err
        else:
            conn = self._ensure_conn()
            try:
                result = conn.run(full_cmd, hide=True, warn=True)
                return result.exited or 0, result.stdout, result.stderr
            except UnexpectedExit as exc:
                return exc.result.exited or 1, exc.result.stdout, exc.result.stderr

    def put(self, local_path: str, remote_path: str) -> None:
        logger.debug(f"PUT {'(dry-run) ' if self.dry_run else ''}{local_path} -> {remote_path}")
        if self.dry_run:
            return
        if self.local:
            os.makedirs(os.path.dirname(remote_path), exist_ok=True)
            with open(local_path, "rb") as src, open(remote_path, "wb") as dst:
                dst.write(src.read())
        else:
            conn = self._ensure_conn()
            conn.put(local_path, remote=remote_path)

    def exists(self, path: str) -> bool:
        code, _, _ = self.run(f"test -e {shlex.quote(path)}")
        return code == 0

    def ensure_dir(self, path: str, sudo: bool = False, mode: str = "0755") -> None:
        self.run(f"install -d -m {mode} {shlex.quote(path)}", sudo=sudo)

    def write_file(self, path: str, content: str, sudo: bool = False, mode: str = "0644") -> None:
        escaped = content.replace("'", "'\\''")
        self.run(f"install -m {mode} /dev/stdin {shlex.quote(path)} <<'EOF'\n{escaped}\nEOF", sudo=sudo)


def prompt_password_if_needed(password: Optional[str]) -> Optional[str]:
    if password:
        return password
    try:
        return getpass.getpass("SSH password: ")
    except Exception:
        return None
