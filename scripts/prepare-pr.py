#!/usr/bin/env python3
"""
Pre-PR preparation: run all pre-PR scripts in sequence.

Usage:
    python3 scripts/prepare-pr.py [--base <ref>]

Steps:
    1. bump-plugin-versions.py  -- bump plugin versions based on what changed
    2. generate-index.py        -- refresh INDEX.md
"""

import argparse
import os
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script, extra_args=None):
    cmd = [sys.executable, os.path.join(SCRIPTS_DIR, script)] + (extra_args or [])
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"\nError: {script} failed (exit {result.returncode}).", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--base", default=None, help="Base ref for bump-plugin-versions (default: origin/main)")
    args = parser.parse_args()

    base_args = ["--base", args.base] if args.base else []

    print("=== Step 1: bump plugin versions ===")
    run_script("bump-plugin-versions.py", base_args)

    print("\n=== Step 2: refresh INDEX.md ===")
    run_script("generate-index.py")


if __name__ == "__main__":
    main()
