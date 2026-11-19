"""Blason du FC Élite (création du projet), variante C choisie par Guillaume le 2026-11-19 (jour-3, b05-b06, b15).

D'après engine/docs/pilotes/jour-3-blason/blason_C.png : écusson noir bordé de jaune, haut crénelé (4 merlons),
grand ballon blanc au centre, ruban rouge plus large que l'écusson avec « FC ÉLITE » en blanc, étoile au-dessus,
en JAUNE (#FFC400, recommandation du DA) et non en blanc. Tout est en blocs (pixels de 12 cm) :

- relief : champ noir 1 bloc d'épaisseur ; bordure, merlons, ballon et étoile ressortent d'1 bloc ;
  ruban encore 1 bloc devant ; texte en relief sur le ruban, avec une ombre rouge foncé décalée (lisibilité) ;
- matériaux : bordure et étoile en OR brillant (métal, faible rugosité) pour le reflet doré qui traverse le blason ;
  noir laqué (il accroche les reflets), blanc cassé, rouge et son ombre ;
- le ballon est dessiné comme un vrai ballon (pentagone noir au centre + 5 taches au bord), plus lisible au
  téléphone que l'anneau du croquis.

Couleurs de la charte (sRVB) -> linéaire, puis un peu plus sombres et saturées pour AgX :
noir #17171F -> (0,009 ; 0,009 ; 0,014) ; jaune #FFC400 -> (1 ; 0,55 ; 0) -> (0,9 ; 0,45 ; 0,0) ;
rouge #E02A2A -> (0,75 ; 0,023 ; 0,023) -> (0,62 ; 0,018 ; 0,018) ; ombre #A01818 -> (0,35 ; 0,009 ; 0,009) -> (0,3 ; 0,008 ; 0,008) ;
blanc #F4F4F0 -> (0,9 ; 0,9 ; 0,87) -> (0,8 ; 0,8 ; 0,77).

Dimensions : 3,6 m de large (ruban) × 4,6 m de haut × 0,5 m ; PIVOT AU CENTRE de la boîte englobante (0, 0, 0) pour
tourner sur lui-même (action « tourner » du moteur, autour de z) et grandir sans dériver ; face vers -y (vu de
la caméra sud). Dans la fiche, « position » = centre du blason (pas sa base).

    blender --background --factory-startup --python engine/outils/atelier/modeles/blason_fc_elite.py
"""
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

P = 0.12                                    # taille d'un pixel-bloc (m)
POLICE = f.RACINE / "engine" / "assets" / "polices" / "Baloo2-variable.ttf"

f.vider()
M = {
    "noir": f.materiau("Blason_noir_laque", (0.009, 0.009, 0.014), 0.3),
    "or": f.materiau("Blason_or", (0.9, 0.45, 0.0), 0.22, metal=0.75),
    "blanc": f.materiau("Blason_blanc", (0.8, 0.8, 0.77), 0.4),
    "rouge": f.materiau("Blason_rouge", (0.62, 0.018, 0.018), 0.4),
    "ombre": f.materiau("Blason_rouge_ombre", (0.3, 0.008, 0.008), 0.5),
}

# ----- 1. dessin en pixels (colonne c de 0 à 25, ligne r de 0 en haut) ----------------------------------
L = 26                                       # largeur de l'écusson en pixels
pix = {}                                     # (c, r) -> type : Y bordure/merlon, N champ, W blanc, K noir du ballon, S étoile

ETOILE = ["   SS   ",
          "   SS   ",
          "SSSSSSSS",
          " SSSSSS ",
          "  SSSS  ",
          " SSSSSS ",
          " SS  SS "]
for r, ligne in enumerate(ETOILE):
    for k, ch in enumerate(ligne):
        if ch == "S":
            pix[(9 + k, r)] = "S"
R_MERLON = 4                                 # merlons : lignes 4 à 6
for c0 in (0, 7, 16, 23):
    for c in range(c0, c0 + 3):
        for r in range(R_MERLON, R_MERLON + 3):
            pix[(c, r)] = "Y"
