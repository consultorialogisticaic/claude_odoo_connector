---
name: odoo-source-install
description: Install Odoo from source after cloning. Full platform coverage (Linux, macOS, Windows) for v14–v19. Covers Python env, system deps, PostgreSQL, wkhtmltopdf, and rtlcss.
---

You have been invoked as the Odoo source-installation expert.
The Odoo community repo is cloned at `odoo-workspace/<version>/odoo/`.
Your job is to install all dependencies and verify the environment is ready to run `odoo-bin`.

---

## Step 1 — Identify version and platform

Ask or detect:
- **Odoo version**: 14.0 through 19.0
- **OS**: Linux (Debian/Ubuntu), macOS, or Windows

All instructions below are keyed to both.

---

## Step 2 — Python version

| Odoo version | Minimum Python | Recommended |
|---|---|---|
| 14.0 | 3.8 | 3.8 |
| 15.0 | 3.8 | 3.8 |
| 16.0 | 3.10 | 3.10 |
| 17.0 | **3.10** (hard minimum) | 3.11 |
| 18.0 | **3.10** (hard minimum) | 3.11 |
| 19.0 | **3.10** (hard minimum) | 3.11 |

> As of Odoo 17 the minimum changed from 3.7 → 3.10 (official docs). Versions 3.7/3.8/3.9 will not work for v17+.

Verify:
```bash
# Linux / macOS
python3 --version

# Windows
python --version
```

If the version is too low, stop and create a new conda/venv environment with the correct Python before continuing.

---

## Step 3 — PostgreSQL

**Minimum version by Odoo release:**

| Odoo version | Min PostgreSQL |
|---|---|
| 14.0 – 18.0 | 12 |
| 19.0 | **13** |

### Linux (Debian/Ubuntu)
```bash
sudo apt install postgresql postgresql-client
sudo -u postgres createuser -d -R -S $USER
createdb $USER
```

