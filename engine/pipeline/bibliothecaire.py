"""Bibliothécaire (partie script) : vérifie que chaque asset demandé est disponible et licite.

- 'primitif:<nom>' : doit être une primitive du kit de décor ;
- 'bibliotheque:<id>' : doit figurer dans engine/assets/registre.json, pointer vers un
  fichier existant, et avoir une ligne dans engine/assets/licences.csv.

Les assets manquants ne sont PAS cherchés ici : la liste est renvoyée au chef d'orchestre,
que prod-chef traite avec engine/pipeline/sources_assets.py (recherche, choix humain, intégration).
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from typing import Any

from . import chemins


@dataclass
class Verification:
    manquants: list[dict[str, str]] = field(default_factory=list)
    attributions: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.manquants


def _registre() -> dict[str, Any]:
    if not chemins.REGISTRE_ASSETS.is_file():
        return {}
    return json.loads(chemins.REGISTRE_ASSETS.read_text(encoding="utf-8")).get("assets", {})


def _licences() -> dict[str, dict[str, str]]:
    if not chemins.LICENCES_ASSETS.is_file():
        return {}
    with chemins.LICENCES_ASSETS.open(encoding="utf-8", newline="") as f:
        return {ligne["id"]: ligne for ligne in csv.DictReader(f) if ligne.get("id")}


def references_assets(donnees: dict[str, Any]) -> dict[str, list[str]]:
    """Asset -> liste des endroits où il est demandé (pour des messages clairs)."""
    refs: dict[str, list[str]] = {}
    for cat in ("elements", "personnages", "modules"):
        for o in donnees.get(cat, []):
            refs.setdefault(o["asset"], []).append(f"{cat}:{o['id']}")
    for b in donnees.get("beats", []):
        for a in b.get("actions", []):
            va = a.get("params", {}).get("vers_asset")
            if va:
                refs.setdefault(va, []).append(f"beat:{b['id']}:transformer")
    return refs


def verifier(donnees: dict[str, Any]) -> Verification:
    reg, lic = _registre(), _licences()
    v = Verification()
    for asset, ou in sorted(references_assets(donnees).items()):
        espace, nom = asset.split(":", 1)
        if espace == "primitif":
            if nom not in chemins.PRIMITIVES:
                v.manquants.append({"asset": asset, "raison": "primitive inconnue du kit",
                                    "utilise_par": ", ".join(ou),
                                    "disponibles": ", ".join(sorted(chemins.PRIMITIVES))})
            continue
        entree = reg.get(nom)
        if entree is None:
            v.manquants.append({"asset": asset, "raison": "absent du registre", "utilise_par": ", ".join(ou)})
            continue
        fichier = chemins.RACINE / entree.get("fichier", "")
        if not fichier.is_file():
            v.manquants.append({"asset": asset, "raison": f"fichier introuvable ({entree.get('fichier')})",
                                "utilise_par": ", ".join(ou)})
            continue
        # Plusieurs entrées du registre peuvent partager un même fichier (variantes : animation,
        # dégâts) : "licence" désigne alors la ligne de licences.csv du fichier d'origine.
        ligne = lic.get(entree.get("licence") or nom)
        if ligne is None:
            v.manquants.append({"asset": asset, "raison": "licence non enregistrée dans licences.csv",
                                "utilise_par": ", ".join(ou)})
            continue
        if ligne.get("attribution_requise", "").strip().lower() in ("oui", "true", "1"):
            v.attributions.append(ligne.get("texte_attribution") or f"{nom} par {ligne.get('auteur')} ({ligne.get('licence')})")
    return v
