from __future__ import annotations

import json
import os
from typing import Optional

import click

from .executor import Executor, SSHConfig, prompt_password_if_needed
from .logging_setup import setup_logging, get_logger
from .os_detect import detect_os


logger = get_logger(__name__)


class NaturalOrderGroup(click.Group):
    def list_commands(self, ctx):
        return list(self.commands)


@click.group(cls=NaturalOrderGroup)
@click.option("--local", "local_mode", is_flag=True, default=False, help="Run on local host")
@click.option("--remote", "remote_mode", is_flag=True, default=False, help="Run via SSH on remote host")
@click.option("--host", default=None, help="Remote host (ip or name)")
@click.option("--ssh-user", default=None, help="SSH username")
@click.option("--ssh-port", default=22, type=int, help="SSH port")
@click.option("--ssh-key", default=None, help="Path to SSH private key")
@click.option("--ssh-pass", default=None, help="SSH password (discouraged); if omitted will prompt")
@click.option("--dry-run", is_flag=True, default=False, help="Print actions without executing")
@click.option("--yes", is_flag=True, default=False, help="Assume yes for confirmations")
@click.option("--verbose", is_flag=True, default=False, help="Verbose logging")
@click.option("--log-file", default="/var/log/host-manager/host-manager.log", show_default=True)
@click.pass_context
def cli(ctx, local_mode, remote_mode, host, ssh_user, ssh_port, ssh_key, ssh_pass, dry_run, yes, verbose, log_file):
    if not local_mode and not remote_mode:
        local_mode = True
    if remote_mode and not host:
        raise click.UsageError("--remote requires --host")
    if remote_mode and not ssh_user:
        raise click.UsageError("--remote requires --ssh-user")

    setup_logging(log_file=log_file, verbose=verbose)

    ssh_cfg = None
    if remote_mode:
        ssh_cfg = SSHConfig(
            host=host,
            user=ssh_user,
            port=ssh_port,
            key=ssh_key,
            password=prompt_password_if_needed(ssh_pass) if ssh_key is None else None,
        )

    executor = Executor(local=local_mode, ssh=ssh_cfg, dry_run=dry_run)

    ctx.ensure_object(dict)
    ctx.obj["executor"] = executor
    ctx.obj["yes"] = yes
    ctx.obj["dry_run"] = dry_run


@cli.command()
@click.pass_context
def install_platform(ctx):
    """Install Docker, Traefik, firewall and base directories."""
    ex: Executor = ctx.obj["executor"]

    os_info = detect_os(ex)
    if not os_info or not os_info.is_supported():
        raise click.ClickException("Unsupported OS. Ubuntu 20.04/22.04/24.04 or Debian 11/12 required.")
    click.echo(f"Detected OS: {os_info.pretty_name}")

    _install_prereqs(ex)
    _install_docker(ex, os_info.id)
    _create_base_dirs(ex)
    click.echo("Platform base installed. Traefik and security stack installation will follow in subsequent steps.")


def _install_prereqs(ex: Executor):
    ex.run("apt-get update", sudo=True)
    ex.run("apt-get install -y ca-certificates curl gnupg lsb-release git ufw fail2ban", sudo=True)


def _install_docker(ex: Executor, os_id: str):
    ex.run("install -d -m 0755 /etc/apt/keyrings", sudo=True)
    ex.run("curl -fsSL https://download.docker.com/linux/$(. /etc/os-release; echo $ID)/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg", sudo=True)
    ex.run("chmod a+r /etc/apt/keyrings/docker.gpg", sudo=True)
    ex.run(
        "echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/\$(. /etc/os-release; echo $ID) \$(. /etc/os-release; echo $VERSION_CODENAME) stable\" > /etc/apt/sources.list.d/docker.list",
        sudo=True,
    )
    ex.run("apt-get update", sudo=True)
    ex.run("apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin", sudo=True)
    ex.run("usermod -aG docker $(id -un)", sudo=True)


def _create_base_dirs(ex: Executor):
    for d in [
        "/srv/sites",
        "/srv/volumes",
        "/srv/traefik",
        "/var/backups/host-manager",
        "/opt/host-manager-config",
    ]:
        ex.ensure_dir(d, sudo=True)


@cli.command()
@click.pass_context
def list_sites(ctx):
    """List managed sites (basic stub)."""
    ex: Executor = ctx.obj["executor"]
    code, out, _ = ex.run("ls -1 /srv/sites | sed 's/^/domain: /'")
    if code != 0:
        click.echo("No sites or cannot access /srv/sites")
        return
    click.echo(out)


def main():
    cli(obj={})


if __name__ == "__main__":
    main()
