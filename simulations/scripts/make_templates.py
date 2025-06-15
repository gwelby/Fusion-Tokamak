#!/usr/bin/env python3
"""
Auto-generate skeleton input decks for the φ-harmonic multi-physics campaign.

This creates baseline and φ-tuned directories for each solver with placeholder
files ready for manual refinement.

Run:
    python make_templates.py
"""
import os
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
DATE = datetime.now().strftime("%Y-%m-%d")

CONFIG = {
    "transp": {
        "baseline_Ra1.8": {"AR": 1.8},
        "phi_Ra1.618": {"AR": 1.618},
    },
    "m3dc1": {
        "baseline": {"phi_spiral": False},
        "phi_spiral": {"phi_spiral": True},
    },
    "ansys": {
        "coil_loads": {},
        "pfc_thermal": {},
    },
    "mcnp": {
        "baseline": {},
        "phi_blanket": {},
    },
}

def write_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def create_decks() -> None:
    for code, cases in CONFIG.items():
        for case, params in cases.items():
            if code == "transp":
                filename = "input.xpt"
                filepath = os.path.join(ROOT, code, case, filename)
                txt = (
                    f";;; TRANSP INPUT DECK ({case})\n"
                    f"; Auto-generated {DATE}\n"
                    f"ASPECT_RATIO = {params['AR']}\n"
                    f"; TODO: fill additional parameters\n"
                )
            elif code == "m3dc1":
                filename = "equilibrium.eqdsk"
                filepath = os.path.join(ROOT, code, case, filename)
                marker = "ON" if params.get("phi_spiral") else "OFF"
                txt = (
                    f"EQDSK PHI_SPIRAL={marker}\n"
                    f"; Auto-generated {DATE}\n"
                    f"; TODO: replace with actual equilibrium data\n"
                )
            else:
                filename = "README.txt"
                filepath = os.path.join(ROOT, code, case, filename)
                txt = (
                    f"{code.upper()} CASE: {case}\n"
                    f"Generated {DATE}\n"
                    f"TODO: provide solver-specific model files.\n"
                )
            write_file(filepath, txt)


if __name__ == "__main__":
    create_decks()
    print("Template decks created under simulations/ directory.")
