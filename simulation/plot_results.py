#!/usr/bin/env python3
"""
plot_results.py: Read results.csv and plot key metrics vs the aspect ratio R/a.
"""
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # Load the aggregated results
    try:
        df = pd.read_csv('results.csv')
    except FileNotFoundError:
        print("results.csv not found. Run aggregate_results.py first.")
        return

    # Ensure sorted by R/a
    df = df.sort_values('R/a')

    plt.figure(figsize=(8, 6))
    # Plot energy confinement time if available
    if 'tau_e' in df.columns:
        plt.plot(df['R/a'], df['tau_e'], marker='o', label='Energy Confinement τₑ')
    # Plot normalized beta if available
    if 'beta_n' in df.columns:
        plt.plot(df['R/a'], df['beta_n'], marker='s', label='Normalized Beta βₙ')
    # Plot growth rate if available
    if 'growth_rate' in df.columns:
        plt.plot(df['R/a'], df['growth_rate'], marker='^', label='Growth Rate γ')

    # Mark the golden ratio φ
    phi = 1.618033988749895
    plt.axvline(phi, color='r', linestyle='--', label='φ ≈ 1.618')

    plt.xlabel('Aspect Ratio R/a')
    plt.ylabel('Metric Value')
    plt.title('Tokamak Aspect-Ratio Scan Results')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    out_file = 'scan_results.png'
    plt.savefig(out_file)
    print(f"Plot saved to {out_file}")
    plt.show()

if __name__ == '__main__':
    main()