R_HAUT = R_MERLON + 3                        # ligne du bord supérieur
R_PENTE = R_HAUT + 21                        # début du rétrécissement en pointe
R_BAS = R_PENTE + 6                          # dernière ligne
for r in range(R_HAUT, R_BAS + 1):
    retrait = max(0, r - R_PENTE + 1) if r >= R_PENTE else 0
    c_min, c_max = retrait, L - 1 - retrait
    for c in range(c_min, c_max + 1):
        bord = r in (R_HAUT, R_BAS) or c in (c_min, c_max) or (r >= R_PENTE and c in (c_min + 1, c_max - 1)
                                                               and r == R_PENTE)
        pix[(c, r)] = "Y" if bord else "N"
    if r > R_PENTE:                          # marches de la pointe : bordure continue en escalier
        pix[(c_min + 1, r - 1)] = "Y"
        pix[(c_max - 1, r - 1)] = "Y"

# Ballon : disque de rayon 7,6 px, pentagone noir au centre + 5 taches à l'intérieur du disque (silhouette ronde intacte).
CX, CY, RB = 13.0, R_HAUT + 10.5, 7.6
for (c, r), t in list(pix.items()):
    if t != "N":
        continue
    x, y = c + 0.5 - CX, r + 0.5 - CY
    d = math.hypot(x, y)
    if d > RB:
        continue
    noir = d < 2.2                           # pentagone central (lu comme un disque de 5 px)
    for k in range(5):
        a = math.radians(-90 + 72 * k)
        if math.hypot(x - 5.0 * math.cos(a), y - 5.0 * math.sin(a)) < 1.45:
            noir = True
    pix[(c, r)] = "K" if noir else "W"

# ----- 2. blocs : profondeur selon le type (avant = -y) ----------------------------------------------------
# (avant, arrière, matériau, biseau relatif)
COUCHES = {"N": (-0.5, 0.5, "noir", 0.06), "Y": (-1.5, 0.5, "or", 0.14), "W": (-1.5, 0.5, "blanc", 0.12),
           "K": (-1.1, 0.5, "noir", 0.12), "S": (-1.5, 0.5, "or", 0.14)}


def maillage_blocs(nom, blocs, mats):
    """blocs : [(x, z, y_avant, y_arriere, largeur_x, hauteur_z, index_materiau, biseau)] -> un objet biseauté."""
    objets = []
    for biseau in sorted({b[7] for b in blocs}):
        bm = bmesh.new()
        for x, z, ya, yr, lx, hz, im, bz in blocs:
            if bz != biseau:
                continue
            g = bmesh.ops.create_cube(bm, size=1.0)
            m = Matrix.Translation((x, (ya + yr) / 2, z)) @ Matrix.Diagonal((lx, yr - ya, hz, 1))
            bmesh.ops.transform(bm, matrix=m, verts=g["verts"])
            for fa in {fa for v in g["verts"] for fa in v.link_faces}:
                fa.material_index = im
        me = bpy.data.meshes.new(nom)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(nom, me)
        bpy.context.scene.collection.objects.link(o)
        for mt in mats:
            me.materials.append(mt)
        if biseau > 0:
            mod = o.modifiers.new("Biseau", "BEVEL")
            mod.width, mod.segments, mod.limit_method = biseau * P, 1, "ANGLE"
            f.appliquer(o)
        objets.append(o)
    o = f.fusionner(objets, nom)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


ORDRE = ["noir", "or", "blanc", "rouge", "ombre"]
MATS = [M[k] for k in ORDRE]


def xz(c, r):
    return (c + 0.5 - L / 2) * P, -(r + 0.5) * P


blocs = []
# Le champ noir (N) en bandes horizontales fusionnées (moins de triangles, pas de grille visible sur le fond).
lignes = {}
for (c, r), t in pix.items():
    if t == "N":
        lignes.setdefault(r, []).append(c)
