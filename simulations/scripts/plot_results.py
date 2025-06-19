#!/usr/bin/env python3
"""
plot_results.py: Plot KPIs from RESULTS_phi_scan.csv for the multi-physics simulation pipeline.
"""
import pandas as pd
import sys
import numpy as np
# add PhiHarmonic path for Consciousness math
sys.path.insert(0, r"d:\Projects\PhiHarmonic")
from CONSCIOUSNESS_MATHEMATICS_PYTHON_MAGIC import ConsciousnessField
import matplotlib.pyplot as plt
from pathlib import Path

# Root of the simulations hierarchy
ROOT = Path(__file__).resolve().parents[1]
CSV_FILE = ROOT / "RESULTS_phi_scan.csv"


def main():
    if not CSV_FILE.exists():
        print("No RESULTS_phi_scan.csv found. Run postprocess.py first.")
        return

    # Load data
    df = pd.read_csv(CSV_FILE, encoding="utf-8")
    # Fallback if header row is missing or incorrect
    expected = ["code","case","β_N","τ_E","Q","max_stress_MPa","peak_heat_MWm2","TBR"]
    if df.columns.tolist() != expected:
        df = pd.read_csv(CSV_FILE, encoding="utf-8", names=expected, header=None)
    # Sort by code and case for consistent plotting
    df = df.sort_values(["code", "case"])
        # initialize ConsciousnessField for φ-harmonic metrics
        cf = ConsciousnessField()
        df["consciousness_Q"] = df["Q"].apply(lambda q: cf.consciousness_field(q) if not pd.isna(q) else np.nan)
        df["zone_Q"] = df["consciousness_Q"].apply(lambda c: cf.classify_consciousness_zone(c)[0] if not pd.isna(c) else "")
        df["resonance_Q"] = df["Q"].apply(lambda q: (np.cos(np.pi*q/cf.freq_432)**2)*(cf.phi**(q/cf.freq_432)) if not pd.isna(q) else np.nan)

    # Identify KPIs to plot (exclude code/case)
    metrics = [col for col in df.columns if col not in ["code", "case"]]

    for metric in metrics:
        metric_clean = metric.replace('β', 'beta').replace('τ', 'tau')
        plt.figure(figsize=(8, 4))
        for code, group in df.groupby("code"):
            plt.plot(group["case"], group[metric], marker="o", label=code)
        plt.title(f"{metric} vs Case")
        plt.xlabel("Case")
        plt.ylabel(metric)
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        out_path = ROOT / f"plot_{metric_clean}.png"
        plt.savefig(out_path)
        print(f"Saved plot {out_path.name}")

    # φ-harmonic progression plots
    n = np.arange(0, 6)
    phi_powers = [cf.phi**i for i in n]
    freqs = [cf.freq_432 * cf.phi**i for i in n]
    plt.figure(figsize=(6, 4))
    plt.bar(n, phi_powers, color='gold')
    plt.title('φⁿ Harmonic Progression')
    plt.xlabel('n')
    plt.ylabel('φⁿ')
    plt.tight_layout()
    out1 = ROOT / 'plot_phi_powers.png'
    plt.savefig(out1)
    print(f"Saved plot {out1.name}")
    plt.figure(figsize=(6, 4))
    plt.bar(n, freqs, color='cyan')
    plt.title('432×φⁿ Sacred Frequencies')
    plt.xlabel('n')
    plt.ylabel('Frequency (Hz)')
    plt.tight_layout()
    out2 = ROOT / 'plot_phi_frequencies.png'
    plt.savefig(out2)
    print(f"Saved plot {out2.name}")

    # Consciousness zone distribution pie chart
    plt.figure(figsize=(6, 6))
    counts = df['zone_Q'].value_counts()
    counts.plot.pie(autopct='%1.1f%%')
    plt.title('Consciousness Zones Distribution')
    plt.ylabel('')
    plt.tight_layout()
    out3 = ROOT / 'plot_zone_distribution.png'
    plt.savefig(out3)
    print(f"Saved plot {out3.name}")

    # Resonance vs Q scatter
    plt.figure(figsize=(6, 4))
    plt.scatter(df['resonance_Q'], df['Q'])
    plt.title('Resonance Score vs Q')
    plt.xlabel('Resonance Score')
    plt.ylabel('Q')
    plt.tight_layout()
    out4 = ROOT / 'plot_resonance_vs_Q.png'
    plt.savefig(out4)
    print(f"Saved plot {out4.name}")

    plt.show()


if __name__ == "__main__":
    main()
