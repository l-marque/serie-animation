"""Formes de base partagées par les kits de décor (maillages bmesh, rendu à facettes).

Chaque fonction de construction reçoit un bmesh vide et le remplit. `maillage(nom, construire)`
transforme le bmesh en maillage Blender. Les primitives d'un kit renvoient des « pièces » :
(nom, maillage, position, rotation_z_rad, role, principale).
"""

from __future__ import annotations

import math
from typing import Callable

import bmesh
import bpy
from mathutils import Matrix, Vector

Piece = tuple[str, bpy.types.Mesh, tuple[float, float, float], float, str, bool]
Construction = Callable[[bmesh.types.BMesh], None]


def maillage(nom: str, construire: Construction, lisse: bool = False) -> bpy.types.Mesh:
    me = bpy.data.meshes.new(nom)
    bm = bmesh.new()
    construire(bm)
    bm.to_mesh(me)
    bm.free()
    for p in me.polygons:  # facettes visibles par défaut : look low-poly
        p.use_smooth = lisse
    return me


def cube(taille: float) -> Construction:
    return lambda bm: bmesh.ops.create_cube(bm, size=taille)


def boite(sx: float, sy: float, sz: float, biseau: float = 0.0) -> Construction:
    """Pavé sx × sy × sz centré sur l'origine, arêtes biseautées si `biseau` > 0."""
    def construire(bm):
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
        if biseau > 0:
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=biseau, segments=2, affect="EDGES", profile=0.5)
    return construire


def cone(segments: int, r1: float, r2: float, hauteur: float) -> Construction:
    return lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=r1, radius2=r2,
                                            depth=hauteur)


def sphere(subdiv: int, rayon: float) -> Construction:
    return lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=rayon)


def deformer(construire: Construction, fonction: Callable[[Vector], None]) -> Construction:
    """Applique `fonction(co)` à chaque sommet après construction (écrasement, irrégularités…)."""
    def nouvelle(bm):
        construire(bm)
        for v in bm.verts:
            fonction(v.co)
    return nouvelle


def tourner(construire: Construction, angle_deg: float, axe: str) -> Construction:
    """Tourne la forme autour de l'origine (axe 'X', 'Y' ou 'Z')."""
    def nouvelle(bm):
        construire(bm)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(angle_deg), 3, axe))
    return nouvelle


def assembler(*formes: tuple[Construction, tuple[float, float, float]]) -> Construction:
    """Réunit plusieurs formes décalées dans un seul maillage (moins d'objets, même matériau)."""
    def construire(bm):
        for forme, decalage in formes:
            tmp = bmesh.new()
            forme(tmp)
            bmesh.ops.translate(tmp, vec=decalage, verts=tmp.verts)
            me = bpy.data.meshes.new("_tmp")
            tmp.to_mesh(me)
            tmp.free()
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
    return construire
