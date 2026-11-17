"""Stade en ruine (création du projet) : le terrain boueux de Guillaume + les ruines autour, en blocs.

Part de engine/assets/modeles/terrain_boueux/terrain_boueux_source.blend (terrain 105 × 68 m modélisé
par Guillaume, cages en x = ±52,5) et écrit stade_ruine.blend, collection « Stade », lue par le
moteur comme un asset de bibliothèque (.blend + collection).

    blender --background --factory-startup --python engine/outils/atelier/modeles/stade_ruine.py

Ajouts : tribune nord en partie effondrée (gradins, sièges cassés, toit troué), 4 pylônes d'éclairage
rouillés (un penché), tableau d'affichage décroché, deux abris de touche abîmés, cages rouillées avec
restes de filet déchiré, débris (pneus, plots, planches, gravats) et touffes d'herbes folles.
Repères nommés « REP_* » (empties) pour viser les plans de caméra.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

DOSSIER = f.MODELES / "terrain_boueux"
rng = random.Random(42)

bpy.ops.wm.open_mainfile(filepath=str(DOSSIER / "terrain_boueux_source.blend"))
sc = bpy.context.scene

# ----- nettoyage : caméras, lumière, ballon et filets intacts (l'histoire veut des cages sans filet) ----
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name in ("Ballon", "Filet_D", "Filet_G"):
        bpy.data.objects.remove(o, do_unlink=True)

M = {
    "beton": f.materiau("Beton_tribune", (0.13, 0.125, 0.115), 0.92),
    "beton_sombre": f.materiau("Beton_fissure", (0.07, 0.07, 0.07), 0.95),
    "gravats": f.materiau("Gravats", (0.09, 0.085, 0.08), 0.95),
    "rouille": f.materiau("Rouille", (0.3, 0.09, 0.02), 0.75, metal=0.3),
    "acier": f.materiau("Acier_peint_ecaille", (0.22, 0.25, 0.27), 0.6, metal=0.5),
    "siege_rouge": f.materiau("Siege_rouge_passe", (0.42, 0.05, 0.04), 0.5),
    "siege_bleu": f.materiau("Siege_bleu_passe", (0.04, 0.12, 0.35), 0.5),
    "verre_casse": f.materiau("Projecteur_eteint", (0.05, 0.06, 0.07), 0.2),
    "verre_ok": f.materiau("Projecteur_sale", (0.55, 0.52, 0.4), 0.3),
    "panneau": f.materiau("Tableau_noir", (0.02, 0.02, 0.025), 0.6),
    "chiffre": f.materiau("Chiffre_eteint", (0.35, 0.2, 0.02), 0.5),
    "bois": f.materiau("Bois_pourri", (0.2, 0.11, 0.04), 0.9),
    "pneu": f.materiau("Pneu", (0.02, 0.02, 0.02), 0.85),
    "plot": f.materiau("Plot_orange", (0.8, 0.18, 0.01), 0.55),
    "herbe": f.materiau("Herbes_folles", (0.08, 0.3, 0.03), 0.9),
    "filet": f.materiau("Filet_dechire", (0.45, 0.45, 0.43), 0.9),
    "toit": f.materiau("Toit_tole", (0.07, 0.075, 0.08), 0.6, metal=0.4),
}
NOUVEAUX = []


def garder(o):
    NOUVEAUX.append(o)
    return o


def bloc(nom, centre, taille, mat, biseau=0.03, rot=(0, 0, 0)):
    return garder(f.boite(nom, centre, taille, M[mat], biseau=biseau, segments=1, rotation=rot))


def repere(nom, p):
    e = bpy.data.objects.new(f"REP_{nom}", None)
    e.location = p
    sc.collection.objects.link(e)
    NOUVEAUX.append(e)


# ----- lignes du terrain effacées par plaques et salies ----------------------------------------------
lignes = bpy.data.objects.get("Lignes")
if lignes:
    gommes = []
    for i in range(90):
        # effacements surtout sur les lignes elles-mêmes (touche, but, médiane, rond central, surfaces)
        choix = rng.random()
        if choix < 0.3:
            x, y = rng.uniform(-52, 52), rng.choice([-34.0, 34.0])
        elif choix < 0.45:
            x, y = rng.choice([-52.5, 52.5]), rng.uniform(-34, 34)
        elif choix < 0.6:
            x, y = 0.0, rng.uniform(-34, 34)
        elif choix < 0.75:
            a = rng.uniform(0, 6.28)
            x, y = 9.15 * math.cos(a), 9.15 * math.sin(a)
        else:
            x, y = rng.choice([-1, 1]) * rng.uniform(36, 52.5), rng.uniform(-20.2, 20.2)
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=rng.uniform(0.8, 3.5), depth=1.0, location=(x, y, 0))
        o = bpy.context.object
        o.scale = (rng.uniform(0.6, 1.6), rng.uniform(0.6, 1.6), 1)
        gommes.append(o)
    gomme = f.fusionner(gommes, "_gomme")
    mod = lignes.modifiers.new("Effacement", "BOOLEAN")
    mod.operation, mod.solver, mod.object = "DIFFERENCE", "EXACT", gomme
    f.appliquer(lignes)
    bpy.data.objects.remove(gomme, do_unlink=True)
    lignes.data.materials.clear()
    lignes.data.materials.append(f.materiau("Lignes_effacees", (0.3, 0.27, 0.22), 0.95))

# ----- barrières publicitaires en ruine : panneaux délavés, manquants, penchés ou tombés ------------
from mathutils import Matrix  # noqa: E402

for o in list(bpy.data.objects):
    if o.name.split(".")[0] in ("Panneau", "Panneau_bande"):
        bpy.data.objects.remove(o, do_unlink=True)
DELAVES = [f.materiau(f"Panneau_delave_{i}", c, 0.8) for i, c in
           enumerate([(0.05, 0.1, 0.25), (0.08, 0.13, 0.22), (0.18, 0.18, 0.2), (0.25, 0.06, 0.04), (0.1, 0.16, 0.3)])]
BANDE = f.materiau("Bande_salie", (0.45, 0.43, 0.38), 0.8)
ROUILLE_P = f.materiau("Coulure_rouille", (0.22, 0.07, 0.02), 0.9)
cotes = [((-56.7, -38.2), (56.7, -38.2)), ((-56.7, 38.2), (56.7, 38.2)), ((-56.7, -38.2), (-56.7, 38.2)),
         ((56.7, -38.2), (56.7, 38.2))]
for ci, (a, b) in enumerate(cotes):
    a, b = Vector((*a, 0)), Vector((*b, 0))
    long_ = (b - a).length
    n_seg = int(long_ / 2.5)
    d = (b - a).normalized()
    angle = math.atan2(d.y, d.x)
    vers_centre = (-(a + b) / 2).normalized()
    sens = 1 if d.cross(Vector((0, 0, 1))).dot(vers_centre) > 0 else -1
    pieces = []
    for k in range(n_seg):
        c = a + d * (k + 0.5) * (long_ / n_seg)
        t = rng.random()
        if t < 0.14:
            continue                                            # panneau arraché
        mat = rng.choice(DELAVES)
        if t < 0.2:                                             # tombé à plat vers le terrain
            p = c + vers_centre * 0.7
            taille = (2.4, 1.1, 0.08) if abs(d.x) > 0.5 else (1.1, 2.4, 0.08)
            pieces.append(f.boite("pt", (p.x, p.y, 0.06), taille, mat, biseau=0.02, rotation=(0, 0, rng.uniform(-0.25, 0.25))))
            continue
        rot = (0, 0, angle)
        groupe = [f.boite("p", (c.x, c.y, 0.55), (2.42, 0.08, 1.2), mat, biseau=0.02, rotation=rot)]
        if rng.random() < 0.7:
            groupe.append(f.boite("b", (c.x, c.y, 0.62), (2.42 * rng.uniform(0.4, 1.0), 0.1, 0.12), BANDE, biseau=0.01, rotation=rot))
        if rng.random() < 0.35:
            groupe.append(f.boite("r", (c.x + rng.uniform(-0.8, 0.8) * d.x, c.y + rng.uniform(-0.8, 0.8) * d.y, 0.55),
                                  (0.18, 0.1, 0.9), ROUILLE_P, biseau=0.0, rotation=rot))
        incl = math.radians(rng.uniform(12, 35)) if t < 0.32 else math.radians(rng.uniform(-3, 3))
        pivot = Vector((c.x, c.y, 0))
        m = Matrix.Translation(pivot) @ Matrix.Rotation(sens * incl, 4, d) @ Matrix.Translation(-pivot)
        for x in groupe:
            x.matrix_world = m @ x.matrix_world
        pieces += groupe
    garder(f.fusionner(pieces, f"barrieres_{ci}"))

# ----- cages rouillées + filet déchiré -------------------------------------------------------------
for o in bpy.data.objects:
    if o.name.split(".")[0] in ("Poteau_D1", "Poteau_D2", "Poteau_G1", "Poteau_G2", "Barre_D", "Barre_G", "Arm_D", "Arm_G"):
        o.data.materials.clear()
        o.data.materials.append(M["rouille"])
for s, x in ((1, 52.5), (-1, -52.5)):
    for y0, larg, haut in ((-3.2, 1.1, 1.5), (-0.4, 0.8, 0.7), (1.9, 1.4, 1.1), (3.0, 0.6, 1.9)):
        bas = 2.44 - haut
        garder(f.filet(f"filet_dechire_{s}_{y0}", [(x + s * 0.05, y0, 2.42), (x + s * 0.05, y0 + larg, 2.42),
                                                  (x + s * 0.35, y0 + larg * 0.8, bas), (x + s * 0.3, y0 + 0.1, bas + 0.2)],
                       max(2, int(larg / 0.15)), max(2, int(haut / 0.15)), 0.006, M["filet"],
                       affaissement=0.12, normale=(s, 0, 0)))
repere("cage_droite", (52.5, 0, 1.2))
repere("cage_gauche", (-52.5, 0, 1.2))

# ----- tribune nord (y de 41 à 51), effondrée entre x = 4 et 14 ----------------------------------
X0, X1, Y0 = -30.0, 30.0, 41.0
MARCHES, PROF, HAUT = 7, 1.4, 0.55
trou = (4.0, 14.0)
for k in range(MARCHES):
    y = Y0 + k * PROF + PROF / 2
    h = (k + 1) * HAUT
    for xa, xb in ((X0, trou[0]), (trou[1], X1)):
        bloc(f"gradin_{k}_{xa:.0f}", ((xa + xb) / 2, y, h / 2), (xb - xa, PROF, h), "beton")
    # sièges : rangée par marche, certains manquants, d'autres tombés
    sieges = []
    x = X0 + 0.5
    while x < X1 - 0.4:
        if not (trou[0] - 0.5 < x < trou[1] + 0.5):
            t = rng.random()
            mat = "siege_rouge" if (int((x - X0) / 6) + k) % 2 else "siege_bleu"
            if t < 0.22:
                pass                                             # siège arraché
            elif t < 0.3:                                        # siège renversé
                sieges.append(f.boite("s", (x, y - 0.1, h + 0.12), (0.46, 0.42, 0.12), M[mat], biseau=0.03,
                                      rotation=(rng.uniform(-1.2, 1.2), rng.uniform(-0.6, 0.6), rng.uniform(-0.5, 0.5))))
            else:
                sieges.append(f.boite("s", (x, y - 0.05, h + 0.22), (0.46, 0.42, 0.08), M[mat], biseau=0.03))
                sieges.append(f.boite("s", (x, y + 0.17, h + 0.48), (0.46, 0.08, 0.5), M[mat], biseau=0.03,
                                      rotation=(math.radians(-8 + rng.uniform(-6, 30) * (t > 0.85)), 0, 0)))
        x += 0.62
    if sieges:
        garder(f.fusionner(sieges, f"sieges_{k}"))
# fissures sombres sur les contremarches
for i in range(14):
    k = rng.randrange(MARCHES)
    x = rng.uniform(X0 + 1, X1 - 1)
    if trou[0] - 1 < x < trou[1] + 1:
        continue
    bloc(f"fissure_{i}", (x, Y0 + k * PROF - 0.01, (k + 0.5) * HAUT), (0.05, 0.03, HAUT * rng.uniform(0.6, 1.0)),
         "beton_sombre", biseau=0, rot=(0, rng.uniform(-0.5, 0.5), 0))
# éboulement : gravats en blocs dans la brèche et au pied
for i in range(70):
    x = rng.uniform(trou[0] - 0.5, trou[1] + 0.5)
    y = rng.uniform(Y0 - 2.5, Y0 + MARCHES * PROF * 0.8)
    c = rng.uniform(0.25, 1.1)
    hauteur_tas = max(0.0, 1.8 - abs(x - 9) * 0.25) * max(0.2, 1 - (y - Y0) / 10)
    bloc(f"gravat_{i}", (x, y, c / 2 + rng.uniform(0, hauteur_tas)), (c, c * rng.uniform(0.6, 1.3), c * 0.7),
         rng.choice(["beton", "gravats"]), biseau=0.04, rot=(rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 3)))
for k in range(3):                                                   # morceaux de gradins effondrés, penchés
    bloc(f"dalle_tombee_{k}", (trou[0] + 2.5 + k * 2.8, Y0 + 1.5 + k, 0.9), (2.6, PROF * 1.5, HAUT * 1.4), "beton",
         rot=(rng.uniform(-0.5, 0.5), rng.uniform(-0.35, 0.35), rng.uniform(-0.3, 0.3)))
repere("tribune_breche", (9, Y0 + 2, 1.5))
repere("tribune", (-12, Y0 + 4, 2.5))

# toit : poteaux à l'arrière, tôles dont certaines manquent ou pendent
yb = Y0 + MARCHES * PROF + 0.4
for x in range(int(X0), int(X1) + 1, 10):
    garder(f.tube(f"poteau_toit_{x}", (x, yb, 0), (x, yb, 8.2), 0.18, M["acier"]))
    garder(f.tube(f"bras_toit_{x}", (x, yb, 8.2), (x, Y0 - 1.0, 7.4), 0.12, M["acier"]))
garder(f.tube("poutre_toit_avant", (X0, Y0 - 1.0, 7.4), (X1, Y0 - 1.0, 7.4), 0.12, M["acier"]))
garder(f.tube("poutre_toit_arriere", (X0, yb, 8.2), (X1, yb, 8.2), 0.12, M["acier"]))
PENTE = math.atan2(8.2 - 7.4, yb - Y0 + 1.0)
for i, x in enumerate(range(int(X0), int(X1), 4)):
    t = rng.random()
    if 6 <= x <= 12 or t < 0.15:
        continue                                                     # tôle arrachée
    if t < 0.28:                                                      # bout de tôle décroché qui pend à l'avant
        bloc(f"tole_{i}", (x + 2, (yb + Y0 - 1.0) / 2 + 2.5, 7.95), (3.95, yb - Y0 - 3.8, 0.08), "toit", biseau=0.01,
             rot=(PENTE, 0, 0))
        bloc(f"tole_pend_{i}", (x + 2 + rng.uniform(-0.3, 0.3), Y0 - 0.6, 6.4), (3.6, 0.08, 2.2), "toit", biseau=0.01,
             rot=(math.radians(rng.uniform(-25, -10)), math.radians(rng.uniform(-12, 12)), 0))
        continue
    bloc(f"tole_{i}", (x + 2, (yb + Y0 - 1.0) / 2, 7.9), (3.95, yb - Y0 + 1.2, 0.08), "toit", biseau=0.01, rot=(PENTE, 0, 0))

# ----- pylônes d'éclairage rouillés aux quatre coins -------------------------------------------------
def pylone(nom, x, y, penche_deg=0.0, lampes_cassees=0.5):
    pieces = []
    H = 20.0
    for dx, dy in ((-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.6, 0.6)):
        pieces.append(f.tube("m", (dx * 1.6, dy * 1.6, 0), (dx * 0.6, dy * 0.6, H), 0.09, M["rouille"]))
    for z in range(2, int(H), 3):
        r0 = 0.6 + 1.0 * (1 - z / H)
        coins = [(-r0, -r0), (r0, -r0), (r0, r0), (-r0, r0)]
        for a, b in zip(coins, coins[1:] + coins[:1]):
            pieces.append(f.tube("e", (a[0], a[1], z), (b[0], b[1], z + 1.5), 0.04, M["rouille"]))
    pieces.append(f.boite("tete", (0, 0, H + 1.2), (4.2, 0.5, 2.6), M["acier"], biseau=0.05))
    o = f.fusionner(pieces, nom)
    lampes = []
    for i in range(3):
        for j in range(2):
            mat = M["verre_casse"] if rng.random() < lampes_cassees else M["verre_ok"]
            lampes.append(f.boite("l", (-1.35 + i * 1.35, -0.27, H + 0.55 + j * 1.25), (1.1, 0.06, 1.0), mat, biseau=0.02))
    lam = f.fusionner(lampes, nom + "_lampes")
    for p in (o, lam):
        p.location = (x, y, 0)
        p.rotation_euler = (math.radians(penche_deg), 0, math.atan2(-y, -x) + math.pi / 2)
        garder(p)
    repere(nom, (x, y, 14))


pylone("pylone_ne", 60, 44, penche_deg=0, lampes_cassees=0.5)
pylone("pylone_no", -60, 44, penche_deg=-11, lampes_cassees=0.85)    # le pylône penché
pylone("pylone_se", 60, -44, lampes_cassees=0.35)
pylone("pylone_so", -60, -44, lampes_cassees=0.7)

# ----- tableau d'affichage décroché, au nord-ouest à côté de la tribune, tourné vers le terrain -------
TX, TY = -40.0, 47.0
for x in (TX - 4.5, TX + 4.5):
    garder(f.tube(f"pied_tableau_{x:.0f}", (x, TY + 0.3, 0), (x, TY + 0.3, 7), 0.16, M["rouille"]))
bloc("tableau", (TX + 0.6, TY, 5.0), (9.2, 0.4, 3.6), "panneau", rot=(0, math.radians(-11), 0))
for i, (x, h) in enumerate(((-2.6, 1.6), (-1.4, 0.0), (1.3, 1.6), (2.6, 0.9))):  # chiffres à moitié tombés
    if h:
        bloc(f"chiffre_{i}", (TX + x + 0.3, TY - 0.25, 4.9 - 0.2 * i), (0.9, 0.1, h), "chiffre", biseau=0.01,
             rot=(0, math.radians(-11 + rng.uniform(-15, 15)), 0))
bloc("chiffre_tombe", (TX + 1.5, TY - 1.6, 0.12), (1.4, 0.9, 0.25), "chiffre", rot=(0.1, 0.2, 0.7))
repere("tableau", (TX, TY, 5))

# ----- abris de touche (côté sud, y = -41) ------------------------------------------------------------
for i, x in enumerate((-9.0, 9.0)):
    pieces_beton = [f.boite("a", (x, -37.6, 1.2), (6.0, 0.25, 2.4), M["beton"], biseau=0.03)]
    for s in (-1, 1):
        pieces_beton.append(f.boite("a", (x + s * 3.0, -36.7, 1.2), (0.25, 1.9, 2.4), M["beton"], biseau=0.03))
    garder(f.fusionner(pieces_beton, f"abri_{i}"))
    if i == 0:
        bloc(f"abri_toit_{i}", (x - 1.2, -36.6, 2.5), (3.8, 2.4, 0.12), "toit", rot=(0, math.radians(-14), 0))
    else:
        bloc(f"abri_toit_{i}", (x, -36.6, 2.5), (6.4, 2.4, 0.12), "toit", rot=(math.radians(4), 0, 0))
    for j in range(7):
        if rng.random() < 0.3:
            continue
        bloc(f"abri_siege_{i}_{j}", (x - 2.4 + j * 0.8, -37.1, 0.5), (0.46, 0.42, 0.08), "siege_bleu",
             rot=(0, 0, rng.uniform(-0.2, 0.2)))
repere("abri", (-9, -36.6, 1.2))

# ----- débris et herbes folles ---------------------------------------------------------------------
for i, (x, y) in enumerate(((40, -8), (44.5, 7), (-30, 20), (12, -22), (-46, -12))):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.32, minor_radius=0.12, location=(x, y, 0.12),
                                     rotation=(rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), 0))
    garder(f._finir(bpy.context.object, M["pneu"], True, f"pneu_{i}"))
for i in range(9):
    x, y = rng.uniform(-48, 48), rng.uniform(-30, 30)
    o = garder(f.revolution(f"plot_{i}", [(0.17, 0), (0.17, 0.03), (0.05, 0.42), (0.0, 0.42)], M["plot"], cotes=12))
    o.location = (x, y, 0)
    if rng.random() < 0.6:
        o.rotation_euler = (math.radians(90), 0, rng.uniform(0, 6.28))
        o.location.z = 0.15
for i in range(6):
    bloc(f"planche_{i}", (rng.uniform(30, 50), rng.uniform(-25, 25), 0.06), (2.2, 0.22, 0.05), "bois",
         rot=(0, rng.uniform(-0.15, 0.15), rng.uniform(0, 3.14)))
for i in range(60):                                            # herbes folles au pied des ruines
    zone = rng.choice([(rng.uniform(-30, 30), rng.uniform(39, 41.5)), (rng.uniform(-62, -58), rng.uniform(-6, 6)),
                       (rng.uniform(-57, 57), rng.uniform(-38, -36.5))])
    brins = []
    for k in range(5):
        h = rng.uniform(0.25, 0.6)
        bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.05, depth=h,
                                        location=(zone[0] + rng.uniform(-0.15, 0.15), zone[1] + rng.uniform(-0.15, 0.15), h / 2),
                                        rotation=(rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0))
        brins.append(bpy.context.object)
    o = f.fusionner(brins, f"herbes_{i}")
    o.data.materials.append(M["herbe"])
    garder(o)

# ----- sol extérieur : herbe terne au lieu du gris -------------------------------------------------
ext = bpy.data.objects.get("Sol_exterieur")
if ext:
    ext.data.materials.clear()
    ext.data.materials.append(f.materiau("Herbe_exterieure", (0.05, 0.12, 0.03), 0.95))

# ----- la ville autour : boulevard, trottoirs, immeubles en blocs, voitures, lampadaires, arbres ------
V = {
    "route": f.materiau("Bitume", (0.03, 0.03, 0.033), 0.85),
    "trottoir": f.materiau("Trottoir", (0.2, 0.2, 0.19), 0.9),
    "marquage": f.materiau("Marquage", (0.7, 0.7, 0.65), 0.6),
    "vitre": f.materiau("Vitres", (0.05, 0.09, 0.13), 0.15),
    "toit_imm": f.materiau("Toit_immeuble", (0.08, 0.08, 0.085), 0.8),
    "tronc": f.materiau("Tronc", (0.1, 0.05, 0.02), 0.9),
    "feuillage": f.materiau("Feuillage", (0.06, 0.28, 0.04), 0.8),
    "roue": f.materiau("Roue", (0.015, 0.015, 0.015), 0.8),
    "lampadaire": f.materiau("Lampadaire", (0.06, 0.07, 0.08), 0.5, metal=0.5),
}
FACADES = [(0.75, 0.42, 0.25), (0.62, 0.55, 0.4), (0.35, 0.45, 0.6), (0.7, 0.62, 0.5), (0.55, 0.25, 0.2),
           (0.42, 0.55, 0.42), (0.8, 0.7, 0.45), (0.5, 0.5, 0.55)]
FACADES = [f.materiau(f"Facade_{i}", c, 0.7) for i, c in enumerate(FACADES)]
CARROSSERIES = [f.materiau(f"Carrosserie_{i}", c, 0.35) for i, c in
                enumerate([(0.7, 0.04, 0.03), (0.04, 0.15, 0.6), (0.85, 0.6, 0.02), (0.75, 0.75, 0.75), (0.05, 0.3, 0.1)])]

# Boulevard périphérique (rectangle) à 8 m de large ; le stade occupe |x| < 70, -48 < y < 56.
XR, YS, YN, LR = 84.0, -60.0, 70.0, 8.0
routes = [((0, YS, 0.01), (2 * XR + LR, LR, 0.02)), ((0, YN, 0.01), (2 * XR + LR, LR, 0.02)),
          ((-XR, (YS + YN) / 2, 0.01), (LR, YN - YS + LR, 0.02)), ((XR, (YS + YN) / 2, 0.01), (LR, YN - YS + LR, 0.02))]
garder(f.fusionner([f.boite("r", c, t, V["route"]) for c, t in routes], "ville_routes"))
traits = []
for x in range(int(-XR), int(XR), 6):
    for y in (YS, YN):
        traits.append(f.boite("m", (x, y, 0.025), (2.5, 0.15, 0.01), V["marquage"]))
for y in range(int(YS), int(YN), 6):
    for x in (-XR, XR):
        traits.append(f.boite("m", (x, y, 0.025), (0.15, 2.5, 0.01), V["marquage"]))
garder(f.fusionner(traits, "ville_marquage"))
trottoirs = []
for c, t in routes:
    horizontal = t[0] > t[1]
    for s in (-1, 1):
        if horizontal:
            trottoirs.append(f.boite("t", (c[0], c[1] + s * (LR / 2 + 1.25), 0.08), (t[0] + 2 * 2.5, 2.5, 0.16), V["trottoir"], biseau=0.03))
        else:
            trottoirs.append(f.boite("t", (c[0] + s * (LR / 2 + 1.25), c[1], 0.08), (2.5, t[1] + 2 * 2.5, 0.16), V["trottoir"], biseau=0.03))
garder(f.fusionner(trottoirs, "ville_trottoirs"))


def immeuble(nom, x, y, l, p, h, rot_z):
    """Immeuble en blocs : corps, rangées de fenêtres sur les 4 faces, acrotère, parfois un rez-de-chaussée vitré."""
    fac = rng.choice(FACADES)
    pieces = [f.boite("corps", (0, 0, h / 2), (l, p, h), fac, biseau=0.08)]
    pieces.append(f.boite("toit", (0, 0, h + 0.15), (l + 0.3, p + 0.3, 0.3), V["toit_imm"], biseau=0.05))
    etages = max(1, int((h - 1.0) / 3.0))
    for face, (lf, nx, ny) in enumerate(((l, 0, -1), (l, 0, 1), (p, -1, 0), (p, 1, 0))):
        n_col = max(1, int(lf / 2.6))
        for e in range(etages):
            z = 2.0 + e * 3.0
            for k in range(n_col):
                u = -lf / 2 + (k + 0.5) * lf / n_col
                if nx == 0:
                    cx, cy = u, ny * (p / 2 + 0.02)
                    t = (1.3, 0.06, 1.5)
                else:
                    cx, cy = nx * (l / 2 + 0.02), u
                    t = (0.06, 1.3, 1.5)
                pieces.append(f.boite("v", (cx, cy, z), t, V["vitre"]))
    o = f.fusionner(pieces, nom)
    o.location = (x, y, 0)
    o.rotation_euler.z = rot_z
    return garder(o)


n = 0
# rangées d'immeubles de l'autre côté du boulevard
for x in range(-110, 111, 16):
    for y, rot in ((YS - 16, 0.0), (YN + 16, math.pi)):
        if rng.random() < 0.12:
            continue
        immeuble(f"immeuble_{n}", x + rng.uniform(-1.5, 1.5), y + rng.uniform(-2, 2), rng.uniform(10, 14),
                 rng.uniform(9, 14), rng.choice([7, 10, 13, 16, 22, 28]), rot)
        n += 1
for y in range(int(YS) - 4, int(YN) + 5, 16):
    for x, rot in ((-XR - 16, -math.pi / 2), (XR + 16, math.pi / 2)):
        if rng.random() < 0.12:
            continue
        immeuble(f"immeuble_{n}", x + rng.uniform(-2, 2), y + rng.uniform(-1.5, 1.5), rng.uniform(10, 14),
                 rng.uniform(9, 14), rng.choice([7, 10, 13, 16, 22, 28]), rot)
        n += 1
# seconde couronne, plus haute (silhouette de ville au fond des plans)
for i in range(26):
    a = 2 * math.pi * i / 26 + rng.uniform(-0.05, 0.05)
    r = rng.uniform(150, 175)
    immeuble(f"tour_{i}", r * math.cos(a), r * math.sin(a) * 0.85, rng.uniform(12, 18), rng.uniform(12, 18),
             rng.choice([24, 32, 40, 48]), a + math.pi / 2)


def voiture(nom, x, y, rot_z):
    mat = rng.choice(CARROSSERIES)
    pieces = [f.boite("caisse", (0, 0, 0.55), (4.0, 1.8, 0.7), mat, biseau=0.12),
              f.boite("habitacle", (-0.2, 0, 1.15), (2.2, 1.6, 0.6), mat, biseau=0.12),
              f.boite("pare_brise", (0.92, 0, 1.15), (0.06, 1.5, 0.5), V["vitre"]),
              f.boite("lunette", (-1.32, 0, 1.15), (0.06, 1.5, 0.5), V["vitre"])]
    for s in (-1, 1):
        pieces.append(f.boite("vitre_l", (-0.2, s * 0.81, 1.15), (1.9, 0.04, 0.45), V["vitre"]))
        for xr in (-1.25, 1.25):
            bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=0.36, depth=0.3, location=(xr, s * 0.85, 0.36),
                                                rotation=(math.pi / 2, 0, 0))
            r = bpy.context.object
            r.data.materials.append(V["roue"])
            pieces.append(r)
    o = f.fusionner(pieces, nom)
    o.location = (x, y, 0)
    o.rotation_euler.z = rot_z
    return garder(o)


for i in range(16):
    cote = rng.randrange(4)
    if cote < 2:
        y = (YS, YN)[cote] + rng.choice([-2.0, 2.0])
        voiture(f"voiture_{i}", rng.uniform(-75, 75), y, 0.0 if y > (YS, YN)[cote] else math.pi)
    else:
        x = (-XR, XR)[cote - 2] + rng.choice([-2.0, 2.0])
        voiture(f"voiture_{i}", x, rng.uniform(YS + 6, YN - 6), math.pi / 2 if x > (-XR, XR)[cote - 2] else -math.pi / 2)

lampes = []
for x in range(-80, 81, 20):
    for y in (YS + LR / 2 + 1.0, YN - LR / 2 - 1.0):
        lampes.append(f.tube("p", (x, y, 0), (x, y, 6.5), 0.08, V["lampadaire"]))
        lampes.append(f.boite("t", (x, y + (1.0 if y < 0 else -1.0) * 0.6, 6.5), (0.5, 1.4, 0.2), V["lampadaire"], biseau=0.05))
garder(f.fusionner(lampes, "ville_lampadaires"))

arbres_troncs, arbres_feuilles = [], []
for i in range(40):
    cote = rng.randrange(4)
    if cote < 2:
        x, y = rng.uniform(-80, 80), (YS - LR / 2 - 3.5, YN + LR / 2 + 3.5)[cote]
    else:
        x, y = (-XR - LR / 2 - 3.5, XR + LR / 2 + 3.5)[cote - 2], rng.uniform(YS, YN)
    h = rng.uniform(3, 4.5)
    arbres_troncs.append(f.boite("tr", (x, y, h / 2), (0.4, 0.4, h), V["tronc"], biseau=0.04))
    c = rng.uniform(2.2, 3.2)
    arbres_feuilles.append(f.boite("fe", (x, y, h + c / 2 - 0.3), (c, c, c), V["feuillage"], biseau=0.25,
                                   rotation=(0, 0, rng.uniform(0, 1.5))))
    if rng.random() < 0.5:
        arbres_feuilles.append(f.boite("fe", (x + 0.3, y - 0.2, h + c - 0.1), (c * 0.6, c * 0.6, c * 0.6), V["feuillage"],
                                       biseau=0.18, rotation=(0, 0, rng.uniform(0, 1.5))))
garder(f.fusionner(arbres_troncs, "ville_troncs"))
garder(f.fusionner(arbres_feuilles, "ville_feuillages"))
repere("ville", (0, YN + 16, 10))

# ----- tout dans la collection « Stade » -------------------------------------------------------------
stade = bpy.data.collections.get("Stade") or bpy.data.collections.new("Stade")
if stade.name not in sc.collection.children:
    sc.collection.children.link(stade)
for o in list(sc.collection.all_objects):
    if stade not in o.users_collection:
        stade.objects.link(o)
    for c in list(o.users_collection):
        if c != stade:
            c.objects.unlink(o)
for c in list(bpy.data.collections):
    if c != stade:
        bpy.data.collections.remove(c)
sortie = DOSSIER / "stade_ruine.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(sortie), compress=True)
n_tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in stade.all_objects if o.type == "MESH")
print(f"STADE_OK {sortie} : {len(stade.all_objects)} objets, {n_tri} triangles, {len(NOUVEAUX)} ajouts")
