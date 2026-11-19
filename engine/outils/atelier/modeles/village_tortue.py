"""Décor et accessoires de la série « Le Village sur la Tortue » (création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/village_tortue.py [-- prairie_tortue cabane_bloc ...]

Écrit un GLB par modèle dans engine/assets/modeles/<id>/<id>.glb :
- prairie_tortue : prairie de 700 m (vert vif), arbres en blocs dispersés (couloir libre devant la tortue,
  vers -y), rochers, fleurs, collines arrondies au loin ; sentier de terre qui part vers -y ;
- montagne_mystere : l'intrigue. Montagne en gradins bleu-violet très loin (à placer vers (0, -420, 0)),
  sommet dans un anneau de nuages, avec une lumière dorée qui brille au sommet ; 150 m de haut ;
- cabane_bloc : la seule maison du village (2,8 × 2,6 m, 3,3 m de haut), planches, toit de paille orange,
  porte vers -y, lanterne ;
- panneau_carapace : panneau d'entrée du village « CARAPACE » (2,6 m de large, 2,2 m de haut), face -y ;
- puits_bloc : puits de pierre à toit de bois (1,8 m de diamètre, 2,6 m de haut), seau ;
- zzz_bloc : trois « Z » en blocs (1,6 m de haut), à poser au-dessus de la tête de la tortue qui dort.
Base à z = 0 pour tout ; les modèles regardent vers -y.
"""
import math
import random
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402


def mats():
    return {
        "herbe": f.materiau("Prairie_herbe", (0.16, 0.5, 0.05), 0.92),
        "herbe_claire": f.materiau("Prairie_herbe_claire", (0.3, 0.62, 0.08), 0.9),
        "terre": f.materiau("Sentier_terre", (0.45, 0.28, 0.12), 0.95),
        "tronc": f.materiau("Arbre_tronc", (0.32, 0.17, 0.07), 0.85),
        "feuille_a": f.materiau("Arbre_feuilles_a", (0.08, 0.42, 0.06), 0.75),
        "feuille_b": f.materiau("Arbre_feuilles_b", (0.16, 0.55, 0.06), 0.75),
        "feuille_c": f.materiau("Arbre_feuilles_c", (0.04, 0.3, 0.08), 0.75),
        "roche": f.materiau("Rocher", (0.5, 0.5, 0.52), 0.9),
        "fleur_j": f.materiau("Fleur_jaune", (1.0, 0.82, 0.05), 0.5),
        "fleur_r": f.materiau("Fleur_rose", (1.0, 0.3, 0.6), 0.5),
        "fleur_b": f.materiau("Fleur_blanche", (0.95, 0.95, 0.95), 0.5),
        "colline": f.materiau("Colline", (0.12, 0.42, 0.08), 0.9),
        "brume": f.materiau("Colline_brume", (0.45, 0.6, 0.62), 0.95, emission=0.15),
        "bois": f.materiau("Bois_planches", (0.55, 0.32, 0.12), 0.75),
        "bois_sombre": f.materiau("Bois_sombre", (0.33, 0.18, 0.07), 0.8),
        "paille": f.materiau("Toit_paille", (0.95, 0.6, 0.12), 0.7),
        "paille_sombre": f.materiau("Toit_paille_sombre", (0.75, 0.42, 0.06), 0.75),
        "vitre": f.materiau("Vitre", (0.35, 0.68, 0.95), 0.1),
        "lumiere": f.materiau("Lanterne", (1.0, 0.75, 0.3), 0.5, emission=2.5),
        "or": f.materiau("Or", (1.0, 0.7, 0.1), 0.3, metal=0.6),
        "pierre": f.materiau("Pierre", (0.62, 0.6, 0.56), 0.9),
        "pierre_sombre": f.materiau("Pierre_sombre", (0.45, 0.43, 0.4), 0.9),
        "panneau": f.materiau("Panneau_vert", (0.04, 0.32, 0.16), 0.5),
        "blanc": f.materiau("Blanc", (0.95, 0.95, 0.92), 0.4),
        "eau": f.materiau("Eau_puits", (0.05, 0.3, 0.55), 0.1),
        "mont_a": f.materiau("Montagne_a", (0.38, 0.42, 0.66), 0.95),
        "mont_b": f.materiau("Montagne_b", (0.48, 0.5, 0.74), 0.95),
        "neige": f.materiau("Montagne_neige", (0.85, 0.88, 0.98), 0.8),
        "nuage": f.materiau("Nuage", (0.95, 0.95, 1.0), 0.9),
        "phare": f.materiau("Lumiere_doree", (1.0, 0.55, 0.05), 0.3, emission=5.0),
        "halo": f.materiau("Halo_dore", (1.0, 0.7, 0.15), 0.3, emission=2.5),
        "zzz": f.materiau("Zzz", (0.85, 0.92, 1.0), 0.4, emission=0.6),
    }


