"""
demo_mitm_decrypt.py
Demuestra que un payload interceptado (ej: copiado de Wireshark) NO se
puede descifrar sin secret.key.

Uso en la VM atacante:
    python demo_mitm_decrypt.py "BASE64_DEL_PAYLOAD"

O con un payload de ejemplo generado al vuelo:
    python demo_mitm_decrypt.py --demo
"""

import argparse
import os
import sys

from crypto_utils import decrypt, encrypt, generate_key, load_key
from app_paths import get_key_path


def main():
    parser = argparse.ArgumentParser(description="Demo MITM: descifrado fallido sin clave")
    parser.add_argument("payload", nargs="?", help="Payload base64 interceptado")
    parser.add_argument("--demo", action="store_true", help="Generar payload de prueba")
    args = parser.parse_args()

    if args.demo:
        key = generate_key()
        original = b"usuario: admin\npassword: Test123!\n"
        payload = encrypt(original, key)
        wrong_key = generate_key()
        print("[*] Modo demo — simulando interceptacion MITM\n")
        print(f"Texto original (solo la victima lo escribio):\n{original.decode()}\n")
        print(f"Payload interceptado (base64):\n{payload[:80]}...\n")
    else:
        if not args.payload:
            parser.print_help()
            sys.exit(1)
        payload = args.payload.strip()
        key_path = get_key_path()
        if not os.path.isfile(key_path):
            print(f"[-] No se encontro {key_path}")
            print("    Copia secret.key de la victima o usa --demo")
            sys.exit(1)
        key = load_key(key_path)
        wrong_key = generate_key()

    print("--- Intento 1: atacante MITM sin la clave ---")
    try:
        result = decrypt(payload, wrong_key)
        print(f"[!] Inesperado, obtuvo: {result[:50]}")
    except Exception as exc:
        print(f"[+] FALLO al descifrar (esperado): {type(exc).__name__}")
        print("    El MITM ve el trafico pero NO puede leer las teclas.\n")

    if args.demo:
        print("--- Intento 2: receptor legitimo con la clave correcta ---")
        try:
            result = decrypt(payload, key)
            print(f"[+] Descifrado exitoso:\n{result.decode()}")
        except Exception as exc:
            print(f"[-] Error: {exc}")


if __name__ == "__main__":
    main()