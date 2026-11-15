"""Validation d'un pack de direction artistique (blender/packs_da/<nom>.json).

Deux niveaux, comme pour la fiche épisode :
1. structure : schemas/pack_da.schema.json ;
2. lisibilité : les rôles qui doivent se détacher (personnage, accent) se distinguent du sol et
   du fond, et le nom du pack correspond au nom du fichier.

Usage : python -m scripts.production.pack_da blender/packs_da/mon_pack.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

from . import chemins

SCHEMA_PACK = chemins.RACINE / "schemas" / "pack_da.schema.json"
# Écart perceptuel minimal (distance dans l'espace Oklab) entre deux couleurs qui doivent se
# distinguer à l'image. 0.02 ≈ à peine visible ; 0.10 = nettement différent même en petit sur mobile.
ECART_MIN = 0.10
PAIRES_A_DISTINGUER = [("personnage", "sol"), ("accent", "sol"), ("batiment", "sol"), ("toit", "batiment")]


class PackInvalide(Exception):
    def __init__(self, erreurs: list[str]):
        super().__init__("\n".join(erreurs))
        self.erreurs = erreurs


def oklab(rgb: list[float]) -> tuple[float, float, float]:
    """Couleur RVB linéaire (convention Blender) vers Oklab (Björn Ottosson, 2020)."""
    r, g, b = rgb
    l_ = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m_ = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s_ = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
            1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
            0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_)


def ecart(a: list[float], b: list[float]) -> float:
    """Distance perceptuelle entre deux couleurs (teinte, saturation et luminosité confondues)."""
    return sum((x - y) ** 2 for x, y in zip(oklab(a), oklab(b))) ** 0.5


def valider(donnees: dict, nom_fichier: str | None = None) -> list[str]:
    """Renvoie la liste des avertissements de lisibilité ; lève PackInvalide si la structure est fausse."""
    validateur = jsonschema.Draft202012Validator(json.loads(SCHEMA_PACK.read_text(encoding="utf-8")))
    erreurs = [f"{'/'.join(map(str, e.path)) or '(racine)'} : {e.message}" for e in validateur.iter_errors(donnees)]
    if nom_fichier and donnees.get("nom") != nom_fichier:
        erreurs.append(f"nom '{donnees.get('nom')}' différent du nom de fichier '{nom_fichier}'")
    if erreurs:
        raise PackInvalide(erreurs)
    m = donnees["materiaux"]
    avertissements = []
    for a, b in PAIRES_A_DISTINGUER:
        e = ecart(m[a]["couleur"], m[b]["couleur"])
        if e < ECART_MIN:
            avertissements.append(f"{a} et {b} peu distincts (écart {e:.3f} < {ECART_MIN})")
    e = ecart(m["personnage"]["couleur"], donnees["monde"]["couleur"])
    if e < ECART_MIN:
        avertissements.append(f"personnage peu distinct du ciel (écart {e:.3f} < {ECART_MIN})")
    return avertissements


def charger(chemin: Path) -> tuple[dict, list[str]]:
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    return donnees, valider(donnees, chemin.stem)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        print("usage : python -m scripts.production.pack_da <pack.json>")
        return 2
    try:
        _, avertissements = charger(Path(args[0]))
    except PackInvalide as e:
        print(json.dumps({"valide": False, "erreurs": e.erreurs}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps({"valide": True, "avertissements": avertissements}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
