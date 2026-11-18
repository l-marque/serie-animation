"""Crocodile en blocs « crocodile_bloc » (série « 7 Jours avant l'Attaque », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/crocodile_bloc.py

Gardien de l'île, environ 3,2 m du museau à la queue, vert pomme et ventre jaune, blocs arrondis.
Silhouette lisible au ras de l'eau : gros yeux ronds sur le dessus de la tête (paupière mi-close,
air malin), museau long, rangée d'écailles sombres sur le dos et la queue qui ondule. Détails : une
dent en or parmi les dents blanches, narines en relief, griffes claires.
Base (ventre) à z = 0, museau vers -y. Repères verticaux : dos à 0,45 m, yeux à 0,68 m.
Dans l'eau (niveau -0,3 de iles_duel) : position z = -0,55 => seuls la tête, les yeux, le dos et les
écailles dépassent ; z = -0,3 => posé sur l'eau (sortie de l'eau, apparition).
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
M = {
    "vert": f.materiau("Croco_vert", (0.2, 0.62, 0.05), 0.45),
    "sombre": f.materiau("Croco_ecailles", (0.05, 0.3, 0.03), 0.5),
    "ventre": f.materiau("Croco_ventre", (0.85, 0.75, 0.2), 0.5),
    "blanc": f.materiau("Croco_blanc", (0.95, 0.95, 0.92), 0.3),
    "noir": f.materiau("Croco_pupille", (0.02, 0.02, 0.03), 0.3),
    "or": f.materiau("Croco_dent_or", (1.0, 0.7, 0.1), 0.25, metal=0.9),
    "bouche": f.materiau("Croco_bouche", (0.55, 0.06, 0.08), 0.6),
}
p = []


def b(nom, c, t, m, bis=0.08, seg=2, rot=(0, 0, 0)):
    o = f.boite(nom, c, t, M[m], biseau=bis, segments=seg, rotation=rot)
    p.append(o)
    return o


# corps
b("corps", (0, 0.1, 0.27), (0.9, 1.4, 0.46), "vert", 0.16, 3)
b("ventre", (0, 0.1, 0.07), (0.8, 1.3, 0.14), "ventre", 0.06, 2)
# tête et museau
b("tete", (0, -0.85, 0.3), (0.72, 0.62, 0.42), "vert", 0.15, 3)
b("museau", (0, -1.38, 0.24), (0.52, 0.62, 0.2), "vert", 0.08, 3)
b("bout_museau", (0, -1.66, 0.25), (0.46, 0.14, 0.2), "vert", 0.07, 2)
for s in (-1, 1):
    b(f"narine_{s}", (s * 0.1, -1.66, 0.37), (0.1, 0.1, 0.06), "sombre", 0.03, 1)
# mâchoire du bas, très légèrement ouverte (sourire en coin)
b("machoire", (0, -1.3, 0.07), (0.5, 0.75, 0.13), "ventre", 0.05, 2, rot=(-0.06, 0, 0))
b("bouche", (0, -1.22, 0.14), (0.44, 0.6, 0.04), "bouche", 0.0, 1)
for s in (-1, 1):
    for k in range(5):
        y = -1.62 + 0.13 * k
        m = "or" if (s == 1 and k == 2) else "blanc"
        b(f"dent_{s}_{k}", (s * 0.23, y, 0.12), (0.06, 0.06, 0.1), m, 0.015, 1, rot=(0, 0, 0.785))
# yeux sur le dessus de la tête
for s in (-1, 1):
    b(f"oeil_{s}", (s * 0.2, -0.78, 0.6), (0.24, 0.24, 0.24), "blanc", 0.1, 3)
    b(f"pupille_{s}", (s * 0.2, -0.9, 0.59), (0.1, 0.03, 0.14), "noir", 0.02, 1)
    b(f"paupiere_{s}", (s * 0.2, -0.79, 0.69), (0.27, 0.27, 0.1), "vert", 0.04, 2, rot=(-0.25, 0, 0))
# queue : tronçons qui rétrécissent et ondulent
x = 0.0
for k in range(5):
    t = k / 4
    y = 0.8 + k * 0.2
    x = 0.12 * math.sin(k * 1.1)
    larg = 0.7 - 0.45 * t
    haut = 0.36 - 0.18 * t
    b(f"queue_{k}", (x, y, haut / 2 + 0.04 * (1 - t)), (larg, 0.36, haut), "vert", min(0.1, larg * 0.2), 2,
      rot=(0, 0, 0.25 * math.cos(k * 1.1)))
    b(f"ecaille_q_{k}", (x, y, haut + 0.06 + 0.04 * (1 - t)), (0.12, 0.2, 0.12 - 0.04 * t), "sombre", 0.03, 1)
# écailles du dos : deux rangées
for k in range(5):
    y = -0.45 + k * 0.3
    for s in (-1, 1):
        b(f"ecaille_{k}_{s}", (s * 0.18, y, 0.53), (0.16, 0.18, 0.1), "sombre", 0.03, 1)
# pattes courtes, écartées, griffes claires
for sy, y in ((-1, -0.42), (1, 0.6)):
    for s in (-1, 1):
        b(f"patte_{sy}_{s}", (s * 0.55, y, 0.12), (0.28, 0.3, 0.24), "vert", 0.08, 2, rot=(0, 0, s * sy * 0.3))
        for g in range(3):
            b(f"griffe_{sy}_{s}_{g}", (s * 0.62 + (g - 1) * 0.08, y - 0.17, 0.03), (0.05, 0.08, 0.05), "ventre", 0.0, 1)

for o in p:
    f.selectionner([o])
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
croco = f.fusionner(p, "crocodile_bloc")
croco.scale = (0.9, 0.9, 0.9)   # environ 3,2 m au total
f.selectionner([croco])
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
f.exporter("crocodile_bloc")
