"""Habillage d'un épisode : fichier interne au pôle Production, facultatif.

Le contrat v1.0 (contracts/fiche-episode.schema.json) ne décrit pas encore les textes en 3D
(nom d'une ville sur un panneau, légendes de cartes de choix). En attendant une version du
contrat validée par Lucas et Guillaume, la production les lit dans un fichier posé à côté de
la fiche : `<fiche>.habillage.json` (schéma engine/schemas/habillage.schema.json).

Le fichier est optionnel : sans lui, rien ne change.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

from . import chemins

SCHEMA_HABILLAGE = chemins.MOTEUR / "schemas" / "habillage.schema.json"


class HabillageInvalide(Exception):
    def __init__(self, erreurs: list[str]):
        self.erreurs = erreurs
        super().__init__("Habillage invalide :\n- " + "\n- ".join(erreurs))


def chemin_pour(fiche_source: Path | None) -> Path | None:
    if fiche_source is None:
        return None
    fiche_source = Path(fiche_source)
    return fiche_source.with_name(f"{fiche_source.stem}.habillage.json")


def valider(donnees: dict[str, Any], fiche: dict[str, Any]) -> list[dict[str, Any]]:
    """Valide l'habillage contre son schéma et contre la fiche ; renvoie les textes 3D (défauts appliqués)."""
    schema = json.loads(SCHEMA_HABILLAGE.read_text(encoding="utf-8"))
    erreurs = [f"{'/'.join(map(str, e.absolute_path)) or 'racine'} : {e.message}"
               for e in jsonschema.Draft202012Validator(schema).iter_errors(donnees)]
    if erreurs:
        raise HabillageInvalide(erreurs)
    ids_fiche = {o["id"] for cle in ("elements", "personnages", "modules") for o in fiche.get(cle, [])}
    parents_possibles = {o["id"] for cle in ("elements", "personnages") for o in fiche.get(cle, [])}
    vus: set[str] = set()
    textes = []
    for t in donnees.get("textes_3d", []):
        if t["id"] in ids_fiche or t["id"] in vus:
            erreurs.append(f"texte '{t['id']}' : id déjà utilisé")
        vus.add(t["id"])
        if t.get("parent") and t["parent"] not in parents_possibles:
            erreurs.append(f"texte '{t['id']}' : parent '{t['parent']}' absent des éléments et personnages de la fiche")
        textes.append({"position": [0.0, 0.0, 0.0], "rotation_z": 0.0, "taille": 0.3, "epaisseur": 0.02,
                       "role": "accent", "visible_au_debut": True, "parent": None, **t})
    if erreurs:
        raise HabillageInvalide(erreurs)
    return textes


def lire(fiche_source: Path | None) -> dict[str, Any] | None:
    chemin = chemin_pour(fiche_source)
    if chemin is None or not chemin.is_file():
        return None
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HabillageInvalide([f"{chemin.name} : JSON illisible ({e})"]) from e


def charger(fiche_source: Path | None, fiche: dict[str, Any]) -> list[dict[str, Any]]:
    """Textes 3D de l'habillage de la fiche, ou [] s'il n'y a pas de fichier d'habillage."""
    donnees = lire(fiche_source)
    return [] if donnees is None else valider(donnees, fiche)


def charger_hud(fiche_source: Path | None) -> list[dict[str, Any]]:
    """Éléments du HUD (déjà validés par le schéma lors de charger()), ou [] sans habillage."""
    donnees = lire(fiche_source)
    return [] if donnees is None else list(donnees.get("hud", []))
