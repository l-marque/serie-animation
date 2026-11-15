"""Outils partagés par les modules Blender de l'agent Production.

Conventions de nommage (voir docs/conventions-blender.md) :
    PROTO_<asset>_<role>   collection prototype (jamais liée à la scène, seulement instanciée)
    EP_<id>                élément ou personnage de la fiche (empty qui instancie un prototype)
    MOD_<id>               racine d'un module procédural ; ses instances : MOD_<id>_<0000>
    CAM_<beat>             caméra d'un beat ; VISEE_<beat> : point visé par cette caméra
    MAT_<role>             matériau du pack de DA pour un rôle ; MAT_contour : contour cartoon
"""

from __future__ import annotations

import bpy

# Propriétés personnalisées posées sur les objets du pipeline.
PROP_ID = "prod_id"
PROP_CATEGORIE = "prod_categorie"
PROP_ECHELLE = "prod_echelle_base"


def fcurves(obj: bpy.types.Object, chemin: str) -> list:
    """F-curves d'un canal, compatible avec l'API des actions « en couches » (Blender 4.4+/5.x)
    et avec l'ancienne API (Action.fcurves)."""
    ad = obj.animation_data
    if ad is None or ad.action is None:
        return []
    action = ad.action
    if hasattr(action, "fcurves"):  # ancienne API
        courbes = action.fcurves
    else:
        from bpy_extras import anim_utils
        sac = anim_utils.animdata_get_channelbag_for_assigned_slot(ad)
        courbes = sac.fcurves if sac is not None else []
    return [f for f in courbes if f.data_path == chemin]


def cle(obj: bpy.types.Object, chemin: str, frame: int, interpolation: str = "BEZIER",
        assouplissement: str | None = None) -> None:
    """Insère une clé d'animation et règle l'interpolation du segment qui PART de cette clé.

    interpolation : CONSTANT, LINEAR, BEZIER, BACK, ELASTIC, SINE…
    assouplissement : EASE_IN, EASE_OUT, EASE_IN_OUT (défaut : EASE_OUT pour BACK/ELASTIC,
    ce qui donne l'effet « pop » avec léger dépassement).
    """
    obj.keyframe_insert(data_path=chemin, frame=frame)
    if assouplissement is None and interpolation in ("BACK", "ELASTIC", "BOUNCE"):
        assouplissement = "EASE_OUT"
    for f in fcurves(obj, chemin):
        for k in f.keyframe_points:
            if abs(k.co.x - frame) < 0.5:
                k.interpolation = interpolation
                if assouplissement:
                    k.easing = assouplissement


def nouvelle_collection(nom: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    col = bpy.data.collections.new(nom)
    if parent is not None:
        parent.children.link(col)
    return col


def lier(obj: bpy.types.Object, collection: bpy.types.Collection) -> bpy.types.Object:
    collection.objects.link(obj)
    return obj


def objets_par_id(scene: bpy.types.Scene) -> dict[str, bpy.types.Object]:
    """Identifiant de la fiche -> objet Blender (éléments, personnages, racines de modules)."""
    return {o[PROP_ID]: o for o in scene.objects if PROP_ID in o and o.get(PROP_CATEGORIE) != "instance"}


def instances_module(racine: bpy.types.Object) -> list[bpy.types.Object]:
    return sorted(racine.children, key=lambda o: o.name)


def journal(message: str) -> None:
    print(f"[production] {message}", flush=True)
