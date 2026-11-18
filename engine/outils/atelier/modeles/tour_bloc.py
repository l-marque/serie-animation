"""Tour de garde en blocs « tour_bloc » (série « 7 Jours avant l'Attaque », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/tour_bloc.py

Tour carrée de 5 m : fût de pierre claire (2,6 m de côté) aux angles renforcés, plateforme qui
déborde sur des consoles, créneaux, porte en bois cintrée vers -y, meurtrières. Même pierre que
rempart_bloc (les deux vont ensemble). Détails : longue-vue posée sur un créneau, cloche d'alarme
dorée sous un petit portique, échelle de bois appuyée sur le côté. Base à z = 0, regarde vers -y.
"""
import math
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
M = {
    "pierre": f.materiau("Pierre_claire", (0.62, 0.48, 0.3), 0.8),
    "angle": f.materiau("Pierre_doree", (0.5, 0.37, 0.22), 0.8),
    "chapeau": f.materiau("Pierre_chapeau", (0.75, 0.66, 0.5), 0.7),
    "bois": f.materiau("Bois_porte", (0.45, 0.22, 0.07), 0.7),
    "ferrure": f.materiau("Ferrure", (0.12, 0.12, 0.14), 0.5, metal=0.6),
    "noir": f.materiau("Meurtriere", (0.04, 0.035, 0.04), 0.9),
    "or": f.materiau("Cloche_or", (1.0, 0.68, 0.1), 0.3, metal=0.8),
    "toile": f.materiau("Toile_rouge", (0.85, 0.08, 0.04), 0.6),
}
C = 2.6       # côté du fût
HF = 3.9      # hauteur du fût
p = [f.boite("fut", (0, 0, HF / 2), (C, C, HF), M["pierre"], biseau=0.14, segments=3)]
for sx in (-1, 1):
    for sy in (-1, 1):
        for k in range(4):   # pierres d'angle en harpe
            l = 0.7 if k % 2 == 0 else 0.45
            p.append(f.boite(f"angle_{sx}{sy}{k}", (sx * (C / 2 - l / 2 + 0.06), sy * (C / 2 - 0.2 + 0.06), 0.45 + k * 0.95),
                             (l, 0.5, 0.6), M["angle"], biseau=0.08, segments=2))
# consoles et plateforme débordante
for i in range(3):
    for s in (-1, 1):
        x = (i - 1) * 0.9
        p.append(f.boite(f"console_y{i}{s}", (x, s * (C / 2 + 0.1), HF - 0.15), (0.35, 0.3, 0.3), M["angle"], biseau=0.06,
                         segments=1))
        p.append(f.boite(f"console_x{i}{s}", (s * (C / 2 + 0.1), x, HF - 0.15), (0.3, 0.35, 0.3), M["angle"], biseau=0.06,
                         segments=1))
p.append(f.boite("plateforme", (0, 0, HF + 0.12), (C + 0.6, C + 0.6, 0.3), M["chapeau"], biseau=0.08, segments=2))
# créneaux : 3 merlons par côté (coins partagés)
D = (C + 0.6) / 2 - 0.25
for i, t in enumerate((-1, 0, 1)):
    for s in (-1, 1):
        p.append(f.boite(f"merlon_y{i}{s}", (t * (D - 0.05), s * D, HF + 0.27 + 0.33), (0.6, 0.5, 0.66), M["pierre"],
                         biseau=0.09, segments=2))
        if t == 0:
            p.append(f.boite(f"merlon_x{i}{s}", (s * D, 0, HF + 0.27 + 0.33), (0.5, 0.6, 0.66), M["pierre"], biseau=0.09,
                             segments=2))
# porte cintrée vers -y
y0 = -C / 2
p.append(f.boite("porte", (0, y0 - 0.04, 0.85), (1.0, 0.12, 1.7), M["bois"], biseau=0.05, segments=2))
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.5, depth=0.12, location=(0, y0 - 0.04, 1.7),
                                    rotation=(math.pi / 2, 0, 0))
arc = bpy.context.object
arc.data.materials.append(M["bois"])
p.append(arc)
for z in (0.5, 1.3):
    p.append(f.boite(f"ferrure_{z}", (0, y0 - 0.11, z), (0.95, 0.04, 0.1), M["ferrure"], biseau=0.02, segments=1))
p.append(f.boite("encadrement", (0, y0 - 0.02, 2.25), (1.3, 0.1, 0.25), M["angle"], biseau=0.06, segments=2))
# meurtrières (face et côtés)
for x, y, rx in ((0, y0 - 0.01, (0.16, 0.05, 0.7)), (-C / 2 - 0.01, 0, (0.05, 0.16, 0.7)), (C / 2 + 0.01, 0, (0.05, 0.16, 0.7))):
    p.append(f.boite("meurtriere", (x, y, 3.0 if y < 0 else 2.0), rx, M["noir"]))
# portique et cloche d'alarme (sur le côté +x arrière)
p.append(f.boite("portique_g", (0.55, 0.55, HF + 0.9), (0.1, 0.1, 1.2), M["bois"], biseau=0.03, segments=1))
p.append(f.boite("portique_d", (0.55, -0.15, HF + 0.9), (0.1, 0.1, 1.2), M["bois"], biseau=0.03, segments=1))
p.append(f.boite("portique_h", (0.55, 0.2, HF + 1.5), (0.12, 0.85, 0.12), M["bois"], biseau=0.03, segments=1))
cloche = f.revolution("cloche", [(0.0, 0.42), (0.1, 0.4), (0.16, 0.3), (0.2, 0.12), (0.26, 0.0), (0.0, 0.0)], M["or"],
                      cotes=16)
cloche.location = (0.55, 0.2, HF + 0.98)
p.append(cloche)
# longue-vue sur un merlon avant
lv = f.tube("longue_vue", (-(D - 0.05), -D + 0.2, HF + 1.0), (-(D - 0.05) - 0.1, -D - 0.6, HF + 1.12), 0.07, M["or"],
            cotes=10)
p.append(lv)
# fanions rouges sous la plateforme, côté -y (une touche de couleur franche, lisible de loin)
for k in range(5):
    x = -1.2 + 0.6 * k
    p.append(f.boite(f"fanion_{k}", (x, -C / 2 - 0.33, HF - 0.3), (0.36, 0.04, 0.36), M["toile"], biseau=0.03, segments=1,
                     rotation=(0, 0.785, 0)))
p.append(f.boite("corde", (0, -C / 2 - 0.33, HF - 0.06), (2.9, 0.04, 0.04), M["bois"]))
# échelle de bois appuyée sur le côté -x
for s in (-1, 1):
    p.append(f.boite(f"montant_{s}", (-C / 2 - 0.35, s * 0.3, 1.68), (0.08, 0.08, 3.4), M["bois"], biseau=0.02, segments=1,
                     rotation=(0, 0.2, 0)))
for k in range(6):
    z = 0.35 + k * 0.55
    p.append(f.boite(f"barreau_{k}", (-C / 2 - 0.35 + (z - 1.6) * math.tan(0.2), 0, z), (0.06, 0.66, 0.06),
                     M["bois"]))

for o in p:
    f.selectionner([o])
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
f.fusionner(p, "tour_bloc")
f.exporter("tour_bloc")
