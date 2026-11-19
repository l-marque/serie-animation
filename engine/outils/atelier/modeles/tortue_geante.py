"""Tortue géante en blocs « tortue_geante » (série « Le Village sur la Tortue », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/tortue_geante.py

La tortue qui porte le village : environ 22 m du nez à la queue, 13 m de large, carapace en gradins de
blocs arrondis (écailles vert sapin et vert mousse, bordure ocre), avec sur le dessus un plateau d'herbe
plat de 9 × 7 m où l'on pose le village. Tête ronde et douce (grands yeux, joues roses, sourire),
pattes épaisses à trois griffes, petite queue.

Repères (coordonnées du modèle, base des pattes à z = 0, tête vers -y) :
- dessus du plateau d'herbe : z = 5,0 ; plateau de x = -4,5 à 4,5 et de y = -3,5 à 3,5 ;
- tête : centre vers (0, -10,2, 2,6) éveillée ; posée au sol quand elle dort.

Squelette maison (os rigides) : Root, Head (avec le cou), Eyelids (paupières, enfant de Head),
Leg.FL, Leg.FR, Leg.BL, Leg.BR, Tail. La carapace ne bouge jamais (le village posé dessus reste en place).
Animations :
- Sleep (96 images, boucle) : tête posée au sol, paupières fermées, respiration lente de la tête, queue ;
- Wake (72 images, une fois) : paupières qui s'ouvrent (image 14), tête qui se lève (images 20 à 44),
  puis regard éveillé ;
- Awake (72 images, boucle) : tête levée, léger balancement, clignement à l'image 54 ;
- Walk (64 images, boucle) : pattes en diagonale (avant gauche + arrière droite, puis l'inverse),
  tête qui dodeline, queue qui balance.
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
M = {
    "peau": f.materiau("Tortue_peau", (0.36, 0.62, 0.16), 0.45),
    "peau_sombre": f.materiau("Tortue_peau_sombre", (0.2, 0.42, 0.08), 0.5),
    "ventre": f.materiau("Tortue_plastron", (0.9, 0.74, 0.36), 0.5),
    "ecaille_a": f.materiau("Tortue_ecaille_sapin", (0.06, 0.3, 0.12), 0.45),
    "ecaille_b": f.materiau("Tortue_ecaille_mousse", (0.16, 0.42, 0.1), 0.45),
    "bordure": f.materiau("Tortue_bordure_ocre", (0.72, 0.42, 0.1), 0.5),
    "herbe": f.materiau("Tortue_herbe", (0.18, 0.62, 0.05), 0.85),
    "terre": f.materiau("Tortue_terre", (0.42, 0.25, 0.1), 0.9),
    "griffe": f.materiau("Tortue_griffes", (0.95, 0.92, 0.82), 0.35),
    "blanc": f.materiau("Tortue_oeil_blanc", (0.97, 0.97, 0.95), 0.25),
    "noir": f.materiau("Tortue_pupille", (0.02, 0.02, 0.04), 0.2),
    "joue": f.materiau("Tortue_joues", (1.0, 0.42, 0.45), 0.5),
    "bouche": f.materiau("Tortue_bouche", (0.12, 0.05, 0.04), 0.6),
    "fleur": f.materiau("Tortue_fleurs", (1.0, 0.85, 0.1), 0.5),
    "fleur_r": f.materiau("Tortue_fleurs_roses", (1.0, 0.3, 0.6), 0.5),
    "mousse": f.materiau("Tortue_mousse", (0.1, 0.5, 0.06), 0.8),
}
parties = []          # (objet, os)


def b(nom, c, t, m, os_="Root", bis=0.12, seg=2, rot=(0, 0, 0)):
    o = f.boite(nom, c, t, M[m], biseau=bis, segments=seg, rotation=rot)
    parties.append((o, os_))
    return o


# ----- carapace : gradins elliptiques -----------------------------------------------------------
Z_PLATEAU = 5.0
# (demi-largeur x, demi-longueur y, z bas, z haut)
GRADINS = [(6.4, 8.2, 1.5, 2.5), (5.9, 7.5, 2.5, 3.5), (5.3, 6.6, 3.5, 4.35), (4.9, 4.1, 4.35, 4.75)]
# corps (masse pleine sous la carapace) et plastron
b("corps", (0, 0, 1.6), (10.4, 13.4, 1.6), "peau", bis=0.5, seg=3)
b("plastron", (0, -0.2, 1.05), (9.6, 12.6, 0.5), "ventre", bis=0.2, seg=2)
# gradins arrondis empilés (couleurs alternées), bordure ocre en bas, écailles carrées sur les flancs
COUL = ["bordure", "ecaille_a", "ecaille_b"]
for g, (ax, ay, z0, z1) in enumerate(GRADINS[:3]):
    h = z1 - z0
    b(f"gradin_{g}", (0, 0, (z0 + z1) / 2), (2 * ax, 2 * ay, h), COUL[g], bis=min(h * 0.45, 0.45), seg=3)
for g, (ax, ay, z0, z1) in enumerate(GRADINS[1:3], start=1):
    zc = (z0 + z1) / 2
    for k in range(-2, 3):                                   # écailles sur les côtés ±x
        for s_ in (-1, 1):
            b(f"ecaille_x_{g}_{k}_{s_}", (s_ * (ax + 0.02), k * ay * 0.36, zc), (0.2, ay * 0.3, (z1 - z0) * 0.62),
              "ecaille_a" if COUL[g] == "ecaille_b" else "ecaille_b", bis=0.08, seg=2)
    for k in range(-1, 2):                                   # devant / derrière
        for s_ in (-1, 1):
            b(f"ecaille_y_{g}_{k}_{s_}", (k * ax * 0.55, s_ * (ay + 0.02), zc), (ax * 0.45, 0.2, (z1 - z0) * 0.62),
              "ecaille_a" if COUL[g] == "ecaille_b" else "ecaille_b", bis=0.08, seg=2)
# dessus : plaque de terre et plateau d'herbe plat (le village se pose à z = 5,0)
b("terre_plateau", (0, 0, 4.6), (9.8, 7.8, 0.5), "terre", bis=0.25, seg=2)
b("plateau", (0, 0, Z_PLATEAU - 0.2), (9.4, 7.4, 0.4), "herbe", bis=0.18, seg=3)
# touffes de mousse et petites fleurs sur les bords du plateau (pas au centre : place du village)
for k, (x, y) in enumerate([(-4.4, -2.8), (4.3, -3.0), (-4.5, 2.9), (4.4, 2.6), (-2.0, 3.6), (2.4, -3.6),
                            (0.6, 3.65), (-4.7, 0.2), (4.7, -0.4)]):
    b(f"mousse_{k}", (x, y, Z_PLATEAU + 0.05), (0.9, 0.7, 0.35), "mousse", bis=0.15, seg=2)
    b(f"fleur_{k}", (x + 0.25, y - 0.1, Z_PLATEAU + 0.28), (0.16, 0.16, 0.12), "fleur" if k % 2 else "fleur_r",
      bis=0.05, seg=1)

# ----- pattes (pivot en haut, z = 1,9) ----------------------------------------------------------
PATTES = {"Leg.FL": (-4.6, -4.6), "Leg.FR": (4.6, -4.6), "Leg.BL": (-4.6, 4.4), "Leg.BR": (4.6, 4.4)}
for nom, (x, y) in PATTES.items():
    b(f"patte_{nom}", (x, y, 1.0), (2.5, 2.5, 2.1), "peau", nom, bis=0.45, seg=3)
    b(f"pied_{nom}", (x, y - 0.15, 0.3), (2.8, 2.9, 0.6), "peau_sombre", nom, bis=0.25, seg=2)
    for k in (-1, 0, 1):
        b(f"griffe_{nom}_{k}", (x + 0.8 * k, y - 1.55, 0.22), (0.42, 0.5, 0.38), "griffe", nom, bis=0.12, seg=2)

# ----- queue ------------------------------------------------------------------------------------
b("queue", (0, 8.9, 1.3), (1.5, 2.2, 1.0), "peau", "Tail", bis=0.35, seg=3, rot=(0.2, 0, 0))
b("queue_bout", (0, 10.0, 1.05), (0.8, 1.2, 0.6), "peau", "Tail", bis=0.25, seg=2, rot=(0.3, 0, 0))

# ----- cou et tête (os Head : pivot à la base du cou) -------------------------------------------
b("cou", (0, -8.4, 2.3), (3.6, 3.8, 2.8), "peau", "Head", bis=0.6, seg=3)
b("tete", (0, -10.6, 2.9), (5.2, 4.0, 4.0), "peau", "Head", bis=1.1, seg=4)
b("museau", (0, -12.55, 2.3), (3.8, 0.6, 2.2), "peau", "Head", bis=0.45, seg=3)
b("dessus_tete", (0, -10.4, 4.85), (2.6, 2.2, 0.3), "peau_sombre", "Head", bis=0.12, seg=2)
for s in (-1, 1):
    b(f"narine_{s}", (s * 0.5, -12.86, 2.95), (0.22, 0.12, 0.16), "bouche", "Head", bis=0.04, seg=1)
    b(f"joue_{s}", (s * 1.75, -12.6, 2.05), (0.8, 0.2, 0.5), "joue", "Head", bis=0.1, seg=2)
    # yeux : grands, sur l'avant de la tête
    b(f"oeil_{s}", (s * 1.25, -12.45, 3.55), (1.35, 0.5, 1.35), "blanc", "Head", bis=0.28, seg=3)
    b(f"pupille_{s}", (s * 1.1, -12.72, 3.45), (0.72, 0.2, 0.82), "noir", "Head", bis=0.14, seg=2)
    b(f"reflet_{s}", (s * 0.92, -12.84, 3.72), (0.24, 0.06, 0.24), "blanc", "Head", bis=0.05, seg=1)
    # paupière : couvre l'œil (fermé) ; l'os Eyelids la remonte de 0,85 m pour ouvrir l'œil
    b(f"paupiere_{s}", (s * 1.25, -12.8, 3.58), (1.5, 0.22, 1.45), "peau_sombre", "Eyelids", bis=0.2, seg=3)
# sourire : trois blocs sombres en arc
for k, (x, z, r) in enumerate([(-0.55, 1.68, 0.35), (0.0, 1.55, 0.0), (0.55, 1.68, -0.35)]):
    b(f"sourire_{k}", (x, -12.88, z), (0.62, 0.1, 0.16), "bouche", "Head", bis=0.04, seg=1, rot=(0, r, 0))

# ----- squelette --------------------------------------------------------------------------------
arm_d = bpy.data.armatures.new("Squelette")
arm = bpy.data.objects.new("Armature", arm_d)
bpy.context.scene.collection.objects.link(arm)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")


def os_edit(nom, tete, queue, parent=None):
    e = arm_d.edit_bones.new(nom)
    e.head, e.tail = Vector(tete), Vector(queue)
    e.roll = 0.0
    if parent:
        e.parent = arm_d.edit_bones[parent]


os_edit("Root", (0, 0, 0), (0, 0, 2.0))
os_edit("Head", (0, -6.8, 2.2), (0, -9.8, 2.2), "Root")          # le long de -y : rotation x = lever / baisser
os_edit("Eyelids", (0, -12.8, 4.3), (0, -12.8, 5.0), "Head")
for nom, (x, y) in PATTES.items():
    os_edit(nom, (x, y, 1.9), (x, y, 0.0), "Root")                  # vers le bas : rotation x = pas avant / arrière
os_edit("Tail", (0, 7.8, 1.5), (0, 10.5, 1.2), "Root")
bpy.ops.object.mode_set(mode="OBJECT")

for o, os_ in parties:
    g = o.vertex_groups.new(name=os_)
    g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
corps = f.fusionner([o for o, _ in parties], "tortue_geante")
corps.parent = arm
mod = corps.modifiers.new("Squelette", "ARMATURE")
mod.object = arm

# ----- animations -------------------------------------------------------------------------------
pb = arm.pose.bones
for bone in pb:
    bone.rotation_mode = "XYZ"
arm.animation_data_create()


def action(nom, cles, longueur):
    """cles : {image: {os: (rx, ry, rz) en degrés, ou "os:loc": (x, y, z) dans le repère de l'os}}."""
    act = bpy.data.actions.new(nom)
    act.use_fake_user = True
    arm.animation_data.action = act
    for img in sorted(cles):
        for bone in pb:
            bone.rotation_euler = (0, 0, 0)
            bone.location = (0, 0, 0)
            bone.scale = (1, 1, 1)
        for os_, val in cles[img].items():
            if os_.endswith(":loc"):
                pb[os_[:-4]].location = val
            elif os_.endswith(":scale"):
                pb[os_[:-6]].scale = val
            else:
                pb[os_].rotation_euler = [math.radians(a) for a in val]
        for bone in pb:
            bone.keyframe_insert("rotation_euler", frame=img)
            bone.keyframe_insert("location", frame=img)
            bone.keyframe_insert("scale", frame=img)
    act.frame_range = (0, longueur)
    return act


# Os Head orienté vers -y : son axe local y = -y du monde, z local = +z du monde, x local = -x du monde.
# Rotation x positive => la tête monte ? (axe x local = -x monde : rotation +x locale baisse le bout vers le bas).
# On garde la convention : BAISSE = rotation x locale négative de l'os... vérifiée sur la planche d'aperçu.
OUVERT = (0, 0, 0.85)       # paupières remontées (repère local de Eyelids : y local = +z monde)
OUVERT_LOC = (0, 0.85, 0)


def dort(d):
    """Tête posée au sol : baissée de 14° et avancée vers le sol ; d = respiration (0 à 1)."""
    return {"Head": (-14 + 1.5 * d, 0, 0), "Head:loc": (0, 0, 0), "Tail": (0, 0, 4 * d)}


action("Sleep", {0: dort(0), 48: dort(1), 96: dort(0)}, 96)

eveil = {"Eyelids:scale": (1, 0.28, 1)}
action("Wake", {
    0: dort(0),
    10: dort(0.3),
    14: {**dort(0.3), "Eyelids:scale": (1, 0.6, 1)},
    18: {**dort(0.3), **eveil},
    24: {**dort(0.2), **eveil},
    26: {**dort(0.2)},                                       # clignement d'étonnement
    29: {**dort(0.2), **eveil},
    44: {"Head": (6, 0, 0), **eveil, "Tail": (0, 0, -6)},
    54: {"Head": (2, 0, -6), **eveil, "Tail": (0, 0, 6)},
    72: {"Head": (3, 0, 0), **eveil, "Tail": (0, 0, 0)}}, 72)

action("Awake", {
    0: {"Head": (3, 0, 0), **eveil},
    18: {"Head": (4.5, 0, 4), **eveil, "Tail": (0, 0, 5)},
    36: {"Head": (3, 0, 0), **eveil},
    52: {"Head": (4.5, 0, -4), **eveil, "Tail": (0, 0, -5)},
    54: {"Head": (4.4, 0, -4)},                                # clignement
    57: {"Head": (4.3, 0, -3.5), **eveil},
    72: {"Head": (3, 0, 0), **eveil}}, 72)


def marche(img):
    t = img / 64
    s = math.sin(2 * math.pi * t)
    lift = max(0.0, math.cos(2 * math.pi * t))
    a = 16 * s
    return {"Leg.FL": (a, 0, 0), "Leg.BR": (a, 0, 0), "Leg.FR": (-a, 0, 0), "Leg.BL": (-a, 0, 0),
            "Head": (4 + 2.5 * math.sin(4 * math.pi * t), 0, 3 * s), **eveil,
            "Tail": (0, 0, 8 * s), "Root:loc": (0, 0, 0.0 * lift)}


action("Walk", {i: marche(i) for i in range(0, 65, 4)}, 64)
arm.animation_data.action = bpy.data.actions[sys.argv[-1] if sys.argv[-1] in ("Sleep", "Wake", "Awake", "Walk") else "Sleep"]

chemin = f.MODELES / "tortue_geante" / "tortue_geante.glb"
chemin.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", export_animation_mode="ACTIONS",
                          export_force_sampling=True)
n_tri = sum(len(p.vertices) - 2 for p in corps.data.polygons)
print(f"MODELE_EXPORTE tortue_geante : {chemin} ({n_tri} triangles)")
