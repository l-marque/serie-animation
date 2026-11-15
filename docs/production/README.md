# Agent Production : démarrage rapide

## Installation (PC de Guillaume, Windows, une seule fois)

```powershell
# Depuis la racine du dépôt cloné
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Blender 5.3 : indiquer son chemin une fois pour toutes (session courante)
$env:BLENDER_PATH = "C:\Program Files\Blender Foundation\Blender 5.3\blender.exe"

# ffmpeg : installer une version « full » (avec libass pour les sous-titres) et l'ajouter au PATH
winget install Gyan.FFmpeg
```

## Produire un épisode

```powershell
# 1. Vérifier la fiche (1 seconde, aucun rendu)
python -m scripts.production.run episodes/exemples/demo_001.json --valider-seulement

# 2. Animatique (basse définition, pour valider le rythme)
python -m scripts.production.run episodes/exemples/demo_001.json

# 3. Rendu final (après validation humaine de l'animatique)
python -m scripts.production.run episodes/exemples/demo_001.json --mode final
```

Résultats dans `renders/<episode>/<mode>/` : `episode.mp4`, `planche_contact.png`, `rapport.json`, `timeline.json`, `scene.blend`.

Dans Claude Code, il suffit de demander : « utilise l'agent production pour faire l'animatique de episodes/exemples/demo_001.json ».

## Options utiles

| Option | Effet |
|---|---|
| `--mode final` | qualité de publication (100 % de la résolution) |
| `--pourcent 25` | résolution réduite (aperçu très rapide) |
| `--moteur BLENDER_WORKBENCH` | moteur le plus rapide (aperçu sans ombres réalistes) |
| `--forcer` | ignore le cache et re-rend tout |
| `--blender <chemin>` | exécutable Blender (sinon `BLENDER_PATH`, sinon `blender`) |

## Tests

```powershell
python -m pytest tests/production -q
```

## Pour aller plus loin

- [Architecture](architecture.md) · [Contrat de la fiche épisode](contrat-fiche-episode.md) · [Vocabulaire d'actions](vocabulaire-actions.md) · [Trouver des modèles 3D](sourcing-assets.md) · [Conventions Blender](../conventions-blender.md)
