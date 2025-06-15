# Makefile for Fusion-Tokamak simulation pipeline

# Tunable parameters
R0 := 2.0
RA_MIN := 1.2
RA_MAX := 2.0
RA_STEP := 0.05
NTASKS := 16
PART := compute

.PHONY: all scan aggregate plot

all: scan aggregate plot

# Submit R/a scan jobs
scan:
	python run_scan.py --R0 $(R0) --ra_min $(RA_MIN) --ra_max $(RA_MAX) --ra_step $(RA_STEP) --ntasks $(NTASKS) --partition $(PART)

# Aggregate JSON metrics into CSV
aggregate:
	python aggregate_results.py

# Plot results and save image
plot:
	python plot_results.py