def b(p, M, nom, c, t, m, bis=0.08, seg=2, rot=(0, 0, 0)):
    o = f.boite(nom, c, t, M[m], biseau=bis, segments=seg, rotation=rot)
    p.append(o)
    return o


def texte(p, mat, chaine, centre, taille, epaisseur=0.04, rot_x=math.pi / 2):
    bpy.ops.object.text_add(location=centre, rotation=(rot_x, 0, 0))
    o = bpy.context.object
    o.data.body = chaine
    o.data.size = taille
    o.data.extrude = epaisseur
    o.data.align_x = "CENTER"
    o.data.align_y = "CENTER"
    o.data.materials.append(mat)
    bpy.ops.object.convert(target="MESH")
    p.append(o)
    return o


# ----- modèles ----------------------------------------------------------------------------------
def arbre(p, M, x, y, s, k):
    h = 2.2 * s
    b(p, M, f"tronc_{k}", (x, y, h / 2), (0.7 * s, 0.7 * s, h), "tronc", 0.08)
    fe = ["feuille_a", "feuille_b", "feuille_c"][k % 3]
    b(p, M, f"feuilles1_{k}", (x, y, h + 1.2 * s), (3.0 * s, 3.0 * s, 2.4 * s), fe, 0.35 * s, 2)
    b(p, M, f"feuilles2_{k}", (x + 0.2 * s, y - 0.1 * s, h + 2.9 * s), (2.0 * s, 2.0 * s, 1.4 * s), fe, 0.3 * s, 2)


def prairie_tortue():
    M = mats()
    p = []
    b(p, M, "sol", (0, 0, -0.25), (2400, 2400, 0.5), "herbe", 0)
    # sentier qui part devant la tortue (vers -y) et serpente
    for k in range(40):
        y = -16 - 5 * k
        x = 3.0 * math.sin(k * 0.25)
        b(p, M, f"sentier_{k}", (x, y, 0.01), (4.2 - 0.04 * k, 5.6, 0.04), "terre", 0.02, 1, rot=(0, 0, 0.1 * math.cos(k * 0.25)))
    rnd = random.Random(7)
    k = 0
    while k < 150:
        r = rnd.uniform(22, 200)
        a = rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if y < -12 and abs(x - 3 * math.sin((-16 - y) / 5 * 0.25)) < 9:
            continue                                     # couloir du sentier libre
        arbre(p, M, x, y, rnd.uniform(0.8, 1.5), k)
        k += 1
    for k in range(40):
        r, a = rnd.uniform(16, 120), rnd.uniform(0, 2 * math.pi)
        s = rnd.uniform(0.5, 1.6)
        b(p, M, f"rocher_{k}", (r * math.cos(a), r * math.sin(a), 0.3 * s), (1.4 * s, 1.1 * s, 0.9 * s), "roche", 0.25 * s, 2,
          rot=(0, 0, a))
    for k in range(260):
        r, a = rnd.uniform(13, 90), rnd.uniform(0, 2 * math.pi)
        m = ["fleur_j", "fleur_r", "fleur_b"][k % 3]
        b(p, M, f"fleur_{k}", (r * math.cos(a), r * math.sin(a), 0.15), (0.35, 0.35, 0.3), m, 0.08, 1)
    for k in range(70):
        r, a = rnd.uniform(12, 80), rnd.uniform(0, 2 * math.pi)
        b(p, M, f"touffe_{k}", (r * math.cos(a), r * math.sin(a), 0.2), (1.2, 0.9, 0.45), "herbe_claire", 0.18, 2)
    # collines arrondies au loin (pas devant : la montagne mystère doit rester visible)
    for k in range(14):
        a = math.radians(-60 + 240 * k / 13)
        r = rnd.uniform(240, 300)
        s = rnd.uniform(30, 55)
        b(p, M, f"colline_{k}", (r * math.cos(a), r * math.sin(a), 0), (s * 2.2, s * 1.6, s * 0.9), "colline", s * 0.4, 4)
    # collines lointaines et brumeuses de part et d'autre du chemin vers la montagne (perspective atmosphérique)
    for k in range(12):
        s_ = rnd.uniform(40, 80)
        cote = -1 if k % 2 else 1
        x = cote * rnd.uniform(140, 420)
        y = -rnd.uniform(380, 760)
        b(p, M, f"colline_brume_{k}", (x, y, 0), (s_ * 2.6, s_ * 1.6, s_ * 0.8), "brume", s_ * 0.35, 4)
    f.fusionner(p, "prairie_tortue")
    f.exporter("prairie_tortue")


