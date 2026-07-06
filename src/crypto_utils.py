"""
crypto_utils.py
Módulo de cifrado y descifrado.
Usaremos AES-256-GCM (Authenticated Encryption) de la librería 'cryptography'.

Justificación (para el informe):
- AES-GCM proporciona confidencialidad + integridad + autenticación.
- Es un estándar moderno recomendado (mejor que AES-CBC + HMAC manual).
- A diferencia de hashes (MD5, SHA), NO es para cifrar datos. Los hashes son one-way.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

KEY_SIZE = 32  # 256 bits para AES-256


def generate_key() -> bytes:
    """Genera una clave AES-256 aleatoria y segura."""
    return os.urandom(KEY_SIZE)


def save_key(key: bytes, path: str):
    """Guarda la clave en un archivo (base64 para facilidad)."""
    with open(path, "wb") as f:
        f.write(base64.b64encode(key))


def load_key(path: str) -> bytes:
    """Carga la clave desde archivo."""
    with open(path, "rb") as f:
        return base64.b64decode(f.read())


def encrypt(data: bytes, key: bytes) -> str:
    """
    Cifra con AES-256-GCM. Retorna base64 de: nonce (12 B) + ciphertext + tag (16 B).
    El nonce es único por envío; reutilizarlo con la misma clave rompe GCM.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # recomendación NIST para GCM
    ciphertext = aesgcm.encrypt(nonce, data, None)  # tag va al final del ciphertext
    encrypted = nonce + ciphertext
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt(encrypted_b64: str, key: bytes) -> bytes:
    """
    Descifra un payload producido por encrypt().
    Si la clave es incorrecta o el dato fue alterado, lanza InvalidTag.
    """
    aesgcm = AESGCM(key)
    data = base64.b64decode(encrypted_b64)
    nonce = data[:12]
    ciphertext = data[12:]  # incluye tag de autenticación
    return aesgcm.decrypt(nonce, ciphertext, None)
