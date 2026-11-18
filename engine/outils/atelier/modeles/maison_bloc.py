"""Maison en blocs « maison_bloc » (série « 7 Jours avant l'Attaque », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/maison_bloc.py

Petite maison d'île, lisible de loin : murs crème, grand toit rouge corail à deux pans qui déborde,
porte bleu turquoise vers -y, fenêtres à volets jaunes, cheminée de pierre. Blocs arrondis (biseaux
généreux) comme les habitants de la série. Détails : jardinière de fleurs roses sous la fenêtre,
lanterne à côté de la porte, marche en bois, une tuile de travers sur le toit (construite à la hâte :
il ne reste que sept jours). Environ 4,4 × 4,0 × 4,5 m, base à z = 0, regarde vers -y.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

f.vider()
M = {
    "mur": f.materiau("Mur_creme", (0.85, 0.66, 0.4), 0.5),
    "soubassement": f.materiau("Soubassement_pierre", (0.55, 0.5, 0.45), 0.85),
    "toit": f.materiau("Toit_corail", (0.8, 0.07, 0.02), 0.45),
    "toit_sombre": f.materiau("Toit_corail_sombre", (0.55, 0.05, 0.02), 0.5),
    "porte": f.materiau("Porte_turquoise", (0.0, 0.42, 0.62), 0.4),
    "bois": f.materiau("Bois_clair", (0.5, 0.28, 0.1), 0.7),
    "vitre": f.materiau("Vitre_ciel", (0.35, 0.68, 0.95), 0.1),
    "volet": f.materiau("Volet_jaune", (1.0, 0.65, 0.02), 0.45),
    "blanc": f.materiau("Cadre_blanc", (0.92, 0.92, 0.9), 0.4),
    "fleur": f.materiau("Fleurs_roses", (1.0, 0.25, 0.55), 0.5),
    "feuille": f.materiau("Feuilles", (0.1, 0.6, 0.05), 0.6),
    "pierre": f.materiau("Cheminee_pierre", (0.5, 0.47, 0.45), 0.85),
    "or": f.materiau("Lanterne_or", (1.0, 0.7, 0.1), 0.3, metal=0.6),
    "flamme": f.materiau("Lanterne_lumiere", (1.0, 0.75, 0.3), 0.5, emission=2.0),
}
L, P, H = 3.6, 3.2, 2.5        # murs : longueur (x), profondeur (y), hauteur
y0 = -P / 2                    # façade
p = []

p.append(f.boite("soubassement", (0, 0, 0.15), (L + 0.2, P + 0.2, 0.3), M["soubassement"], biseau=0.1, segments=2))
p.append(f.boite("murs", (0, 0, 0.3 + H / 2), (L, P, H), M["mur"], biseau=0.12, segments=3))
# toit : deux pans débordants + faîtage
p.append(f.prisme("toit", (0, 0, 0.3 + H - 0.05), L + 0.7, P + 1.0, 1.7, M["toit"], biseau=0.12, segments=3))
p.append(f.boite("faitage", (0, 0, 0.3 + H + 1.6), (L + 0.8, 0.35, 0.25), M["toit_sombre"], biseau=0.1, segments=2))
pente = math.atan(1.7 / ((P + 1.0) / 2))
for i in range(3):
    t = (i + 1) / 4
    y = -(P + 1.0) / 2 * (1 - t)
    z = 0.3 + H - 0.05 + 1.7 * t
    p.append(f.boite(f"rang_{i}", (0, y - 0.04, z + 0.04), (L + 0.72, 0.12, 0.1), M["toit_sombre"], biseau=0.04,
                     segments=1, rotation=(pente, 0, 0)))
# tuile de travers (construite à la hâte)
p.append(f.boite("tuile", (1.0, -1.0, 0.3 + H + 0.75), (0.5, 0.35, 0.1), M["toit"], biseau=0.04, segments=1,
                 rotation=(pente, 0.25, 0.35)))
# cheminée
p.append(f.boite("cheminee", (-1.0, 0.6, 0.3 + H + 1.3), (0.6, 0.6, 1.4), M["pierre"], biseau=0.08, segments=2))
p.append(f.boite("cheminee_haut", (-1.0, 0.6, 0.3 + H + 2.05), (0.75, 0.75, 0.18), M["pierre"], biseau=0.06, segments=2))
# porte (vers -y), cadre, marche, poignée
p.append(f.boite("cadre_porte", (-0.55, y0 - 0.04, 1.35), (1.15, 0.12, 2.1), M["blanc"], biseau=0.05, segments=2))
p.append(f.boite("porte", (-0.55, y0 - 0.09, 1.3), (0.9, 0.1, 1.9), M["porte"], biseau=0.06, segments=2))
p.append(f.boite("poignee", (-0.25, y0 - 0.17, 1.25), (0.1, 0.08, 0.1), M["or"], biseau=0.03, segments=1))
p.append(f.boite("marche", (-0.55, y0 - 0.3, 0.12), (1.3, 0.55, 0.24), M["bois"], biseau=0.06, segments=2))
# fenêtre de façade + volets + jardinière fleurie
xf = 1.0
p.append(f.boite("cadre_fenetre", (xf, y0 - 0.04, 1.7), (1.0, 0.1, 1.0), M["blanc"], biseau=0.05, segments=2))
p.append(f.boite("vitre", (xf, y0 - 0.08, 1.7), (0.78, 0.06, 0.78), M["vitre"], biseau=0.03, segments=1))
p.append(f.boite("croisillon_v", (xf, y0 - 0.11, 1.7), (0.08, 0.04, 0.8), M["blanc"]))
p.append(f.boite("croisillon_h", (xf, y0 - 0.11, 1.7), (0.8, 0.04, 0.08), M["blanc"]))
for s in (-1, 1):
    p.append(f.boite(f"volet_{s}", (xf + s * 0.75, y0 - 0.06, 1.7), (0.45, 0.08, 1.0), M["volet"], biseau=0.05,
                     segments=2))
p.append(f.boite("jardiniere", (xf, y0 - 0.25, 1.1), (1.05, 0.3, 0.25), M["bois"], biseau=0.05, segments=2))
for k in range(5):
    x = xf - 0.4 + 0.2 * k
    p.append(f.boite(f"feuille_{k}", (x, y0 - 0.25, 1.3), (0.2, 0.2, 0.18), M["feuille"], biseau=0.06, segments=1))
    p.append(f.boite(f"fleur_{k}", (x + 0.03, y0 - 0.28, 1.42 + 0.04 * (k % 2)), (0.14, 0.14, 0.14), M["fleur"],
                     biseau=0.05, segments=1))
# fenêtres latérales (côtés ±x)
for s in (-1, 1):
    p.append(f.boite(f"cadre_lat_{s}", (s * (L / 2 + 0.04), 0.2, 1.7), (0.1, 0.9, 0.9), M["blanc"], biseau=0.05, segments=2))
    p.append(f.boite(f"vitre_lat_{s}", (s * (L / 2 + 0.08), 0.2, 1.7), (0.06, 0.7, 0.7), M["vitre"], biseau=0.03,
                     segments=1))
# lanterne
p.append(f.boite("potence", (-1.35, y0 - 0.15, 2.25), (0.06, 0.3, 0.06), M["or"]))
p.append(f.boite("lanterne", (-1.35, y0 - 0.3, 2.05), (0.18, 0.18, 0.28), M["flamme"], biseau=0.04, segments=1))
p.append(f.boite("lanterne_toit", (-1.35, y0 - 0.3, 2.23), (0.24, 0.24, 0.07), M["or"], biseau=0.02, segments=1))

f.fusionner(p, "maison_bloc")
f.exporter("maison_bloc")