def montagne_mystere():
    """L'énigme de la série : montagne lointaine et brumeuse (couleur proche du ciel), sommet caché à demi
    par des bancs de nuages, lumière dorée au sommet et rayon doré qui monte vers le ciel.
    Hauteur du sommet : 165 m (lumière vers 170 m), rayon jusqu'à 420 m ; à placer à environ 800 m."""
    M = mats()
    M["mont_a"] = f.materiau("Montagne_brume_a", (0.5, 0.55, 0.78), 0.95, emission=0.35)
    M["mont_b"] = f.materiau("Montagne_brume_b", (0.58, 0.62, 0.84), 0.95, emission=0.35)
    M["neige"] = f.materiau("Montagne_neige_brume", (0.8, 0.84, 0.97), 0.8, emission=0.4)
    M["nuage"] = f.materiau("Nuage_brume", (0.93, 0.94, 1.0), 0.9, emission=0.5)
    M["rayon"] = f.materiau("Rayon_dore", (1.0, 0.62, 0.12), 0.3, emission=4.0)
    p = []
    G = [(220, 40), (170, 35), (125, 32), (85, 26), (50, 20)]
    for g, (l, h) in enumerate(G):
        z0 = sum(hh for _, hh in G[:g])
        b(p, M, f"gradin_{g}", (0, 0, z0 + h / 2), (l, l * 0.8, h), "mont_a" if g % 2 == 0 else "mont_b", min(h * 0.3, 10), 2,
          rot=(0, 0, 0.15 * g))
    b(p, M, "neige", (0, 0, 153 + 2), (34, 28, 8), "neige", 3, 2)
    rnd = random.Random(3)
    for k in range(22):                                   # deux bancs de nuages qui cachent les flancs
        a_ = 2 * math.pi * k / 11 + rnd.uniform(-0.2, 0.2)
        z = 70 if k < 11 else 128
        r = (115 if k < 11 else 62) * rnd.uniform(0.9, 1.1)
        b(p, M, f"nuage_{k}", (r * math.cos(a_), r * 0.8 * math.sin(a_), z + rnd.uniform(-6, 6)),
          (rnd.uniform(50, 80), rnd.uniform(25, 40), rnd.uniform(12, 18)), "nuage", 6, 2, rot=(0, 0, a_))
    b(p, M, "socle", (0, 0, 160), (10, 10, 6), "pierre_sombre", 1.5, 2)
    b(p, M, "lumiere", (0, 0, 168), (7, 7, 9), "phare", 2.5, 3)
    b(p, M, "halo", (0, 0, 168), (13, 13, 3), "halo", 1.2, 2, rot=(0, 0, 0.785))
    b(p, M, "rayon", (0, 0, 295), (4.5, 4.5, 250), "rayon", 1.5, 2)
    f.fusionner(p, "montagne_mystere")
    f.exporter("montagne_mystere")


