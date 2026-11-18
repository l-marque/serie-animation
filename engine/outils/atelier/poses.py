"""Planche des poses clés d'un personnage animé : une ligne par action, 4 images par action.

    blender --background --factory-startup --python engine/outils/atelier/poses.py -- perso.glb planche.png [Run Kick_Right ...]

Vue de trois-quarts face ; sert à vérifier le sens des rotations, les interpénétrations et la lisibilité.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
modele, sortie = Path(args[0]), Path(args[1])
voulues = args[2:] or ["Idle", "Run", "Kick_Right", "Wave", "Jump", "Clapping"]
dossier = sortie.parent / f"_{sortie.stem}_poses"
dossier.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(modele))
arm = next(o for o in sc.objects if o.type == "ARMATURE")
ad = arm.animation_data or arm.animation_data_create()
for piste in list(ad.nla_tracks):
    ad.nla_tracks.remove(piste)
hauteur = max((o.matrix_world @ Vector(c)).z for o in sc.objects if o.type == "MESH" for c in o.bound_box)

bpy.ops.mesh.primitive_plane_add(size=30)
sol = bpy.context.object
ms = bpy.data.materials.new("sol")
ms.use_nodes = True
ms.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.3, 0.5, 0.25, 1)
sol.data.materials.append(ms)
soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.5
soleil.rotation_euler = (math.radians(45), 0, math.radians(-30))
sc.collection.objects.link(soleil)
monde = bpy.data.worlds.new("m")
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs["Color"].default_value = (0.6, 0.7, 0.85, 1)
sc.world = monde
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 50
sc.collection.objects.link(cam)
sc.camera = cam
d = hauteur * 3.2
cam.location = Vector((-0.55, -0.85, 0.25)).normalized() * d + Vector((0, 0, hauteur * 0.55))
cible = Vector((0, 0, hauteur * 0.5))
cam.rotation_euler = (cible - cam.location).to_track_quat("-Z", "Y").to_euler()
moteurs = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in moteurs else "BLENDER_EEVEE"
sc.view_settings.view_transform = "AgX"
sc.render.resolution_x, sc.render.resolution_y = 300, 400

lignes = []
for nom in voulues:
    act = next((a for a in bpy.data.actions if a.name == nom or a.name.split("|")[-1] == nom), None)
    if act is None:
        print(f"ACTION_ABSENTE {nom}")
        continue
    ad.action = act
    debut, fin = act.frame_range
    images = []
    for k, img in enumerate([debut + (fin - debut) * t for t in (0.0, 0.18, 0.36, 0.55)] if nom != "Kick_Right"
                            else [debut + 3, debut + 4, debut + 8, debut + 14]):
        sc.frame_set(int(round(img)))
        sc.render.filepath = str(dossier / f"{nom}_{k}.png")
        bpy.ops.render.render(write_still=True)
        images.append(sc.render.filepath)
    lignes.append(images)

w, h = 300, 400
planche = bpy.data.images.new("planche", 4 * w, len(lignes) * h)
pixels = [0.0] * (4 * w * h * 4 * len(lignes))
for li, images in enumerate(lignes):
    for k, chemin in enumerate(images):
        src = list(bpy.data.images.load(chemin).pixels)
        ox, oy = k * w, (len(lignes) - 1 - li) * h
        for y in range(h):
            debut_px = ((oy + y) * 4 * w + ox) * 4
            pixels[debut_px:debut_px + w * 4] = src[y * w * 4:(y + 1) * w * 4]
planche.pixels = pixels
planche.filepath_raw = str(sortie)
planche.file_format = "PNG"
planche.save()
print(f"POSES_OK {sortie} : {', '.join(voulues)}")
