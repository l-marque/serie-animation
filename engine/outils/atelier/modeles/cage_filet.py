"""Cage de foot réparée, avec filet (création du projet) : choix « FILETS » du vote de jour-1.

Mêmes dimensions et même orientation que cage_rouillee (4 × 2 m, ouverture face à -x, profondeur
vers +x) pour la remplacer au même endroit avec l'action « transformer ».

    blender --background --factory-startup --python engine/outils/atelier/modeles/cage_filet.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

L, H = 4.0, 2.0                 # largeur et hauteur intérieures
R = 0.06                        # rayon des tubes
X_HAUT, Z_HAUT = 0.8, 1.85      # barre arrière haute
X_BAS = 1.4                     # barre arrière au sol
Y = L / 2

f.vider()
peinture = f.materiau("Peinture_blanche", (0.93, 0.93, 0.9), rugosite=0.35)
corde = f.materiau("Filet", (0.62, 0.64, 0.66), rugosite=0.9)
acier = f.materiau("Acier_sol", (0.32, 0.34, 0.36), rugosite=0.5, metal=0.6)

# Cadre avant : poteaux et barre transversale, raccords arrondis.
f.tube("poteau_g", (0, -Y, 0), (0, -Y, H), R, peinture, bouts_ronds=True)
f.tube("poteau_d", (0, Y, 0), (0, Y, H), R, peinture, bouts_ronds=True)
f.tube("barre", (0, -Y, H), (0, Y, H), R, peinture)

# Montants arrière cintrés (barre haute -> sol), plus fins.
for s, nom in ((-1, "g"), (1, "d")):
    f.tube_courbe(f"montant_{nom}", [(0, s * Y, H), (X_HAUT * 0.6, s * Y, Z_HAUT + 0.08),
                                      (X_HAUT, s * Y, Z_HAUT), (X_BAS, s * Y, 0.25), (X_BAS, s * Y, 0.03)],
                  R * 0.7, peinture)
f.tube("barre_arriere_haute", (X_HAUT, -Y, Z_HAUT), (X_HAUT, Y, Z_HAUT), R * 0.7, peinture)
f.tube("barre_sol", (X_BAS, -Y, 0.035), (X_BAS, Y, 0.035), 0.035, acier)
f.tube("barre_sol_g", (0, -Y, 0.035), (X_BAS, -Y, 0.035), 0.035, acier)
f.tube("barre_sol_d", (0, Y, 0.035), (X_BAS, Y, 0.035), 0.035, acier)

# Filet : maille de 15 cm environ, légèrement détendu.
r_c = 0.0045
f.filet("filet_toit", [(0, -Y, H), (0, Y, H), (X_HAUT, Y, Z_HAUT), (X_HAUT, -Y, Z_HAUT)],
        26, 6, r_c, corde, affaissement=0.07, normale=(0, 0, -1))
f.filet("filet_fond", [(X_HAUT, -Y, Z_HAUT), (X_HAUT, Y, Z_HAUT), (X_BAS, Y, 0.04), (X_BAS, -Y, 0.04)],
        26, 13, r_c, corde, affaissement=0.16, normale=(1, 0, 0))
for s, nom in ((-1, "g"), (1, "d")):
    f.filet(f"filet_cote_{nom}", [(0, s * Y, 0.04), (X_BAS, s * Y, 0.04), (X_HAUT, s * Y, Z_HAUT), (0, s * Y, H)],
            9, 13, r_c, corde, affaissement=0.06, normale=(0, s, 0))

f.exporter("cage_filet")
