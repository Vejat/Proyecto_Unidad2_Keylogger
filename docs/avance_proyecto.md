# Avance del Proyecto — Unidad 2 Keylogger

**Curso:** Desarrollo de Software para Seguridad  
**Universidad:** Universidad de Talca  
**Fecha:** Julio 2026

---

## Introducción

Para este proyecto desarrollamos un keylogger educativo en Python dentro de un entorno de laboratorio con VirtualBox. Simulamos un escenario entre una máquina víctima y una máquina atacante, todo controlado y aislado, sin usar equipos de terceros.

Completamos los cuatro ejercicios del proyecto: captura de teclado con persistencia, cifrado y envío de datos, compilación a ejecutable con demostración MITM y análisis en VirusTotal, e informe técnico de amenaza. Este documento resume paso a paso lo que hicimos, los comandos que usamos y las evidencias que obtuvimos.

---

## Paso 1 — Configurar las máquinas virtuales

Lo primero fue crear dos VMs con Windows 11 en VirtualBox: una llamada **windows 11 pro** (atacante) y otra **windows 11 victima** (keylogger).

En ambas configuramos un adaptador de red **Host-Only**. Las IPs que quedaron fueron:

- VM Víctima: `192.168.56.107`
- VM Atacante: `192.168.56.108`
- Host (interfaz Ethernet): `192.168.56.1`

![VMs corriendo en VirtualBox](../evidencias/capturas/mv%20windows%2011%20pro%20victima%20y%20atacante.png)

---

## Paso 2 — Pasar el código a las VMs con carpeta compartida

Configuramos una carpeta compartida en VirtualBox apuntando a `Proyecto_Unidad2_Keylogger`, con nombre `Proyecto`, **Automontar** y **Make Machine-permanent** activados.

![Configuración de carpeta compartida](../evidencias/capturas/pasando%20el%20software%20kylogger%20a%20las%20mv.png)

En cada VM montamos la unidad:

```powershell
net use Y: \\vboxsrv\Proyecto /persistent:yes
Y:
dir
```

El código quedó accesible en `Y:\src`.

---

## Paso 3 — Instalar las dependencias de Python

```powershell
cd Y:\src
pip install -r requirements.txt
```

Usamos `pynput` (teclado), `cryptography` (AES-GCM), `requests` (envío HTTP) y `flask` (receptor).

![Montaje de Y: e instalación de dependencias](../evidencias/capturas/dependencias%20.png)

---

## Paso 4 — Configurar la comunicación entre víctima y atacante

En `config.py`:

```python
SERVER_URL = "http://192.168.56.108:5000/upload"
SEND_INTERVAL = 20  # segundos
```

