"""Serpents en blocs (série « 10 000 serpents contre 1 hamster », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/serpent_bloc.py [-- serpent_bloc serpent_chef_bloc]

- `serpent_bloc` : le serpent de la foule. Version légère (moins de 600 triangles) : corps en 11 segments
  chanfreinés qui rétrécissent vers la queue, posé en S sur le sol, cou dressé, tête tournée vers -y ;
  vert foncé à bandes violettes (sombres mais pas noirs : révision désert du 2026-11-19), gros YEUX ROUGES
  émissifs (force 1,1 : plus fort, AgX les rend roses) devant un halo = plaque rouge émissive translucide (pas d'éblouissement au compositeur),
  pupille noire fendue verticale, sourcils en blocs presque noirs inclinés vers le centre (regard méchant), langue
  rouge fourchue. La foule (foule_serpents.py) ajoute un liseré rouge-orangé de contre-jour (contour()).
  Hauteur hors tout 1,55 m, longueur au sol environ 2,2 m.
- `serpent_chef_bloc` : le chef, pour le gros plan de b03. Même famille mais inversée (violet à bandes
  vert foncé : on le distingue tout de suite de la masse), 1,6 fois plus grand (2,5 m), 16 segments biseautés,
  crête de plaques sur la nuque, gueule entrouverte rouge sombre, grands crochets blancs (le droit cassé), petites dents, cicatrice rose en zigzag qui
  barre l'œil gauche (paupière à moitié fermée), langue longue qui sort et vibre (action Tongue).

Squelette (glb) : Root, S0…S4 (corps → cou), Head, Tongue (+ Jaw pour le chef). Animations à 24 i/s :
Idle (ondulation latérale qui remonte le corps, tête qui se balance, langue qui pointe deux fois),
Tongue (b03 : la langue sort et vibre, tête un peu penchée en avant ; sortie complète à l'image 6),
Hiss (le chef se dresse, gueule ouverte, recule la tête : sifflement), Attack (détente vers l'avant, image 8).
Le maillage de la foule (foule_serpents.py) réutilise construire_maillage() avec l'attribut « s »
(0 = queue, 1 = tête) qui sert à l'ondulation dans les nœuds de géométrie.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

# Palette « désert » (révision du 2026-11-19, pack desert_hamster v1.1, lumineux) : corps sombres mais PAS noirs
# (vert foncé, violet) pour que la lumière de contour rouge-orangé du soleil en contre-jour les découpe sur le sable
# clair ; YEUX ROUGES vifs très émissifs avec halo translucide (il n'y a pas d'éblouissement au compositeur).
VERT = (0.05, 0.12, 0.06)          # vert foncé
VIOLET = (0.12, 0.04, 0.14)        # violet
NOIR = (0.004, 0.003, 0.004)       # pupilles, narines
ROUGE = (0.45, 0.005, 0.01)        # langue
VENTRE = (0.1, 0.16, 0.05)         # écailles du ventre, un peu plus claires que le dos
CICATRICE = (0.6, 0.22, 0.26)
BLANC = (0.75, 0.72, 0.62)         # crochets
GORGE = (0.2, 0.0, 0.015)          # intérieur de la gueule, rouge sombre
OEIL = (1.0, 0.02, 0.01)           # yeux rouges vifs
# Vérifié sur rendu avec le pack desert_hamster (ciel intense, exposition +0,5, AgX) : un œil rouge ÉCLAIRÉ par ce
# ciel additionne sa lumière diffuse à son émission et vire au rose saumon. Les yeux et halos ont donc une couleur
# de base presque noire (lueur(), seule l'émission compte) et une émission modérée : rouge saturé, pas rose.
OEIL_FORCE = 1.1
OEIL_FORCE_LOIN = 2.0              # silhouettes d'horizon (d = 0) : le point est sous le pixel, on force un peu
HALO = (0.7, 0.0, 0.0)             # halo : plaque rouge sombre émissive translucide, un peu plus grande que l'œil
HALO_FORCE = 0.5
HALO_OPACITE = 0.6
CONTOUR = (1.0, 0.3, 0.07)         # liseré du soleil en contre-jour (même couleur que le soleil du pack)
CONTOUR_FORCE = 1.6
SOURCIL = (0.01, 0.004, 0.006)     # sourcils en blocs presque noirs, inclinés vers le bas au centre


def contour(mat, couleur=CONTOUR, force=CONTOUR_FORCE, durete=3.0):
    """Liseré lumineux sur les bords vus de biais (couche « facing ») : le contre-jour découpe la silhouette même
    sans lumière arrière dédiée. Branché sur l'émission du Principled : à n'utiliser que dans les .blend
    (foule_serpents) ; l'export glTF transformerait le liseré en émission sur tout le corps."""
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.5
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = durete
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = force
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mul.inputs[0])
    bsdf.inputs["Emission Color"].default_value = (*couleur, 1.0)
    nt.links.new(mul.outputs[0], bsdf.inputs["Emission Strength"])
    return mat


