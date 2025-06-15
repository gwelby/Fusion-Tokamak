#!/usr/bin/env python3
"""
aggregate_results.py: Aggregate metrics_*.json files into a CSV for analysis.
"""
import glob
import json
import csv
import os

def main():
    files = sorted(glob.glob('metrics_*.json'))
    if not files:
        print("No metrics files found.")
        return

    # Gather all keys
    all_keys = set()
    records = []
    for fname in files:
        ra = os.path.basename(fname)[len('metrics_'):-len('.json')]
        with open(fname) as f:
            data = json.load(f)
        rec = {'R/a': float(ra)}
        rec.update(data)
        records.append(rec)
        all_keys.update(data.keys())

    # Write CSV
    fieldnames = ['R/a'] + sorted(all_keys)
    with open('results.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            writer.writerow(rec)
    print(f"Aggregated {len(records)} records into results.csv")

if __name__ == '__main__':
    main()
