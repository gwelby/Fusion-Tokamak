#!/usr/bin/env python3
"""
Generate synthetic simulation outputs for testing the pipeline.
Creates dummy output files with KPI entries for each case.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def simulate_transp():
    for case in (ROOT / "transp").iterdir():
        if case.is_dir():
            out_file = case / "output.out"
            with out_file.open("w", encoding="utf-8") as f:
                f.write(f"BN = {1.3}\n")
                f.write(f"TAUE = {0.05}\n")
                f.write(f"Q = {5.0}\n")


def simulate_m3dc1():
    for case in (ROOT / "m3dc1").iterdir():
        if case.is_dir():
            log_file = case / "m3dc1.log"
            with log_file.open("w", encoding="utf-8") as f:
                f.write(f"BN = {1.1}\n")


def simulate_ansys():
    for case in (ROOT / "ansys").iterdir():
        if case.is_dir():
            data = {
                "max_stress_MPa": 300,
                "peak_heat_MWm2": 1.2,
            }
            with (case / "results.json").open("w", encoding="utf-8") as f:
                json.dump(data, f)


def simulate_mcnp():
    for case in (ROOT / "mcnp").iterdir():
        if case.is_dir():
            out_file = case / "mcnp.out"
            with out_file.open("w", encoding="utf-8") as f:
                f.write(f"TBR = {0.95}\n")


def main():
    simulate_transp()
    simulate_m3dc1()
    simulate_ansys()
    simulate_mcnp()
    print("Synthetic metrics generated for all cases.")


if __name__ == "__main__":
    main()
