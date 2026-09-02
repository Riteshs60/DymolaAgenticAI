"""
Shared Python-environment bootstrap for the Dymola agentic skill scripts.

Scripts that need third-party packages (DyMat, matplotlib, numpy, scipy)
self-provision a managed venv so the agent never has to pip-install into
system Python.

    from _env import reexec_under_managed_venv
    reexec_under_managed_venv(["DyMat", "matplotlib", "numpy", "scipy"])

Override the venv location with $DYMOLA_SKILLS_VENV.
"""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
import time

_PIP_NAME = {
    "DyMat": "DyMat",
    "matplotlib": "matplotlib",
    "numpy": "numpy",
    "scipy": "scipy",
}

_EXTRA_DEPS = {
    "DyMat": ["numpy", "scipy"],
}

_REEXEC_FLAG = "DYMOLA_SKILLS_ENV_ACTIVE"
_READY_MARKER = ".dymola-skills-ready"


def _expand(modules):
    out = []
    for m in modules:
        for dep in _EXTRA_DEPS.get(m, []):
            if dep not in out:
                out.append(dep)
        if m not in out:
            out.append(m)
    return out


def _default_venv_dir():
    override = os.environ.get("DYMOLA_SKILLS_VENV")
    if override:
        return os.path.abspath(override)
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "dymola-skills", "venv")
    base = os.environ.get("XDG_CACHE_HOME") or os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(base, "dymola-skills", "venv")


def venv_python(venv_dir):
    if sys.platform.startswith("win"):
        return os.path.join(venv_dir, "Scripts", "python.exe")
    return os.path.join(venv_dir, "bin", "python")


def _modules_importable(modules):
    for m in _expand(modules):
        try:
            importlib.import_module(m)
        except Exception:
            return False
    return True


def _create_venv(venv_dir):
    if os.path.isdir(venv_dir) and not os.path.isfile(os.path.join(venv_dir, _READY_MARKER)):
        shutil.rmtree(venv_dir, ignore_errors=True)
    if not os.path.isdir(venv_dir):
        subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
    py = venv_python(venv_dir)
    subprocess.check_call([py, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    with open(os.path.join(venv_dir, _READY_MARKER), "w", encoding="utf-8") as fh:
        fh.write(str(time.time()))
    return py


def ensure_managed_venv(modules):
    modules = _expand(modules)
    if os.environ.get(_REEXEC_FLAG) == "1" and _modules_importable(modules):
        return sys.executable
    if _modules_importable(modules) and os.environ.get(_REEXEC_FLAG) != "1":
        # Prefer already-available packages when present.
        return sys.executable

    venv_dir = _default_venv_dir()
    py = venv_python(venv_dir)
    if not os.path.isfile(py) or not os.path.isfile(os.path.join(venv_dir, _READY_MARKER)):
        py = _create_venv(venv_dir)

    missing = []
    for m in modules:
        try:
            subprocess.check_call(
                [py, "-c", f"import {m}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            missing.append(_PIP_NAME.get(m, m))

    if missing:
        subprocess.check_call([py, "-m", "pip", "install", *missing])
    return py


def reexec_under_managed_venv(modules):
    if os.environ.get(_REEXEC_FLAG) == "1":
        return
    if _modules_importable(modules):
        return
    py = ensure_managed_venv(modules)
    env = os.environ.copy()
    env[_REEXEC_FLAG] = "1"
    os.execve(py, [py] + sys.argv, env)
