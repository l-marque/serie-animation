"""Chemins du dépôt, utilisés par tous les modules (aucun chemin en dur ailleurs)."""

from __future__ import annotations

from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

SCHEMA_FICHE = RACINE / "schemas" / "fiche_episode.schema.json"
PACKS_DA = RACINE / "blender" / "packs_da"
REGISTRE_ASSETS = RACINE / "blender" / "assets" / "registre.json"
LICENCES_ASSETS = RACINE / "blender" / "assets" / "licences.csv"
SCRIPTS_BLENDER = RACINE / "blender" / "scripts" / "production"
SCRIPT_CONSTRUCTION = SCRIPTS_BLENDER / "construire_scene.py"
SERIES = RACINE / "series"
RENDUS = RACINE / "renders"

# Primitives fournies par le kit de décor « primitifs » (blender/scripts/production/kits/primitifs.py).
# Toute nouvelle primitive doit être ajoutée aux deux endroits (un test le vérifie).
PRIMITIVES = frozenset({"maison", "tour", "arbre", "rocher", "personnage", "caisse", "lampadaire"})

KITS_DECOR = frozenset({"primitifs"})


def dossier_sortie(episode_id: str, mode: str) -> Path:
    """Dossier de travail d'un épisode pour un mode de rendu (animatique ou final)."""
    return RENDUS / episode_id / mode
