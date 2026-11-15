"""Continuité de série : ce qui doit persister d'un épisode à l'autre.

Fichier : series/<serie_id>/etat.json. Il contient les éléments, personnages et modules
dans leur état de FIN du dernier épisode produit en mode final (position après les
déplacements, visibilité après les apparitions/disparitions, nombre d'instances).

À l'épisode suivant, si la fiche demande la continuité, ces objets sont repris.
Un objet redéclaré dans la nouvelle fiche (même id) remplace l'ancien : c'est ainsi que
l'on fait grandir un module (ex. 'village' passe de 40 à 55 maisons).
"""

from __future__ import annotations

import copy
import json
from datetime import date
from typing import Any

from . import chemins

CATEGORIES = ("elements", "personnages", "modules")


def chemin_etat(serie_id: str):
    return chemins.SERIES / serie_id / "etat.json"


def fusionner(fiche_donnees: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Ajoute à la fiche les objets persistants de la série. Renvoie (fiche, notes)."""
    serie = fiche_donnees.get("serie")
    if not serie or not serie.get("continuite"):
        return fiche_donnees, []
    chemin = chemin_etat(serie["id"])
    if not chemin.is_file():
        return fiche_donnees, [f"série '{serie['id']}' : aucun état précédent, premier épisode"]
    etat = json.loads(chemin.read_text(encoding="utf-8"))
    d = copy.deepcopy(fiche_donnees)
    notes = []
    for cat in CATEGORIES:
        declares = {o["id"] for o in d.get(cat, [])}
        repris = [o for o in etat.get(cat, []) if o["id"] not in declares]
        d[cat] = repris + d.get(cat, [])
        if repris:
            notes.append(f"{cat} repris de l'épisode {etat.get('dernier_episode')} : {[o['id'] for o in repris]}")
    return d, notes


def etat_final(timeline: dict[str, Any]) -> dict[str, Any]:
    """Calcule l'état de fin d'épisode à partir de la timeline."""
    objets = {o["id"]: copy.deepcopy(o) for o in timeline["objets"]}
    modules = {m["id"]: copy.deepcopy(m) for m in timeline["modules"]}
    actions = sorted((a for b in timeline["beats"] for a in b["actions"]), key=lambda a: a["t_debut_s"])
    for a in actions:
        cible = objets.get(a["cible"]) or modules.get(a["cible"])
        if cible is None:
            continue
        if a["type"] == "apparaitre":
            cible["visible_au_debut"] = True
        elif a["type"] == "disparaitre":
            cible["visible_au_debut"] = False
        elif a["type"] == "deplacer":
            p = a["params"]
            if "vers" in p:
                v = list(p["vers"])
                cible["position"] = v if len(v) == 3 else [*v, 0]
            elif p.get("vers_cible") in objets:
                cible["position"] = list(objets[p["vers_cible"]]["position"])
        elif a["type"] == "tourner":
            cible["rotation_z"] = (cible.get("rotation_z", 0) + a["params"].get("degres", 360)) % 360
        elif a["type"] == "grandir":
            cible["echelle"] = cible.get("echelle", 1) * a["params"].get("facteur", 1.5)
        elif a["type"] == "transformer":
            cible["asset"] = a["params"]["vers_asset"]
    elements = [o for o in objets.values() if o.get("categorie") == "element"]
    personnages = [o for o in objets.values() if o.get("categorie") == "personnage"]
    for o in elements + personnages:
        o.pop("categorie", None)
    return {
        "dernier_episode": timeline["episode_id"],
        "mis_a_jour": date.today().isoformat(),
        "elements": elements,
        "personnages": personnages,
        "modules": list(modules.values()),
    }


def enregistrer(serie_id: str, etat: dict[str, Any]) -> None:
    chemin = chemin_etat(serie_id)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(etat, ensure_ascii=False, indent=2), encoding="utf-8")
