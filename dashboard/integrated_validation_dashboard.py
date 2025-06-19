#!/usr/bin/env python3
"""
Tokamak Integrated Validation Dashboard
======================================
A lightweight control-room GUI that fuses the original PhiHarmonic
`integrated_validation_dashboard.py` with project-specific data feeds:

• KPI CSV (simulation/results.csv) ───► real-time performance plots
• TF coil geometry (tf_coils*.csv) ───► displays metadata & verifies counts

The GUI intentionally remains dependency-light (Tkinter + Matplotlib).  If the
source files are missing it falls back to φ-harmonic dummy data so that the
interface always comes up for operators.

Run:
    python dashboard/integrated_validation_dashboard.py

The design keeps the original layout/style but renames the title & database to
reflect the Fusion-Tokamak context.
"""
from __future__ import annotations

import csv
import json
import math
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import numpy as np
import tkinter as tk
from tkinter import ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ----------------------------------------------------------------------------
# Project paths (relative to repo root)
# ----------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
KPI_CSV_PATH = REPO_ROOT / "simulation" / "results.csv"
COIL_CSV_GLOB = REPO_ROOT.glob("tf_coils*.csv")
DB_PATH = REPO_ROOT / "tokamak_validation.db"

# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------

def read_kpi_csv(path: Path) -> Tuple[List[float], List[float]]:
    """Return (times, tau_e) from the results CSV.

    CSV format expected: time, tau_e, beta_n, growth_rate (header optional).
    If file doesn't exist or is empty, returns generated φ-harmonic dummy data.
    """
    if not path.exists():
        return gen_dummy_kpi()

    times, tau_es = [], []
    try:
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            # Skip header if non-numeric
            peek = next(reader)
            if not peek[0].replace(".", "", 1).isdigit():
                # header row -> skip and continue reading
                pass
            else:
                times.append(float(peek[0])); tau_es.append(float(peek[1]))
            for row in reader:
                if len(row) < 2:
                    continue
                times.append(float(row[0]))
                tau_es.append(float(row[1]))
    except Exception as exc:
        print(f"[Dashboard] KPI CSV read error: {exc}; using dummy data.")
        return gen_dummy_kpi()

    if not times:
        return gen_dummy_kpi()

    return times, tau_es


def gen_dummy_kpi(num: int = 200) -> Tuple[List[float], List[float]]:
    """Generate synthetic KPI curves centred on φ."""
    phi = (1 + 5 ** 0.5) / 2
    sigma = 0.1
    tau_max = 1.0
    ra_vals = np.linspace(phi - 0.3, phi + 0.3, num)
    tau_e = tau_max * np.exp(-0.5 * ((ra_vals - phi) / sigma) ** 2)
    times = list(range(num))
    return times, tau_e.tolist()


def count_coils() -> int:
    try:
        file = next(COIL_CSV_GLOB)
        with file.open() as fh:
            # coil_id in first column; last id gives count-1 so compute max+1
            max_id = -1
            for _ in range(1000):  # sample first 1k lines, enough for count
                line = fh.readline()
                if not line:
                    break
                if line.startswith("coil_id"):
                    continue
                cid = int(line.split(",", 1)[0])
                if cid > max_id:
                    max_id = cid
            return max_id + 1 if max_id >= 0 else 0
    except StopIteration:
        return 0
    except Exception:
        return 0

# ----------------------------------------------------------------------------
# GUI Class
# ----------------------------------------------------------------------------

class TokamakDashboard:
    """Simple Tkinter dashboard for KPI and coil metadata."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("🌀 Tokamak Control-Room Dashboard (φ-Harmonic)")
        self.root.geometry("1280x820")
        self.root.configure(bg="#0D1117")

        # Data containers
        self.times: List[float] = []
        self.tau_e: List[float] = []

        # UI setup
        self._setup_ui()

        # DB init (for archival, optional)
        self._init_db()

        # Launch periodic update
        self._update_loop()

    # ---------------------------------------------------------------------
    # DB
    # ---------------------------------------------------------------------

    def _init_db(self) -> None:
        try:
            self.conn = sqlite3.connect(DB_PATH)
            cur = self.conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS kpi_history (
                    ts TEXT, tau_e REAL
                )
                """
            )
            self.conn.commit()
        except Exception as exc:
            print(f"[Dashboard] DB init failed: {exc}")
            self.conn = None

    def _insert_db(self, ts: datetime, tau_e: float) -> None:
        if not self.conn:
            return
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO kpi_history (ts, tau_e) VALUES (?, ?)",
                (ts.isoformat(), tau_e),
            )
            self.conn.commit()
        except Exception:
            pass

    # ---------------------------------------------------------------------
    # UI helpers
    # ---------------------------------------------------------------------

    def _setup_ui(self) -> None:
        # Header
        header = tk.Label(
            self.root,
            text="Tokamak Integrated Validation Dashboard",
            font=("Arial", 18, "bold"),
            fg="#58A6FF",
            bg="#0D1117",
        )
        header.pack(pady=10)

        # Coil info label
        coil_count = count_coils()
        coil_lbl = tk.Label(
            self.root,
            text=f"Loaded TF Coil File: {coil_count} coils detected",
            font=("Arial", 12),
            fg="#7C3AED" if coil_count else "#8B949E",
            bg="#0D1117",
        )
        coil_lbl.pack(pady=2)

        # Figure
        self.fig, self.ax = plt.subplots(figsize=(7, 4), facecolor="#0D1117")
        self.ax.set_facecolor("#0D1117")
        self.ax.tick_params(colors="#F0F6FC")
        self.ax.spines["bottom"].set_color("#F0F6FC")
        self.ax.spines["top"].set_color("#F0F6FC")
        self.ax.spines["left"].set_color("#F0F6FC")
        self.ax.spines["right"].set_color("#F0F6FC")
        self.ax.set_title("Energy Confinement Time τₑ (s)", color="#58A6FF")
        self.ax.set_xlabel("Time Step")
        self.ax.set_ylabel("τₑ (arb)")
        self.line, = self.ax.plot([], [], color="#3FB950", lw=2)

        canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack()
        self.canvas = canvas

        # Log text box
        self.log = scrolledtext.ScrolledText(
            self.root,
            width=120,
            height=10,
            bg="#161B22",
            fg="#F0F6FC",
            insertbackground="#F0F6FC",
        )
        self.log.pack(pady=6)

        self._log("Dashboard initialised. Awaiting data…")

    # ---------------------------------------------------------------------
    # Logging & update loop
    # ---------------------------------------------------------------------

    def _log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {msg}\n")
        self.log.see(tk.END)

    def _update_loop(self) -> None:
        # Read KPI data
        times, tau_e = read_kpi_csv(KPI_CSV_PATH)
        if len(times) != len(self.times):
            self._log(f"Loaded {len(times)} KPI points from {KPI_CSV_PATH.name}")
            self.times, self.tau_e = times, tau_e
            self.line.set_data(self.times, self.tau_e)
            self.ax.relim(); self.ax.autoscale_view()
            self.canvas.draw()
            # Store newest point in DB
            if self.tau_e:
                self._insert_db(datetime.now(), self.tau_e[-1])

        # schedule next update
        self.root.after(5000, self._update_loop)  # every 5 s

    # ---------------------------------------------------------------------
    # Start loop
    # ---------------------------------------------------------------------

    def run(self) -> None:
        self.root.mainloop()


# ----------------------------------------------------------------------------
# ENTRY-POINT
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    dashboard = TokamakDashboard()
    dashboard.run()
