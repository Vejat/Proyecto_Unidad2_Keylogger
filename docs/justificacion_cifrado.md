# Justificación del Cifrado y Gestión de Clave

**Ejercicio 2** — Algoritmo: AES-256-GCM

---

## Por qué elegimos AES-256-GCM

Necesitábamos proteger los logs para que solo el receptor pudiera leerlos, pero también recuperar el texto original. Por eso usamos cifrado simétrico autenticado, no un hash.

AES-256-GCM nos da confidencialidad (nadie sin la clave lee las teclas), integridad (si alguien altera el paquete en tránsito, el descifrado falla) y autenticación (GCM incluye un tag que valida que el mensaje no fue modificado). Es un estándar moderno implementado en la librería `cryptography` de Python.

En cada envío generamos un nonce aleatorio de 12 bytes, ciframos el log con AES-GCM, concatenamos `nonce + ciphertext` y lo codificamos en base64 para transmitirlo por HTTP. En el receptor hacemos el proceso inverso con la misma clave.

## Por qué no usamos un hash (MD5, SHA-256)

Un hash transforma datos en un valor fijo de forma irreversible. Sirve para verificar integridad o almacenar contraseñas con salt, pero no permite recuperar el texto original.

Si usáramos SHA-256 sobre los logs, el receptor solo obtendría algo como `a3f8b2c1...` y nunca podría mostrar qué teclas se escribieron. Eso incumple el ejercicio, que pide descifrar y mostrar lo capturado.

MD5 además está roto para seguridad: tiene colisiones prácticas y no fue diseñado para cifrado. Aunque lo usáramos como hash, seguiría sin servir porque no es reversible.

En resumen: los hashes verifican y comparan, el cifrado protege y permite leer el contenido con la clave.

## Gestión de la clave

La clave no está embebida en el código. Se genera dinámicamente la primera vez que corre el keylogger y se guarda en `secret.key` junto al programa. El receptor lee ese mismo archivo (en nuestro lab se comparte por la carpeta `Y:\` de VirtualBox).

**Ventajas:** no hay clave hardcodeada en el repositorio y cada instalación puede tener una clave distinta.

**Desventajas:** si un analista accede a `secret.key` en la víctima, puede descifrar todo el tráfico. En nuestro laboratorio compartimos la clave manualmente al atacante, lo cual no escala en un ataque real. Un atacante real podría embeber la clave en el `.exe` o derivarla de forma determinística.

Consideramos embeber la clave en el ejecutable, pero es fácil de extraer con ingeniería inversa. También descartamos intercambio Diffie-Hellman por complejidad. Para el proyecto académico, la generación dinámica con archivo compartido es suficiente y fácil de demostrar.

## Intervalo de envío

Configurado en `config.py` como `SEND_INTERVAL = 20` segundos. Cada 20 segundos el hilo de exfiltración toma el buffer, lo cifra y lo envía. Es configurable cambiando ese valor y reiniciando el programa.