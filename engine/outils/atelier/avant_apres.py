"""Avant / après d'un décor : mêmes plans de caméra sur deux .blend (collection « Stade » par défaut).

    blender --background --factory-startup --python engine/outils/atelier/avant_apres.py -- \
        <avant.blend> <apres.blend> <dossier_sortie> [decalage_y]

Rend chaque plan de PLANS (mêmes mouvements de caméra que engine/blender/camera.py, image prise au
milieu du mouvement, focale 35 mm, 9:16) avec la lumière du pack stade_bloc, puis assemble pour chaque
plan une planche « avant | après » (<dossier>/avant_apres_<plan>.png). decalage_y : position du décor
dans l'épisode (jour-1 : le stade est posé en (0 ; 0,6 ; 0)).
"""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

R = Path(__file__).resolve().parents[3]
args = sys.argv[sys.argv.index("--") + 1:]
avant, apres, dossier = Path(args[0]), Path(args[1]), Path(args[2])
DY = float(args[3]) if len(args) > 3 else 0.6
dossier.mkdir(parents=True, exist_ok=True)
pack = json.loads((R / "engine/packs_da/stade_bloc.json").read_text(encoding="utf-8"))
L, H = 540, 960

# (nom, mouvement, cible (coordonnées épisode), distance, hauteur) : plans des fiches jour-1 / jour-2.
PLANS = [
    ("b12_boue", "travelling_lateral", (18, 3, 0), 6, 1.3),        # jour-1 b12 = jour-2 b02
    ("b01_kevin", "plan_fixe", (30, 0, 0), 6, 1.5),                 # jour-2 b01
    ("b06_cage", "travelling_lateral", (51.3, 0, 1.2), 8, 1),       # jour-2 b06 a
    ("ensemble", "plan_fixe", (0, 0, 0), 62, 30),                   # vue d'ensemble
    ("b02b_terrain", "revelation", (41, -0.6, 0), 42, 20),          # jour-1 b02b (fin du mouvement)
]


def position(mvt, c, d, h, u=0.5):
    def polaire(a, r, z):
        a = math.radians(a)
        return c + Vector((r * math.cos(a), r * math.sin(a), z))
    if mvt == "plan_fixe":
        return polaire(-90, d, h)
    if mvt == "travelling_lateral":
        return (c + Vector((-d * 0.4, -d, h))).lerp(c + Vector((d * 0.4, -d, h)), u)
    if mvt == "revelation":
        return polaire(-90, d * 0.45, max(1.0, h * 0.25)).lerp(polaire(-90, d, h), 1.0)
    raise ValueError(mvt)


def scene_pour(blend: Path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    with bpy.data.libraries.load(str(blend), link=False) as (src, dst):
        dst.collections = ["Stade"]
    col = dst.collections[0]
    sc.collection.children.link(col)
    for o in col.all_objects:
        if o.parent is None:
            o.location.y += DY
    monde = bpy.data.worlds.new("Monde")
    monde.use_nodes = True
    nt = monde.node_tree
    fond = nt.nodes["Background"]
    hdri = R / pack["monde"]["hdri"]
    if hdri.is_file():
        tex = nt.nodes.new("ShaderNodeTexEnvironment")
        tex.image = bpy.data.images.load(str(hdri))
        nt.links.new(tex.outputs["Color"], fond.inputs["Color"])
    fond.inputs["Strength"].default_value = pack["monde"]["intensite"]
    sc.world = monde
    soleil = bpy.data.objects.new("Soleil", bpy.data.lights.new("Soleil", "SUN"))
    soleil.data.energy = pack["soleil"]["energie"]
    soleil.data.color = pack["soleil"]["couleur"]
    soleil.rotation_euler = [math.radians(a) for a in pack["soleil"]["rotation_deg"]]
    sc.collection.objects.link(soleil)
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    cam.data.lens = 35
    cam.data.clip_end = 2000
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.engine = "BLENDER_EEVEE"
    sc.eevee.taa_render_samples = 32
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = pack.get("exposition", 0.0)
    sc.render.resolution_x, sc.render.resolution_y = L, H
    return sc, cam


images = {}
for etiquette, blend in (("avant", avant), ("apres", apres)):
    if etiquette == "avant" and all((dossier / f"_avant_{p[0]}.png").is_file() for p in PLANS):
        images.update({("avant", p[0]): dossier / f"_avant_{p[0]}.png" for p in PLANS})
        continue                                  # « avant » déjà rendu : on ne refait que « après »
    sc, cam = scene_pour(blend)
    for nom, mvt, cible, d, h in PLANS:
        c = Vector(cible) + Vector((0, 0, 1.2))
        cam.location = position(mvt, c, d, h)
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        chemin = dossier / f"_{etiquette}_{nom}.png"
        sc.render.filepath = str(chemin)
        bpy.ops.render.render(write_still=True)
        images[(etiquette, nom)] = chemin

# Planches côte à côte (marge blanche de 12 px).
for nom, *_ in PLANS:
    a = bpy.data.images.load(str(images[("avant", nom)]))
    b = bpy.data.images.load(str(images[("apres", nom)]))
    pa = np.array(a.pixels[:]).reshape(H, L, 4)
    pb = np.array(b.pixels[:]).reshape(H, L, 4)
    marge = np.ones((H, 12, 4))
    out = np.concatenate([pa, marge, pb], axis=1)
    img = bpy.data.images.new(f"aa_{nom}", 2 * L + 12, H, alpha=True)
    img.pixels = out.ravel().tolist()
    img.filepath_raw = str(dossier / f"avant_apres_{nom}.png")
    img.file_format = "PNG"
    img.save()
    print(f"AVANT_APRES_OK {img.filepath_raw}")
