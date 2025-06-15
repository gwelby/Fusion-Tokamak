#requires -Version 5.0
<#+
.SYNOPSIS
    Orchestrates the φ-harmonic multi-physics simulation campaign.
.DESCRIPTION
    1. Optionally generates/refreshes skeleton input decks via make_templates.py.
    2. Submits or runs each solver job for every case found in the simulations tree.
    3. On completion, triggers postprocess.py to collate KPIs.
    NOTE: Replace placeholder commands (TODO) with actual solver invocations or
    SLURM/HTCondor submission lines according to your environment.
.EXAMPLE
    ./run_all.ps1 -GenerateTemplates -Cluster
#>
param(
    [switch]$GenerateTemplates,
    [switch]$Cluster # Submit to scheduler if specified; otherwise run locally
)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot ".."))

function Invoke-Cmd($cmd) {
    Write-Host "→ $cmd" -ForegroundColor Cyan
    if (-not $Cluster) {
        & cmd /c $cmd
    } else {
        # Example SLURM submission; modify to match your scheduler
        sbatch -J "$(Split-Path $cmd -Leaf)" --wrap $cmd
    }
}

# 1) Generate templates if requested
if ($GenerateTemplates) {
    Write-Host "Generating skeleton input decks…" -ForegroundColor Green
    Invoke-Cmd "python `"$($Root)\scripts\make_templates.py`""
}

# 2) Loop through cases and run simulations (placeholders)
$cases = @(
    @{Code='transp'; Pattern='input.xpt'; RunCmd='run_transp {file}'},
    @{Code='m3dc1'; Pattern='equilibrium.eqdsk'; RunCmd='run_m3dc1 {file}'},
    @{Code='ansys'; Pattern='*.dat'; RunCmd='run_ansys {file}'},
    @{Code='mcnp'; Pattern='*.i'; RunCmd='mpirun -n 8 mcnp6 i={file} o={file}.out'},
)

foreach ($case in $cases) {
    $paths = Get-ChildItem -Path $Root -Recurse -Filter $($case.Pattern) -ErrorAction SilentlyContinue
    foreach ($p in $paths) {
        $cmd = $case.RunCmd.Replace('{file}', $p.FullName)
        Invoke-Cmd $cmd
    }
}

# 3) Post-processing
Invoke-Cmd "python `"$($Root)\scripts\postprocess.py`""

Write-Host "Simulation campaign launched. Monitor your scheduler / output logs." -ForegroundColor Yellow
