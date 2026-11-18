"""Tribune réparée (création du projet) : miniature de la carte de choix « TRIBUNE – 1000 PIÈCES » (jour-2).

Même principe que la miniature de cage du jour 1 : un vrai modèle à l'échelle 1, posé sur la carte avec
une échelle réduite (fiche : échelle 0,08, rotation 0). C'est la tribune nord du stade, en version
réparée : gradins en béton propre, sièges neufs rouges et bleus (mêmes couleurs que la tribune en ruine,
mais vives), toit de tôle neuf sur poteaux blancs, ruban d'inauguration doré noué en façade.
Lisible même réduite à 1,5 m de large sur la carte.

Dimensions : 18 m de large (x), 7,5 m de profondeur (y), 4,3 m de haut ; base à z = 0, face vers -y
(les sièges regardent la caméra).

    blender --background --factory-startup --python engine/outils/atelier/modeles/tribune_reparee.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
M = {
    "beton": f.materiau("Beton_neuf", (0.42, 0.41, 0.38), 0.85),
    "beton_nez": f.materiau("Nez_de_marche", (0.62, 0.61, 0.57), 0.8),
    "rouge": f.materiau("Siege_rouge_neuf", (0.62, 0.04, 0.03), 0.35),
    "bleu": f.materiau("Siege_bleu_neuf", (0.02, 0.12, 0.55), 0.35),
    "blanc": f.materiau("Acier_blanc", (0.8, 0.8, 0.78), 0.4, metal=0.2),
    "toit": f.materiau("Toit_neuf", (0.05, 0.11, 0.3), 0.45, metal=0.3),
    "jaune": f.materiau("Ruban_dore", (0.85, 0.5, 0.01), 0.35, metal=0.3),
    "vert": f.materiau("Bande_verte", (0.04, 0.2, 0.02), 0.85),
}
LARG, MARCHES, PROF, HAUT = 18.0, 5, 1.15, 0.48
X0 = -LARG / 2
pieces = []

# Gradins : une marche = un bloc ; nez de marche plus clair (lit la forme en escalier de loin).
for k in range(MARCHES):
    y = k * PROF + PROF / 2
    h = (k + 1) * HAUT
    pieces.append(f.boite("gradin", (0, y, h / 2), (LARG, PROF, h), M["beton"], biseau=0.03, segments=1))
    pieces.append(f.boite("nez", (0, k * PROF + 0.06, h - 0.03), (LARG + 0.02, 0.14, 0.08), M["beton_nez"]))
# murs de côté
for s in (-1, 1):
    pieces.append(f.boite("joue", (s * (LARG / 2 + 0.15), MARCHES * PROF / 2, MARCHES * HAUT / 2 + 0.1),
                          (0.3, MARCHES * PROF, MARCHES * HAUT + 0.2), M["beton_nez"], biseau=0.04, segments=1))
# bande d'herbe au pied (la tribune posée sur la pelouse neuve)
pieces.append(f.boite("herbe", (0, -0.8, 0.02), (LARG + 1.0, 1.6, 0.04), M["vert"]))

# Sièges neufs : blocs de 6 sièges d'une même couleur, rouge et bleu en damier (comme la vraie tribune).
for k in range(MARCHES):
    y = k * PROF + 0.5
    h = (k + 1) * HAUT
    x = X0 + 0.45
    while x < LARG / 2 - 0.3:
        mat = M["rouge"] if (int((x - X0) / 3.0) + k) % 2 else M["bleu"]
        pieces.append(f.boite("assise", (x, y - 0.05, h + 0.2), (0.44, 0.4, 0.08), mat))
        pieces.append(f.boite("dossier", (x, y + 0.16, h + 0.44), (0.44, 0.07, 0.44), mat, rotation=(math.radians(-8), 0, 0)))
        x += 0.6

# Toit : poteaux blancs à l'arrière, porte-à-faux, tôle neuve d'un seul tenant avec rive blanche.
yb = MARCHES * PROF + 0.3
for x in (-8.0, -2.7, 2.7, 8.0):
    pieces.append(f.tube("poteau", (x, yb, 0), (x, yb, 4.25), 0.12, M["blanc"]))
    pieces.append(f.tube("bras", (x, yb, 4.25), (x, -0.6, 3.9), 0.08, M["blanc"]))
pente = math.atan2(4.25 - 3.9, yb + 0.6)
pieces.append(f.boite("toit", (0, (yb - 0.6) / 2, 4.15), (LARG + 0.6, yb + 1.1, 0.1), M["toit"], biseau=0.02,
                      segments=1, rotation=(pente, 0, 0)))
pieces.append(f.boite("rive", (0, -0.6, 3.92), (LARG + 0.6, 0.1, 0.22), M["blanc"], biseau=0.02, segments=1))
# Ruban d'inauguration doré tendu en façade, avec un gros nœud au centre : « tout neuf, on coupe le ruban ».
pieces.append(f.boite("ruban", (0, -0.35, 0.95), (LARG + 0.4, 0.04, 0.16), M["jaune"]))
for s_ in (-1, 1):
    pieces.append(f.boite("boucle", (s_ * 0.42, -0.4, 1.0), (0.8, 0.08, 0.5), M["jaune"], biseau=0.06, segments=1,
                          rotation=(0, math.radians(-22 * s_), 0)))
    pieces.append(f.boite("pan", (s_ * 0.22, -0.4, 0.55), (0.16, 0.05, 0.7), M["jaune"],
                          rotation=(0, math.radians(18 * s_), 0)))
pieces.append(f.boite("noeud", (0, -0.43, 0.98), (0.26, 0.1, 0.26), M["jaune"], biseau=0.04, segments=1))

f.fusionner(pieces, "tribune_reparee")
f.exporter("tribune_reparee")
