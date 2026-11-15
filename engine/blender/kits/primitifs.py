"""Kit de décor « primitifs » : assets low-poly générés par code (aucun fichier externe).

Chaque fonction construit les pièces d'un asset, posé au sol (z = 0), centré en (0, 0),
d'environ 1 m de large. Chaque pièce porte un rôle (sol, batiment, toit…) qui décide de
sa couleur via le pack de DA. Une seule pièce par asset est « principale » : c'est elle qui
prend le rôle demandé dans la fiche (ex. un phare en rôle 'accent').

Si tu ajoutes une primitive, ajoute aussi son nom dans engine/pipeline/chemins.py
(PRIMITIVES) : un test vérifie que les deux listes concordent.
"""

from __future__ import annotations

import math
import random

import bmesh
import bpy

Piece = tuple[str, bpy.types.Mesh, tuple[float, float, float], float, str, bool]
# (nom, maillage, position, rotation_z_rad, role, principale)


def _maillage(nom: str, construire) -> bpy.types.Mesh:
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    construire(bm)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:  # facettes visibles : look low-poly
        p.use_smooth = False
    return me


def _cube(taille: float):
    return lambda bm: bmesh.ops.create_cube(bm, size=taille)


def _cone(segments: int, r1: float, r2: float, hauteur: float):
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2, depth=hauteur)


def _sphere(subdiv: int, rayon: float):
    return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=rayon)


def maison(seed: int) -> list[Piece]:
    return [
        ("mur", _maillage("mur", _cube(1.0)), (0, 0, 0.5), 0.0, "batiment", True),
        ("toit", _maillage("toit", _cone(4, 0.85, 0.0, 0.7)), (0, 0, 1.35), math.radians(45), "toit", False),
    ]


def tour(seed: int) -> list[Piece]:
    return [
        ("corps", _maillage("corps", _cone(8, 0.7, 0.45, 4.0)), (0, 0, 2.0), 0.0, "batiment", True),
        ("lanterne", _maillage("lanterne", _cone(8, 0.5, 0.5, 0.6)), (0, 0, 4.3), 0.0, "accent", False),
        ("chapeau", _maillage("chapeau", _cone(8, 0.65, 0.0, 0.5)), (0, 0, 4.85), 0.0, "toit", False),
    ]


def arbre(seed: int) -> list[Piece]:
    return [
        ("tronc", _maillage("tronc", _cone(6, 0.12, 0.1, 0.8)), (0, 0, 0.4), 0.0, "accessoire", False),
        ("feuillage", _maillage("feuillage", _cone(6, 0.7, 0.0, 1.6)), (0, 0, 1.6), 0.0, "vegetation", True),
    ]


def rocher(seed: int) -> list[Piece]:
    rng = random.Random(seed)

    def construire(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.6)
        for v in bm.verts:
            v.co *= 0.8 + 0.35 * rng.random()
            v.co.z *= 0.7

    return [("roche", _maillage("roche", construire), (0, 0, 0.3), 0.0, "roche", True)]


def personnage(seed: int) -> list[Piece]:
    return [
        ("corps", _maillage("corps", _cone(8, 0.3, 0.24, 0.9)), (0, 0, 0.45), 0.0, "personnage", True),
        ("tete", _maillage("tete", _sphere(2, 0.25)), (0, 0, 1.15), 0.0, "personnage", False),
    ]


def caisse(seed: int) -> list[Piece]:
    return [("caisse", _maillage("caisse", _cube(0.8)), (0, 0, 0.4), 0.0, "accessoire", True)]


def lampadaire(seed: int) -> list[Piece]:
    return [
        ("poteau", _maillage("poteau", _cone(6, 0.05, 0.05, 2.2)), (0, 0, 1.1), 0.0, "accessoire", True),
        ("lampe", _maillage("lampe", _sphere(1, 0.15)), (0, 0, 2.3), 0.0, "accent", False),
    ]


PRIMITIVES = {
    "maison": maison,
    "tour": tour,
    "arbre": arbre,
    "rocher": rocher,
    "personnage": personnage,
    "caisse": caisse,
    "lampadaire": lampadaire,
}


def sol(taille: float) -> bpy.types.Mesh:
    return _maillage("sol", lambda bm: bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=taille / 2))
