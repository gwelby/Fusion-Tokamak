#!/usr/bin/env python3
"""
postprocess.py: Extract performance metrics from M3D-C1 HDF5 output and save as JSON.
"""
import argparse
import h5py
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Post-process M3D-C1 output.")
    parser.add_argument('--input', '-i', required=True, help="Input HDF5 file (out_*.h5)")
    parser.add_argument('--output', '-o', required=True, help="Output JSON filename (metrics_*.json)")
    args = parser.parse_args()

    metrics = {}
    try:
        with h5py.File(args.input, 'r') as f:
            # Example dataset names; adjust to actual code output
            metrics['growth_rate'] = float(f['stability/growth_rate'][()]) if 'stability/growth_rate' in f else None
            metrics['beta_n'] = float(f['global/beta_n'][()]) if 'global/beta_n' in f else None
            metrics['tau_e'] = float(f['transport/tau_e'][()]) if 'transport/tau_e' in f else None
    except Exception as e:
        print(f"Error reading HDF5: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.output, 'w') as out:
            json.dump(metrics, out, indent=2)
        print(f"Metrics written to {args.output}")
    except Exception as e:
        print(f"Error writing JSON: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
