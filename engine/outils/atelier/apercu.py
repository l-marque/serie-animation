"""Planche d'aperçu d'un modèle : 4 vues (face, trois-quarts, profil, plongée) sur une image 2 × 2.

Sert à l'autocontrôle après chaque itération de modélisation (boucle de ref-lookdev) :

    blender --background --factory-startup --python engine/outils/atelier/apercu.py -- modele.glb planche.png

Échelle : un mannequin gris de 1,75 m est posé à côté du modèle pour juger des proportions.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index("--") + 1:]
modele, sortie = Path(args[0]), Path(args[1])
dossier = sortie.parent / f"_{sortie.stem}_vues"
dossier.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=str(modele))
objets = [o for o in sc.objects if o.type == "MESH"]
bpy.context.view_layer.update()
mn = Vector((1e9,) * 3)
mx = Vector((-1e9,) * 3)
for o in objets:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        mn = Vector(map(min, mn, w))
        mx = Vector(map(max, mx, w))
centre = (mn + mx) / 2
taille = max((mx - mn).length, 1.0)

# Repère d'échelle : silhouette de 1,75 m à gauche du modèle.
x_ref = mn.x - 0.6
bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.45, location=(x_ref, centre.y, 0.725))
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x_ref, centre.y, 1.6))
gris = bpy.data.materials.new("ref")
gris.diffuse_color = (0.5, 0.5, 0.5, 1)
for o in sc.objects[-2:]:
    o.data.materials.append(gris)

bpy.ops.mesh.primitive_plane_add(size=taille * 8, location=(centre.x, centre.y, 0))
sol = bpy.context.object
m_sol = bpy.data.materials.new("sol")
m_sol.use_nodes = True
m_sol.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.42, 0.3, 1)
sol.data.materials.append(m_sol)

soleil = bpy.data.objects.new("soleil", bpy.data.lights.new("soleil", "SUN"))
soleil.data.energy = 3.5
soleil.rotation_euler = (math.radians(50), 0, math.radians(35))
sc.collection.objects.link(soleil)
monde = bpy.data.worlds.new("monde")
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs["Color"].default_value = (0.55, 0.65, 0.8, 1)
monde.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
sc.world = monde

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
cam.data.lens = 50
sc.collection.objects.link(cam)
sc.camera = cam
cible = bpy.data.objects.new("cible", None)
cible.location = centre
sc.collection.objects.link(cible)
contrainte = cam.constraints.new("TRACK_TO")
contrainte.target = cible
contrainte.track_axis = "TRACK_NEGATIVE_Z"
contrainte.up_axis = "UP_Y"

moteurs = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in moteurs else "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 640
sc.view_settings.view_transform = "Standard"

d = taille * 1.6
vues = {"face": (0, -1, 0.25), "trois_quarts": (0.75, -0.75, 0.35), "profil": (1, 0, 0.2), "plongee": (-0.5, -0.6, 0.9)}
for nom, (vx, vy, vz) in vues.items():
    v = Vector((vx, vy, vz)).normalized()
    cam.location = centre + v * d
    sc.render.filepath = str(dossier / f"{nom}.png")
    bpy.ops.render.render(write_still=True)

# Assemblage 2 × 2 dans Blender (pas de dépendance à PIL ni à ffmpeg).
images = [bpy.data.images.load(str(dossier / f"{n}.png")) for n in vues]
w = h = 640
planche = bpy.data.images.new("planche", 2 * w, 2 * h)
pixels = [0.0] * (4 * w * h * 4)
for k, img in enumerate(images):
    src = list(img.pixels)
    ox, oy = (k % 2) * w, (1 - k // 2) * h
    for y in range(h):
        ligne = src[y * w * 4:(y + 1) * w * 4]
        debut = ((oy + y) * 2 * w + ox) * 4
        pixels[debut:debut + w * 4] = ligne
planche.pixels = pixels
planche.filepath_raw = str(sortie)
planche.file_format = "PNG"
planche.save()
print(f"APERCU_OK {sortie}")
