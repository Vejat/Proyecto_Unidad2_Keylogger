# Análisis de Mitigación

**Ejercicio 3** — Alternativas para usuarios y especialistas TI

---

## Para usuarios finales

Un usuario puede sospechar de infección si el PC va lento sin razón, si aparecen procesos desconocidos en el Administrador de tareas (como `pythonw.exe` o `WindowsSecurityUpdateService.exe`), o si hay tráfico de red periódico hacia IPs internas inusuales.

Las buenas prácticas incluyen no ejecutar archivos de origen desconocido, mantener Windows y el antivirus actualizados, usar gestores de contraseñas con autocompletado protegido, y revisar periódicamente las aplicaciones de inicio en Configuración de Windows.

## Para especialistas TI y SOC

**Detección en el endpoint.** Revisar `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` buscando entradas sospechosas. En nuestro proyecto la IoC es el valor `WindowsSecurityUpdateService` apuntando a un `.bat` o `.exe`. También conviene revisar la carpeta `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` y buscar procesos sin ventana que consuman red de forma periódica con herramientas como Autoruns o Process Explorer.

**Detección en red.** Nuestro keylogger genera un patrón reconocible: POST HTTP cada 20 segundos hacia el mismo host en el puerto 5000, con un JSON que contiene un campo `payload` en base64 largo. Wireshark, Zeek o un IDS con reglas personalizadas pueden alertar sobre este comportamiento.

**Análisis forense.** Buscar `secret.key` en el disco de la víctima y comparar el hash SHA-256 del ejecutable (`7CEFCF86B89F2323E5279BF7D24D5BD424F4A52A6E831FE6CD6FDBF838E5F421`) con listas de bloqueo.

## Medidas de mitigación

Un EDR como Defender for Endpoint puede detectar hooks de teclado y comportamiento anómalo. Application Control (AppLocker o WDAC) bloquea la ejecución de binarios PyInstaller no firmados. La segmentación de red impide que la víctima alcance el servidor receptor en `192.168.56.108:5000`, y el bloqueo de puertos salientes corta la exfiltración HTTP.

El monitoreo de cambios en claves Run detecta la persistencia rápidamente. Ninguna medida es perfecta por sí sola, pero en capas son efectivas.

## Respuesta ante incidente

Ante una sospecha, aislar el equipo de la red, eliminar las entradas del registro y archivos en Startup, terminar el proceso malicioso, borrar el ejecutable y `secret.key`, identificar el servidor receptor en los logs de red, y rotar las credenciales que se hayan usado en el equipo comprometido.

## Limitaciones de las defensas frente a nuestro implante

El tráfico cifrado con AES-GCM no se lee con solo inspeccionar la red. El nombre `WindowsSecurityUpdateService` intenta mezclarse con procesos legítimos. La persistencia en HKCU no requiere privilegios de administrador. Por eso se necesita un enfoque combinado de antivirus, EDR, monitoreo de red y educación del usuario.