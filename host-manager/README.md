# host-manager

Automates provisioning and lifecycle management of multi-technology websites on a single VPS using Docker + Traefik. Supports local and remote (SSH) modes, idempotent operations, and a dry-run planner.

## Quickstart

1. Install Python 3.10+ and pipx or venv
2. From project root:

```bash
pip install -e ./host-manager
host-manager --help
```

## Demo flow (local)

```bash
host-manager --local --verbose install-platform
host-manager list-sites
```

Full documentation to be expanded as features land.