def lueur(nom, couleur, force):
    """Matériau qui ne fait que briller : base presque noire (le ciel ne l'éclaircit pas), émission `couleur`."""
    m = f.materiau(nom, (0.02, 0.0, 0.0), 0.6)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (*couleur, 1.0)
    bsdf.inputs["Emission Strength"].default_value = force
    m.diffuse_color = (*couleur, 1.0)
    return m


def halo(nom, couleur=HALO, force=HALO_FORCE, opacite=HALO_OPACITE):
    """Disque de lumière translucide (émission + transparence, base presque noire), sans ombre ni contour."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.02, 0.0, 0.0, 1.0)
    bsdf.inputs["Emission Color"].default_value = (*couleur, 1.0)
    bsdf.inputs["Emission Strength"].default_value = force
    bsdf.inputs["Alpha"].default_value = opacite
    m.surface_render_method = "DITHERED"
    m.use_backface_culling = False
    m.diffuse_color = (*couleur, 1.0)
    return m


SERPENTS = {
    # Foule : 11 segments, chanfrein d'un seul segment, pas de mâchoire.
    "serpent_bloc": dict(echelle=1.0, segments=11, biseau=0.025, seg_biseau=1, corps=VERT, bande=VIOLET,
                         bande_tous=3, chef=False),
    # Chef : 16 segments biseautés (gros plan), palette inversée, cicatrice, crête, crochet cassé.
    "serpent_chef_bloc": dict(echelle=1.6, segments=16, biseau=0.03, seg_biseau=2, corps=VIOLET, bande=VERT,
                              bande_tous=3, chef=True, tete=1.3),
}

# Colonne vertébrale (serpent de 1 m d'échelle) : queue au fond (+y), S posé au sol, cou qui se dresse.
COLONNE = [(0.45, 2.05, 0.08), (-0.25, 1.85, 0.11), (-0.6, 1.35, 0.14), (-0.25, 0.85, 0.16),
           (0.4, 0.62, 0.17), (0.5, 0.2, 0.18), (0.08, 0.0, 0.3), (-0.02, 0.02, 0.75),
           (0.0, -0.02, 1.15), (0.0, -0.16, 1.36)]


# ----- géométrie ---------------------------------------------------------------------------------
class Maillage:
    """Accumule des boîtes (chanfreinées) : sommets, faces, matériau par face, attribut s et os par sommet."""

    def __init__(self):
        self.v, self.faces, self.mat, self.s, self.os = [], [], [], [], []

    def boite(self, c, side, fwd, up, taille, mat, s, os_, biseau=0.0, seg=1):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * taille[0], v.co.y * taille[1], v.co.z * taille[2]))
        if biseau > 0:
            b = min(biseau, 0.45 * min(taille))
            bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=seg, affect="EDGES", profile=0.5)
        base = len(self.v)
        c, side, fwd, up = Vector(c), Vector(side), Vector(fwd), Vector(up)
        for v in bm.verts:
            self.v.append(c + side * v.co.x + fwd * v.co.y + up * v.co.z)
            self.s.append(s)
            self.os.append(os_)
        for fa in bm.faces:
            self.faces.append([base + v.index for v in fa.verts])
            self.mat.append(mat)
        bm.free()

    def objet(self, nom, materiaux, lisse=False):
        me = bpy.data.meshes.new(nom)
        me.from_pydata([tuple(p) for p in self.v], [], self.faces)
        for m in materiaux:
            me.materials.append(m)
        me.polygons.foreach_set("material_index", self.mat)
        if lisse:
            me.polygons.foreach_set("use_smooth", [True] * len(self.faces))
        at = me.attributes.new("s", "FLOAT", "POINT")
        at.data.foreach_set("value", self.s)
        o = bpy.data.objects.new(nom, me)
        bpy.context.scene.collection.objects.link(o)
        groupes = {}
        for i, g in enumerate(self.os):
            groupes.setdefault(g, []).append(i)
        for g, idx in groupes.items():
            o.vertex_groups.new(name=g).add(idx, 1.0, "REPLACE")
        return o


def _catmull(points, n=240):
    pts = [Vector(p) for p in points]
    pts = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    sortie = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n // (len(points) - 1)):
            t = k / (n // (len(points) - 1))
            sortie.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                                 + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    sortie.append(pts[-2])
    return sortie


def _repere(t, prec=None):
    side = t.cross(Vector((0, 0, 1)))
    side = Vector((-1, 0, 0)) if side.length < 0.35 else side.normalized()
    if prec is not None and side.dot(prec) < 0:
        side = -side
    up = side.cross(t).normalized()
    return side, up


def epaisseur(s):
    """Largeur du corps selon s (0 = bout de la queue, 1 = cou) : fine au bout, ventrue au milieu."""
    if s < 0.55:
        u = s / 0.55
        return 0.07 + 0.23 * (u * u * (3 - 2 * u))
    return 0.30 - 0.07 * min(1.0, (s - 0.55) / 0.3)      # cou un peu plus fin que le ventre


def construire_maillage(p, nom):
    """Renvoie (objet maillage, positions des os, données de tête). Unités : serpent d'échelle 1 (foule)."""
    k = 1.0
    M = Maillage()
    mats = [f.materiau(f"Serpent_corps_{nom}", p["corps"], 0.45), f.materiau(f"Serpent_bande_{nom}", p["bande"], 0.5),
            lueur(f"Serpent_oeil_{nom}", OEIL, OEIL_FORCE if p.get("detail", 2) >= 1 else OEIL_FORCE_LOIN),
            f.materiau(f"Serpent_noir_{nom}", NOIR, 0.3), f.materiau(f"Serpent_langue_{nom}", ROUGE, 0.4, emission=0.35),
            f.materiau(f"Serpent_ventre_{nom}", VENTRE, 0.5), halo(f"Serpent_halo_{nom}"),
            f.materiau(f"Serpent_sourcil_{nom}", SOURCIL, 0.6)]
    CORPS, BANDE, OEILM, NOIRM, LANGUE, VENTREM, HALOM, SOURCILM = range(8)
    if p["chef"]:
        mats += [f.materiau("Serpent_cicatrice", CICATRICE, 0.6, emission=0.3), f.materiau("Serpent_blanc", BLANC, 0.3, emission=0.4),
                 f.materiau("Serpent_gorge", GORGE, 0.7, emission=0.6)]
    CIC, BLANCM, GORGEM = 8, 9, 10
    courbe = _catmull(COLONNE)
    longs = [0.0]
    for a, b in zip(courbe, courbe[1:]):
        longs.append(longs[-1] + (b - a).length)
    L = longs[-1]

    def point(d):
        for i in range(1, len(longs)):
            if longs[i] >= d:
                t = (d - longs[i - 1]) / max(longs[i] - longs[i - 1], 1e-9)
                return courbe[i - 1].lerp(courbe[i], t), (courbe[i] - courbe[i - 1]).normalized()
        return courbe[-1], (courbe[-1] - courbe[-2]).normalized()

    d = p.get("detail", 2)          # 2 : complet ; 1 : foule au loin ; 0 : silhouette d'horizon
    n = p["segments"]
    pas = L / n
    side = None
    os_noms = ["S0", "S1", "S2", "S3", "S4"]
    for i in range(n):
        s = (i + 0.5) / n
        c, t = point((i + 0.5) * pas)
        side, up = _repere(t, side)
        w = epaisseur(s)
        h = w * (0.8 if s < 0.6 else 0.95)
        mat = BANDE if (n - 1 - i) % p["bande_tous"] == 1 else CORPS
        os_ = os_noms[min(4, int(s * 5))]
        M.boite(c, side, t, up, (w, pas * 1.12, h), mat, s, os_, p["biseau"], p["seg_biseau"])
        if d >= 2 and s > 0.6 and abs(up.y) > 0.4:      # ventre clair sur le cou dressé (côté -y, face à la caméra)
            devant = up if up.y < 0 else -up
            M.boite(c + devant * (h * 0.5), side, t, up, (w * 0.72, pas * 1.0, 0.03), VENTREM, s, os_, 0.0, 1)
        if p["chef"] and s > 0.55:      # crête de plaques sur la nuque
            dos = up if (up.y + up.z) > 0 else -up
            M.boite(c + dos * (h * 0.55), side, t, up, (0.05, pas * 0.6, 0.12), BANDE, s, os_, 0.012, 1)

    # Tête au bout du cou : repère horizontal regardant vers -y, un peu baissé (air menaçant).
    cou, t = point(L)
    F = Vector((0, -1, -0.18)).normalized()
    S = Vector((1, 0, 0))
    U = S.cross(F).normalized()      # vers le haut
    U = -U if U.z < 0 else U
    o = cou + (F * 0.14 + U * 0.02) * p.get("tete", 1.0)

    kt = p.get("tete", 1.0)

    def tb(df, du, ds, taille, mat, bis=0.03, seg=None, os_="Head", rot=None):
        s_, f_, u_ = S, F, U
        df, du, ds, taille = df * kt, du * kt, ds * kt, tuple(x * kt for x in taille)
        bis = bis * kt if p["biseau"] > 0 else 0.0      # niveaux de détail de la foule : pas de biseau du tout
        if rot:                       # rotation autour de F (inclinaison latérale : sourcils)
            q = Quaternion(F, rot)
            s_, u_ = q @ S, q @ U
        M.boite(o + F * df + U * du + S * ds, s_, f_, u_, taille, mat, 1.0, os_, bis, seg or p["seg_biseau"])

    tb(0.0, 0.0, 0.0, (0.40, 0.44, 0.24), CORPS, 0.06)                 # crâne
    if d >= 1:
        tb(0.2, -0.03, 0.0, (0.32, 0.22, 0.17), CORPS, 0.05)           # museau
    if d >= 2:
        tb(-0.04, 0.125, 0.0, (0.16, 0.3, 0.02), BANDE, 0.0)           # bande violette sur le crâne
    # Yeux rouges vifs (révision désert : 15 % plus gros), devant un halo = plaque rouge émissive translucide plus
    # large qui fait « baver » la lumière autour de l'œil ; la silhouette d'horizon (d = 0) a des yeux et un halo
    # exagérés (1,5 fois) pour rester visibles à 300 m. Pupille noire fendue verticale ; sourcils en blocs presque
    # noirs inclinés vers le centre (regard méchant).
    ko = 1.5 if d == 0 else 1.0
    for sx in (-1, 1):
        cote_gauche = sx == 1        # gauche du serpent = +x (il regarde vers -y)
        tb(0.17, 0.085, sx * 0.125, (0.205 * ko, 0.16, 0.195 * ko), OEILM, 0.03)          # œil rouge (front à 0,25)
        tb(0.238, 0.085, sx * 0.125, (0.245 * ko, 0.012, 0.235 * ko), HALOM, 0.0)        # halo translucide
        if d == 0:
            continue
        if p["chef"] and cote_gauche:
            tb(0.19, 0.135, sx * 0.12, (0.2, 0.16, 0.085), CORPS, 0.02)    # paupière tombante (œil balafré)
            tb(0.256, 0.05, sx * 0.125, (0.036, 0.012, 0.07), NOIRM, 0.0)   # pupille à demi cachée
        else:
            tb(0.256, 0.08, sx * 0.125, (0.038, 0.012, 0.15), NOIRM, 0.0)    # pupille fendue verticale
        # Sourcil : pavé noir épais devant le haut de l'œil, bout intérieur plus bas (regard méchant).
        tb(0.25, 0.19, sx * 0.115, (0.26, 0.07, 0.07), SOURCILM, 0.01, rot=sx * 0.5)
        if d >= 2:
            tb(0.315, 0.03, sx * 0.07, (0.035, 0.02, 0.03), NOIRM, 0.0)    # narines
    if p["chef"]:
        # Cicatrice : trois traits roses en zigzag qui barrent l'œil gauche (du front à la joue), face avant.
        for df, du, ds, ang in ((0.29, 0.2, 0.15, 0.6), (0.28, 0.085, 0.12, -0.6), (0.315, 0.005, 0.095, 0.6)):
            tb(df, du, ds, (0.026, 0.012, 0.09), CIC, 0.0, rot=ang)
        tb(-0.02, 0.125, 0.1, (0.03, 0.14, 0.012), CIC, 0.0)               # entaille sur le crâne
        # Gueule entrouverte : intérieur rouge sombre (un peu lumineux, il se lit en contre-jour), mâchoire (os Jaw),
        # deux grands crochets blancs (le droit cassé à mi-longueur) et une rangée de petites dents.
        tb(0.15, -0.135, 0.0, (0.3, 0.33, 0.07), GORGEM, 0.0)
        tb(0.14, -0.2, 0.0, (0.3, 0.34, 0.07), VENTREM, 0.02, os_="Jaw")
        tb(0.315, -0.135, -0.095, (0.04, 0.04, 0.07), BLANCM, 0.0)           # crochet droit cassé (court)
        tb(0.315, -0.16, 0.095, (0.042, 0.042, 0.13), BLANCM, 0.0)         # crochet gauche entier
        tb(0.315, -0.235, 0.095, (0.022, 0.022, 0.04), BLANCM, 0.0)         # pointe du crochet
        for k in range(4):                                                  # petites dents du haut
            tb(0.31, -0.125, -0.045 + k * 0.03, (0.018, 0.02, 0.035), BLANCM, 0.0)
    elif d >= 2:
        tb(0.3, -0.07, 0.0, (0.26, 0.03, 0.022), NOIRM, 0.0)               # fente de la bouche
    # Langue fourchue (os Tongue) : tige et deux pointes écartées.
    lt = 0.2 if p["chef"] else 0.14
    if d >= 1:
        tb(0.31 + lt / 2, -0.08, 0.0, (0.04, lt, 0.018), LANGUE, 0.0, os_="Tongue")
    for sx in ((-1, 1) if d >= 2 else ()):
        M.boite(o + (F * (0.31 + lt + 0.035) + U * -0.08 + S * (sx * 0.025)) * kt,
                (Quaternion(U, sx * 0.5) @ S), (Quaternion(U, sx * 0.5) @ F), U,
                (0.026 * kt, 0.08 * kt, 0.014 * kt), LANGUE, 1.0, "Tongue", 0.0, 1)

    obj = M.objet(nom, mats)
    os_pos = {"tete": o, "F": F, "U": U, "cou": cou, "point": point, "L": L, "langue": o + (F * 0.31 + U * -0.08) * kt}
    return obj, os_pos


