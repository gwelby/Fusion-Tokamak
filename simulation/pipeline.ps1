<# 
Pipeline script for Fusion-Tokamak simulation study
Usage:
  .\pipeline.ps1 [-R0 <major radius>] [-ra_min <min ratio>] [-ra_max <max ratio>] [-ra_step <step>] [-ntasks <tasks>] [-partition <partition>]
#>
param(
    [double]$R0 = 2.0,
    [double]$ra_min = 1.2,
    [double]$ra_max = 2.0,
    [double]$ra_step = 0.05,
    [int]$ntasks = 16,
    [string]$partition = 'compute'
)

Write-Host "--- Fusion-Tokamak Simulation Pipeline ---"
Write-Host "1) Submitting R/a=$ra_min↔$ra_max scan jobs on SLURM"
& python .\run_scan.py --R0 $R0 --ra_min $ra_min --ra_max $ra_max --ra_step $ra_step --ntasks $ntasks --partition $partition

Write-Host "\n2) Waiting for SLURM jobs to complete..."
Write-Host "   Monitoring SLURM queue for ra_ jobs..."
while ($null -ne (squeue -u $env:USERNAME | Select-String '^ra_')) {
    Start-Sleep -Seconds 60
    Write-Host "."
}
Write-Host "All SLURM ra_ jobs have completed."

Write-Host "\n3) Aggregating JSON metrics into CSV"
& python .\aggregate_results.py

Write-Host "\n4) Plotting results"
& python .\plot_results.py

Write-Host "\nPipeline complete. See scan_results.png for the figure."
