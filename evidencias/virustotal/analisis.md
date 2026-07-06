# Análisis VirusTotal

**Archivo:** WindowsSecurityUpdateService.exe  
**Fecha:** 06/07/2026  
**Enlace:** https://www.virustotal.com/gui/file/7cefcf86b89f2323e5279bf7d24d5bd424f4a52a6e831fe6cd6fdbf838e5f421

---

## Resultado

**19 de 69 motores** marcaron el archivo como malicioso (**27,5%**). Los otros 50 no lo detectaron.

VirusTotal lo etiquetó como `trojan.clyp/keylogger`, con categorías trojan y dropper, y familias clyp y keylogger.

El archivo pesa 14.39 MB, es un PE32+ x86-64 empaquetado con PyInstaller, compilado el 05/07/2026. Su SHA-256 es `7CEFCF86B89F2323E5279BF7D24D5BD424F4A52A6E831FE6CD6FDBF838E5F421`.

## Motores que lo detectan

Los más relevantes: **ESET** lo marcó como `Python/Spy.KeyLogger.MT` (identifica keylogger directamente), **Kaspersky** como `HEUR:Trojan-Spy.Python.Keylogger.ae`, y **Yandex** como `Riskware.PyInstaller` (desconfía del empaquetador).

Varios motores (BitDefender, GData, Emsisoft, eScan, VIPRE, Arcabit) usan la heurística `Gen:Heur.Clyp.13`. **CrowdStrike** y **SentinelOne** lo marcaron por machine learning. **McAfee** lo detectó por hash (`Ti!7CEFCF86B89F`).

En total fueron 19 motores, la mayoría por firma o heurística sobre PyInstaller y comportamiento de keylogger Python.

## Motores que no lo detectan

Entre los 50 sin detección destacan **Microsoft, Avast, AVG, Symantec, Sophos, Malwarebytes, Google, Fortinet y Trend Micro**. Esto demuestra evasión parcial: no todos los antivirus lo marcan, cumpliendo el requisito del ejercicio.

## Conclusión

La evasión total no es posible con PyInstaller y `pynput`, pero logramos evasión parcial frente a motores importantes. Los que sí detectan identifican el empaquetador Python y la funcionalidad de keylogger. El cifrado AES-GCM del tráfico sigue siendo efectivo: aunque se intercepte la comunicación HTTP, el contenido no es legible sin `secret.key`.

Evidencias: `nota general .png`, `detecciones.pdf` y `detalles.pdf` en esta carpeta.