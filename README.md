# Proyecto Unidad 2 — Keylogger Seguro

**Estudiante:** Vejat Olea  
**Universidad:** Universidad de Talca  
**Curso:** Desarrollo de Software para Seguridad  
**Fecha:** Julio 2026

---

## Aviso

Este proyecto es exclusivamente educativo. Todo el desarrollo y las pruebas se realizaron en máquinas virtuales propias dentro de VirtualBox. Está prohibido usar este software en equipos de terceros o redes no autorizadas.

---

## Qué hace el proyecto

Keylogger en Python para Windows 11 que captura teclas, las cifra con AES-256-GCM, las envía periódicamente a un receptor Flask, persiste tras reinicio y se entrega compilado como `WindowsSecurityUpdateService.exe`.

---

## Documentación

| Archivo | Contenido |
|---|---|
| `docs/avance_proyecto.md` | **Informe principal** — paso a paso de todo lo que hicimos |
| `docs/analisis_limitaciones.md` | Qué no captura el keylogger (Ejercicio 1) |
| `docs/justificacion_cifrado.md` | Por qué AES-GCM y cómo se maneja la clave (Ejercicio 2) |
| `docs/mitigacion.md` | Cómo detectar y mitigar la amenaza (Ejercicio 3) |
| `docs/informe_tecnico.md` | Informe de amenaza estilo Threat Intelligence (Ejercicio 4) |
| `docs/guion_video.md` | Guion para el video demostrativo |
| `docs/preparacion_defensa.md` | Preguntas y cambios en vivo para la defensa |
| `evidencias/virustotal/analisis.md` | Resultado del análisis en VirusTotal |

---

## Estructura del código

```
src/
├── keylogger.py       # Captura + envío + persistencia
├── persistence.py     # Registro Windows + launcher .bat
├── crypto_utils.py    # Cifrado AES-256-GCM
├── exfiltration.py    # Cliente HTTP
├── receiver.py        # Servidor Flask (VM atacante)
├── demo_mitm_decrypt.py  # Demo MITM
└── config.py          # IPs, intervalo, nombre de persistencia

build/build.ps1        # Compila el .exe con PyInstaller
dist/                  # Ejecutable generado
evidencias/            # Capturas y análisis VirusTotal
```

---

## Comandos rápidos

```powershell
# Receptor (VM atacante)
cd Y:\src && python receiver.py

# Keylogger (VM víctima)
cd Y:\src && python keylogger.py

# Compilar .exe
cd Y:\build && .\build.ps1

# Limpiar persistencia
cd Y:\src && python persistence.py remove
```