for r, cs in lignes.items():
    cs.sort()
    debut = prec = cs[0]
    for c in cs[1:] + [None]:
        if c is not None and c == prec + 1:
            prec = c
            continue
        x0, z = xz(debut, r)
        x1, _ = xz(prec, r)
        ya, yr, mat, bz = COUCHES["N"]
        blocs.append(((x0 + x1) / 2, z, ya * P, yr * P, x1 - x0 + P, P, ORDRE.index(mat), 0.0))
        if c is not None:
            debut = prec = c
for (c, r), t in pix.items():
    if t == "N":
        continue
    ya, yr, mat, bz = COUCHES[t]
    x, z = xz(c, r)
    blocs.append((x, z, ya * P, yr * P, P, P, ORDRE.index(mat), bz))

# Ruban : plus large que l'écusson, 5 pixels de haut, devant (1 bloc), bouts repliés en arrière, plus foncés,
# légèrement plus bas, terminés en queue d'aronde.
R_RUBAN = R_PENTE - 2
for c in range(-1, L + 1):
    for k in range(5):
        x, z = xz(c, R_RUBAN + k)
        blocs.append((x, z, -2.5 * P, -1.5 * P, P, P, ORDRE.index("rouge"), 0.1))
for s, cs in ((-1, (-2, -3, -4)), (1, (L + 1, L + 2, L + 3))):
    for c in cs:
        for k in range(5):
            bout = c in (-4, L + 3)
            if bout and k == 2:
                continue                         # encoche de la queue d'aronde
            x, z = xz(c, R_RUBAN + 1 + k)
            blocs.append((x, z, -1.5 * P, -0.5 * P, P, P, ORDRE.index("ombre"), 0.1))
    # pli : un bloc d'ombre entre le ruban avant et le bout replié
    x, z = xz(-1 if s < 0 else L, R_RUBAN + 5)
    blocs.append((x, z, -2.5 * P, -0.5 * P, P, P, ORDRE.index("ombre"), 0.1))

blason = maillage_blocs("blason_fc_elite", blocs, MATS)


# ----- 3. texte « FC ÉLITE » en relief sur le ruban, avec ombre décalée ---------------------------------
def texte(nom, corps, mat, decalage, epaisseur, grossir):
    cu = bpy.data.curves.new(nom, "FONT")
    cu.body = corps
    if POLICE.is_file():
        cu.font = bpy.data.fonts.load(str(POLICE))
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.size = 0.62
    cu.resolution_u = 3                        # courbes plus grossières : moins de triangles, invisible à l'écran
    cu.extrude = epaisseur / 2
    cu.offset = grossir                        # épaissit les lettres (police variable chargée en graisse normale)
    o = bpy.data.objects.new(nom, cu)
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.radians(90), 0, 0)
    _, zr = xz(0, R_RUBAN + 2)
    o.location = (decalage[0], -2.5 * P - epaisseur / 2 + decalage[1], zr + decalage[2])
    o = f.convertir_en_maillage(o)
    o.data.materials.clear()
    o.data.materials.append(mat)
    return o


t_blanc = texte("texte", "FC ÉLITE", M["blanc"], (0, -0.002, -0.01), 0.05, 0.012)
t_ombre = texte("texte_ombre", "FC ÉLITE", M["ombre"], (0.035, 0.02, -0.045), 0.03, 0.012)

# ----- 4. pivot au centre, export --------------------------------------------------------------------------
objets = [blason, t_blanc, t_ombre]
bpy.context.view_layer.update()
coins = [o.matrix_world @ Vector(c) for o in objets for c in o.bound_box]
mn = Vector([min(p[i] for p in coins) for i in range(3)])
mx = Vector([max(p[i] for p in coins) for i in range(3)])
centre = (mn + mx) / 2
final = f.fusionner(objets, "blason_fc_elite")
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
final.data.transform(Matrix.Translation(-centre))
final.location = (0, 0, 0)
print(f"BLASON taille {tuple(round(v, 3) for v in (mx - mn))}")
f.exporter("blason_fc_elite")
