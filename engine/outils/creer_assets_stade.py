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


def pelouse_abimee():
    """Terrain de 20 × 12 m en herbe abîmée : plaques de terre, lignes à moitié effacées (épisode Jour 1)."""
    vider()
    herbe = materiau("Herbe_abimee", (0.16, 0.58, 0.08), 0.95)
    terre = materiau("Terre_plaque", (0.62, 0.36, 0.12), 0.95)
    blanc = materiau("Ligne_blanche", (0.85, 0.84, 0.80), 0.8)
    boite("herbe", 0, 0, 20.0, 12.0, 0.02, herbe)
    random.seed(21)
    for i in range(16):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=1.0, depth=0.006,
                                            location=(random.uniform(-9, 9), random.uniform(-5.2, 5.2), 0.022))
        o = bpy.context.object
        o.name = f"plaque_{i}"
        o.scale = (random.uniform(0.5, 1.8), random.uniform(0.4, 1.2), 1)
        o.rotation_euler[2] = random.uniform(0, math.pi)
        o.data.materials.append(terre)
    # surface de but usée devant chaque cage
    for x in (-8.6, 8.6):
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.0, depth=0.006, location=(x, 0, 0.022))
        o = bpy.context.object
        o.scale = (1.4, 2.6, 1)
        o.data.materials.append(terre)
    larg, ep, z = 0.12, 0.004, 0.026
    segments = [(-6.5, 5.9, 6.0, larg), (4.5, 5.9, 7.0, larg), (-3.0, -5.9, 9.0, larg), (7.5, -5.9, 3.5, larg),
                (-9.9, -2.0, larg, 6.0), (9.9, 1.5, larg, 7.0), (0, 3.6, larg, 4.0), (0, -4.2, larg, 3.0)]
    for i, (cx, cy, lx, ly) in enumerate(segments):
        o = boite(f"ligne_{i}", cx, cy, lx, ly, ep, blanc)
        o.location.z = z
    n = 28
    for i in range(n):
        if i % 4 == 2:
            continue
        a = 2 * math.pi * i / n
        o = boite(f"rond_{i}", 1.8 * math.cos(a), 1.8 * math.sin(a), larg, 2 * math.pi * 1.8 / n * 0.95, ep, blanc, rot=a)
        o.location.z = z
    exporter(SORTIE / "terrain_pelouse_abimee" / "terrain_pelouse_abimee.glb")


def cage_rouillee():
    """Cage de 4 × 2 m sans filet, tubes rouillés ; ouverture face à -x, profondeur vers +x."""
    vider()
    rouille = materiau("Rouille", (0.62, 0.24, 0.05), 0.75)
    r, l, h, p = 0.06, 4.0, 2.0, 1.2

    def tube(nom, a, b):
        ax, ay, az = a
        bx, by, bz = b
        lg = math.dist(a, b)
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=r, depth=lg,
                                            location=((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2))
        o = bpy.context.object
        o.name = nom
        d = (bx - ax, by - ay, bz - az)
        o.rotation_mode = "QUATERNION"
        o.rotation_quaternion = __import__("mathutils").Vector((0, 0, 1)).rotation_difference(__import__("mathutils").Vector(d))
        o.data.materials.append(rouille)

    tube("poteau_g", (0, -l / 2, 0), (0, -l / 2, h))
    tube("poteau_d", (0, l / 2, 0), (0, l / 2, h))
    tube("barre", (0, -l / 2, h), (0, l / 2, h - 0.12))  # barre légèrement tordue
    tube("arriere_g", (0, -l / 2, h), (p, -l / 2, 0))
    tube("arriere_d", (0, l / 2, h - 0.12), (p, l / 2, 0))
    tube("sol_arriere", (p, -l / 2, 0.05), (p, l / 2, 0.05))
    exporter(SORTIE / "cage_rouillee" / "cage_rouillee.glb")


def route():
    """Route droite de 120 × 7 m (enrobé, pointillés) avec deux trottoirs, le long de x."""
    vider()
    enrobe = materiau("Enrobe", (0.06, 0.06, 0.065), 0.9)
    trottoir = materiau("Trottoir", (0.45, 0.44, 0.42), 0.9)
    blanc = materiau("Marquage", (0.9, 0.9, 0.85), 0.7)
    boite("enrobe", 0, 0, 120, 7, 0.03, enrobe)
    boite("trottoir_n", 0, 4.25, 120, 1.5, 0.12, trottoir)
    boite("trottoir_s", 0, -4.25, 120, 1.5, 0.12, trottoir)
    for i in range(30):
        o = boite(f"pointille_{i}", -58 + i * 4, 0, 2.0, 0.15, 0.004, blanc)
        o.location.z = 0.032
    exporter(SORTIE / "route" / "route.glb")


terrain()
touffe()
pelouse_abimee()
cage_rouillee()
route()
print("ASSETS_STADE_OK")
