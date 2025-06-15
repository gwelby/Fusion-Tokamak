#!/usr/bin/env python3
"""Post-process simulation outputs and aggregate KPIs.

For each simulation case, this script attempts to parse solver output files
(*e.g.* TRANSP `.out`, M3D-C1 `.log`, ANSYS result summary, MCNP tally)
and extract a common minimal KPI set:
    β_N, τ_E, Q, max_stress_MPa, peak_heat_MWm2, TBR (tritium breeding ratio)

It writes / appends to `RESULTS_phi_scan.csv` under the `simulations` root.

Usage:
    python postprocess.py

The parsing functions are intentionally lightweight placeholders; replace with
real logic once solver output formats are available.
"""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parents[1]
RESULTS_CSV = ROOT / "RESULTS_phi_scan.csv"

# -----------------------------------------------------------------------------
# Helper parsers (STUB)
# -----------------------------------------------------------------------------

def parse_transp(out_file: Path) -> Dict[str, Optional[float]]:
    """Return dict of KPIs from TRANSP output (stub)."""
    kpis = {"β_N": None, "τ_E": None, "Q": None}
    if out_file.is_file():
        txt = out_file.read_text(errors="ignore")
        if m := re.search(r"BN\s*=\s*([0-9.]+)", txt):
            kpis["β_N"] = float(m.group(1))
        if m := re.search(r"TAUE\s*=\s*([0-9.]+)", txt):
            kpis["τ_E"] = float(m.group(1))
        if m := re.search(r"Q\s*=\s*([0-9.]+)", txt):
            kpis["Q"] = float(m.group(1))
    return kpis


def parse_m3dc1(log_file: Path) -> Dict[str, Optional[float]]:
    return {"β_N": None}


def parse_ansys(result_json: Path) -> Dict[str, Optional[float]]:
    if result_json.is_file():
        try:
            data = json.loads(result_json.read_text())
            return {
                "max_stress_MPa": data.get("max_stress_MPa"),
                "peak_heat_MWm2": data.get("peak_heat_MWm2"),
            }
        except json.JSONDecodeError:
            pass
    return {"max_stress_MPa": None, "peak_heat_MWm2": None}


def parse_mcnp(out_file: Path) -> Dict[str, Optional[float]]:
    return {"TBR": None}

# ----------------------------------------------------------------------------

PARSERS = {
    "transp": parse_transp,
    "m3dc1": parse_m3dc1,
    "ansys": parse_ansys,
    "mcnp": parse_mcnp,
}

FIELDS = [
    "code",
    "case",
    "β_N",
    "τ_E",
    "Q",
    "max_stress_MPa",
    "peak_heat_MWm2",
    "TBR",
]


def gather_results() -> None:
    rows = []
    for code, parser in PARSERS.items():
        for path in (ROOT / code).rglob("*"):
            if path.is_file():
                kpi = parser(path)
                if any(v is not None for v in kpi.values()):
                    rows.append({"code": code, "case": path.parent.name, **kpi})
    if not rows:
        print("No KPI data extracted – ensure solver outputs exist and parser functions are implemented.")
        return

    # Write / append CSV
    write_header = not RESULTS_CSV.exists()
    with RESULTS_CSV.open("a", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {len(rows)} rows → {RESULTS_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    gather_results()
