# Ejecutar DESPUES de crear el repo vacio en GitHub.
# Uso: .\push-github.ps1 -Usuario TU_USUARIO_GITHUB

param(
    [Parameter(Mandatory = $true)]
    [string]$Usuario
)

$ErrorActionPreference = "Stop"
$Repo = "Proyecto_Unidad2_Keylogger"
$Url = "https://github.com/$Usuario/$Repo.git"

git remote remove origin 2>$null
git remote add origin $Url
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "[+] Repositorio publicado en: https://github.com/$Usuario/$Repo"