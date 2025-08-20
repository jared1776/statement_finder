from __future__ import annotations

import csv
import logging
import os
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Dict, Optional

logger = logging.getLogger(__name__)

def configure_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    fmt = logging.Formatter(
        "User: %(user)s\nTimestamp: %(asctime)s\nBase Directory: %(base_dir)s\n"
        "Year: %(year)s\nMonth: %(month)s\nClient Name: %(client_name)s\n"
        "Statement Type: %(statement_type)s\nOutput File: %(output_file)s\n",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(fmt)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)

def log_context(base_dir: Path, year: str, month: str, client_name: str, statement_type: str, output_file: str) -> dict:
    user = os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"
    return {
        "user": user,
        "base_dir": str(base_dir),
        "year": year or "all",
        "month": month or "all",
        "client_name": client_name or "N/A",
        "statement_type": statement_type or "N/A",
        "output_file": output_file or "N/A",
    }

def sanitize_filename(s: str) -> str:
    return "".join(c for c in s if c.isalnum() or c in (" ", "_", "-")).rstrip()

def discover_managers(base_directory: Path) -> List[Path]:
    return [p for p in base_directory.iterdir() if p.is_dir() and not p.name.lower().startswith("zz")]

def months_to_process(year_path: Path, month: Optional[str]) -> List[Path]:
    if month:
        m = year_path / month
        return [m] if m.exists() else []
    return [p for p in year_path.iterdir() if p.is_dir()]

def matches_client(filename: str, client_name: str) -> bool:
    if not client_name:
        return True
    return client_name.lower() in filename.lower()

def matches_types(filename: str, types: Iterable[str]) -> bool:
    types = list(types)
    if not types:
        return True
    return any(re.search(rf"(?i)(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", filename) for t in types)

def scan_manager(
    manager_path: Path,
    year: Optional[str],
    month: Optional[str],
    client_name: str,
    types: List[str],
) -> List[List[str]]:
    out: List[List[str]] = []
    if year:
        year_path = manager_path / year
        if not year_path.exists():
            return out
        m_paths = months_to_process(year_path, month)
    else:
        m_paths = []
        for yp in manager_path.iterdir():
            if yp.is_dir():
                m_paths.extend(months_to_process(yp, month=None))

    for mp in m_paths:
        for f in mp.rglob("*"):
            if not f.is_file():
                continue
            fn = f.name
            if not matches_client(fn, client_name):
                continue
            if not matches_types(fn, types):
                continue
            modified_date = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            year_val = mp.parent.name
            month_val = mp.name
            out.append(
                [
                    manager_path.name,
                    year_val,
                    month_val,
                    fn,
                    client_name or "N/A",
                    str(f),
                    modified_date,
                    str(f),
                ]
            )
    return out

def export_to_csv(statement_details: List[List[str]], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Manager", "Year", "Month", "File Name", "Client", "File Path", "Modified Date"])
        for row in statement_details:
            w.writerow(row[:-1])

def zip_files(statement_details: List[List[str]], output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for row in statement_details:
            fpath = Path(row[-1])
            if fpath.exists():
                z.write(fpath, arcname=fpath.name)

def process(
    base_directory: Path,
    output_dir: Path,
    year: Optional[str],
    month: Optional[str],
    client_names_list: List[str],
    statement_types_list: List[str],
    max_workers: Optional[int] = None,
    progress_cb: Optional[callable] = None,
) -> Dict[str, List[List[str]]]:
    managers = discover_managers(base_directory)
    client_statements: Dict[str, List[List[str]]] = {c: [] for c in client_names_list}
    total = max(1, len(managers) * max(1, len(client_names_list)))
    done = 0

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = []
        for m in managers:
            for c in client_names_list:
                futures.append(ex.submit(scan_manager, m, year, month, c, statement_types_list))
        for fut in as_completed(futures):
            try:
                rows = fut.result()
                if rows:
                    client_key = rows[0][4] if rows[0][4] != "N/A" else ""
                    if client_key in client_statements:
                        client_statements[client_key].extend(rows)
            finally:
                done += 1
                if progress_cb:
                    progress_cb(100 * done / total)

    for client_name, rows in client_statements.items():
        if not rows:
            continue
        stypes = "_".join(statement_types_list) or "AllTypes"
        out_name = f"{year or 'all'}_{month or 'all'}_statements_{sanitize_filename(client_name)}_{sanitize_filename(stypes)}.csv"
        out_csv = output_dir / out_name
        out_zip = output_dir / out_name.replace(".csv", ".zip")
        export_to_csv(rows, out_csv)
        zip_files(rows, out_zip)

        ctx = log_context(base_directory, year or "", month or "", client_name, ",".join(statement_types_list), str(out_csv))
        logger.info("Processing summary", extra=ctx)

    return client_statements