### macOS
Install [Postgres.app](https://postgresapp.com) (PG 13+) or via Homebrew:
```bash
brew install postgresql@16
brew services start postgresql@16
# Add to PATH (add to ~/.zshrc permanently)
export PATH="$(brew --prefix postgresql@16)/bin:$PATH"
```

Create a role for Odoo (Odoo refuses to connect as `postgres`):
```bash
createuser -d -R -S odoo
# If prompted for password: odoo
```

### Windows
1. Download PostgreSQL 13+ from https://www.postgresql.org/download/windows
2. Add `C:\Program Files\PostgreSQL\<version>\bin` to PATH
3. Create the Odoo role via pgAdmin:
   - Object → Create → Login/Group Role
   - Role Name: `odoo`, Password: `odoo`
   - Privileges tab: **Can login** = Yes, **Create database** = Yes

---

## Step 4 — System-level build dependencies

These are needed to compile C-extension wheels (`python-ldap`, `psycopg2`, `lxml`, etc.).

### Linux (Debian/Ubuntu) — preferred: debinstall.sh

The fastest path uses the script shipped with Odoo (v15+):
```bash
cd odoo-workspace/<version>/odoo
sudo ./setup/debinstall.sh
```

This parses `debian/control` and installs exactly what's needed. For v14 (no debinstall.sh) or as a fallback:
```bash
sudo apt install python3-dev python3-pip \
  libldap2-dev libpq-dev libsasl2-dev \
  libxml2-dev libxslt1-dev zlib1g-dev libffi-dev
```

### macOS
```bash
# Xcode command-line tools (one-time)
xcode-select --install 2>/dev/null || true

# Homebrew dependencies
brew install libxml2 libxslt openldap postgresql
```

For v14/v15 `python-ldap` (needs explicit flags):
```bash
LDFLAGS="-L$(brew --prefix openldap)/lib" \
CPPFLAGS="-I$(brew --prefix openldap)/include" \
pip install python-ldap
```

### Windows
1. Download **Build Tools for Visual Studio** from https://visualstudio.microsoft.com/downloads/
2. In the installer, select **"C++ build tools"** workload → Install
3. Open terminal **as Administrator** for pip install steps

---

## Step 5 — pip install

```bash
ODOO_SRC="odoo-workspace/<version>/odoo"

# Upgrade build tooling first (critical for v14/v15)
pip install --upgrade pip setuptools wheel   # Linux/macOS: pip3
# Windows: py -m pip install --upgrade pip setuptools wheel

# Install Odoo's pinned dependencies
pip install -r "$ODOO_SRC/requirements.txt"
# Windows: py -m pip install -r %ODOO_SRC%\requirements.txt
```

### Version-specific extras

| Odoo | Extra action |
|---|---|
| v14 | `pip install Mako` (removed in v15) |
| v14/v15 | macOS: install `python-ldap` with explicit LDFLAGS/CPPFLAGS (see Step 4) |
| v17+ | `geoip2` is in requirements.txt — GeoLite2 DB optional for demos |
| v18/v19 | `asn1crypto`, `cbor2`, `openpyxl` in requirements.txt — no extra action |
| v19 Python 3.13+ | `PyPDF` replaces `PyPDF2`; `gevent>=24.11.1`, `greenlet>=3.1.1` required — pip resolves automatically |

---

## Step 6 — wkhtmltopdf

Required for PDF report generation. **Not a pip package** — must be a system binary installed separately. The repository version on Debian/Ubuntu **does not** include the patched Qt needed for headers/footers.

### Version compatibility table

| Odoo version | wkhtmltopdf | Notes |
|---|---|---|
| ≤ 9.0 | 0.12.1 | Minimal supported; known memory issues on 500+ page docs |
| 10.0 – 15.0 | **0.12.5-1** | `--zoom 96/DPI` workaround auto-enabled from v10 onward |
| 16.0 – 19.0 | **0.12.6.1-3** | `--disable-local-file-access` on by default |

> Versions 0.12.2 / 0.12.3 / 0.12.4: **do not use** — `--dpi` is broken on these.

### Installation by platform

**Linux (Debian/Ubuntu) — v10–v15 (0.12.5-1):**
```bash
# Download the .deb for your distro from:
# https://github.com/wkhtmltopdf/wkhtmltopdf/releases/tag/0.12.5
wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
sudo apt-get install -f   # resolve dependencies if any
```

**Linux (Debian/Ubuntu) — v16–v19 (0.12.6.1-3):**
```bash
# Download the .deb for your distro from:
# https://github.com/wkhtmltopdf/packaging/releases/tag/0.12.6.1-3
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-3.jammy_amd64.deb
sudo apt-get install -f
```

**macOS — all versions:**

Download the `.pkg` from the appropriate release page:
- 0.12.5-1: https://github.com/wkhtmltopdf/wkhtmltopdf/releases/tag/0.12.5
- 0.12.6.1-3: https://github.com/wkhtmltopdf/packaging/releases/tag/0.12.6.1-3

> The Homebrew `wkhtmltopdf` formula does **not** include the patched Qt build. Always use the official `.pkg`.

On Apple Silicon (M1/M2/M3), use the macOS Intel build under Rosetta, or check for an ARM64 build in the release assets.

**Windows — all versions:**

Download the `.exe` installer from the same release pages above and run it. Add the install directory to PATH if not done automatically.

**Verify:**
```bash
wkhtmltopdf --version
# Should output e.g.: wkhtmltopdf 0.12.6.1 (with patched qt)
# "with patched qt" is required — if missing, headers/footers won't work
```

> For demo purposes wkhtmltopdf is optional — Odoo runs without it, PDF reports just won't render.

---

## Step 7 — rtlcss (optional)

Only needed for right-to-left language support (Arabic, Hebrew, Farsi).

**Linux / macOS:**
```bash
# Install Node.js first if needed
sudo apt install nodejs npm   # Linux
brew install node             # macOS

npm install -g rtlcss
```

**Windows:**
1. Download Node.js from https://nodejs.org/en/download
2. `npm install -g rtlcss`
3. Add `%APPDATA%\npm\` to PATH

---

## Step 8 — Smoke-test odoo-bin

```bash
# Linux / macOS
python3 odoo-workspace/<version>/odoo/odoo-bin --version

# Windows
python odoo-workspace\<version>\odoo\odoo-bin --version
```

Expected output: `Odoo Server <version>` (e.g., `Odoo Server 19.0`).

If this prints the version without import errors, the source install is complete.

---

## Quick-reference: key differences by version

| | v14 | v15 | v16 | v17 | v18 | v19 |
|---|---|---|---|---|---|---|
| **Python min** | 3.8 | 3.8 | 3.10 | **3.10** | **3.10** | **3.10** |
| **Python recommended** | 3.8 | 3.8 | 3.10 | 3.11 | 3.11 | 3.11 |
| **PostgreSQL min** | 12 | 12 | 12 | 12 | 12 | **13** |
| **debinstall.sh** | no | yes | yes | yes | yes | yes |
| **wkhtmltopdf** | 0.12.5-1 | 0.12.5-1 | 0.12.6.1-3 | 0.12.6.1-3 | 0.12.6.1-3 | 0.12.6.1-3 |
| **Mako** | yes | no | no | no | no | no |
| **geoip2** | no | no | no | yes | yes | yes |
| **openpyxl** | no | no | no | no | yes | yes |
| **cbor2 / asn1crypto** | no | no | no | no | yes | yes |
| **ebaysdk** | yes | yes | yes | yes | no | no |
| **Werkzeug min** | 0.16 | 0.16 | 2.0 | 2.0 | 2.0 | 2.0 |
| **python-ldap** | 3.1.0 | 3.1.0 | 3.4.0 | 3.4.0 | 3.4.0 | 3.4.4 |

---

## Troubleshooting

**`lxml` build fails on Python 3.12+:**
```bash
pip install lxml-html-clean   # split from lxml 5.x
```

**`gevent` / `greenlet` build fails:**
Needs a C compiler. macOS: ensure Xcode CLI tools installed. Python 3.13: use `gevent>=24.11.1` and `greenlet>=3.1.1`.

**`psycopg2` fails to compile:**
```bash
# macOS: point pip at Homebrew's libpq
export PATH="$(brew --prefix postgresql)/bin:$PATH"
pip install psycopg2 --no-cache-dir
```

**wkhtmltopdf says "without patched qt":**
You installed the wrong build (e.g. from Homebrew or system repo). Uninstall it and use the official `.pkg`/`.deb` from the release pages above.

**`xlrd 2.x` can't read `.xls` files (v18/v19):**
`xlrd 2.0+` dropped `.xls` support. Convert files to `.xlsx` or use `openpyxl` (already in requirements for v18/v19).

**`No module named 'odoo'` at import:**
Expected — `odoo-bin` bootstraps its own path. Always run via `python odoo-bin`, never `import odoo` directly.
