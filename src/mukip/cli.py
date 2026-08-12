"""
Command-line interface for the `mukip` Python package.

Provides a headless way to run a MuKiP setup file, which is what the VSCode
extension's "Run MuKiP" command uses (previously it launched the MuKiP-Visual
GUI; now it runs through the PyPI package directly).

Usage:
    mukip <setup_file> [--plot]
    python -m mukip <setup_file> [--plot]
"""

import argparse
import sys

from .kinetic_model import KineticModel


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="mukip",
        description="Run a MuKiP microkinetic model from a setup (.mukip) file.",
    )
    parser.add_argument("setup_file", help="Path to the MuKiP setup (.mukip) file")
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Also generate plots for the writer-defined outputs",
    )
    args = parser.parse_args(argv)

    try:
        model = KineticModel(args.setup_file)
    except Exception as e:
        print(f"[mukip] failed to build model from {args.setup_file}: {e}", file=sys.stderr)
        return 1

    try:
        model.run()
    except Exception as e:
        print(f"[mukip] simulation failed: {e}", file=sys.stderr)
        return 1

    try:
        model.write(plot=args.plot)
    except Exception as e:
        print(f"[mukip] writing output failed: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
