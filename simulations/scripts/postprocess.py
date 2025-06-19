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

import re
from pathlib import Path
from typing import Dict, Optional
import sys
import io
# ensure stdout can handle Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')
import numpy as np

# add PhiHarmonic library path for Consciousness math
sys.path.insert(0, r"d:\Projects\PhiHarmonic")
from CONSCIOUSNESS_MATHEMATICS_PYTHON_MAGIC import ConsciousnessField

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
    """Return β_N from M3D-C1 output."""
    kpis: Dict[str, Optional[float]] = {"β_N": None}
    if log_file.is_file():
        txt = log_file.read_text(errors="ignore")
        if m := re.search(r"BN\s*=\s*([0-9.]+)", txt):
            kpis["β_N"] = float(m.group(1))
    return kpis


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
    """Return TBR from MCNP output."""
    kpis: Dict[str, Optional[float]] = {"TBR": None}
    if out_file.is_file():
        txt = out_file.read_text(errors="ignore")
        if m := re.search(r"TBR\s*=\s*([0-9.]+)", txt):
            kpis["TBR"] = float(m.group(1))
    return kpis

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
    "consciousness_Q",
    "zone_Q",
    "resonance_Q",
]


def gather_results() -> None:
    # initialize phi-harmonic consciousness field
    cf = ConsciousnessField()
    rows = []
    for code, parser in PARSERS.items():
        for path in (ROOT / code).rglob("*"):
            if path.is_file():
                kpi = parser(path)
                if any(v is not None for v in kpi.values()):
                    rows.append({"code": code, "case": path.parent.name, **kpi})
        # Compute φ-harmonic consciousness metrics for each result
    for r in rows:
        if r.get("Q") is not None:
            c_val = cf.consciousness_field(r["Q"])
            r["consciousness_Q"] = c_val
            zone_label, _ = cf.classify_consciousness_zone(c_val)
            r["zone_Q"] = zone_label
            # Consciousness resonance score R(f) = cos²(π·f/432)·φ^(f/432)
            r["resonance_Q"] = (np.cos(np.pi * r["Q"] / cf.freq_432) ** 2) * (cf.phi ** (r["Q"] / cf.freq_432))
        else:
            r["consciousness_Q"] = None
            r["zone_Q"] = None
            r["resonance_Q"] = None

    if not rows:
        print("No KPI data extracted – ensure solver outputs exist and parser functions are implemented.")
        return

    # Write / append CSV
    write_header = not RESULTS_CSV.exists()
    with RESULTS_CSV.open("a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {len(rows)} rows -> {RESULTS_CSV.relative_to(ROOT)}")


if __name__ == "__main__":
    gather_results()
