# Guion del Video Demostrativo

**Estudiante:** Vejat Olea  
**Duración estimada:** 10–12 minutos  
**Requisito:** cámara encendida durante todo el video

---

## Antes de grabar

- VMs encendidas: víctima y atacante
- Receptor corriendo en la VM atacante
- Keylogger o `.exe` listo en la víctima
- Capturas de Wireshark y VirusTotal por si falla algo en vivo

---

## Introducción (1 min)

> "Hola, soy Vejat Olea. Video demostrativo del Proyecto Unidad 2 de Seguridad Informática, Universidad de Talca. Desarrollé un keylogger educativo en Python para Windows 11, probado solo en VMs propias. Captura teclas, cifra con AES-256-GCM, envía al atacante, persiste tras reinicio y se entrega como ejecutable."

---

## 1. Entorno (1 min)

Mostrar VirtualBox con las dos VMs.

> "Víctima en 192.168.56.107, atacante en 192.168.56.108, red Host-Only. El código está en carpeta compartida Y:."

---

## 2. Keylogger funcionando (2 min)

**Atacante:** `python receiver.py`  
**Víctima:** `python keylogger.py`  
Escribir en Bloc de notas.

> "Cada 20 segundos cifra el buffer y lo envía. El receptor descifra y muestra las teclas."

---

## 3. Cifrado (1 min)

> "Usamos AES-GCM, no un hash. SHA es irreversible y no permite leer las teclas. La clave está en secret.key compartida por Y:."

---

## 4. Persistencia (1.5 min)

Mostrar Task Manager con `pythonw.exe` o captura post-reinicio.

> "Se registra como WindowsSecurityUpdateService en HKCU Run, usando un .bat que apunta al pythonw real."

---

## 5. Ejecutable (1 min)

Mostrar `WindowsSecurityUpdateService.exe` compilado con PyInstaller.

---

## 6. MITM Wireshark (2 min)

Mostrar capturas `filtro oficial.png` y `mensaje cifrado.png`.

> "Capturé en la VM atacante. Se ven POST /upload pero el payload es base64 ilegible. El MITM no puede leer las teclas sin la clave."

---

## 7. VirusTotal (1 min)

> "19 de 69 motores lo detectaron. ESET lo marcó como keylogger Python. Microsoft no lo detectó. Evasión parcial, no total."

---

## 8. Cierre (30 seg)

> "Todo está en el repositorio de GitHub. Gracias."

Mostrar link del repo.