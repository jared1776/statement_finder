from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from .core import configure_logging, process


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find client statements and export CSV + ZIP.")
    p.add_argument("--config", type=Path, default=Path("config.yaml"), help="Path to config file")
    p.add_argument("--base-dir", type=Path, help="Override: base directory with manager folders")
    p.add_argument("--output-dir", type=Path, help="Override: output directory for CSV/ZIP")
    p.add_argument(
        "--year", type=str, default="", help="Year folder, for example 2024. Empty means all"
    )
    p.add_argument(
        "--month",
        type=str,
        default="",
        help="Month folder name, for example 03-March. Empty means all",
    )
    p.add_argument("--clients", type=str, default="", help="Comma separated client names")
    p.add_argument(
        "--types",
        type=str,
        default="",
        help="Comma separated statement types, for example K-1,CC,STMT",
    )
    p.add_argument("--workers", type=int, default=None, help="Max worker threads")
    p.add_argument("--log-file", type=Path, help="Override: log file path")
    return p.parse_args()


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)

    base_dir = args.base_dir or Path(
        cfg.get("base_directory", "YOUR_FILE_PATH_HERE/Client Statements")
    )
    output_dir = args.output_dir or Path(
        cfg.get("output_directory", "YOUR_FILE_PATH_HERE/statement_finder_output")
    )
    log_file = args.log_file or Path(cfg.get("log_file", "logs/activity.log"))

    configure_logging(log_file)

    clients = [c.strip() for c in (args.clients or "").split(",") if c.strip()]
    stypes = [t.strip() for t in (args.types or "").split(",") if t.strip()]

    process(
        base_directory=base_dir,
        output_dir=output_dir,
        year=args.year or None,
        month=args.month or None,
        client_names_list=clients,
        statement_types_list=stypes,
        max_workers=args.workers,
    )


if __name__ == "__main__":
    main()
