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


def canard(seed: int) -> list[Piece]:
    """Canard en plastique stylisé (≈ 0,4 m de long), tourné vers +x."""
    def corps(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.18)
        for v in bm.verts:
            v.co.x *= 1.25
            v.co.z *= 0.75
            if v.co.x < -0.1 and v.co.z > 0:  # petite queue relevée
                v.co.z += 0.05

    def bec(bm):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.05, radius2=0.0, depth=0.1)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.radians(-90), 3, "Y"))

    return [
        ("corps", _maillage("corps", corps), (0, 0, 0.13), 0.0, "personnage", True),
        ("tete", _maillage("tete", _sphere(2, 0.11)), (0.13, 0, 0.3), 0.0, "personnage", False),
        ("bec", _maillage("bec", bec), (0.27, 0, 0.29), 0.0, "accent", False),
    ]


def baignoire(seed: int) -> list[Piece]:
    """Baignoire creuse aux bords arrondis (2,4 × 1,2 × 0,7 m), ouverte sur le dessus, sur 4 pieds."""
    def cuve(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(2.4, 1.2, 0.7), verts=bm.verts)
        haut = [f for f in bm.faces if f.normal.z > 0.9]
        bmesh.ops.inset_region(bm, faces=haut, thickness=0.09, depth=0.0)
        bmesh.ops.translate(bm, vec=(0, 0, -0.55), verts=list({v for f in haut for v in f.verts}))
        # fond intérieur rétréci : parois inclinées, comme une vraie baignoire
        bmesh.ops.scale(bm, vec=(0.9, 0.85, 1.0), verts=list({v for f in haut for v in f.verts}))
        aretes = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > 0.5]
        bmesh.ops.bevel(bm, geom=aretes, offset=0.05, segments=3, affect="EDGES", profile=0.5)

    def pied(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.09)
        for v in bm.verts:
            v.co.z *= 0.8

    return [("cuve", _maillage("cuve", cuve), (0, 0, 0.42), 0.0, "batiment", True)] + [
        (f"pied{i}", _maillage(f"pied{i}", pied), (x, y, 0.06), 0.0, "accessoire", False)
        for i, (x, y) in enumerate([(-0.95, -0.42), (0.95, -0.42), (-0.95, 0.42), (0.95, 0.42)])
    ]


def flaque(seed: int) -> list[Piece]:
    """Flaque d'eau irrégulière (≈ 1 m), à poser au sol ; animée avec « grandir » pour un débordement."""
    rng = random.Random(seed)

    def disque(bm):
        n = 24
        centre = bm.verts.new((0, 0, 0))
        bord = [bm.verts.new((0.5 * (0.75 + 0.35 * rng.random()) * math.cos(2 * math.pi * i / n),
                              0.5 * (0.75 + 0.35 * rng.random()) * math.sin(2 * math.pi * i / n), 0)) for i in range(n)]
        for i in range(n):
            bm.faces.new((centre, bord[i], bord[(i + 1) % n]))

    return [("flaque", _maillage("flaque", disque), (0, 0, 0.004), 0.0, "eau", True)]


def eau(seed: int) -> list[Piece]:
    """Surface d'eau plane et immobile (2,2 × 1,0 m), à poser dans la baignoire (z ≈ 0,45)."""
    def plan(bm):
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        bmesh.ops.scale(bm, vec=(2.2, 1.0, 1.0), verts=bm.verts)

    return [("eau", _maillage("eau", plan), (0, 0, 0.0), 0.0, "eau", True)]


def donut(seed: int) -> list[Piece]:
    """Donut (≈ 0,5 m) : tore de pâte + glaçage."""
    def tore(r_grand: float, r_petit: float, demi: bool):
        def construire(bm):
            n1, n2 = 16, 8
            anneaux = []
            for i in range(n1):
                a = 2 * math.pi * i / n1
                anneau = []
                for j in range(n2 + (1 if demi else 0)):
                    b = (math.pi * j / n2) if demi else (2 * math.pi * j / n2)
                    r = r_grand + r_petit * math.cos(b)
                    anneau.append(bm.verts.new((r * math.cos(a), r * math.sin(a), r_petit * math.sin(b))))
                anneaux.append(anneau)
            m = len(anneaux[0])
            for i in range(n1):
                for j in range(m if not demi else m - 1):
                    a, b = anneaux[i], anneaux[(i + 1) % n1]
                    bm.faces.new((a[j], b[j], b[(j + 1) % m], a[(j + 1) % m]))
        return construire

    return [
        ("pate", _maillage("pate", tore(0.18, 0.09, False)), (0, 0, 0.09), 0.0, "accessoire", True),
        ("glacage", _maillage("glacage", tore(0.18, 0.095, True)), (0, 0, 0.095), 0.0, "accent", False),
    ]


def ballon(seed: int) -> list[Piece]:
    """Ballon de baudruche (≈ 0,5 m) au bout d'une ficelle."""
    def enveloppe(bm):
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.25)
        for v in bm.verts:
            v.co.z *= 1.15

    return [
        ("enveloppe", _maillage("enveloppe", enveloppe), (0, 0, 0.95), 0.0, "accent", True),
        ("ficelle", _maillage("ficelle", _cone(4, 0.008, 0.008, 0.65)), (0, 0, 0.33), 0.0, "accessoire", False),
    ]


PRIMITIVES = {
    "maison": maison,
    "tour": tour,
    "arbre": arbre,
    "rocher": rocher,
    "personnage": personnage,
    "caisse": caisse,
    "lampadaire": lampadaire,
    "canard": canard,
    "baignoire": baignoire,
    "eau": eau,
    "flaque": flaque,
    "donut": donut,
    "ballon": ballon,
}


def sol(taille: float) -> bpy.types.Mesh:
    return _maillage("sol", lambda bm: bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=taille / 2))
