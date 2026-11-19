"""Aperçu d'un plan de la série « 10 000 serpents contre 1 hamster » chargé PAR LE MOTEUR (autocontrôle).

Les assets sont importés avec engine/blender/bibliotheque.py (pieces_bibliotheque, comme le décorateur : collection
prototype + empty qui l'instancie, matériaux d'origine gardés via look.appliquer_role), la lumière et le moteur de
rendu viennent du pack pre_hamster (look.monde_et_lumiere, look.moteur). On vérifie donc que les instances (nœuds
de géométrie) et les animations survivent à l'import du moteur. Ce n'est pas un rendu d'épisode.

    blender --background --factory-startup -noaudio --python engine/outils/atelier/hamster_apercu.py -- sortie.png '<json>'

json : {"cam": [x, y, z], "cible": [x, y, z], "lens": 35, "res": [540, 960], "image": 30, "mode": "animatique",
        "assets": [{"id": "pre_hamster"}, {"id": "foule_serpents"},
                   {"id": "hamster_bloc", "pos": [0, 0, 0], "rot_z": 0, "echelle": 1, "action": "Tremble",
                    "emission_chaude": 0.35}],
        "mesurer": false}
"emission_chaude" (facultatif, par asset) : essai de matériaux légèrement émissifs dans leur propre couleur (lisibilité
en contre-jour) sans toucher au modèle.
"mesurer" : affiche la hauteur de chaque asset dans la pose de son animation de base (image 1), comme _placer.
"""
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R / "engine" / "blender"))
import bibliotheque  # noqa: E402
import look  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:]
sortie = Path(args[0])
cfg = json.loads(args[1])
pack = json.loads((R / "engine/packs_da" / f"{cfg.get('pack', 'pre_hamster')}.json").read_text(encoding="utf-8"))
registre = bibliotheque.charger_registre(R)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
look.monde_et_lumiere(sc, pack)
look.moteur(sc, pack, cfg.get("mode", "animatique"))

if cfg.get("mesurer"):
    for a in cfg["assets"]:
        entree = registre[a["id"]]
        objets = bibliotheque._retirer_parasites(bibliotheque._importer(R / entree["fichier"], entree), entree, a["id"])
        if entree.get("animation"):
            bibliotheque._jouer_animation(objets, entree["animation"])
        sc.frame_set(1)
        mn, mx = bibliotheque._boite_monde(objets)
        print(f"MESURE {a['id']} : hauteur {mx.z - mn.z:.3f} m, largeur x {mx.x - mn.x:.3f}, profondeur y "
              f"{mx.y - mn.y:.3f}, bas z {mn.z:.3f}")
        for o in objets:
            bpy.data.objects.remove(o, do_unlink=True)
    sys.exit(0)

t0 = time.time()
for i, a in enumerate(cfg["assets"]):
    pieces = bibliotheque.pieces_bibliotheque(R, a["id"], 0)
    objets = [o for o, _, _ in pieces]
    if a.get("action"):
        bibliotheque._jouer_animation(objets, a["action"])
        if a.get("decalage"):                     # décale la boucle (deux recrues pas synchrones)
            for o in objets:
                if o.type == "ARMATURE":
                    for piste in o.animation_data.nla_tracks:
                        for bande in piste.strips:
                            bande.frame_start_ui += a["decalage"]
    proto = bpy.data.collections.new(f"PROTO_{a['id']}_{i}")
    garder = registre[a["id"]].get("materiaux") == "origine"
    for o, role, principal in pieces:
        if o.type == "MESH":
            look.appliquer_role(o, role, pack, garder)
            if a.get("emission_chaude"):         # essai : matériaux légèrement émissifs (leur propre couleur)
                for i_m, m in enumerate(o.data.materials):
                    b = m and next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                    if b is None or b.inputs["Emission Strength"].default_value > a["emission_chaude"]:
                        continue                 # les yeux et reflets déjà lumineux restent tels quels
                    m2 = m.copy()
                    b2 = next(n for n in m2.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
                    b2.inputs["Emission Color"].default_value = b2.inputs["Base Color"].default_value
                    b2.inputs["Emission Strength"].default_value = a["emission_chaude"]
                    o.data.materials[i_m] = m2
        proto.objects.link(o)
    e = bpy.data.objects.new(f"EP_{a['id']}_{i}", None)
    e.instance_type = "COLLECTION"
    e.instance_collection = proto
    e.location = a.get("pos", (0, 0, 0))
    e.rotation_euler.z = math.radians(a.get("rot_z", 0))
    s = a.get("echelle", 1.0)
    e.scale = (s, s, s)
    sc.collection.objects.link(e)
t_import = time.time() - t0
# Comme le moteur (rendu.regler après le décorateur) : 30 i/s APRÈS les imports. Les glb sont importés à 24 i/s,
# leurs actions sont donc lues image pour image ; régler 30 i/s avant l'import étirerait les actions de 25 %.
sc.render.fps = 30

cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = cfg.get("lens", 35)
cam.data.clip_end = 1000                         # comme engine/blender/camera.py
cam.location = Vector(cfg["cam"])
cam.rotation_euler = (Vector(cfg["cible"]) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.collection.objects.link(cam)
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = cfg.get("res", [540, 960])
sc.render.resolution_percentage = 100
sc.frame_set(cfg.get("image", 30))
sc.render.filepath = str(sortie)
sortie.parent.mkdir(parents=True, exist_ok=True)
t1 = time.time()
bpy.ops.render.render(write_still=True)
t_rendu = time.time() - t1
if cfg.get("deuxieme_image"):                    # 2e image : temps hors préparation (shaders compilés)
    sc.frame_set(cfg.get("image", 30) + 1)
    t2 = time.time()
    bpy.ops.render.render(write_still=False)
    print(f"TEMPS_IMAGE_SUIVANTE {time.time() - t2:.2f} s")
print(f"HAMSTER_APERCU_OK {sortie} : import {t_import:.1f} s, rendu {t_rendu:.1f} s, moteur {sc.render.engine}, "
      f"échantillons {getattr(sc.eevee, 'taa_render_samples', '?')}")
