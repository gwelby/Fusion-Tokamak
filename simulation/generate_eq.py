#!/usr/bin/env python3
"""
generate_eq.py: Create an equilibrium XML file for M3D-C1 simulations.
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate tokamak equilibrium XML.")
    parser.add_argument("--R", type=float, required=True, help="Major radius [m]")
    parser.add_argument("--a", type=float, required=True, help="Minor radius [m]")
    parser.add_argument("--elongation", type=float, default=1.7, help="Plasma elongation")
    parser.add_argument("--triangularity", type=float, default=0.33, help="Plasma triangularity")
    parser.add_argument("--output", type=str, default="equilibrium.xml", help="Output XML filename")
    args = parser.parse_args()

    xml = f"""<equilibrium>
  <R0>{args.R}</R0>
  <a>{args.a}</a>
  <elongation>{args.elongation}</elongation>
  <triangularity>{args.triangularity}</triangularity>
</equilibrium>
"""
    with open(args.output, "w") as f:
        f.write(xml)
    print(f"Equilibrium XML written to {args.output}")

if __name__ == "__main__":
    main()
