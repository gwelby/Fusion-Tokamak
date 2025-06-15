#!/usr/bin/env python3
"""
simulate_metrics.py: Generate synthetic metrics JSON files
for demonstration of the Aspect-Ratio φ Hypothesis.
"""
import argparse
import json
import os
import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description="Simulate metrics JSON for R/a scan."
    )
    parser.add_argument('--ra_min', type=float, default=1.2)
    parser.add_argument('--ra_max', type=float, default=2.0)
    parser.add_argument('--ra_step', type=float, default=0.05)
    parser.add_argument(
        '--sigma',
        type=float,
        default=0.1,
        help="Gaussian width for tau_e peak"
    )
    parser.add_argument(
        '--tau_max',
        type=float,
        default=1.0,
        help="Max energy confinement time"
    )
    args = parser.parse_args()

    phi = 1.618033988749895
    os.makedirs('.', exist_ok=True)
    ra = args.ra_min
    while ra <= args.ra_max + 1e-8:
        ra_val = round(ra, 5)
        # synthetic tau_e: Gaussian centered at phi
        factor = -0.5 * ((ra_val - phi) / args.sigma) ** 2
        tau_e = args.tau_max * np.exp(factor)
        
        beta_n = 3.0 * tau_e  # scaled
        growth_rate = 0.2 * (1 - tau_e)
        data = {
            'tau_e': float(np.round(tau_e, 4)),
            'beta_n': float(np.round(beta_n, 4)),
            'growth_rate': float(np.round(growth_rate, 4)),
        }
        fname = f"metrics_{ra_val:.5f}.json"
        with open(fname, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Generated {fname}")
        ra += args.ra_step


if __name__ == '__main__':
    main()
