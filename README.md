<!-- Language: Switcher -->
<p align="center">
  <a href="#english">English</a> | <a href="#فارسی">فارسی</a>
</p>

---

# host-manager

Automate provisioning and lifecycle management of multi-technology customer websites on a single VPS using Docker + Traefik. Supports Ubuntu LTS and Debian, local or remote (SSH) execution, idempotent operations, and dry-run mode, with sensible security defaults.

- Tech: Python 3.10+, Docker Engine + Compose v2, Traefik v2, UFW, fail2ban, optional Netdata
- Modes: `--local` (run on target) or `--remote` (Fabric/SSH)
- Sites: Node.js, PHP (php-fpm+nginx), Python (gunicorn+nginx), optional per-site DB
- Quotas: CPU/memory/pids via Docker limits; disk via Hetzner Volume or XFS project quotas
- Security: UFW (SSH/HTTP/HTTPS), fail2ban basic jail
- TLS: Traefik ACME/Let's Encrypt (HTTP-01)
- Backups: per-site tar + DB dump, local retention, optional SFTP upload

> Note: Initial version includes platform install and listing. Site create/update/delete will be added incrementally.

---

## Table of Contents
- [English](#english)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Examples](#examples)
  - [Architecture](#architecture)
  - [Security & Operations](#security--operations)
  - [Troubleshooting](#troubleshooting)
  - [Development](#development)
- [فارسی](#فارسی)
  - [پیش‌نیازها](#پیشنیازها)
  - [نصب](#نصب)
  - [نحوه استفاده](#نحوه-استفاده)
  - [مثال‌ها](#مثالها)
  - [معماری](#معماری)
  - [امنیت و عملیات](#امنیت-و-عملیات)
  - [رفع اشکال](#رفع-اشکال)
  - [توسعه](#توسعه)

---

## English

### Requirements
- Python 3.10+
- A target VPS (typical: 2 vCPU, 4 GB RAM)
- Supported OS on target: Ubuntu 20.04/22.04/24.04, Debian 11/12
- Network access: 22/tcp (SSH), 80/tcp (HTTP), 443/tcp (HTTPS)
- Optional: Hetzner API token (`HCLOUD_TOKEN`) for per-site volumes

### Installation

Install from source (editable):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ./host-manager
host-manager --help
```

Remote mode prerequisites (running from your workstation):
- SSH key access recommended; user must have sudo on the target

### Usage

Global flags:
- `--local` or `--remote --host <host> --ssh-user <user> [--ssh-key <path>] [--ssh-port N]`
- `--dry-run` to preview actions; `--yes` for non-interactive
- `--verbose` for detailed logs; `--log-file /var/log/host-manager/host-manager.log`

Commands:
- `install-platform` — Install Docker/Compose, base dirs, security packages
- `list-sites` — Show managed sites
- Planned: `create-site`, `update-site`, `delete-site`, `backup-site`, `restore-site`, `install-hcloud`

### Examples

Local bootstrap:
```bash
host-manager --local install-platform
host-manager --local list-sites
```

Remote bootstrap with SSH key:
```bash
host-manager --remote --host 203.0.113.10 --ssh-user root install-platform
```

Dry-run:
```bash
host-manager --local --dry-run --verbose install-platform
```

### Architecture
```mermaid
flowchart LR
  subgraph VPS
    Traefik[Traefik v2]
    UFW[UFW]
    F2B[fail2ban]
    Netdata[(Netdata)]
    subgraph SiteStacks[/Sites/]
      S1[Node/PHP/Python Stack A]
      S2[Node/PHP/Python Stack B]
    end
  end

  Internet -->|80/443| Traefik
  Traefik -->|Docker provider + labels| S1
  Traefik -->|Docker provider + labels| S2
  UFW -. allows .->|22/80/443| Internet
  F2B -. monitors .-> VPS
  Netdata -. optional metrics .-> VPS

  subgraph Storage
    Vols[/Hetzner Volumes or XFS loopback/]
  end

  S1 --- Vols
  S2 --- Vols
```

### Security & Operations
- UFW default deny incoming; allow SSH (configurable port), HTTP, HTTPS
- fail2ban basic SSH jail (extendable)
- Prefer SSH keys; never store plaintext passwords
- Logs under `/var/log/host-manager/host-manager.log` with rotation

### Troubleshooting
- Docker permission denied: add user to `docker` group and re-login
- Traefik ACME issues: correct domain DNS; check `acme.json` perms (600)
- Hetzner volume attach fails: ensure `hcloud` is installed and token is valid
- UFW blocks web: verify 80/443 allows

### Development
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./host-manager
pytest -q
```

---

## فارسی

### پیش‌نیازها
- پایتون 3.10 یا بالاتر
- سرور VPS (مثلاً 2 vCPU و 4GB RAM)
- سیستم‌عامل پشتیبانی‌شده: Ubuntu 20.04/22.04/24.04 یا Debian 11/12
- دسترسی شبکه: پورت‌های 22 (SSH)، 80 (HTTP)، 443 (HTTPS)
- اختیاری: توکن Hetzner (`HCLOUD_TOKEN`) برای ساخت Volume اختصاصی هر سایت

### نصب

نصب از سورس (حالت قابل ویرایش):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ./host-manager
host-manager --help
```

در حالت ریموت (از سیستم مدیریت):
- پیشنهاد می‌شود از کلید SSH استفاده کنید و کاربر روی سرور دسترسی sudo داشته باشد.

### نحوه استفاده

سوئیچ‌های عمومی:
- `--local` یا `--remote --host <host> --ssh-user <user> [--ssh-key <path>] [--ssh-port N]`
- `--dry-run` برای پیش‌نمایش عملیات؛ `--yes` برای اجرا بدون سوال
- `--verbose` برای لاگ بیشتر؛ `--log-file /var/log/host-manager/host-manager.log`

دستورات:
- `install-platform` — نصب Docker/Compose، پوشه‌های پایه، پکیج‌های امنیتی
- `list-sites` — نمایش سایت‌های مدیریت‌شده
- برنامه آینده: `create-site`، `update-site`، `delete-site`، `backup-site`، `restore-site`، `install-hcloud`

### مثال‌ها

راه‌اندازی محلی:
```bash
host-manager --local install-platform
host-manager --local list-sites
```

راه‌اندازی ریموت با کلید SSH:
```bash
host-manager --remote --host 203.0.113.10 --ssh-user root install-platform
```

Dry-run:
```bash
host-manager --local --dry-run --verbose install-platform
```

### معماری
```mermaid
flowchart LR
  subgraph VPS
    Traefik[Traefik v2]
    UFW[UFW]
    F2B[fail2ban]
    Netdata[(Netdata)]
    subgraph SiteStacks[/سایت‌ها/]
      S1[استک Node/PHP/Python A]
      S2[استک Node/PHP/Python B]
    end
  end

  Internet -->|80/443| Traefik
  Traefik -->|Docker provider + labels| S1
  Traefik -->|Docker provider + labels| S2
  UFW -. مجاز می‌کند .->|22/80/443| Internet
  F2B -. مانیتور می‌کند .-> VPS
  Netdata -. شاخص‌ها (اختیاری) .-> VPS

  subgraph Storage
    Vols[/Hetzner Volumes یا XFS loopback/]
  end

  S1 --- Vols
  S2 --- Vols
```

### امنیت و عملیات
- UFW به‌صورت پیش‌فرض ورودی را مسدود می‌کند؛ پورت‌های SSH/HTTP/HTTPS را باز کنید
- fail2ban برای SSH (قابل گسترش برای سرویس‌های دیگر)
- استفاده از کلید SSH توصیه می‌شود؛ رمزها را ذخیره نکنید
- لاگ‌ها در مسیر `/var/log/host-manager/host-manager.log` با چرخش

### رفع اشکال
- خطای مجوز Docker: کاربر را به گروه `docker` اضافه کنید و مجدد وارد شوید
- مشکل صدور گواهی Traefik/ACME: DNS صحیح، دسترسی فایل `acme.json` (مجوز 600)
- مشکل اتصال Volume در Hetzner: نصب بودن `hcloud` و اعتبار توکن را بررسی کنید
- بلاک بودن وب توسط UFW: اجازه پورت‌های 80/443 را بررسی کنید

### توسعه
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ./host-manager
pytest -q
```

---

<p align="center">
  <a id="english"></a>
  <a href="#فارسی">Switch to فارسی</a>
  ·
  <a href="#english">Back to English</a>
</p>
