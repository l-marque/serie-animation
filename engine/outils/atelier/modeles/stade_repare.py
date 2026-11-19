"""Stade réparé (création du projet) : état `repare` de l'épisode jour-3.

Part de stade_ruine_pelouse.blend tel qu'il est sur le disque (pelouse neuve du jour 2, retouches de
Guillaume comprises) et ne change que deux choses, votées par l'audience :

1. Tribune nord réparée, MÊME EMPRISE que la tribune effondrée (x de -30 à 30, y de 41 à 51,2, 7 marches de
   1,4 × 0,55 m, toit à 7,4-8,2 m) avec le design de `tribune_reparee` (carte du jour 2) : béton neuf, nez de
   marche clair, sièges neufs rouges et bleus en blocs de 6 m, poteaux blancs, toit bleu nuit d'un seul tenant
   avec rive blanche. La brèche (x de 4 à 14) disparaît : gravats, dalles tombées, fissures, tôles arrachées ou
   pendantes sont retirés. Détails qui racontent la réparation faite par les abonnés : le tronçon de l'ancienne
   brèche est d'un béton un peu plus clair (coulé de frais), un siège jaune dépareillé au milieu des rouges et
   des bleus, et au pied de la tribune trois pots de peinture, un rouleau et un escabeau oubliés.
2. Cages gauche (x = -52,5) et droite (x = 52,5) remplacées par des cages au design de `cage_filet` (poteaux
   blancs propres, barres arrière cintrées, vrais filets à maille de 15 cm), AUX DIMENSIONS DES CAGES DU STADE
   (poteaux en y = ±3,72, barre à 2,41 m, profondeur 2 m comme les anciens montants) ; `cage_filet` mesure
   4 × 2 m (taille de `cage_rouillee`, pas des cages du terrain de Guillaume) : on ne peut pas le poser tel quel.

Tout le reste (pylônes, tableau, abris, barrières, lignes, ville, repères REP_*) est conservé tel quel, aux
mêmes positions. Le fichier source n'est jamais réenregistré : sortie dans un nouveau .blend, collection « Stade ».
Repères ajoutés : REP_tribune_centre, REP_rang_<k> (centre de chaque rang de sièges, pour poser des supporters).

    blender --background --factory-startup --python engine/outils/atelier/modeles/stade_repare.py

Si stade_ruine_pelouse.blend est régénéré, relancer ce script.
Sièges (pour poser un supporter assis) : rang k (0 = bas) : y = 41,65 + 1,4 k ; assise à z = 0,55 (k + 1) + 0,24 ;
x = -29,5 + 0,62 i (i de 0 à 95). Le supporter regarde vers -y (le terrain), comme la caméra.
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

SOURCE = f.MODELES / "stade_ruine_pelouse" / "stade_ruine_pelouse.blend"
SORTIE = f.MODELES / "stade_repare" / "stade_repare.blend"

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
stade = bpy.data.collections["Stade"]
retires = {}

# ----- 1. retrait de la tribune effondrée et des cages rouillées ---------------------------------------
TRIBUNE = ("gradin_", "sieges_", "fissure_", "gravat_", "dalle_tombee_", "poteau_toit_", "bras_toit_",
           "poutre_toit_", "tole_")
CAGES = ("filet_dechire_", "Poteau_D", "Poteau_G", "Barre_D", "Barre_G", "Arm_D", "Arm_G")
for o in list(bpy.data.objects):
    n = o.name
    motif = None
    if n.startswith(TRIBUNE):
        motif = "tribune effondrée"
    elif n.startswith(CAGES):
        motif = "cages rouillées"
    elif n.startswith("herbes_"):
        c = sum((o.matrix_world @ Vector(v) for v in o.bound_box), Vector()) / 8
        if c.y > 38.2 and abs(c.x) < 32:
            motif = "herbes folles au pied de la tribune"
    if motif:
        retires[motif] = retires.get(motif, 0) + 1
        bpy.data.objects.remove(o, do_unlink=True)

M = {
    "beton": f.materiau("Beton_neuf", (0.42, 0.41, 0.38), 0.85),
    "beton_frais": f.materiau("Beton_frais", (0.52, 0.51, 0.47), 0.8),
    "nez": f.materiau("Nez_de_marche_tribune", (0.62, 0.61, 0.57), 0.8),
    "rouge": f.materiau("Siege_rouge_neuf", (0.62, 0.04, 0.03), 0.35),
    "bleu": f.materiau("Siege_bleu_neuf", (0.02, 0.12, 0.55), 0.35),
    "jaune": f.materiau("Siege_jaune_depareille", (0.85, 0.5, 0.01), 0.35),
    "blanc": f.materiau("Acier_blanc_tribune", (0.8, 0.8, 0.78), 0.4, metal=0.2),
    "toit": f.materiau("Toit_neuf", (0.05, 0.11, 0.3), 0.45, metal=0.3),
    "peinture": f.materiau("Peinture_cage_neuve", (0.93, 0.93, 0.9), 0.35),
    "corde": f.materiau("Filet_neuf", (0.62, 0.64, 0.66), 0.9),
    "acier": f.materiau("Acier_sol_cage", (0.32, 0.34, 0.36), 0.5, metal=0.6),
    "pot": f.materiau("Pot_metal", (0.55, 0.56, 0.58), 0.4, metal=0.7),
    "bois": f.materiau("Escabeau_bois", (0.45, 0.28, 0.12), 0.7),
}
NOUVEAUX = []


def garder(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    stade.objects.link(o)
    NOUVEAUX.append(o)
    return o


def boites(nom, liste, mat_par_defaut, biseau=0.03):
    """Beaucoup de boîtes en un seul maillage, construit en bmesh (rapide), puis un seul biseau.
    liste : [(centre, taille, rotation_x, materiau ou None)]."""
    mats = [mat_par_defaut]
    bm = bmesh.new()
    for centre, taille, rx, mat in liste:
        mat = mat or mat_par_defaut
        if mat not in mats:
            mats.append(mat)
        geo = bmesh.ops.create_cube(bm, size=1.0)
        m = Matrix.Translation(centre) @ Matrix.Rotation(rx, 4, "X") @ Matrix.Diagonal((*taille, 1))
        bmesh.ops.transform(bm, matrix=m, verts=geo["verts"])
        idx = mats.index(mat)
        for fa in {fa for v in geo["verts"] for fa in v.link_faces}:
            fa.material_index = idx
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    bpy.context.scene.collection.objects.link(o)
    for mat in mats:
        me.materials.append(mat)
    if biseau:
        mod = o.modifiers.new("Biseau", "BEVEL")
        mod.width, mod.segments, mod.limit_method = biseau, 1, "ANGLE"
        f.appliquer(o)
    for p in me.polygons:
        p.use_smooth = True
    return garder(o)


def repere(nom, p):
    e = bpy.data.objects.new(f"REP_{nom}", None)
    e.location = p
    garder(e)


# ----- 2. tribune nord réparée (même emprise que la tribune effondrée) ---------------------------------
X0, X1, Y0 = -30.0, 30.0, 41.0
MARCHES, PROF, HAUT = 7, 1.4, 0.55
BRECHE = (4.0, 14.0)
gradins, nez = [], []
for k in range(MARCHES):
    y = Y0 + k * PROF + PROF / 2
    h = (k + 1) * HAUT
    for xa, xb, mat in ((X0, BRECHE[0], None), (BRECHE[0], BRECHE[1], M["beton_frais"]), (BRECHE[1], X1, None)):
        gradins.append((((xa + xb) / 2, y, h / 2), (xb - xa, PROF, h), 0.0, mat))
    nez.append(((0, Y0 + k * PROF + 0.07, h - 0.04), (X1 - X0 + 0.02, 0.16, 0.09), 0.0, None))
for s in (-1, 1):                                                    # murs de côté
    gradins.append(((s * (X1 + 0.18), Y0 + MARCHES * PROF / 2, MARCHES * HAUT / 2 + 0.1),
                    (0.36, MARCHES * PROF, MARCHES * HAUT + 0.2), 0.0, M["nez"]))
boites("tribune_gradins", gradins, M["beton"], biseau=0.03)
boites("tribune_nez", nez, M["nez"], biseau=0.02)

sieges = []
SIEGE_JAUNE = (3, 41)                                                # (rang, n° de siège) : le siège dépareillé
for k in range(MARCHES):
    y = Y0 + k * PROF + 0.65
    h = (k + 1) * HAUT
    for i in range(96):
        x = X0 + 0.5 + i * 0.62
        mat = M["rouge"] if (int((x - X0) / 6) + k) % 2 else M["bleu"]
        if (k, i) == SIEGE_JAUNE:
            mat = M["jaune"]
        sieges.append(((x, y, h + 0.2), (0.46, 0.42, 0.08), 0.0, mat))
        sieges.append(((x, y + 0.22, h + 0.46), (0.46, 0.08, 0.46), math.radians(-8), mat))
boites("tribune_sieges", sieges, M["bleu"], biseau=0.025)
for k in range(MARCHES):
    repere(f"rang_{k}", (0, Y0 + k * PROF + 0.65, (k + 1) * HAUT + 0.24))
repere("tribune_centre", (0, Y0 + 4, 2.5))

# Toit : poteaux blancs à l'arrière tous les 10 m, bras en porte-à-faux, tôle bleu nuit d'un seul tenant.
yb = Y0 + MARCHES * PROF + 0.4
acier = []
for x in range(int(X0), int(X1) + 1, 10):
    acier.append(f.tube(f"poteau_toit_{x}", (x, yb, 0), (x, yb, 8.2), 0.18, M["blanc"]))
    acier.append(f.tube(f"bras_toit_{x}", (x, yb, 8.2), (x, Y0 - 1.0, 7.4), 0.12, M["blanc"]))
acier.append(f.tube("poutre_avant", (X0, Y0 - 1.0, 7.4), (X1, Y0 - 1.0, 7.4), 0.12, M["blanc"]))
acier.append(f.tube("poutre_arriere", (X0, yb, 8.2), (X1, yb, 8.2), 0.12, M["blanc"]))
garder(f.fusionner(acier, "tribune_charpente"))
PENTE = math.atan2(8.2 - 7.4, yb - Y0 + 1.0)
boites("tribune_toit", [((0, (yb + Y0 - 1.0) / 2, 7.92), (X1 - X0 + 0.8, yb - Y0 + 1.6, 0.1), PENTE, None),
                        ((0, Y0 - 1.25, 7.2), (X1 - X0 + 0.8, 0.12, 0.34), 0.0, M["blanc"])], M["toit"], biseau=0.02)

# Les traces de la réparation : pots de peinture (rouge, bleu, blanc), rouleau, escabeau, au pied de la brèche.
outils = []
for i, (x, y, mat, couche) in enumerate(((5.2, 40.3, M["rouge"], True), (5.75, 40.55, M["bleu"], False),
                                         (12.6, 40.4, M["peinture"], True))):
    o = f.revolution(f"pot_{i}", [(0.15, 0), (0.15, 0.3), (0.14, 0.31), (0.0, 0.31)], M["pot"], cotes=16)
    o.location = (x, y, 0)
    outils.append(o)
    if couche:                                                       # coulure de peinture sur le flanc
        outils.append(f.boite(f"coulure_{i}", (x, y - 0.15, 0.24), (0.07, 0.02, 0.14), mat, biseau=0.01))
    outils.append(f.boite(f"dessus_{i}", (x, y, 0.312), (0.2, 0.2, 0.01), mat))   # peinture visible dessus
rouleau = [f.tube("rouleau", (6.3, 40.0, 0.06), (6.55, 40.0, 0.06), 0.06, M["bleu"]),
           f.tube("manche", (6.42, 40.0, 0.06), (6.6, 39.3, 0.1), 0.015, M["blanc"])]
outils += rouleau
# escabeau ouvert, appuyé contre la première marche
for s in (-1, 1):
    outils.append(f.tube(f"esc_{s}", (9.5 + s * 0.25, 40.2, 0), (9.5 + s * 0.18, 40.75, 1.5), 0.035, M["bois"]))
    outils.append(f.tube(f"esc_ar_{s}", (9.5 + s * 0.25, 41.0, 0.55), (9.5 + s * 0.18, 40.8, 1.5), 0.03, M["bois"]))
for j in range(4):
    z = 0.35 + j * 0.33
    t = z / 1.5
    outils.append(f.boite(f"marche_esc_{j}", (9.5, 40.2 + 0.55 * t, z), (0.5 - 0.07 * t, 0.12, 0.03), M["bois"]))
garder(f.fusionner(outils, "outils_reparation"))


# ----- 3. cages réparées avec filets, aux dimensions des cages du stade ------------------------------
def cage(nom, x0, s):
    """Cage au design de cage_filet : ouverture vers le centre du terrain, profondeur vers s·x."""
    Y, H, R = 3.72, 2.41, 0.06
    XH, ZH, XB = 1.0, 2.22, 2.0                                       # barre arrière haute, barre au sol
    def p(dx, y, z):
        return (x0 + s * dx, y, z)
    tubes = [f.tube("pg", p(0, -Y, 0), p(0, -Y, H), R, M["peinture"], bouts_ronds=True),
             f.tube("pd", p(0, Y, 0), p(0, Y, H), R, M["peinture"], bouts_ronds=True),
             f.tube("barre", p(0, -Y, H), p(0, Y, H), R, M["peinture"])]
    for c in (-1, 1):
        tubes.append(f.tube_courbe("montant", [p(0, c * Y, H), p(XH * 0.6, c * Y, ZH + 0.08), p(XH, c * Y, ZH),
                                               p(XB, c * Y, 0.3), p(XB, c * Y, 0.03)], R * 0.7, M["peinture"]))
        tubes.append(f.tube("sol_c", p(0, c * Y, 0.035), p(XB, c * Y, 0.035), 0.035, M["acier"]))
    tubes.append(f.tube("arriere_haute", p(XH, -Y, ZH), p(XH, Y, ZH), R * 0.7, M["peinture"]))
    tubes.append(f.tube("sol_arriere", p(XB, -Y, 0.035), p(XB, Y, 0.035), 0.035, M["acier"]))
    cadre = garder(f.fusionner(tubes, f"{nom}_cadre"))
    rc = 0.0055
    filets = [f.filet("toit", [p(0, -Y, H), p(0, Y, H), p(XH, Y, ZH), p(XH, -Y, ZH)], 48, 7, rc, M["corde"],
                      affaissement=0.08, normale=(0, 0, -1)),
              f.filet("fond", [p(XH, -Y, ZH), p(XH, Y, ZH), p(XB, Y, 0.04), p(XB, -Y, 0.04)], 48, 16, rc, M["corde"],
                      affaissement=0.2, normale=(s, 0, 0))]
    for c in (-1, 1):
        filets.append(f.filet("cote", [p(0, c * Y, 0.04), p(XB, c * Y, 0.04), p(XH, c * Y, ZH), p(0, c * Y, H)],
                              13, 16, rc, M["corde"], affaissement=0.06, normale=(0, c, 0)))
    filet = garder(f.fusionner(filets, f"{nom}_filet"))
    return cadre, filet


cage("cage_droite", 52.5, 1)
cage("cage_gauche", -52.5, -1)

# ----- 4. nettoyage et enregistrement d'une COPIE --------------------------------------------------------
for o in list(bpy.context.scene.collection.objects):                 # rien ne doit rester hors de « Stade »
    if o.name not in stade.objects:
        stade.objects.link(o)
    bpy.context.scene.collection.objects.unlink(o)
for _ in range(3):
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
SORTIE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SORTIE), compress=True, copy=True)
n_tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in stade.all_objects if o.type == "MESH")
print(f"STADE_REPARE_OK {SORTIE} : {len(stade.all_objects)} objets, {n_tri} triangles, retirés : {retires}, "
      f"ajoutés : {len(NOUVEAUX)}")
