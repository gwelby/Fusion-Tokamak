#!/usr/bin/env python3
"""
run_scan.py: Driver for R/a parameter scan SLURM jobs (Aspect-Ratio φ Hypothesis).
"""
import os
import subprocess
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--R0', type=float, default=2.0, help="Major radius [m]")
    parser.add_argument('--ra_min', type=float, default=1.2, help="Minimum R/a ratio")
    parser.add_argument('--ra_max', type=float, default=2.0, help="Maximum R/a ratio")
    parser.add_argument('--ra_step', type=float, default=0.05, help="Step size for R/a scan")
    parser.add_argument('--ntasks', type=int, default=16, help="MPI tasks per job")
    parser.add_argument('--partition', default='compute', help="SLURM partition name")
    args = parser.parse_args()

    # Prepare directories
    os.makedirs('jobs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

    # Generate scan values
    ra = args.ra_min
    while ra <= args.ra_max + 1e-8:
        ra_val = round(ra, 5)
        a = args.R0 / ra_val
        jobname = f"ra_{ra_val}"
        script = f"""#!/bin/bash
#SBATCH --job-name={jobname}
#SBATCH --output=logs/{jobname}.out
#SBATCH --error=logs/{jobname}.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={args.ntasks}
#SBATCH --partition={args.partition}

module load m3d-c1

# Generate equilibrium
python generate_eq.py --R {args.R0} --a {a:.5f} --output eq_{ra_val}.xml

# Run M3D-C1 simulation
mpirun -np {args.ntasks} m3d-c1 input=eq_{ra_val}.xml output=out_{ra_val}.h5

# Post-process results
python postprocess.py --input out_{ra_val}.h5 --output metrics_{ra_val}.json
"""
        path = os.path.join('jobs', jobname + '.sh')
        with open(path, 'w') as f:
            f.write(script)
        # Submit job
        subprocess.run(['sbatch', path])
        ra += args.ra_step

if __name__ == '__main__':
    main()
