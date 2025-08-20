# Statement Finder

[![CI](https://github.com/jared1776/statement_finder/actions/workflows/ci.yml/badge.svg)](https://github.com/jared1776/statement_finder/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue)

**Statement Finder** scans manager folders for client statements, filtered by **year**, **month**, **client**, and **statement type**.  
It exports a **CSV** of matches and a **ZIP** containing the matched files. Use the **CLI** for automation or the simple **Tkinter GUI** for quick runs.

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI](#cli)
  - [GUI](#gui)
- [Output](#output)
- [Matching Rules](#matching-rules)
- [Project Layout](#project-layout)
- [Development](#development)
- [Package to EXE (optional)](#package-to-exe-optional)
- [Use this as a Template](#use-this-as-a-template)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features
- Filter by **year** (`2024`), **month** (`03-March`), **client** (substring match), and **type** (`K-1`, `CC`, `STMT`, etc.).
- Exports a **CSV** (metadata) and a **ZIP** (the files themselves) per client.
- Works with **UNC network paths** on Windows (e.g., `//server/share/...`).
- Threaded scanning for decent performance on large directory trees.
- Clean repo structure ready for reuse as a GitHub **template**.

---

## Requirements
- **Python 3.10+** (Windows/macOS).
- Access to the share/folder where your data lives (manager → year → month → files).
- Optional for GUI: a desktop session (Tkinter apps won’t launch on headless servers).

---

## Quick Start

```powershell
# 1) Clone and enter the folder (or use GitHub's "Use this template")
git clone https://github.com/jared1776/statement_finder.git
cd statement_finder

# 2) Create & activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3) Install the package
python -m pip install --upgrade pip
pip install -e .

# 4) Create a config file and edit paths
Copy-Item config.example.yaml config.yaml
# then open config.yaml and set your paths (see below)

# 5) Try it out (CLI example)
statement-finder --year 2024 --month "03-March" `
  --clients "Smith Family,Johnson Trust" `
  --types "K-1,CC"

# Or launch the GUI
statement-finder-gui
---
## Configuration

Copy the example and update the paths:

Copy-Item config.example.yaml config.yaml


Edit config.yaml:

# Use quotes. UNC works well with forward slashes on Windows.
base_directory: '//server-or-host/Client/CLIENTS/Client Statements'
output_directory: '//server-or-host/Client/Generic/Performance/statement_finder_output'
logo_path: ''        # optional, only used by the GUI
log_file: 'logs/activity.log'


Tip: You can also pass --base-dir and --output-dir on the CLI to override config values.

---
## Usage
### CLI
# Show help
statement-finder --help

# Typical run (paths read from config.yaml)
statement-finder `
  --year 2024 `
  --month "03-March" `
  --clients "Smith Family,Johnson Trust" `
  --types "K-1,CC"


--year: folder like 2024. Leave empty to scan all years.

--month: folder like 03-March. Leave empty to scan all months.

--clients: comma-separated. Match is case-insensitive substring in filename.

--types: comma-separated codes (e.g., K-1,CC,STMT). Matching uses “whole-word-ish” boundaries, so CC will not match inside ACCOUNTS.

Override paths when needed:

statement-finder `
  --base-dir "//server/share/Client Statements" `
  --output-dir "//server/share/statement_finder_output" `
  --year 2025 --clients "Jones Family" --types "K-1"

### GUI
statement-finder-gui


Enter Base/Output directories (pre-filled from config.yaml if present), Year, Month, Clients, and Types.

Click Submit. The progress bar updates and a log appears below.
---

## Output

For each client with matches, the app writes two files to output_directory:

CSV with columns:

Manager, Year, Month, File Name, Client, File Path, Modified Date


ZIP containing the matched files.

File naming pattern

{year_or_all}_{month_or_all}_statements_{client}_{types}.csv


Example:
2024_03-March_statements_Smith_Family_K-1_CC.csv
---

## Matching Rules

Client → case-insensitive substring in filename.
Example: “Smith Family” matches 2024-03_Smith Family_STMT.pdf.

Statement type → regex with letter boundaries to avoid partial matches.
Example: CC matches _CC.pdf but not ACCOUNTS.pdf.

---

## Project Layout
statement_finder/
├─ src/
│  └─ statement_finder/
│     ├─ __init__.py
│     ├─ core.py          # search, CSV/ZIP, logging
│     ├─ cli.py           # CLI entry point
│     └─ gui.py           # Tkinter GUI
├─ tests/
│  └─ test_smoke.py
├─ config.example.yaml
├─ .github/workflows/ci.yml
├─ .pre-commit-config.yaml
├─ .gitignore
├─ pyproject.toml
└─ README.md

---

## Development
# (optional) dev tools
pip install pytest black isort

# run tests
pytest -q

# format & sort imports
black src tests
isort src tests

# enable pre-commit hooks so formatting runs on every commit
pip install pre-commit
pre-commit install


CI runs tests and formatting checks on every push/PR.

---

## Package to EXE (optional)

If you want a single-file Windows executable:

pip install pyinstaller
pyinstaller --onefile --name StatementFinder `
  --console `
  --add-data "config.example.yaml;." `
  src\statement_finder\cli.py


This creates dist\StatementFinder.exe.
For a GUI build, point PyInstaller at src\statement_finder\gui.py instead and add --noconsole.

---

## Use this as a Template

Click Use this template on GitHub.

Search/replace statement_finder with your new project name.

Copy config.example.yaml → config.yaml and set your paths.

pip install -e ., then run statement-finder or statement-finder-gui.

---

## Troubleshooting

FileNotFoundError for base directory
Set the correct base_directory in config.yaml. Use quotes. For UNC shares prefer forward slashes:

base_directory: '//server/share/Client Statements'


No matches
Confirm folder names on disk (e.g., 2024, 03-March) and that the client substring appears in filenames.

Slow scans
Narrow the search with both --year and --clients. Large trees benefit from tighter filters.

GUI doesn’t open
The GUI requires a desktop session. Use the CLI on headless machines or remote servers.

---

## License

MIT — see LICENSE.

Portions of this project were drafted with AI assistance and reviewed by the author.
'@ | Set-Content README.md -Encoding utf8