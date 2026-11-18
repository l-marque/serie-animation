"""Aperçu léger d'un plan de la série « 7 Jours avant l'Attaque » : décor iles_duel + modèles posés,
lumière et ciel du pack « iles » (HDRI, soleil, AgX, exposition), Eevee à peu d'échantillons.

    blender --background --factory-startup -noaudio --python engine/outils/atelier/iles_apercu.py -- sortie.png '<json>'

json : {"cam": [x, y, z], "cible": [x, y, z], "lens": 24, "res": [540, 960], "decor": true,
        "blends": [{"fichier": "engine/assets/modeles/ile_instagram/ile_instagram.blend", "collection": "Ile",
                    "pos": [-11, 0, 0], "echelle": 1.2}],   (remplace le décor iles_duel si présent)
        "objets": [{"glb": "engine/assets/...glb", "pos": [x, y, z], "rot_z": 0, "action": "Wave", "image": 7}]}
Chemins relatifs au dépôt. Sert à l'autocontrôle des modèles (pas un rendu d'épisode).
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
cfg = json.loads(args[1])
pack = json.loads((R / "engine/packs_da" / f"{cfg.get('pack', 'iles')}.json").read_text(encoding="utf-8"))

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
for bl in cfg.get("blends", []):   # assets .blend séparés : {"fichier", "collection", "pos", "echelle"}
    with bpy.data.libraries.load(str(R / bl["fichier"]), link=False) as (src, dst):
        dst.collections = [bl["collection"]]
    c = dst.collections[0]
    sc.collection.children.link(c)
    for o in c.all_objects:
        if o.parent is None:
            k = bl.get("echelle", 1.0)   # comme le moteur : échelle depuis l'origine de l'asset, puis position
            o.scale = o.scale * k
            o.location = o.location * k + Vector(bl.get("pos", (0, 0, 0)))
if cfg.get("blends"):
    pass
elif cfg.get("decor", True):
    with bpy.data.libraries.load(str(R / "engine/assets/modeles/iles_duel/iles_duel.blend"), link=False) as (src, dst):
        dst.collections = ["Iles"]
    sc.collection.children.link(dst.collections[0])
else:
    bpy.ops.mesh.primitive_plane_add(size=40)
    sol = bpy.context.object
    m = bpy.data.materials.new("sol")
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*pack["materiaux"]["sol"]["couleur"], 1)
    sol.data.materials.append(m)

IMAGE_SCENE = 100
for obj in cfg.get("objets", []):
    avant = set(bpy.data.objects)
    actions_avant = set(bpy.data.actions)
    bpy.ops.import_scene.gltf(filepath=str(R / obj["glb"]))
    nouveaux = [o for o in bpy.data.objects if o not in avant]
    for o in nouveaux:
        if o.parent is None:
            o.location = obj["pos"]
            o.rotation_euler.z += math.radians(obj.get("rot_z", 0))
    arm = next((o for o in nouveaux if o.type == "ARMATURE"), None)
    if arm and obj.get("action"):
        ad = arm.animation_data or arm.animation_data_create()
        for piste in list(ad.nla_tracks):
            ad.nla_tracks.remove(piste)
        ad.action = None
        act = next(a for a in bpy.data.actions if a not in actions_avant
                   and a.name.split("|")[-1].split(".")[0] == obj["action"])
        piste = ad.nla_tracks.new()
        bande = piste.strips.new(act.name, int(IMAGE_SCENE - obj.get("image", 0) - act.frame_range[0]), act)
        bande.extrapolation = "HOLD"
bpy.context.view_layer.update()

monde = bpy.data.worlds.new("Monde")
monde.use_nodes = True
nt = monde.node_tree
fond = nt.nodes["Background"]
fond.inputs["Color"].default_value = (*pack["monde"]["couleur"], 1)
hdri = R / pack["monde"].get("hdri", "")
if pack["monde"].get("hdri") and hdri.is_file():
    tex = nt.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(str(hdri))
    nt.links.new(tex.outputs["Color"], fond.inputs["Color"])
fond.inputs["Strength"].default_value = pack["monde"].get("intensite", 1.0)
sc.world = monde
soleil = bpy.data.objects.new("Soleil", bpy.data.lights.new("Soleil", "SUN"))
soleil.data.energy = pack["soleil"]["energie"]
soleil.data.color = pack["soleil"]["couleur"]
soleil.rotation_euler = [math.radians(a) for a in pack["soleil"]["rotation_deg"]]
sc.collection.objects.link(soleil)

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = cfg.get("lens", 24)
cam.data.clip_end = 5000
cam.location = Vector(cfg["cam"])
cam.rotation_euler = (Vector(cfg["cible"]) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(cam)
sc.camera = cam

sc.render.engine = "BLENDER_EEVEE"
if hasattr(sc.eevee, "taa_render_samples"):
    sc.eevee.taa_render_samples = 16
sc.view_settings.view_transform = pack.get("transformation_vue", "AgX")
sc.view_settings.exposure = pack.get("exposition", 0.0)
sc.render.resolution_x, sc.render.resolution_y = cfg.get("res", [540, 960])
sc.frame_set(IMAGE_SCENE)
sc.render.filepath = str(sortie)
sortie.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.render.render(write_still=True)
print(f"ILES_APERCU_OK {sortie}")