def cabane_bloc():
    M = mats()
    p = []
    L, P, H = 2.8, 2.6, 2.0
    y0 = -P / 2
    b(p, M, "plancher", (0, 0, 0.1), (L + 0.3, P + 0.3, 0.2), "bois_sombre", 0.06)
    for k in range(5):                                      # planches horizontales
        b(p, M, f"planche_{k}", (0, 0, 0.2 + H / 5 * (k + 0.5)), (L - 0.04 * (k % 2), P - 0.04 * (k % 2), H / 5 - 0.03), "bois",
          0.06, 2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b(p, M, f"poteau_{sx}_{sy}", (sx * L / 2, sy * P / 2, 0.2 + H / 2), (0.25, 0.25, H + 0.1), "bois_sombre", 0.05)
    f_toit = f.prisme("toit", (0, 0, 0.2 + H - 0.05), L + 0.9, P + 1.0, 1.4, M["paille"], biseau=0.15, segments=3)
    p.append(f_toit)
    b(p, M, "faitage", (0, 0, 0.2 + H + 1.3), (L + 1.0, 0.35, 0.25), "paille_sombre", 0.1)
    b(p, M, "porte", (-0.5, y0 - 0.06, 0.2 + 0.85), (0.8, 0.1, 1.6), "bois_sombre", 0.05)
    b(p, M, "poignee", (-0.25, y0 - 0.12, 1.0), (0.08, 0.06, 0.08), "or", 0.02, 1)
    b(p, M, "fenetre", (0.75, y0 - 0.05, 1.3), (0.7, 0.08, 0.6), "vitre", 0.03, 1)
    b(p, M, "cadre_f", (0.75, y0 - 0.03, 1.3), (0.86, 0.06, 0.76), "bois_sombre", 0.03, 1)
    b(p, M, "lanterne", (-1.15, y0 - 0.25, 1.75), (0.2, 0.2, 0.3), "lumiere", 0.04, 1)
    b(p, M, "potence", (-1.15, y0 - 0.12, 1.95), (0.06, 0.28, 0.06), "bois_sombre", 0.0, 1)
    b(p, M, "tonneau", (1.55, y0 + 0.2, 0.45), (0.6, 0.6, 0.7), "bois", 0.15, 2)
    b(p, M, "bois_empile", (-1.7, 0.4, 0.3), (0.5, 1.4, 0.6), "bois_sombre", 0.1, 2)
    f.fusionner(p, "cabane_bloc")
    f.exporter("cabane_bloc")


def panneau_carapace():
    M = mats()
    p = []
    for s in (-1, 1):
        b(p, M, f"poteau_{s}", (s * 1.05, 0, 1.0), (0.18, 0.18, 2.0), "bois_sombre", 0.04)
    b(p, M, "cadre", (0, 0, 1.6), (2.6, 0.16, 0.95), "blanc", 0.06, 2)
    b(p, M, "fond", (0, -0.03, 1.6), (2.42, 0.14, 0.78), "panneau", 0.04, 2)
    texte(p, M["blanc"], "CARAPACE", (0, -0.13, 1.6), 0.4, 0.025)
    f.fusionner(p, "panneau_carapace")
    f.exporter("panneau_carapace")


def puits_bloc():
    M = mats()
    p = []
    n = 10
    for k in range(n):
        a = 2 * math.pi * k / n
        b(p, M, f"pierre_{k}", (0.8 * math.cos(a), 0.8 * math.sin(a), 0.45), (0.55, 0.38, 0.9),
          "pierre" if k % 2 else "pierre_sombre", 0.08, 2, rot=(0, 0, a + math.pi / 2))
    b(p, M, "eau", (0, 0, 0.6), (1.2, 1.2, 0.1), "eau", 0.05, 1)
    for s in (-1, 1):
        b(p, M, f"montant_{s}", (s * 0.85, 0, 1.4), (0.15, 0.15, 1.9), "bois_sombre", 0.04)
    b(p, M, "treuil", (0, 0, 1.75), (1.8, 0.14, 0.14), "bois", 0.04)
    p.append(f.prisme("toit", (0, 0, 2.2), 2.2, 1.9, 0.7, M["paille"], biseau=0.08, segments=2))
    b(p, M, "corde", (0.2, 0, 1.4), (0.04, 0.04, 0.7), "bois_sombre", 0.0, 1)
    b(p, M, "seau", (0.2, 0, 1.0), (0.32, 0.32, 0.32), "bois", 0.06, 2)
    f.fusionner(p, "puits_bloc")
    f.exporter("puits_bloc")


def zzz_bloc():
    M = mats()
    p = []
    for k, (x, z, t) in enumerate([(0, 0.35, 0.7), (0.55, 0.95, 0.55), (0.95, 1.4, 0.42)]):
        o = texte(p, M["zzz"], "Z", (x, 0, z), t, 0.08)
        o.rotation_euler.z = 0
    f.fusionner(p, "zzz_bloc")
    f.exporter("zzz_bloc")


TOUS = {"prairie_tortue": prairie_tortue, "montagne_mystere": montagne_mystere, "cabane_bloc": cabane_bloc,
        "panneau_carapace": panneau_carapace, "puits_bloc": puits_bloc, "zzz_bloc": zzz_bloc}
demandes = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(TOUS)
for nom in demandes:
    f.vider()
    TOUS[nom]()
