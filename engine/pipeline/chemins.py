"""Chemins du dépôt, utilisés par tous les modules (aucun chemin en dur ailleurs)."""

from __future__ import annotations

from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

MOTEUR = RACINE / "engine"
CONTRATS = RACINE / "contracts"

SCHEMA_FICHE = CONTRATS / "fiche-episode.schema.json"
SCHEMA_PACK_DA = MOTEUR / "schemas" / "pack-da.schema.json"
PACKS_DA = MOTEUR / "packs_da"
ASSETS = MOTEUR / "assets"
REGISTRE_ASSETS = ASSETS / "registre.json"
LICENCES_ASSETS = ASSETS / "licences.csv"
SCRIPTS_BLENDER = MOTEUR / "blender"
SCRIPT_CONSTRUCTION = SCRIPTS_BLENDER / "construire_scene.py"
SERIES = RACINE / "series"
RENDUS = RACINE / "renders"

# Primitives fournies par le kit de décor « primitifs » (engine/blender/kits/primitifs.py).
# Toute nouvelle primitive doit être ajoutée aux deux endroits (un test le vérifie).
PRIMITIVES = frozenset({"maison", "tour", "arbre", "rocher", "personnage", "caisse", "lampadaire",
                        "canard", "baignoire", "eau", "donut", "ballon"})

KITS_DECOR = frozenset({"primitifs"})


def dossier_sortie(episode_id: str, mode: str) -> Path:
    """Dossier de travail d'un épisode pour un mode de rendu (animatique ou final)."""
    return RENDUS / episode_id / mode
