<#
.SYNOPSIS
  Installe un vrai clone git du depot sur le PC de rendu (Windows) et y recopie
  ce que Git ne transporte pas : .env (cles API) et assets telecharges.

.DESCRIPTION
  Idempotent : relancer le script ne casse rien.
    1. Clone https://github.com/l-marque/serie-animation dans -Destination (ou fait un fetch s'il existe deja).
    2. Copie .env et les dossiers d'assets ignores par Git depuis -AncienneCopie (sans ecraser l'existant).
    3. Cree l'environnement Python .venv et installe engine/requirements.txt.
    4. Lance les tests (pytest -q) pour verifier l'installation.
  Ne pousse rien, ne modifie aucune branche distante.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File engine\outils\windows\installer-clone.ps1 `
    -AncienneCopie C:\Users\guill\Documents\serie-animation-tests\depot3
#>
[CmdletBinding()]
param(
    [string]$Destination = (Join-Path $env:USERPROFILE 'Documents\serie-animation'),
    [string]$AncienneCopie = '',
    [string]$Depot = 'https://github.com/l-marque/serie-animation.git',
    [string]$Python = 'py',
    [switch]$SansTests
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Etape([string]$texte) { Write-Host "==> $texte" -ForegroundColor Cyan }
function Executer([string]$exe, [string[]]$arguments) {
    & $exe @arguments
    if ($LASTEXITCODE -ne 0) { throw "Echec ($LASTEXITCODE) : $exe $($arguments -join ' ')" }
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'git est introuvable : installer Git for Windows.' }

# 1. Clone ou mise a jour
if (Test-Path (Join-Path $Destination '.git')) {
    Etape "Clone deja present : git fetch dans $Destination"
    Executer git @('-C', $Destination, 'fetch', '--prune', 'origin')
} elseif (Test-Path $Destination) {
    throw "$Destination existe mais n'est pas un clone git : choisir une autre -Destination."
} else {
    Etape "Clone de $Depot vers $Destination"
    Executer git @('clone', $Depot, $Destination)
}

# 2. Fichiers hors Git (secrets et assets lourds)
$horsGit = @('.env', 'engine\assets\modeles', 'engine\assets\textures', 'engine\assets\hdri', 'engine\assets\sons\kenney')
if ($AncienneCopie) {
    if (-not (Test-Path $AncienneCopie)) { throw "Ancienne copie introuvable : $AncienneCopie" }
    foreach ($rel in $horsGit) {
        $src = Join-Path $AncienneCopie $rel
        $dst = Join-Path $Destination $rel
        if (-not (Test-Path $src)) { Write-Host "    (absent dans l'ancienne copie) $rel"; continue }
        if ((Get-Item $src).PSIsContainer) {
            New-Item -ItemType Directory -Force -Path $dst | Out-Null
            # /XC /XN /XO : ne remplace jamais un fichier deja present dans le clone
            robocopy $src $dst /E /XC /XN /XO /NFL /NDL /NJH /NJS /NP | Out-Null
            if ($LASTEXITCODE -ge 8) { throw "robocopy a echoue pour $rel (code $LASTEXITCODE)" }
            Write-Host "    copie : $rel"
        } elseif (-not (Test-Path $dst)) {
            Copy-Item $src $dst
            Write-Host "    copie : $rel"
        } else {
            Write-Host "    deja present, garde : $rel"
        }
    }
} else {
    Write-Host '    -AncienneCopie non fourni : .env et assets a recopier a la main (ou retelecharger).'
}
if (-not (Test-Path (Join-Path $Destination '.env'))) {
    Write-Warning '.env absent : les sources qui demandent une cle (Poly Pizza, 3DTexel, Sketchfab) ne marcheront pas.'
}

# 3. Environnement Python
$venv = Join-Path $Destination '.venv'
$py = Join-Path $venv 'Scripts\python.exe'
if (-not (Test-Path $py)) {
    Etape 'Creation de .venv'
    if ($Python -eq 'py') { Executer py @('-3', '-m', 'venv', $venv) } else { Executer $Python @('-m', 'venv', $venv) }
}
Etape 'Installation des dependances (engine/requirements.txt)'
Executer $py @('-m', 'pip', 'install', '--quiet', '--upgrade', 'pip')
Executer $py @('-m', 'pip', 'install', '--quiet', '-r', (Join-Path $Destination 'engine\requirements.txt'))

# 4. Verification
if (-not $SansTests) {
    Etape 'Tests'
    Push-Location $Destination
    try { Executer $py @('-m', 'pytest', '-q') } finally { Pop-Location }
}

Etape "Termine. Ouvrir Claude Code dans : $Destination"
