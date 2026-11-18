"""Atelier de modélisation : briques pour construire des modèles propres en Python dans Blender.

Ces fonctions s'importent depuis un script de modèle (voir modeles/*.py) exécuté par Blender :

    blender --background --factory-startup --python engine/outils/atelier/modeles/cage_filet.py

Principes (repris de ref-stylized-style et ref-lowpoly-style) : silhouettes lisibles, bords biseautés
qui accrochent la lumière, ombrage lisse sur les formes rondes, palette courte, pas de micro-détail.
Toutes les longueurs sont en mètres ; un modèle posé au sol a sa base à z = 0 et regarde vers -y.
"""
from __future__ import annotations

import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

RACINE = Path(__file__).resolve().parents[3]
MODELES = RACINE / "engine" / "assets" / "modeles"


# ----- scène et matériaux ------------------------------------------------------------------------
def vider() -> None:
    bpy.ops.wm.read_factory_settings(use_empty=True)


def materiau(nom: str, couleur, rugosite: float = 0.8, metal: float = 0.0, emission: float = 0.0):
    """Matériau Principled simple (exporté tel quel en glTF)."""
    m = bpy.data.materials.get(nom) or bpy.data.materials.new(nom)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*couleur[:3], 1.0)
    bsdf.inputs["Roughness"].default_value = rugosite
    bsdf.inputs["Metallic"].default_value = metal
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*couleur[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    m.diffuse_color = (*couleur[:3], 1.0)
    return m


def _finir(o, mat, lisse: bool, nom: str):
    o.name = nom
    if mat is not None:
        o.data.materials.append(mat)
    if lisse:
        for p in o.data.polygons:
            p.use_smooth = True
    return o


# ----- formes de base ----------------------------------------------------------------------------
def boite(nom, centre, taille, mat=None, biseau: float = 0.0, segments: int = 2, rotation=(0, 0, 0)):
    """Boîte aux bords biseautés (biseau en mètres) : les arêtes vives d'un cube nu font « primitive »."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre, rotation=rotation)
    o = bpy.context.object
    o.scale = taille
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if biseau > 0:
        mod = o.modifiers.new("Biseau", "BEVEL")
        mod.width = biseau
        mod.segments = segments
        mod.limit_method = "ANGLE"
        appliquer(o)
    return _finir(o, mat, lisse=biseau > 0, nom=nom)


def tube(nom, a, b, rayon: float, mat=None, cotes: int = 12, bouts_ronds: bool = False):
    """Cylindre de a à b. bouts_ronds : ajoute une sphère à chaque bout (raccords de tubes propres)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(vertices=cotes, radius=rayon, depth=d.length, location=(a + b) / 2)
    o = bpy.context.object
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    pieces = [o]
    if bouts_ronds:
        for p in (a, b):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=cotes, ring_count=cotes // 2, radius=rayon, location=p)
            pieces.append(bpy.context.object)
    o = fusionner(pieces, nom)
    return _finir(o, mat, lisse=True, nom=nom)


def tube_courbe(nom, points, rayon: float, mat=None, cotes: int = 10, resolution: int = 8):
    """Tube lisse qui passe par une liste de points (courbe de Bézier automatique) : tuyaux, cordes, rambardes."""
    cu = bpy.data.curves.new(nom, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = resolution
    cu.bevel_depth = rayon
    cu.bevel_resolution = max(1, cotes // 4)
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(points) - 1)
    for bp, p in zip(sp.bezier_points, points):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    o = bpy.data.objects.new(nom, cu)
    bpy.context.scene.collection.objects.link(o)
    o = convertir_en_maillage(o)
    return _finir(o, mat, lisse=True, nom=nom)


def revolution(nom, profil, mat=None, cotes: int = 24, centre=(0, 0, 0)):
    """Solide de révolution autour de z à partir d'un profil [(rayon, z), ...] : vases, poteaux, têtes, ballons."""
    bm = bmesh.new()
    anneaux = []
    for r, z in profil:
        anneau = []
        for i in range(cotes):
            a = 2 * math.pi * i / cotes
            anneau.append(bm.verts.new((centre[0] + r * math.cos(a), centre[1] + r * math.sin(a), centre[2] + z)))
        anneaux.append(anneau)
    for r1, r2 in zip(anneaux, anneaux[1:]):
        for i in range(cotes):
            j = (i + 1) % cotes
            bm.faces.new((r1[i], r1[j], r2[j], r2[i]))
    for anneau, inverse in ((anneaux[0], True), (anneaux[-1], False)):
        if profil[0 if inverse else -1][0] > 1e-6:
            bm.faces.new(list(reversed(anneau)) if inverse else anneau)
    me = bpy.data.meshes.new(nom)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    return _finir(o, mat, lisse=True, nom=nom)


def organique(nom, noeuds, aretes, mat=None, subdivision: int = 2):
    """Forme organique (corps, membres, branches, nuages) avec le modificateur Skin.

    noeuds : [(x, y, z, rayon), ...] ; aretes : [(i, j), ...]. Le Skin habille ce squelette de points,
    la subdivision arrondit. C'est la base pour un personnage modélisé de zéro."""
    me = bpy.data.meshes.new(nom)
    me.from_pydata([n[:3] for n in noeuds], aretes, [])
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("Skin", "SKIN")
    for v, n in zip(o.data.skin_vertices[0].data, noeuds):
        v.radius = (n[3], n[3])
    o.data.skin_vertices[0].data[0].use_root = True
    sub = o.modifiers.new("Subdiv", "SUBSURF")
    sub.levels = sub.render_levels = subdivision
    appliquer(o)
    return _finir(o, mat, lisse=True, nom=nom)


def filet(nom, coins, n_u: int, n_v: int, rayon: float, mat=None, affaissement: float = 0.0, normale=(0, 0, 0)):
    """Filet (grille de cordes) tendu entre 4 coins [a, b, c, d] (a→b = sens u, a→d = sens v).

    affaissement : creux maximal au centre (m), dans la direction `normale` ; parabole en u et v,
    nulle sur les bords. Les cordes sont des maillages (pas des courbes) : export glTF sûr."""
    a, b, c, d = (Vector(p) for p in coins)
    n = Vector(normale)

    def point(u, v):
        p = a.lerp(b, u).lerp(d.lerp(c, u), v)
        return p + n * affaissement * 4 * u * (1 - u) * 4 * v * (1 - v)

    pieces = []
    for i in range(n_u + 1):
        u = i / n_u
        pieces.append(_polyligne([point(u, k / 16) for k in range(17)], rayon))
    for j in range(n_v + 1):
        v = j / n_v
        pieces.append(_polyligne([point(k / 16, v) for k in range(17)], rayon))
    o = fusionner(pieces, nom)
    return _finir(o, mat, lisse=True, nom=nom)


def _polyligne(points, rayon: float, cotes: int = 4):
    cu = bpy.data.curves.new("_corde", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = rayon
    cu.bevel_resolution = 0
    sp = cu.splines.new("POLY")
    sp.points.add(len(points) - 1)
    for sp_p, p in zip(sp.points, points):
        sp_p.co = (*p, 1.0)
    o = bpy.data.objects.new("_corde", cu)
    bpy.context.scene.collection.objects.link(o)
    return convertir_en_maillage(o)


# ----- opérations --------------------------------------------------------------------------------
def selectionner(objets):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objets:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objets[0]


def appliquer(o):
    """Applique tous les modificateurs de l'objet."""
    selectionner([o])
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)
    return o


def convertir_en_maillage(o):
    selectionner([o])
    bpy.ops.object.convert(target="MESH")
    return bpy.context.object


def fusionner(objets, nom: str):
    """Réunit plusieurs objets en un seul maillage (moins d'objets = scène plus légère)."""
    objets = [o for o in objets if o is not None]
    for o in objets:
        if o.type != "MESH":
            convertir_en_maillage(o)
    selectionner(objets)
    if len(objets) > 1:
        bpy.ops.object.join()
    o = bpy.context.object
    o.name = nom
    return o


def miroir_x(o):
    """Symétrie gauche-droite (personnages, véhicules) : on modélise le côté +x seulement."""
    mod = o.modifiers.new("Miroir", "MIRROR")
    mod.use_axis = (True, False, False)
    mod.use_clip = True
    return appliquer(o)


def usure(o, force: float = 0.02, graine: int = 1):
    """Déforme légèrement les sommets (bruit) : casse le côté « trop parfait » d'un objet abîmé."""
    tex = bpy.data.textures.new(f"usure_{o.name}", "CLOUDS")
    tex.noise_scale = 0.4
    mod = o.modifiers.new("Usure", "DISPLACE")
    mod.texture = tex
    mod.strength = force
    mod.mid_level = 0.5
    bpy.context.scene.frame_set(graine)
    return appliquer(o)


# ----- export ------------------------------------------------------------------------------------
def exporter(asset_id: str) -> Path:
    """Exporte toute la scène en engine/assets/modeles/<asset_id>/<asset_id>.glb et renvoie le chemin."""
    chemin = MODELES / asset_id / f"{asset_id}.glb"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", use_selection=False, export_apply=True)
    n_tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
    print(f"MODELE_EXPORTE {asset_id} : {chemin} ({n_tri} triangles)")
    return chemin
