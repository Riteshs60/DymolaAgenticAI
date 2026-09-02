#!/usr/bin/env python3
"""Provision (or report) the managed Python venv for plotting/analysis scripts."""

from __future__ import annotations

import argparse
import os
import sys

from _env import _default_venv_dir, ensure_managed_venv, venv_python

DEFAULT_PACKAGES = ["DyMat", "matplotlib", "numpy", "scipy"]


def main():
    ap = argparse.ArgumentParser(description="Provision the managed venv for Dymola skills")
    ap.add_argument("packages", nargs="*", help="Module names (default: DyMat matplotlib numpy scipy)")
    ap.add_argument("--print-python", action="store_true", help="Print venv python path only")
    args = ap.parse_args()
    modules = args.packages or DEFAULT_PACKAGES

    if args.print_python:
        venv_dir = _default_venv_dir()
        py = venv_python(venv_dir)
        if not os.path.isfile(py):
            py = ensure_managed_venv(modules)
        print(py)
        return 0

    print(ensure_managed_venv(modules))
    return 0


if __name__ == "__main__":
    sys.exit(main())
