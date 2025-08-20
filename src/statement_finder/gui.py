from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, font, scrolledtext, ttk
from pathlib import Path
from typing import Optional
from PIL import ImageTk, Image
import yaml

from .core import process, configure_logging

def load_logo(logo_path: Optional[Path]) -> Optional[ImageTk.PhotoImage]:
    try:
        if logo_path and logo_path.exists():
            return ImageTk.PhotoImage(Image.open(logo_path))
    except Exception:
        pass
    return None

def main() -> None:
    cfg = {}
    cfg_file = Path("config.yaml")
    if cfg_file.exists():
        try:
            cfg = yaml.safe_load(cfg_file.read_text(encoding="utf-8")) or {}
        except Exception:
            cfg = {}

    base_dir_default = cfg.get("base_directory", "YOUR_FILE_PATH_HERE/Client Statements")
    output_dir_default = cfg.get("output_directory", "YOUR_FILE_PATH_HERE/statement_finder_output")
    logo_path = Path(cfg.get("logo_path", "")) if cfg.get("logo_path") else None
    log_file = Path(cfg.get("log_file", "logs/activity.log"))

    configure_logging(log_file)

    root = tk.Tk()
    root.title("Statement Finder")
    root.configure(bg="#e6f0fa")

    header_font = font.Font(family="Franklin Gothic Medium", size=12)
    body_font = font.Font(family="Franklin Gothic Book", size=10)

    logo_img = load_logo(logo_path)
    if logo_img:
        tk.Label(root, image=logo_img, bg="#e6f0fa").grid(row=0, column=0, columnspan=2, pady=10)
    else:
        tk.Label(root, text="Logo", bg="#e6f0fa", fg="#616365", font=header_font).grid(row=0, column=0, columnspan=2, pady=10)

    def label(r, text):
        tk.Label(root, text=text, font=header_font, bg="#e6f0fa", fg="#616365").grid(row=r, column=0, sticky=tk.W, padx=6, pady=4)

    label(1, "Base directory:")
    base_entry = tk.Entry(root, font=body_font, width=48)
    base_entry.insert(0, base_dir_default)
    base_entry.grid(row=1, column=1, padx=6, pady=4)

    label(2, "Output directory:")
    out_entry = tk.Entry(root, font=body_font, width=48)
    out_entry.insert(0, output_dir_default)
    out_entry.grid(row=2, column=1, padx=6, pady=4)

    label(3, "Year (e.g., 2024):")
    year_entry = tk.Entry(root, font=body_font)
    year_entry.grid(row=3, column=1, padx=6, pady=4)

    months = [""] + [f"{i:02d}-{m}" for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June",
         "July", "August", "September", "October", "November", "December"], start=1)]
    label(4, "Month (e.g., 03-March):")
    month_combo = ttk.Combobox(root, values=months, font=body_font)
    month_combo.grid(row=4, column=1, padx=6, pady=4)
    month_combo.current(0)

    label(5, "Client name(s), comma separated:")
    client_entry = tk.Entry(root, font=body_font)
    client_entry.grid(row=5, column=1, padx=6, pady=4)

    label(6, "Statement type(s), comma separated (e.g., K-1, CC, STMT):")
    type_entry = tk.Entry(root, font=body_font)
    type_entry.grid(row=6, column=1, padx=6, pady=4)

    output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=60, height=12, font=body_font)
    output_area.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

    progress_var = tk.DoubleVar()
    ttk.Progressbar(root, variable=progress_var, maximum=100).grid(row=8, column=0, columnspan=2, padx=10, pady=6, sticky=tk.EW)

    msg_q: "queue.Queue[tuple[str, str|float|None]]" = queue.Queue()

    def progress_cb(pct: float) -> None:
        msg_q.put(("progress", pct))

    def worker():
        try:
            base_dir = Path(base_entry.get().strip())
            output_dir = Path(out_entry.get().strip())
            year = year_entry.get().strip() or None
            month = month_combo.get().strip() or None
            clients = [c.strip() for c in client_entry.get().split(",") if c.strip()]
            stypes = [t.strip() for t in type_entry.get().split(",") if t.strip()]

            if year and not year.isdigit():
                msg_q.put(("log", "Year must be numeric"))
                msg_q.put(("done", None))
                return

            if not (year and clients):
                output_area.insert(tk.END, "Warning: blank fields may lead to a very large scan.\n")

            results = process(
                base_directory=base_dir,
                output_dir=output_dir,
                year=year,
                month=month,
                client_names_list=clients,
                statement_types_list=stypes,
                max_workers=None,
                progress_cb=progress_cb,
            )

            for c, rows in results.items():
                if rows:
                    msg_q.put(("log", f"Generated CSV and ZIP for client: {c}"))
                else:
                    msg_q.put(("log", f"No statements found for client: {c}"))
        except Exception as e:
            msg_q.put(("log", f"Unexpected error: {e}"))
        finally:
            msg_q.put(("done", None))

    def pump():
        try:
            while True:
                kind, payload = msg_q.get_nowait()
                if kind == "progress":
                    progress_var.set(float(payload))  # type: ignore[arg-type]
                elif kind == "log":
                    output_area.insert(tk.END, str(payload) + "\n")
                    output_area.see(tk.END)
                elif kind == "done":
                    submit_btn.config(state=tk.NORMAL)
        except queue.Empty:
            pass
        root.after(100, pump)

    def submit():
        submit_btn.config(state=tk.DISABLED)
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Processing...\n")
        threading.Thread(target=worker, daemon=True).start()

    submit_btn = tk.Button(root, text="Submit", command=submit, bg="#009dce", fg="white", font=header_font)
    submit_btn.grid(row=7, column=1, pady=8, sticky=tk.E)

    root.after(120, pump)
    root.mainloop()

if __name__ == "__main__":
    main()
