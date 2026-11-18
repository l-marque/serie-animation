"""Photo de profil Instagram : Kevin en gros plan qui salue, stade en ruine flouté derrière.

    blender --background --factory-startup --python engine/outils/atelier/photo_profil.py -- <sortie.png> [pose] [image]

1080 × 1080, cadrage pensé pour la découpe ronde d'Instagram (tête et main dans le cercle central).
Lumière et ciel du pack stade_bloc (HDRI, soleil, AgX). pose : action du personnage (défaut Wave),
image : image de l'action (défaut 7, bras levé).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

R = Path(__file__).resolve().parents[3]
args = sys.argv[sys.argv.index("--") + 1:]
sortie = Path(args[0])
pose = args[1] if len(args) > 1 else "Wave"
image_pose = int(args[2]) if len(args) > 2 else 7
pack = json.loads((R / "engine/packs_da/stade_bloc.json").read_text(encoding="utf-8"))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# Décor : le stade en ruine (collection « Stade ») ajouté tel quel.
with bpy.data.libraries.load(str(R / "engine/assets/modeles/terrain_boueux/stade_ruine.blend"), link=False) as (src, dst):
    dst.collections = ["Stade"]
sc.collection.children.link(dst.collections[0])

# Kevin, au même endroit que dans l'épisode, face caméra.
X, Y = 44.0, -2.0
avant = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=str(R / "engine/assets/modeles/personnages_bloc/kevin_bloc.glb"))
kevin = [o for o in bpy.data.objects if o not in avant]
for o in kevin:
    if o.parent is None:
        o.location = (X, Y, 0)
arm = next(o for o in kevin if o.type == "ARMATURE")
ad = arm.animation_data or arm.animation_data_create()
for piste in list(ad.nla_tracks):
    ad.nla_tracks.remove(piste)
ad.action = next(a for a in bpy.data.actions if a.name.split("|")[-1] == pose)
sc.frame_set(image_pose)
bpy.context.view_layer.update()

# Ciel et soleil du pack.
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

# Caméra : gros plan légèrement en contre-plongée (Kevin paraît plus attachant), profondeur de champ.
tete = Vector((X + 0.05, Y, 1.24))
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = 55
cam.location = Vector((X + 0.3, Y - 2.1, 1.12))
cam.rotation_euler = (tete - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = (tete - cam.location).length
cam.data.dof.aperture_fstop = 1.8
sc.collection.objects.link(cam)
sc.camera = cam

sc.render.engine = "BLENDER_EEVEE"
if hasattr(sc.eevee, "taa_render_samples"):
    sc.eevee.taa_render_samples = 128
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = pack.get("exposition", 0.0)
sc.render.resolution_x = sc.render.resolution_y = 1080
sc.render.filepath = str(sortie)
sortie.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.render.render(write_still=True)
print(f"PROFIL_OK {sortie}")
