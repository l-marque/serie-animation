"""Rempart en blocs « rempart_bloc » (série « 7 Jours avant l'Attaque », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/rempart_bloc.py

Tronçon de mur crénelé de 6 m (selon x), 1,1 m d'épaisseur, 3,1 m de haut créneaux compris. Gros
blocs de pierre claire arrondis posés en quinconce (deux teintes), créneaux, chemin de ronde.
Les deux bouts sont droits : on peut aligner plusieurs tronçons bout à bout (pas de 6 m).
Détails : bannière jaune soleil (sans motif) accrochée au milieu, deux torches, un bloc plus sombre
rapiécé et une touffe d'herbe au pied. Base à z = 0, face visible vers -y.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
rng = random.Random(3)
M = {
    "pierre": f.materiau("Pierre_claire", (0.62, 0.48, 0.3), 0.8),
    "pierre2": f.materiau("Pierre_doree", (0.5, 0.37, 0.22), 0.8),
    "rapiece": f.materiau("Pierre_grise", (0.3, 0.32, 0.36), 0.85),
    "chapeau": f.materiau("Pierre_chapeau", (0.75, 0.66, 0.5), 0.7),
    "banniere": f.materiau("Banniere_jaune", (1.0, 0.68, 0.0), 0.55),
    "bois": f.materiau("Bois_torche", (0.4, 0.2, 0.07), 0.7),
    "flamme": f.materiau("Flamme", (1.0, 0.45, 0.05), 0.5, emission=4.0),
    "herbe": f.materiau("Touffe", (0.15, 0.65, 0.05), 0.8),
}
LONG, EP = 6.0, 1.1
p = []
rangs = 4
hb = 0.6
for r in range(rangs):
    decale = 0.5 if r % 2 else 0.0
    x = -LONG / 2
    largeurs = []
    reste = LONG
    premier = 0.5 if decale else 1.0
    largeurs.append(premier)
    reste -= premier
    while reste > 1e-6:
        w = min(1.0, reste)
        largeurs.append(w)
        reste -= w
    for k, w in enumerate(largeurs):
        cx = x + w / 2
        mat = "pierre" if (k + r) % 3 else "pierre2"
        if r == 1 and k == 3:
            mat = "rapiece"
        p.append(f.boite(f"bloc_{r}_{k}", (cx, 0, hb * r + hb / 2), (w - 0.03, EP, hb - 0.03), M[mat], biseau=0.09,
                         segments=2))
        x += w
z_top = hb * rangs
p.append(f.boite("chapeau", (0, 0, z_top + 0.1), (LONG, EP + 0.2, 0.2), M["chapeau"], biseau=0.07, segments=2))
for k in range(5):  # créneaux : merlons de 0,8 m, vides de 0,5 m
    x = -LONG / 2 + 0.4 + k * 1.3
    p.append(f.boite(f"merlon_{k}", (x, -0.15, z_top + 0.2 + 0.4), (0.8, 0.7, 0.8), M["pierre"], biseau=0.1, segments=2))
# bannière au milieu, en deux pans avec pointe (queue d'aronde)
p.append(f.boite("hampe", (0, -0.62, z_top - 0.05), (1.3, 0.08, 0.08), M["bois"], biseau=0.03, segments=1))
p.append(f.boite("banniere", (0, -0.6, z_top - 0.75), (1.1, 0.05, 1.3), M["banniere"], biseau=0.02, segments=1))
for s in (-1, 1):
    p.append(f.boite(f"pointe_{s}", (s * 0.3, -0.6, z_top - 1.5), (0.4, 0.05, 0.4), M["banniere"], biseau=0.02,
                     segments=1, rotation=(0, 0.785, 0)))
# torches de part et d'autre
for s in (-1, 1):
    x = s * 2.0
    p.append(f.boite(f"support_{s}", (x, -0.65, 1.55), (0.12, 0.25, 0.12), M["bois"], biseau=0.03, segments=1))
    p.append(f.boite(f"manche_{s}", (x, -0.75, 1.75), (0.12, 0.12, 0.5), M["bois"], biseau=0.04, segments=1,
                     rotation=(0.25, 0, 0)))
    p.append(f.boite(f"flamme_{s}", (x, -0.83, 2.1), (0.2, 0.2, 0.28), M["flamme"], biseau=0.08, segments=2))
# touffe d'herbe au pied
for k in range(4):
    p.append(f.boite(f"herbe_{k}", (-1.7 + 0.12 * k, -0.62, 0.19 + 0.03 * k), (0.12, 0.12, 0.3 + 0.08 * (k % 2)),
                     M["herbe"], biseau=0.04, segments=1, rotation=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0)))

f.fusionner(p, "rempart_bloc")
f.exporter("rempart_bloc")
