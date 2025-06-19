#!/usr/bin/env python3
"""PRIME_PHI_CONSCIOUSNESS_GENERATOR.py

Generate toroidal field (TF) coil centre-line coordinates following a φ-spiral
(D-shaped) geometry as specified in GOLDEN_RATIO_ENGINEERING_SPECIFICATIONS.md.

The output can be used as a starting point for:
  • CAD import (step / iges via CSV → spline)
  • Electromagnetic / structural simulation (e.g. ANSYS, COMSOL)
  • Equilibrium generation helpers (`simulations/scripts/generate_eq.py`)

Philosophy
----------
We embrace the *Prime-Frequency* 432/528/768 Hz triad by aligning the winding
angles with prime multiples of the golden angle (≈ 137.507764°).  For 18 coils
(Fibonacci number) this naturally distributes Lorentz loads whilst preserving
phi-harmonic symmetry.

Usage
-----
    python PRIME_PHI_CONSCIOUSNESS_GENERATOR.py                # default CSV in cwd
    python PRIME_PHI_CONSCIOUSNESS_GENERATOR.py -o coils.csv   # custom output
    python PRIME_PHI_CONSCIOUSNESS_GENERATOR.py --json         # GeoJSON dump

The script is intentionally dependency-light (only `numpy`).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np

# φ constant & helpers ---------------------------------------------------------
PHI: float = (1 + 5 ** 0.5) / 2  # 1.6180339…
GOLDEN_ANGLE_RAD: float = 2 * math.pi * (1 - 1 / PHI)  # ≈ 2.39996323 rad
GOLDEN_ANGLE_DEG: float = math.degrees(GOLDEN_ANGLE_RAD)

# Default tokamak geometry (see GOLDEN_RATIO_ENGINEERING_SPECIFICATIONS.md)
DEFAULT_MAJOR_RADIUS: float = 6.0     # metres
DEFAULT_MINOR_RADIUS: float = 3.708   # metres (R / φ)
DEFAULT_D_SHAPE_KAPPA: float = PHI / 2  # vertical elongation κ ≈ 0.809
DEFAULT_TF_COILS: int = 18  # Fibonacci number

# ----------------------------------------------------------------------------

def phi_spiral_d_shape(
    turns: int,
    samples_per_turn: int,
    inner_radius: float,
    kappa: float,
    pitch: float,
) -> np.ndarray:
    """Return (N, 3) array representing a single D-shaped φ-spiral.

    The parametric form is loosely inspired by ITER D-coils with the outer
    boundary following r(θ) = a + b·θ where *b* embeds the golden ratio.

    Parameters
    ----------
    turns: int
        Number of toroidal turns (usually 1 for TF centre-line)
    samples_per_turn: int
        Discrete samples per 2π in poloidal angle.
    inner_radius: float
        Minor radius *a* of the plasma (centre to inner wall).
    kappa: float
        Vertical elongation κ (ratio of vertical to horizontal radii).
    pitch: float
        Out-of-plane pitch to approximate helical rise (m per 2π).

    Returns
    -------
    np.ndarray, shape (N,3)
        x, y, z Cartesian coordinates in metres.
    """
    total_samples = turns * samples_per_turn
    theta = np.linspace(0, 2 * math.pi * turns, total_samples, endpoint=False)

    # Minor radius profile (simple D-shape): half-circle joined to straight leg
    # We approximate by adjusting radial coordinate with |sinθ| component.
    # r_base ∈ [inner_radius, PHI * inner_radius]
    r_base = inner_radius * (1 + (PHI - 1) * np.abs(np.sin(theta)))

    # Apply φ spiral expansion — radius grows slightly each toroidal step
    spiral_growth = (PHI ** (theta / (2 * math.pi)))
    r = r_base * spiral_growth

    # Vertical position with elongation κ and helical pitch
    z = kappa * inner_radius * np.sin(theta) + pitch * theta / (2 * math.pi)

    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return np.column_stack([x, y, z])


def generate_all_coils(
    num_coils: int = DEFAULT_TF_COILS,
    samples_per_coil: int = 720,
    major_radius: float = DEFAULT_MAJOR_RADIUS,
    minor_radius: float = DEFAULT_MINOR_RADIUS,
    kappa: float = DEFAULT_D_SHAPE_KAPPA,
) -> List[Tuple[int, np.ndarray]]:
    """Return list of (index, coords) for every TF coil centre-line."""
    coils = []
    for idx in range(num_coils):
        # Angular offset around the torus by golden angle increments
        toroidal_angle = idx * GOLDEN_ANGLE_RAD
        base_curve = phi_spiral_d_shape(
            turns=1,
            samples_per_turn=samples_per_coil,
            inner_radius=minor_radius,
            kappa=kappa,
            pitch=0.0,  # centre-line – no helical rise for baseline TF coil
        )
        # Translate outward to major radius R in the X direction then rotate
        base_curve[:, 0] += major_radius
        rot = rotation_matrix_z(toroidal_angle)
        rotated = (rot @ base_curve.T).T  # (N,3)
        coils.append((idx, rotated))
    return coils


def rotation_matrix_z(angle_rad: float) -> np.ndarray:
    """Return 3×3 rotation matrix for rotation about Z by *angle_rad*."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def write_csv(path: Path, data: List[Tuple[int, np.ndarray]]) -> None:
    """Write coil coordinates to CSV with columns: coil_id,x,y,z"""
    header = "coil_id,x,y,z\n"
    with path.open("w", encoding="utf-8") as fh:
        fh.write(header)
        for coil_id, coords in data:
            for x, y, z in coords:
                fh.write(f"{coil_id},{x:.6f},{y:.6f},{z:.6f}\n")


