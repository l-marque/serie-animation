<#
.SYNOPSIS
  Previent Guillaume quand un episode de Lucas attend le PC de rendu.

.DESCRIPTION
  Fait un « git fetch » (lecture seule : aucune branche locale modifiee, aucun checkout,
  aucun push), lit episodes/suivi/<id>.json sur chaque branche distante episode/*, et
  affiche une notification Windows pour les episodes dont machine_requise designe le
  PC de Guillaume ou dont l'etape courante est la plaquette Figma. Une meme situation
  (branche + commit) n'est signalee qu'une fois (memoire dans .git/episodes-signales.txt).

  -Installer : enregistre une tache planifiee Windows qui lance ce script toutes les
  -IntervalleMinutes minutes (session utilisateur, sans droits administrateur).
  -Desinstaller : supprime cette tache.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File engine\outils\windows\surveiller-episodes.ps1
  powershell -ExecutionPolicy Bypass -File engine\outils\windows\surveiller-episodes.ps1 -Installer
#>
[CmdletBinding()]
param(
    [string]$Clone = (Resolve-Path (Join-Path $PSScriptRoot '..\..\..')).Path,
    [switch]$Installer,
    [switch]$Desinstaller,
    [int]$IntervalleMinutes = 15
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$nomTache = 'Serie animation - episodes a produire'

if ($Desinstaller) {
    Unregister-ScheduledTask -TaskName $nomTache -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Tache « $nomTache » supprimee."
    return
}

if ($Installer) {
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Clone `"$Clone`""
    $declencheur = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
        -RepetitionInterval (New-TimeSpan -Minutes $IntervalleMinutes)
    $reglages = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopIfGoingOnBatteries -AllowStartIfOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 5)
    Register-ScheduledTask -TaskName $nomTache -Action $action -Trigger $declencheur -Settings $reglages -Force | Out-Null
    Write-Host "Tache « $nomTache » installee : toutes les $IntervalleMinutes min."
    return
}

if (-not (Test-Path (Join-Path $Clone '.git'))) { throw "$Clone n'est pas un clone git." }
$journal = Join-Path $Clone '.git\surveiller-episodes.log'
$memoire = Join-Path $Clone '.git\episodes-signales.txt'
function Log([string]$t) { Add-Content -Path $journal -Value "$(Get-Date -Format s) $t" -Encoding UTF8 }

function Notifier([string]$titre, [string]$texte) {
    try {
        Add-Type -AssemblyName System.Windows.Forms, System.Drawing
        $n = New-Object System.Windows.Forms.NotifyIcon
        $n.Icon = [System.Drawing.SystemIcons]::Information
        $n.BalloonTipTitle = $titre
        $n.BalloonTipText = $texte
        $n.Visible = $true
        $n.ShowBalloonTip(10000)
        Start-Sleep -Seconds 10
        $n.Dispose()
    } catch {
        Log "notification impossible : $($_.Exception.Message)"
    }
    Write-Host "$titre : $texte"
}

& git -C $Clone fetch --quiet --prune origin 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { Log 'git fetch en echec (reseau ?)'; exit 1 }

$dejaVus = @{}
if (Test-Path $memoire) { Get-Content $memoire -Encoding UTF8 | ForEach-Object { $dejaVus[$_] = $true } }

$branches = & git -C $Clone for-each-ref --format='%(refname:short) %(objectname:short)' 'refs/remotes/origin/episode/'
$aSignaler = @()
foreach ($ligne in $branches) {
    if (-not $ligne) { continue }
    $ref, $commit = $ligne -split ' ', 2
    $id = $ref.Substring('origin/episode/'.Length)
    $brut = & git -C $Clone show "${ref}:episodes/suivi/$id.json" 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $brut) { Log "$ref : suivi absent"; continue }
    try { $suivi = ($brut -join "`n") | ConvertFrom-Json } catch { Log "$ref : suivi illisible"; continue }
    $machine = [string]$suivi.machine_requise
    $etape = [string]$suivi.etape_courante
    $pourMoi = ($machine -match 'Guillaume') -or ($etape -eq 'plaquette')
    $cle = "$ref $commit"
    if ($pourMoi -and -not $dejaVus.ContainsKey($cle)) {
        $aSignaler += [pscustomobject]@{ Id = $id; Etape = $etape; Cle = $cle }
    }
}

foreach ($e in $aSignaler) {
    Notifier "Episode « $($e.Id) » pour toi" "Etape : $($e.Etape). Dans Claude Code : /episode reprendre $($e.Id)"
    Add-Content -Path $memoire -Value $e.Cle -Encoding UTF8
    Log "signale $($e.Cle) (etape $($e.Etape))"
}
if (-not $aSignaler) { Log 'rien de nouveau' }
