"""Crée les assets du stade qui n'existent dans aucune banque libre : terrain_miteux et touffe_herbe.

Lancement (depuis la racine du dépôt) :
    blender --background --factory-startup --python engine/outils/creer_assets_stade.py

Sorties :
    engine/assets/modeles/terrain_miteux/terrain_miteux.glb  (terre sèche 20 × 12 m, lignes à moitié effacées)
    engine/assets/modeles/touffe_herbe/touffe_herbe.glb      (une touffe verte d'environ 0,35 m)
Les deux sont des créations du projet (pas de licence tierce).
"""
import math
import random
from pathlib import Path

import bpy

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "engine" / "assets" / "modeles"


def vider():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def materiau(nom, couleur, rugosite=0.9):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*couleur, 1.0)
    bsdf.inputs["Roughness"].default_value = rugosite
    return m


def boite(nom, cx, cy, lx, ly, ep, mat, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, ep / 2))
    o = bpy.context.object
    o.name = nom
    o.scale = (lx, ly, ep)
    o.rotation_euler[2] = rot
    o.data.materials.append(mat)
    return o


def exporter(chemin: Path):
    chemin.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", use_selection=False, export_apply=True)


def terrain():
    vider()
    terre = materiau("Terre_seche", (0.55, 0.36, 0.17), 0.95)
    blanc = materiau("Ligne_blanche", (0.85, 0.84, 0.80), 0.8)
    L, l, ep, larg = 20.0, 12.0, 0.004, 0.12
    boite("terre", 0, 0, L, l, 0.02, terre)
    z = 0.02  # les lignes sont posées sur la terre
    segments = []
    # lignes de touche (y = ±6) et de but (x = ±10), effacées sur environ la moitié de leur longueur
    segments += [(-7.5, 5.9, 5.0, larg), (3.0, 5.9, 4.0, larg), (8.0, 5.9, 2.0, larg)]
    segments += [(-4.0, -5.9, 6.0, larg), (6.5, -5.9, 3.0, larg)]
    segments += [(-9.9, 2.5, larg, 4.0), (9.9, -1.5, larg, 5.0)]
    # ligne médiane, coupée au milieu
    segments += [(0, 4.2, larg, 3.4), (0, -3.6, larg, 2.6)]
    for i, (cx, cy, lx, ly) in enumerate(segments):
        o = boite(f"ligne_{i}", cx, cy, lx, ly, ep, blanc)
        o.location.z = z
    # rond central (rayon 1,8 m) : 60 % des tronçons seulement
    random.seed(4)
    n = 28
    for i in range(n):
        if i % 5 in (1, 3) or random.random() < 0.15:
            continue
        a = 2 * math.pi * i / n
        r = 1.8
        o = boite(f"rond_{i}", r * math.cos(a), r * math.sin(a), larg, 2 * math.pi * r / n * 0.95, ep, blanc, rot=a)
        o.location.z = z
    exporter(SORTIE / "terrain_miteux" / "terrain_miteux.glb")


def touffe():
    vider()
    vert = materiau("Herbe_verte", (0.20, 0.55, 0.15), 0.85)
    random.seed(11)
    for i in range(9):
        a = 2 * math.pi * i / 9 + random.uniform(-0.2, 0.2)
        d = random.uniform(0.02, 0.08)
        h = random.uniform(0.22, 0.38)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.035, depth=h,
                                        location=(d * math.cos(a), d * math.sin(a), h / 2))
        o = bpy.context.object
        o.rotation_euler = (random.uniform(-0.35, 0.35), random.uniform(-0.35, 0.35), a)
        o.data.materials.append(vert)
    exporter(SORTIE / "touffe_herbe" / "touffe_herbe.glb")


terrain()
touffe()
print("ASSETS_STADE_OK")
