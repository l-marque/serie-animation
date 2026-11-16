# Outils pour le PC de rendu (Windows)

Deux scripts PowerShell pour le PC de Guillaume. Ils ne poussent rien et ne touchent à aucune branche distante.

| Script | Rôle |
|---|---|
| `installer-clone.ps1` | Clone le dépôt, recopie `.env` et les assets ignorés par Git depuis une ancienne copie, crée `.venv`, lance les tests. Relançable sans risque. |
| `surveiller-episodes.ps1` | `git fetch`, puis notification Windows quand une branche `episode/<id>` attend le PC de Guillaume (`machine_requise`) ou la plaquette Figma. Avec `-Installer`, s'exécute tout seul toutes les 15 min (tâche planifiée). |

## Installation (une fois)

```powershell
powershell -ExecutionPolicy Bypass -File installer-clone.ps1 -AncienneCopie C:\Users\guill\Documents\serie-animation-tests\depot3
cd $env:USERPROFILE\Documents\serie-animation
powershell -ExecutionPolicy Bypass -File engine\outils\windows\surveiller-episodes.ps1 -Installer
```

(La première commande se lance depuis une copie du script, puisque le clone n'existe pas encore.)

## Ce que la surveillance ne fait pas

Elle ne change pas de branche et ne lance aucun agent : une notification veut dire « ouvre Claude Code dans le clone et tape `/episode reprendre <id>` ». La plaquette Figma et le rendu restent soumis à la validation de Guillaume. Journal : `.git/surveiller-episodes.log`. Désinstaller : `-Desinstaller`.
