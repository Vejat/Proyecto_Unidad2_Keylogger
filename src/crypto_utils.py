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

KEY_SIZE = 32  # 256 bits


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
    Cifra los datos usando AES-256-GCM.
    Retorna un string base64: nonce + ciphertext + tag
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # GCM recomienda 12 bytes
    ciphertext = aesgcm.encrypt(nonce, data, None)
    # nonce + ciphertext (incluye el tag de 16 bytes al final)
    encrypted = nonce + ciphertext
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt(encrypted_b64: str, key: bytes) -> bytes:
    """
    Descifra datos en formato base64 producidos por encrypt().
    """
    aesgcm = AESGCM(key)
    data = base64.b64decode(encrypted_b64)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)
