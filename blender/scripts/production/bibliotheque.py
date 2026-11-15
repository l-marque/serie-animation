"""Chargement des assets de bibliothèque ('bibliotheque:<id>') dans des collections prototypes.

Le registre blender/assets/registre.json décrit chaque asset :
    {
      "fichier": "blender/assets/modeles/phare_01.glb",   # .blend, .glb, .gltf ou .fbx
      "collection": "Phare",                              # pour les .blend uniquement
      "echelle": 1.0,                                     # facteur appliqué à l'import
      "role_defaut": "batiment",                          # rôle des pièces non listées
      "roles": {"Lanterne": "accent"},                    # rôle par nom d'objet (facultatif)
      "principal": "Corps"                                # pièce qui prend le rôle de la fiche
    }

ÉTAT : écrit mais non testé sur de vrais fichiers (aucun asset de bibliothèque pour l'instant).
"""

from __future__ import annotations

import json
from pathlib import Path

import bpy

from commun import journal


def charger_registre(racine: Path) -> dict:
    chemin = racine / "blender" / "assets" / "registre.json"
    return json.loads(chemin.read_text(encoding="utf-8")).get("assets", {}) if chemin.is_file() else {}


def _importer(fichier: Path, entree: dict) -> list[bpy.types.Object]:
    ext = fichier.suffix.lower()
    if ext == ".blend":
        with bpy.data.libraries.load(str(fichier), link=False) as (source, cible):
            cible.collections = [entree["collection"]]
        col = cible.collections[0]
        if col is None:
            raise RuntimeError(f"collection '{entree['collection']}' absente de {fichier}")
        return list(col.all_objects)
    avant = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(fichier))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(fichier))
    else:
        raise RuntimeError(f"format non pris en charge : {ext}")
    return [o for o in bpy.data.objects if o not in avant]


def pieces_bibliotheque(racine: Path, asset_id: str) -> list[tuple[bpy.types.Object, str, bool]]:
    """Importe un asset et renvoie [(objet, role, principal)] prêts à être rangés dans un prototype."""
    entree = charger_registre(racine).get(asset_id)
    if entree is None:
        raise RuntimeError(f"asset 'bibliotheque:{asset_id}' absent du registre")
    fichier = racine / entree["fichier"]
    objets = _importer(fichier, entree)
    echelle = float(entree.get("echelle", 1.0))
    roles = entree.get("roles", {})
    sortie = []
    for o in objets:
        for col in list(o.users_collection):
            col.objects.unlink(o)
        if o.parent is None:
            o.scale = [s * echelle for s in o.scale]
            o.location = [c * echelle for c in o.location]
        role = roles.get(o.name, entree.get("role_defaut", "accessoire"))
        sortie.append((o, role, o.name == entree.get("principal")))
    journal(f"asset bibliotheque:{asset_id} importé ({len(objets)} objet(s))")
    return sortie
