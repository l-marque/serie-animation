"""Photo de profil du compte général (toutes les séries « c'est vous qui construisez ») : un petit monde en blocs
qui flotte (cube d'herbe et de terre), avec la cabane, un arbre, un tas de briques et l'habitant n°1 qui salue,
sur un fond uni et vif. 1080 × 1080, sujet centré dans le cercle d'Instagram, lisible en tout petit.

    blender --background --factory-startup -noaudio --python engine/outils/atelier/photo_profil_compte.py -- <sortie.png>

Rendu sur fond transparent ; la couleur du fond est posée ensuite avec Pillow (voir
renders/compte/outils/fond.py), pour qu'elle reste franche (AgX délave un fond rendu dans Blender).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import formes as f  # noqa: E402

R = Path(__file__).resolve().parents[2].parent
args = sys.argv[sys.argv.index("--") + 1:]
sortie = Path(args[0])
M = R / "engine/assets/modeles"

f.vider()
sc = bpy.context.scene
mat = {
    "herbe": f.materiau("Herbe", (0.2, 0.62, 0.06), 0.8),
    "herbe_bord": f.materiau("Herbe_bord", (0.14, 0.5, 0.05), 0.8),
    "terre": f.materiau("Terre", (0.5, 0.3, 0.13), 0.9),
    "terre_sombre": f.materiau("Terre_sombre", (0.36, 0.2, 0.08), 0.9),
    "pierre": f.materiau("Pierre", (0.55, 0.55, 0.58), 0.9),
    "brique": f.materiau("Brique", (0.82, 0.3, 0.14), 0.7),
    "tronc": f.materiau("Tronc", (0.32, 0.17, 0.07), 0.85),
    "feuille": f.materiau("Feuilles", (0.1, 0.48, 0.08), 0.75),
    "fleur": f.materiau("Fleur", (1.0, 0.3, 0.6), 0.5),
}
# Le cube-monde : herbe sur le dessus (z = 0), terre et pierres en dessous, bords en escalier.
L = 6.0
f.boite("herbe", (0, 0, -0.2), (L, L, 0.4), mat["herbe"], biseau=0.12, segments=2)
f.boite("terre", (0, 0, -1.3), (L - 0.15, L - 0.15, 1.8), mat["terre"], biseau=0.1, segments=2)
f.boite("terre_bas", (0, 0, -2.6), (L - 1.4, L - 1.4, 1.0), mat["terre_sombre"], biseau=0.15, segments=2)
f.boite("pointe", (0, 0, -3.4), (L - 3.4, L - 3.4, 0.8), mat["pierre"], biseau=0.15, segments=2)
for k, (x, y, z) in enumerate([(-2.0, -3.0, -1.0), (1.2, -3.0, -1.6), (-3.0, 0.8, -0.9), (2.4, -3.0, -0.6)]):
    f.boite(f"caillou_{k}", (x, y, z), (0.6, 0.12, 0.45), mat["pierre"], biseau=0.06, segments=1)
for k, (x, y) in enumerate([(-2.6, -2.6), (2.5, -2.4), (-2.4, 1.9), (0.3, -2.7)]):
    f.boite(f"touffe_{k}", (x, y, 0.1), (0.5, 0.4, 0.25), mat["herbe_bord"], biseau=0.08, segments=1)
    f.boite(f"fleur_{k}", (x + 0.15, y, 0.3), (0.16, 0.16, 0.14), mat["fleur"], biseau=0.04, segments=1)
# Tas de briques (« 1 like = 1 brique ») devant à droite.
for k, (x, y, z) in enumerate([(1.6, -1.6, 0.12), (2.15, -1.6, 0.12), (1.88, -1.55, 0.36), (1.6, -1.1, 0.12)]):
    f.boite(f"brique_{k}", (x, y, z), (0.5, 0.26, 0.24), mat["brique"], biseau=0.04, segments=1, rotation=(0, 0, 0.1 * k))
# Arbre en blocs à gauche.
f.boite("tronc", (-2.2, 0.9, 0.8), (0.45, 0.45, 1.6), mat["tronc"], biseau=0.06)
f.boite("feuilles1", (-2.2, 0.9, 2.2), (1.9, 1.9, 1.5), mat["feuille"], biseau=0.25, segments=2)
f.boite("feuilles2", (-2.1, 0.85, 3.25), (1.2, 1.2, 0.9), mat["feuille"], biseau=0.2, segments=2)


def importer(glb, pos, rot_z=0.0, action=None, image=0):
    avant = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    nouveaux = [o for o in bpy.data.objects if o not in avant]
    for o in nouveaux:
        if o.parent is None:
            o.location = Vector(pos)
            o.rotation_euler.z += math.radians(rot_z)
    if action:
        for o in nouveaux:
            if o.type == "ARMATURE":
                ad = o.animation_data or o.animation_data_create()
                for piste in list(ad.nla_tracks):
                    ad.nla_tracks.remove(piste)
                ad.action = next(a for a in bpy.data.actions if a.name.split("|")[-1] == action)
    return nouveaux


importer(M / "cabane_bloc/cabane_bloc.glb", (0.7, 1.2, 0), -12)
hab = importer(M / "personnages_bloc/habitant_iles_jaune.glb", (-0.2, -1.5, 0), 12, action="Wave")
for o in hab:
    if o.parent is None:
        o.scale = [1.7 * v for v in o.scale]   # habitant agrandi : lisible dans une vignette de 110 px
sc.frame_set(7)

# Fond uni (couleur du compte) et lumière douce.
monde = bpy.data.worlds.new("Fond")
sc.world = monde
monde.use_nodes = True
monde.node_tree.nodes["Background"].inputs["Color"].default_value = (0.75, 0.85, 1.0, 1)   # ciel neutre pour l'éclairage
monde.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
soleil_d = bpy.data.lights.new("Soleil", "SUN")
soleil_d.energy = 3.5
soleil = bpy.data.objects.new("Soleil", soleil_d)
soleil.rotation_euler = (math.radians(40), 0, math.radians(-35))
sc.collection.objects.link(soleil)
sc.view_settings.view_transform = "AgX"
try:
    sc.view_settings.look = "Punchy"
except TypeError:
    sc.view_settings.look = "AgX - Punchy"

cam_d = bpy.data.cameras.new("Cam")
cam_d.lens = 68
cam = bpy.data.objects.new("Cam", cam_d)
sc.collection.objects.link(cam)
cam.location = (-11.5, -19, 11)
cam.rotation_euler = (Vector((0, 0, 0.2)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sc.render.engine = "BLENDER_EEVEE"
sc.render.resolution_x = sc.render.resolution_y = 1080
sc.render.film_transparent = True   # le fond uni est posé ensuite (couleur non délavée par AgX)
sc.render.filepath = str(sortie)
bpy.ops.render.render(write_still=True)
print("PHOTO_PROFIL_OK", sortie)
