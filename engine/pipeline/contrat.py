"""Chargement et validation de la fiche épisode reçue des autres agents.

Versions acceptées : "1.0" et "1.1" (la v1.1 ajoute le champ `habillage` et la caméra
`descente` ; une fiche 1.0 se comporte exactement comme avant).

Deux niveaux de contrôle :
1. structure (JSON Schema, contracts/fiche-episode.schema.json) ;
2. cohérence (identifiants uniques, cibles existantes, pack de DA présent, actions compatibles).

Toutes les erreurs sont collectées puis renvoyées ensemble, avec un message actionnable,
pour que l'agent qui a envoyé la fiche puisse tout corriger en une seule fois.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from . import chemins, pack_da

VERSIONS_ACCEPTEES = ("1.0", "1.1")

# Actions qui ne s'appliquent qu'à un objet unique (pas à un module entier).
ACTIONS_OBJET_SEUL = frozenset({"deplacer", "tourner", "transformer", "cycle"})
CYCLES_CONNUS = frozenset({"flotter", "sautiller", "tourner_sur_soi", "osciller"})


class FicheInvalide(Exception):
    """Levée quand la fiche ne peut pas être produite. Contient la liste complète des erreurs."""

    def __init__(self, erreurs: list[str]):
        self.erreurs = erreurs
        super().__init__("Fiche épisode invalide :\n- " + "\n- ".join(erreurs))


@dataclass
class Fiche:
    """Fiche validée, valeurs par défaut appliquées."""

    donnees: dict[str, Any]
    source: Path | None = None
    avertissements: list[str] = field(default_factory=list)

    @property
    def episode_id(self) -> str:
        return self.donnees["episode_id"]


def _schema() -> dict[str, Any]:
    with chemins.SCHEMA_FICHE.open(encoding="utf-8") as f:
        return json.load(f)


def _appliquer_defauts(d: dict[str, Any]) -> dict[str, Any]:
    """Complète les champs facultatifs. Les valeurs reflètent les 'default' du schéma."""
    d = copy.deepcopy(d)
    fmt = d.setdefault("format", {})
    fmt.setdefault("resolution", [1080, 1920])
    fmt.setdefault("fps", 30)
    d.setdefault("titre", d["episode_id"])
    d.setdefault("pack_da", "test_lowpoly")
    decor = d.setdefault("decor", {})
    decor.setdefault("kit", "primitifs")
    decor.setdefault("sol", True)
    decor.setdefault("taille_sol", 40)
    d.setdefault("audio", {})
    d["audio"].setdefault("volume_musique", 0.25)
    for cle in ("elements", "personnages"):
        for o in d.setdefault(cle, []):
            o.setdefault("position", [0, 0, 0])
            if len(o["position"]) == 2:
                o["position"] = [*o["position"], 0]
            o.setdefault("rotation_z", 0)
            o.setdefault("echelle", 1)
            if cle == "personnages":
                o.setdefault("role", "personnage")  # pas de rôle par défaut pour un élément : celui de sa pièce s'applique
            o.setdefault("visible_au_debut", True)
    for m in d.setdefault("modules", []):
        m.setdefault("motif", "spirale")
        m.setdefault("centre", [0, 0, 0])
        if len(m["centre"]) == 2:
            m["centre"] = [*m["centre"], 0]
        m.setdefault("espacement", 1.6)
        m.setdefault("variation_echelle", [0.8, 1.1])
        m.setdefault("seed", 42)
        m.setdefault("rayon_interieur", 0)
        m.setdefault("visible_au_debut", True)
    for b in d["beats"]:
        b.setdefault("voix", "")
        b.setdefault("actions", [])
        for a in b["actions"]:
            a.setdefault("duree_s", 0.6)
            a.setdefault("params", {})
    return d


def _verifier_coherence(d: dict[str, Any]) -> tuple[list[str], list[str]]:
    erreurs: list[str] = []
    avert: list[str] = []

    # Identifiants uniques entre éléments, personnages et modules.
    vus: dict[str, str] = {}
    for cle in ("elements", "personnages", "modules"):
        for o in d[cle]:
            if o["id"] in vus:
                erreurs.append(f"identifiant '{o['id']}' utilisé deux fois ({vus[o['id']]} et {cle})")
            vus[o["id"]] = cle
    modules = {m["id"] for m in d["modules"]}

    ids_beats = [b["id"] for b in d["beats"]]
    if len(ids_beats) != len(set(ids_beats)):
        erreurs.append("deux beats ont le même identifiant")

    if d["decor"]["kit"] not in chemins.KITS_DECOR:
        erreurs.append(f"kit de décor inconnu '{d['decor']['kit']}' (disponibles : {sorted(chemins.KITS_DECOR)})")

    pack = chemins.PACKS_DA / f"{d['pack_da']}.json"
    if not pack.is_file():
        dispo = sorted(p.stem for p in chemins.PACKS_DA.glob("*.json"))
        erreurs.append(f"pack de DA '{d['pack_da']}' introuvable (disponibles : {dispo})")
    else:
        try:
            pack_da.charger(pack)
        except pack_da.PackInvalide as e:
            erreurs += [f"pack de DA '{d['pack_da']}' : {m}" for m in e.erreurs]
        except json.JSONDecodeError as e:
            erreurs.append(f"pack de DA '{d['pack_da']}' : JSON illisible ({e})")

    for b in d["beats"]:
        cible_plan = b["plan"].get("cible")
        if cible_plan and cible_plan not in vus:
            erreurs.append(f"beat {b['id']} : la caméra vise '{cible_plan}', qui n'existe pas")
        if not b["voix"].strip() and "duree_s" not in b:
            avert.append(f"beat {b['id']} : ni voix ni duree_s, durée par défaut de 2 s")
        for i, a in enumerate(b["actions"]):
            ref = f"beat {b['id']}, action {i + 1} ({a['type']})"
            if a["cible"] not in vus:
                erreurs.append(f"{ref} : cible '{a['cible']}' inexistante")
            elif a["cible"] in modules and a["type"] in ACTIONS_OBJET_SEUL:
                erreurs.append(f"{ref} : '{a['type']}' ne s'applique pas à un module entier ('{a['cible']}')")
            if "mot" in a and not b["voix"].strip():
                erreurs.append(f"{ref} : déclenchée sur le mot '{a['mot']}' mais le beat n'a pas de voix")
            if "mot" not in a and "debut" not in a:
                avert.append(f"{ref} : ni 'mot' ni 'debut', déclenchée au début du beat")
            p = a["params"]
            if a["type"] == "deplacer" and not ("vers" in p or "vers_cible" in p):
                erreurs.append(f"{ref} : params.vers [x, y, z] ou params.vers_cible requis")
            if a["type"] == "deplacer" and "vers_cible" in p and p["vers_cible"] not in vus:
                erreurs.append(f"{ref} : vers_cible '{p['vers_cible']}' inexistante")
            if a["type"] == "transformer":
                va = p.get("vers_asset", "")
                if not (isinstance(va, str) and (va.startswith("primitif:") or va.startswith("bibliotheque:"))):
                    erreurs.append(f"{ref} : params.vers_asset requis (ex. 'primitif:tour')")
            if a["type"] == "cycle" and p.get("nom") not in CYCLES_CONNUS:
                erreurs.append(f"{ref} : params.nom doit être l'un de {sorted(CYCLES_CONNUS)}")
    return erreurs, avert


def valider_donnees(donnees: dict[str, Any], source: Path | None = None) -> Fiche:
    """Valide un dictionnaire de fiche. Lève FicheInvalide avec toutes les erreurs."""
    validateur = Draft202012Validator(_schema())
    erreurs = []
    for e in sorted(validateur.iter_errors(donnees), key=lambda e: list(e.absolute_path)):
        chemin = "/".join(str(p) for p in e.absolute_path) or "(racine)"
        erreurs.append(f"{chemin} : {e.message}")
    if erreurs:
        raise FicheInvalide(erreurs)
    complete = _appliquer_defauts(donnees)
    erreurs, avert = _verifier_coherence(complete)
    if erreurs:
        raise FicheInvalide(erreurs)
    return Fiche(donnees=complete, source=source, avertissements=avert)


def charger(chemin: str | Path) -> Fiche:
    chemin = Path(chemin)
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FicheInvalide([f"fichier introuvable : {chemin}"]) from None
    except json.JSONDecodeError as e:
        raise FicheInvalide([f"JSON invalide ({chemin}, ligne {e.lineno}) : {e.msg}"]) from None
    return valider_donnees(donnees, source=chemin)
