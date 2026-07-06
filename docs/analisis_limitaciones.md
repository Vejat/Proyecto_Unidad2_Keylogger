# Análisis de Limitaciones del Keylogger

**Ejercicio 1** — SO objetivo: Windows 11 · Librería: `pynput`

---

Nuestro keylogger funciona correctamente en el laboratorio, pero no captura absolutamente todo lo que hace un usuario. Esto es esperable: los sistemas modernos tienen protecciones que limitan este tipo de herramientas.

## Lo que no captura o captura mal

**Contraseñas en navegadores.** Cuando el usuario escribe en un campo de contraseña (`<input type="password">`), los navegadores modernos no entregan el carácter real al hook de teclado. En la práctica vemos asteriscos, caracteres vacíos o directamente nada.

**Sesiones con privilegios elevados (UAC).** Si aparece un cuadro de UAC pidiendo permisos de administrador, el keylogger que corre como usuario normal no captura esas pulsaciones de forma fiable, porque los procesos elevados operan en una sesión separada.

**Aplicaciones con protección anti-keylogger.** Bancos, gestores de contraseñas y algunas apps corporativas usan campos protegidos o teclados virtuales que nuestro hook a nivel de usuario no supera.

**Portapapeles y ratón.** Solo registramos teclado. Si el usuario copia y pega con Ctrl+V, el contenido pegado no aparece como pulsaciones (aunque sí capturamos la tecla `v` y `[CTRL_L]` por separado). Tampoco registramos clics ni movimientos del ratón.

**Teclado en pantalla.** En dispositivos táctiles o con el teclado virtual de Windows, las pulsaciones no pasan por el mismo mecanismo que intercepta `pynput`.

## Lo que sí captura

Registra letras, números y símbolos en aplicaciones normales como Bloc de notas o la consola. También mapeamos teclas especiales como Espacio, Enter, Tab y Backspace, y otras como `[SHIFT]`, `[CTRL_L]` o `[ALT_L]`. Las combinaciones se ven como teclas individuales, no como un atajo interpretado (Ctrl+C aparece como `[CTRL_L]` + `c`, no como "copiar").

## Sobre la persistencia en carpeta compartida

Inicialmente la persistencia fallaba al reiniciar porque el registro apuntaba a un alias de Python de 0 bytes. Lo corregimos con un `.bat` que usa la ruta real de `pythonw.exe` y espera 15 segundos antes de ejecutar, dando tiempo a que la unidad `Y:` de VirtualBox se monte. En un entorno real sería más fiable copiar el ejecutable a una ruta local como `C:\Users\<user>\AppData\`.

## Por qué importa documentar esto

Estas limitaciones demuestran que un keylogger de usuario no es infalible. Las empresas complementan con EDR, monitoreo del registro de inicio y análisis de tráfico. Windows Defender puede detectar comportamiento sospechoso, y los navegadores protegen las credenciales incluso si hay un keylogger activo.