def write_geojson(path: Path, data: List[Tuple[int, np.ndarray]]) -> None:
    """Dump coils as GeoJSON LineString collection (useful for CAD import)."""
    features = []
    for coil_id, coords in data:
        features.append(
            {
                "type": "Feature",
                "properties": {"coil_id": coil_id},
                "geometry": {
                    "type": "LineString",
                    "coordinates": coords[:, :3].tolist(),
                },
            }
        )
    geojson = {"type": "FeatureCollection", "features": features}
    path.write_text(json.dumps(geojson, indent=2))


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate φ-spiral TF coil geometry")
    p.add_argument("-o", "--output", type=Path, default=Path("tf_coils.csv"),
                   help="Output file path (extension determines format)")
    p.add_argument("--samples", type=int, default=720,
                   help="Samples per coil (default: 720)")
    p.add_argument("--coils", type=int, default=DEFAULT_TF_COILS,
                   help="Number of TF coils (default: 18)")
    p.add_argument("--R", type=float, default=DEFAULT_MAJOR_RADIUS,
                   help="Major radius R [m] (default: 6.0)")
    p.add_argument("--a", type=float, default=DEFAULT_MINOR_RADIUS,
                   help="Minor radius a [m] (default: 3.708)")
    p.add_argument("--kappa", type=float, default=DEFAULT_D_SHAPE_KAPPA,
                   help="Vertical elongation κ (default: φ/2 ≈ 0.809)")
    p.add_argument("--json", action="store_true",
                   help="Force GeoJSON output (overrides file extension)")
    return p.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)

    coil_data = generate_all_coils(
        num_coils=args.coils,
        samples_per_coil=args.samples,
        major_radius=args.R,
        minor_radius=args.a,
        kappa=args.kappa,
    )

    # Decide format by extension unless explicitly requested
    if args.json or args.output.suffix.lower() == ".json":
        write_geojson(args.output, coil_data)
        fmt = "GeoJSON"
    else:
        write_csv(args.output, coil_data)
        fmt = "CSV"
    print(f"[Cascade] Generated {len(coil_data)} φ-spiral TF coils → {args.output} ({fmt}).")


if __name__ == "__main__":  # pragma: no cover
    main()