La primera ejecución del keylogger genera `secret.key`. Como ambas VMs comparten `Y:\`, el receptor lee la misma clave para descifrar.

---

## Paso 5 — Levantar el receptor en la VM atacante

```powershell
cd Y:\src
python receiver.py
```

El receptor escucha en el puerto 5000, descifra cada POST a `/upload` y guarda los logs en `received_logs.txt`.

---

## Paso 6 — Ejecutar el keylogger en la VM víctima

```powershell
cd Y:\src
python keylogger.py
```

El programa captura teclas con `pynput`, las acumula en un buffer y cada 20 segundos las cifra con AES-256-GCM y las envía al atacante.

```
[+] Datos capturados (37 eventos). Enviando cifrado...
[+] Datos enviados exitosamente.
```

![Keylogger capturando y enviando](../evidencias/capturas/kyloger%20ejecutandose.png)

![Receptor mostrando las teclas recibidas](../evidencias/capturas/receptor%20funcioanndo.png)

Elegimos AES-GCM y no un hash porque necesitamos recuperar el texto original en el receptor. Un hash como SHA es unidireccional y no sirve para descifrar logs.

---

## Paso 7 — Instalar la persistencia

```powershell
cd Y:\src
python persistence.py install
```

Esto creó `run_keylogger.bat`, lo registró en `HKCU\...\Run` como `WindowsSecurityUpdateService` y lo copió a la carpeta de Inicio.

```powershell
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v WindowsSecurityUpdateService
type run_keylogger.bat
```

**Problema que tuvimos:** al principio la persistencia no funcionaba tras reiniciar. El registro apuntaba a un alias de Python de la Microsoft Store (archivo de 0 bytes). La solución fue registrar un `.bat` con la ruta real de `pythonw.exe` y un `timeout` de 15 segundos para que la unidad `Y:` alcance a montarse.

---

## Paso 8 — Probar la persistencia tras reinicio

Reiniciamos la VM víctima sin ejecutar nada manualmente. Después de iniciar sesión:

- Apareció `pythonw.exe` en el Administrador de tareas.
- El receptor empezó a recibir teclas automáticamente.

![Proceso en Administrador de tareas](../evidencias/capturas/admin%20tareas%20python.exe.png)

---

## Paso 9 — Compilar el keylogger a ejecutable (Ejercicio 3)

El proyecto exige entregar un binario, no solo el script. Compilamos con PyInstaller:

```powershell
cd Y:\build
.\build.ps1
```

Esto generó `dist/WindowsSecurityUpdateService.exe` (~14.4 MB). Probamos el ejecutable en la VM víctima y funcionó igual que el script: capturó teclas y las envió cifradas al receptor.

![Ejecutable corriendo](../evidencias/capturas/windows%20securityupdateservice.png)

El hash SHA-256 del binario es:

```
7CEFCF86B89F2323E5279BF7D24D5BD424F4A52A6E831FE6CD6FDBF838E5F421
```

---

## Paso 10 — Demostración MITM con Wireshark (Ejercicio 3)

**Problema que tuvimos:** capturamos primero en el host (interfaz Ethernet `192.168.56.1`) y el filtro quedaba vacío aunque el keylogger enviaba datos correctamente. Esto pasa porque en VirtualBox el tráfico entre dos VMs (`.107` → `.108`) no pasa por la tarjeta del host.

**Solución:** instalamos Wireshark en la **VM atacante** y capturamos ahí.

Aplicamos el filtro:

```
ip.addr == 192.168.56.107 && ip.addr == 192.168.56.108 && tcp.port == 5000
```

Vimos múltiples paquetes **HTTP POST /upload** de la víctima al atacante y respuestas **200 OK**, confirmando la exfiltración periódica.

![Tráfico HTTP capturado con filtro](../evidencias/capturas/filtro%20oficial.png)

Al abrir el cuerpo de un paquete POST, el campo `payload` aparece como base64 ilegible. Un atacante MITM puede interceptar el tráfico, pero **no puede leer las teclas** sin `secret.key`.

![Payload cifrado en Wireshark](../evidencias/capturas/mensaje%20cifrado.png)

También creamos el script `demo_mitm_decrypt.py` para demostrar que un payload interceptado falla al descifrar sin la clave correcta.

---

## Paso 11 — Análisis en VirusTotal (Ejercicio 3)

Subimos `WindowsSecurityUpdateService.exe` a https://www.virustotal.com

**Resultado: 19 de 69 motores lo detectaron (27,5%).**

Etiqueta de amenaza: `trojan.clyp/keylogger`

Los que lo detectan lo clasifican principalmente como keylogger Python empaquetado con PyInstaller:
- ESET: `Python/Spy.KeyLogger.MT`
- Kaspersky: `HEUR:Trojan-Spy.Python.Keylogger.ae`
- Yandex: `Riskware.PyInstaller`
- Varios más con heurística `Gen:Heur.Clyp.13`

Los que **no** lo detectan incluyen **Microsoft, Avast, AVG, Symantec, Sophos y Malwarebytes**. Esto demuestra evasión parcial: no todos los antivirus lo marcan.

![Resultado general VirusTotal](../evidencias/virustotal/nota%20general%20.png)

El análisis completo está en `evidencias/virustotal/analisis.md`.

---

## Conclusión

Montamos un laboratorio con dos VMs Windows 11 donde el keylogger captura teclas, las cifra con AES-256-GCM, las envía cada 20 segundos al atacante, sobrevive reinicios mediante persistencia en el registro de Windows, y se entrega como ejecutable compilado con PyInstaller.

Demostramos con Wireshark que un MITM intercepta el tráfico HTTP pero no puede leer el contenido cifrado. En VirusTotal, 19 de 69 motores detectaron el binario, confirmando que la evasión total es difícil pero la evasión parcial y el cifrado de red sí funcionan como capas de protección del atacante.

El proyecto cumple los objetivos técnicos de los cuatro ejercicios en entorno controlado.