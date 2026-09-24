"""Canonical role names — moved to backend/app/core/job_roles.py.

Loaded by file path rather than `import app.core...`: importing the package
runs app/core/__init__, which pulls in settings and the security stack the
pipeline neither has nor needs.
"""
import importlib.util
import pathlib

_path = pathlib.Path(__file__).resolve().parents[2] / "app" / "core" / "job_roles.py"
_spec = importlib.util.spec_from_file_location("ishtop_job_roles", _path)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ROLES = _mod.ROLES
COMPILED = _mod.COMPILED
STACK_ROLES = _mod.STACK_ROLES
is_russian = _mod.is_russian
role_name = _mod.role_name
role_from_stack = _mod.role_from_stack
