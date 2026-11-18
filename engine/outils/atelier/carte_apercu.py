"""Aperçu d'une carte de choix (2,0 × 2,6 m, comme le primitif carte_choix) avec sa miniature, vue comme dans
l'épisode (plan fixe, 8,4 m / 2,2 m, lumière du pack stade_bloc) : vérifie la lisibilité de la miniature.

    blender --background --factory-startup --python engine/outils/atelier/carte_apercu.py -- <sortie.png> \
        <titre> <prix> <miniature.glb> <echelle> <rotation_z_deg> [<titre2> <prix2> <glb2> <echelle2> <rot2>]

Les cartes sont posées comme au jour 1 (échelle 0,95, x = ∓1,15) ; la miniature en (x ; -0,4 ; 0,75).
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

R = Path(__file__).resolve().parents[3]
a = sys.argv[sys.argv.index("--") + 1:]
sortie, cartes = Path(a[0]), [a[i:i + 5] for i in range(1, len(a), 5)]
pack = json.loads((R / "engine/packs_da/stade_bloc.json").read_text(encoding="utf-8"))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def mat(nom, c, r=0.6):
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = r
    return m


BLANC, ACCENT, TEXTE, PRIX = mat("blanc", (0.85, 0.85, 0.83)), mat("accent", (0.9, 0.5, 0.02)), \
    mat("texte", (0.03, 0.03, 0.05)), mat("prix", (0.02, 0.25, 0.6))
xs = [0.0] if len(cartes) == 1 else [-1.15, 1.15]
for (titre, prix, glb, ech, rot), x in zip(cartes, xs):
    E = 0.95
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, 1.3 * E))
    c = bpy.context.object
    c.scale = (2.0 * E, 0.08 * E, 2.6 * E)
    c.data.materials.append(BLANC)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0.05 * E, 1.3 * E))
    o = bpy.context.object
    o.scale = (2.06 * E, 0.04 * E, 2.66 * E)
    o.data.materials.append(ACCENT)
    for t, z, taille, m in ((titre, 0.48, 0.3, TEXTE), (prix, 0.14, 0.2, PRIX)):
        bpy.ops.object.text_add(location=(x, -0.07 * E, z * E), rotation=(math.pi / 2, 0, 0))
        tx = bpy.context.object
        tx.data.body, tx.data.size, tx.data.extrude = t, taille * E, 0.02
        tx.data.align_x, tx.data.align_y = "CENTER", "CENTER"
        tx.data.materials.append(m)
    avant = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    for o in set(bpy.data.objects) - avant:
        if o.parent is None:
            o.location = (x, -0.4, 0.75)
            o.scale = (float(ech),) * 3
            o.rotation_euler.z = math.radians(float(rot))

monde = bpy.data.worlds.new("Monde")
monde.use_nodes = True
nt = monde.node_tree
hdri = R / pack["monde"]["hdri"]
if hdri.is_file():
    tex = nt.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(str(hdri))
    nt.links.new(tex.outputs["Color"], nt.nodes["Background"].inputs["Color"])
sc.world = monde
sol = bpy.data.objects.new("Soleil", bpy.data.lights.new("Soleil", "SUN"))
sol.data.energy, sol.data.color = pack["soleil"]["energie"], pack["soleil"]["couleur"]
sol.rotation_euler = [math.radians(v) for v in pack["soleil"]["rotation_deg"]]
sc.collection.objects.link(sol)
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = 35
visee = Vector((0, 0, 1.2))
cam.location = visee + Vector((0, -8.4, 2.2))
cam.rotation_euler = (visee - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = 32
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = pack.get("exposition", 0.0)
sc.render.resolution_x, sc.render.resolution_y = 540, 960
sc.render.filepath = str(sortie)
bpy.ops.render.render(write_still=True)
print(f"CARTE_OK {sortie}")
