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

Choose one of the two modes below.

1) Run directly ON the VPS (local mode):
```bash
# Log in to the VPS, then install prerequisites
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
# Optional: make `python` point to python3
sudo apt install -y python-is-python3

# Clone the repository (adjust directory as you like)
cd /opt
sudo git clone https://github.com/younes-salimnezhad/host-manager.git
sudo chown -R "$USER":"$USER" host-manager
cd host-manager/host-manager

# Create and activate virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode
pip install -U pip
pip install -e .

# Verify CLI
host-manager --help
```

2) Run from your workstation against the VPS (remote mode):
```bash
# On your workstation with network access to the VPS
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ./host-manager

# First-time bootstrap on the remote server using SSH key
host-manager --remote --host <IP_OR_NAME> --ssh-user <USER> install-platform
```
Notes:
- If using password instead of key, omit `--ssh-key` and you’ll be securely prompted.
- Ensure the remote user has sudo privileges.

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
- Command `python` not found:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip
  sudo apt install -y python-is-python3 # optional
  ```
- `.venv/bin/activate: No such file or directory`:
  - You are not in the correct directory or did not create the venv.
  - Run inside `host-manager/host-manager`:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
- `host-manager: command not found`:
  - Ensure the venv is active and you ran `pip install -e .` in the same folder as `pyproject.toml`.
- Docker permission denied:
  ```bash
  sudo usermod -aG docker $USER
  # log out and log back in (or reboot) to apply group changes
  ```
- Traefik ACME issues: correct domain DNS; check `acme.json` perms (600)
- Hetzner volume attach fails: ensure `hcloud` is installed and token is valid
- UFW blocks web: verify 80/443 allows

### Development
```bash
python3 -m venv .venv
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

دو حالت نصب وجود دارد:

1) اجرا روی خود سرور (local):
```bash
# ورود به سرور و نصب پیش‌نیازها
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
# اختیاری: اشاره دستور python به python3
sudo apt install -y python-is-python3

# کلون ریپازیتوری
cd /opt
sudo git clone https://github.com/younes-salimnezhad/host-manager.git
sudo chown -R "$USER":"$USER" host-manager
cd host-manager/host-manager

# ساخت و فعال‌سازی محیط مجازی
python3 -m venv .venv
source .venv/bin/activate

# نصب پکیج
pip install -U pip
pip install -e .

# تست ابزار
host-manager --help
```

2) اجرا از روی سیستم مدیریت (remote) روی سرور:
```bash
# روی سیستم مدیریت
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ./host-manager

# اجرای اولیه نصب روی سرور با SSH
host-manager --remote --host <آی‌پی_یا_نام> --ssh-user <کاربر> install-platform
```
نکات:
- در صورت استفاده از رمز به‌جای کلید، `--ssh-key` را نگذارید تا رمز امن پرسیده شود.
- کاربر روی سرور باید دسترسی sudo داشته باشد.

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
- خطای `python` یا `pip` پیدا نشد:
  ```bash
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip
  sudo apt install -y python-is-python3  # اختیاری
  ```
- خطای `.venv/bin/activate: No such file or directory`:
  - مسیر اشتباه است یا venv ساخته نشده است.
  - داخل پوشه `host-manager/host-manager` اجرا کنید:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
- خطای `host-manager: command not found`:
  - مطمئن شوید venv فعال است و `pip install -e .` را در همان پوشه‌ی `pyproject.toml` اجرا کرده‌اید.
- خطای مجوز Docker:
  ```bash
  sudo usermod -aG docker $USER
  # برای اعمال گروه، یک‌بار خروج/ورود کنید یا سرور را ریبوت کنید
  ```
- مشکلات Traefik/ACME: تنظیم DNS دامنه و سطح دسترسی `acme.json` (مجوز 600)
- مشکل اتصال Volume در Hetzner: نصب بودن `hcloud` و اعتبار توکن
- بلاک بودن وب توسط UFW: اجازه پورت‌های 80/443 را بررسی کنید

### توسعه
```bash
python3 -m venv .venv
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
