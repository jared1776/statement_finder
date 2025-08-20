# Statement Finder

![CI](https://github.com/jared1776/statement_finder/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue)

Statement Finder scans manager folders for client statements, filtered by year, month, client, and statement type.  
It exports a CSV of matches and a ZIP of the matched files. You can run it from a CLI or a simple Tkinter GUI.

## Features
- Filter by **year**, **month**, **client name**, and **statement type**  
- Exports **CSV** metadata and a **ZIP** with the files  
- Works with **UNC network paths** on Windows  
- CLI for automation, GUI for quick use  
- Threaded search for decent performance on large trees

---

## Quick start

### Prerequisites
- Python 3.10 or newer. Windows or macOS supported.  
- Access to the share or folder that contains your “manager → year → month → files” hierarchy.

### Install
```powershell
# from your local clone
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
Configure
Copy the example config and set real paths.

powershell
Copy
Edit
Copy-Item config.example.yaml config.yaml
Edit config.yaml:

yaml
Copy
Edit
# Use your real paths. Forward slashes work well with UNC shares.
base_directory: '//'
output_directory: '//'
logo_path: ''        # optional, used by the GUI
log_file: 'logs/activity.log'
Tip: wrap Windows paths in quotes. You can use forward slashes to avoid escape issues.

Usage
CLI
powershell
Copy
Edit
# Show help
statement-finder --help

# Typical run, paths taken from config.yaml
statement-finder `
  --year 2024 `
  --month "03-March" `
  --clients "Smith Family,Johnson Trust" `
  --types "K-1,CC"
--year is a folder name such as 2024. Leave empty to scan all years.

--month is a folder name such as 03-March. Leave empty to scan all months.

--clients is a comma separated list. Matching is a case-insensitive substring of the filename.

--types is a comma separated list such as K-1,CC,STMT. Matching uses whole-word style boundaries.
Example: CC will not match inside ACCOUNT.

You can override paths from the CLI if you do not want to use the config file:

powershell
Copy
Edit
statement-finder `
  --base-dir "//server/path/Client Statements" `
  --output-dir "//server/path/statement_finder_output" `
  --year 2025 --clients "Jones Family" --types "K-1"
GUI
powershell
Copy
Edit
statement-finder-gui
Fill in fields and click Submit.

The progress bar updates as managers and clients are processed.

Logs appear in the output area.

Output
For each client with matches the app writes two artifacts to output_directory:

A CSV with columns:

mathematica
Copy
Edit
Manager, Year, Month, File Name, Client, File Path, Modified Date
A ZIP that contains the matched files.

File naming

pgsql
Copy
Edit
{year_or_all}_{month_or_all}_statements_{client}_{types}.csv
Example: 2024_03-March_statements_Smith_Family_K-1_CC.csv

Matching rules
Client: case-insensitive substring in the filename.
Example: client “Smith Family” matches 2024-03_Smith Family_STMT.pdf.

Statement types: regular expression with letter boundaries to avoid partial matches.
Example: CC matches _CC.pdf but not ACCOUNTS.pdf.

Project layout
bash
Copy
Edit
statement_finder/
├─ src/
│  └─ statement_finder/
│     ├─ __init__.py
│     ├─ core.py          # search, CSV, ZIP, logging
│     ├─ cli.py           # CLI entrypoint
│     └─ gui.py           # Tkinter GUI
├─ tests/
│  └─ test_smoke.py
├─ config.example.yaml
├─ .github/workflows/ci.yml
├─ .pre-commit-config.yaml
├─ .gitignore
├─ pyproject.toml
└─ README.md
Development
powershell
Copy
Edit
# optional quality tools
pip install pytest black isort mypy pre-commit
pytest
black src tests
isort src tests
mypy src

# enable pre-commit hooks
pre-commit install
Troubleshooting
FileNotFoundError for base directory
Set the correct base_directory in config.yaml. Use quotes. For UNC shares prefer forward slashes:

yaml
Copy
Edit
base_directory: '//server/share/Client Statements'
No matches
Confirm folder names match what is on disk.
Examples: 2024 for year, 03-March for month. Confirm the client substring exists in filenames.

Slow scans
Provide both --year and --clients to reduce the search space. The tool uses a thread pool, but very large trees still benefit from narrower filters.

GUI does not launch on headless servers
The GUI requires a desktop session. Use the CLI on headless machines.

Use this as a template
Click Use this template on GitHub.

Search and replace statement_finder with your new project name.

Copy config.example.yaml to config.yaml and set paths.

pip install -e . then run statement-finder or statement-finder-gui.

License
MIT. See LICENSE.

Note: portions of this project were drafted with AI assistance and reviewed by the author.

yaml
Copy
Edit