# ----- squelette et animations (glb) ---------------------------------------------------------------
def greer(corps, info, chef):
    arm_d = bpy.data.armatures.new("Squelette")
    arm = bpy.data.objects.new("Armature", arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    point, L = info["point"], info["L"]
    r = arm_d.edit_bones.new("Root")
    r.head, r.tail = (0, 0, 0), (0, 0, 0.3)
    parent = r
    for i in range(5):
        a, _ = point(L * i / 5)
        b, _ = point(L * (i + 1) / 5)
        e = arm_d.edit_bones.new(f"S{i}")
        e.head, e.tail = a, b
        e.parent = parent
        e.use_connect = i > 0
        parent = e
    h = arm_d.edit_bones.new("Head")
    h.head, h.tail = info["cou"], info["tete"] + info["F"] * 0.3
    h.parent = parent
    lg = arm_d.edit_bones.new("Tongue")
    lg.head, lg.tail = info["langue"], info["langue"] + info["F"] * 0.2
    lg.parent = h
    if chef:
        j = arm_d.edit_bones.new("Jaw")
        j.head, j.tail = info["tete"] - info["U"] * 0.1 - info["F"] * 0.05, info["tete"] - info["U"] * 0.1 + info["F"] * 0.25
        j.parent = h
    bpy.ops.object.mode_set(mode="OBJECT")
    corps.parent = arm
    corps.modifiers.new("Squelette", "ARMATURE").object = arm
    return arm


def animer(arm, chef):
    pb = arm.pose.bones
    for b in pb:
        b.rotation_mode = "QUATERNION"
    arm.animation_data_create()
    repos = {b.name: arm.data.bones[b.name].matrix_local.to_quaternion() for b in pb}

    def monde(nom, axe, angle_deg):
        """Rotation autour d'un axe du MONDE (au repos) convertie dans le repère local de l'os."""
        q0 = repos[nom]
        return q0.inverted() @ Quaternion(Vector(axe), math.radians(angle_deg)) @ q0

    prefixe = "Chef_" if chef else "Serpent_"      # noms d'actions propres à chaque rig (voir hamster_bloc.py)

    def action(nom, cles, longueur):
        act = bpy.data.actions.new(prefixe + nom)
        act.use_fake_user = True
        arm.animation_data.action = act
        for img in sorted(cles):
            for b in pb:
                b.rotation_quaternion = (1, 0, 0, 0)
                b.location = (0, 0, 0)
                b.scale = (1, 1, 1)
            for os_, val in cles[img].items():
                if os_.endswith(":scale"):
                    pb[os_[:-6]].scale = val
                elif os_.endswith(":loc"):
                    pb[os_[:-4]].location = val
                else:
                    q = Quaternion((1, 0, 0, 0))
                    for axe, ang in val:
                        q = monde(os_, axe, ang) @ q
                    pb[os_].rotation_quaternion = q
            for b in pb:
                b.keyframe_insert("rotation_quaternion", frame=img)
                b.keyframe_insert("location", frame=img)
                b.keyframe_insert("scale", frame=img)
        act.frame_range = (0, longueur)
        return act

    Z, X = (0, 0, 1), (1, 0, 0)

    def ondule(img, periode, amp=9.0, tete=6.0, langue=1.0):
        ph = 2 * math.pi * img / periode
        c = {f"S{i}": [(Z, amp * (1 - i / 6) * math.sin(ph - i * 1.1))] for i in range(4)}
        c["S4"] = [(Z, 4 * math.sin(ph - 4.4)), (X, 2 * math.sin(2 * ph))]
        c["Head"] = [(Z, tete * math.sin(ph - 5.0)), (X, 3 * math.sin(2 * ph + 1))]
        c["Tongue:scale"] = (1, langue, 1)
        return c

    # Idle : 48 images ; la langue pointe deux fois (images 10-14 et 34-38), rentrée sinon.
    def langue_idle(i):
        return 1.0 if (10 <= i <= 14 or 34 <= i <= 38) else 0.25
    action("Idle", {i: ondule(i, 48, langue=langue_idle(i)) for i in range(0, 49, 2)}, 48)
    # Tongue (b03) : tête qui s'avance un peu, langue sortie à l'image 6, vibre, rentre à 30, ressort à 36.
    def tongue(i):
        c = ondule(i, 48, amp=4, tete=2)
        c["Head"] = c["Head"] + [(X, 8 * min(1, i / 6))] if i < 40 else c["Head"]
        out = min(1, i / 6) if i <= 24 else (max(0.2, 1 - (i - 24) / 6) if i < 34 else min(1.0, 0.2 + (i - 34) / 4))
        c["Tongue:scale"] = (1, 0.2 + 1.3 * out, 1)
        c["Tongue"] = [(Z, 14 * math.sin(i * 2.4) * out)]      # vibration de la pointe
        if chef:
            c["Jaw"] = [(X, -10 * out)]
        return c
    action("Tongue", {i: tongue(i) for i in range(0, 49, 1)}, 48)
    # Hiss : se dresse et recule (cou en arrière), gueule ouverte, puis revient. 36 images.
    def hiss(i):
        a = math.sin(math.pi * min(1, i / 30))
        c = ondule(i, 36, amp=3, tete=1)
        c["S3"] = [(X, -10 * a)]
        c["S4"] = [(X, -14 * a)]
        c["Head"] = [(X, 16 * a), (Z, 3 * math.sin(i))]
        c["Tongue:scale"] = (1, 0.3 + 1.0 * a, 1)
        if chef:
            c["Jaw"] = [(X, -28 * a)]
        return c
    action("Hiss", {i: hiss(i) for i in range(0, 37, 2)}, 36)
    # Attack : armé en arrière (images 0-5), détente vers l'avant (image 8), retour (20).
    def attack(i):
        if i <= 5:
            a = -i / 5
        elif i <= 8:
            a = -1 + 2 * (i - 5) / 3
        else:
            a = max(0.0, 1 - (i - 8) / 12)
        c = {"S3": [(X, 18 * a)], "S4": [(X, 22 * a)], "Head": [(X, -10 * a)], "Tongue:scale": (1, 0.3, 1)}
        if chef:
            c["Jaw"] = [(X, -30 * max(0, a))]
        return c
    action("Attack", {i: attack(i) for i in range(0, 21)}, 20)
    arm.animation_data.action = bpy.data.actions[prefixe + "Idle"]


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(SERPENTS)
    for asset_id in args:
        p = SERPENTS[asset_id]
        f.vider()
        corps, info = construire_maillage(p, asset_id)
        arm = greer(corps, info, p["chef"])
        animer(arm, p["chef"])
        k = p["echelle"]
        arm.scale = (k, k, k)
        chemin = f.MODELES / asset_id / f"{asset_id}.glb"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", export_animation_mode="ACTIONS",
                                  export_force_sampling=True)
        n_tri = sum(len(q.vertices) - 2 for q in corps.data.polygons)
        print(f"MODELE_EXPORTE {asset_id} : {chemin} ({n_tri} triangles)")


if __name__ == "__main__":
    main()
