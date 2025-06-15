#!/bin/bash
#SBATCH --job-name=ra_1.2
#SBATCH --output=logs/ra_1.2.out
#SBATCH --error=logs/ra_1.2.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --partition=compute

module load m3d-c1

# Generate equilibrium
python generate_eq.py --R 2.0 --a 1.66667 --output eq_1.2.xml

# Run M3D-C1 simulation
mpirun -np 16 m3d-c1 input=eq_1.2.xml output=out_1.2.h5

# Post-process results
python postprocess.py --input out_1.2.h5 --output metrics_1.2.json
