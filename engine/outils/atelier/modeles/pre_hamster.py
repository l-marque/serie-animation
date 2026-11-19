"""Décor « pre_hamster » : grand pré d'herbe haute en fin d'après-midi (série « 10 000 serpents contre 1 hamster »).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/pre_hamster.py

Écrit engine/assets/modeles/pre_hamster/pre_hamster.blend, collection « Pre » (à placer en [0, 0, 0]) :
- sol de prairie plat (disque de 1 200 m de rayon, z = 0), matériau procédural très foncé (révision « peur » du
  2026-11-19 : verts noirs, herbe sèche brun sombre) qui se fond dans une brume rouge brun avec la distance (brume d'horizon intégrée
  au matériau : le moteur n'a pas de brume ; la caméra du moteur coupe à 1 000 m) ;
- environ 33 000 touffes d'herbe en INSTANCES (nœuds de géométrie sur un nuage de points, 8 variantes : herbe
  courte, moyenne, haute, épis dorés, marguerites, coquelicots, pissenlits, pissenlits en graines). Clairière d'herbe
  rase de 6 m de rayon autour de l'origine (là où se tient le hamster et son armée), herbe haute au-delà ;
- brume basse rougeâtre : quatre anneaux émissifs translucides (230 à 900 m, 10 à 70 m de haut, sans ombre) qui
  noient la fin de la foule de serpents dans une lueur rouge au ras de l'horizon (impression d'infini) ;
- nuages d'orage en blocs : plafond bas de pavés plats biseautés qui se chevauchent (trois rangs, 380 à 860 m au
  nord, 7 à 26° au-dessus de l'horizon), silhouettes violet noir au dessous rougeoyant, sans ombre ;
- détails qui racontent : le terrier du hamster (butte de terre et trou sombre) en (-2,6 ; 1,8), son petit tas de
  graines de tournesol en (1,7 ; 1,1), trois cailloux, une taupinière.
Les modèles des touffes sont dans la collection « Pre_sources » (hors de « Pre », importée avec l'arbre de nœuds).
Repères (empties) : REP_hamster (0, 0, 0), REP_terrier, REP_graines.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402
import instances as ins  # noqa: E402

PACK = json.loads((f.RACINE / "engine" / "packs_da" / "pre_hamster.json").read_text(encoding="utf-8"))
# Révision « peur » (pack v1.1 : ciel violet-sang sombre, soleil rouge au nord en contre-jour) : le lointain se fond
# dans une brume rouge brun un peu plus chaude et plus claire que le ciel (lueur basse du soleil couchant) ; la même
# couleur que foule_serpents.BRUME. Les anneaux de brume (ANNEAUX) montent cette lueur au-dessus de l'horizon.
BRUME = (0.11, 0.012, 0.014)
# Anneaux de brume basse : (rayon m, hauteur m, opacité au pied). Cylindres émissifs translucides (opacité qui
# décroît vers le haut), sans ombre portée : ils noient le fond de la foule (180-650 m) dans le rouge.
ANNEAUX = [(230.0, 10.0, 0.3), (380.0, 20.0, 0.45), (560.0, 36.0, 0.75), (900.0, 70.0, 0.95)]
CLAIRIERE = 6.0


def brume(mat, debut=70.0, fin=950.0, force=1.0):
    return ins.brume(mat, BRUME, debut, fin, force)


def materiau_sol():
    m = f.materiau("Pre_sol", (0.012, 0.04, 0.005), rugosite=0.92)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    coord = nt.nodes.new("ShaderNodeTexCoord")
    grand = nt.nodes.new("ShaderNodeTexNoise")
    grand.inputs["Scale"].default_value = 0.035
    grand.inputs["Detail"].default_value = 3.0
    petit = nt.nodes.new("ShaderNodeTexNoise")
    petit.inputs["Scale"].default_value = 0.6
    petit.inputs["Detail"].default_value = 2.0
    rampe = nt.nodes.new("ShaderNodeValToRGB")
    cr = rampe.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.35, (0.005, 0.025, 0.003, 1)
    cr.elements[1].position, cr.elements[1].color = 0.66, (0.04, 0.04, 0.01, 1)      # herbe sèche, brun sombre
    e = cr.elements.new(0.5)
    e.color = (0.01, 0.05, 0.004, 1)
    melange = nt.nodes.new("ShaderNodeMath")
    melange.operation = "MULTIPLY_ADD"
    melange.inputs[1].default_value = 0.25
    nt.links.new(coord.outputs["Object"], grand.inputs["Vector"])
    nt.links.new(coord.outputs["Object"], petit.inputs["Vector"])
    nt.links.new(petit.outputs["Fac"], melange.inputs[0])
    nt.links.new(grand.outputs["Fac"], melange.inputs[2])
    nt.links.new(melange.outputs[0], rampe.inputs["Fac"])
    nt.links.new(rampe.outputs["Color"], bsdf.inputs["Base Color"])
    return brume(m)


def anneau_brume(nom, rayon, hauteur, opacite, segments=128):
    """Cylindre émissif translucide (vu de l'intérieur) : opacité `opacite` au pied, nulle en haut (courbe douce)."""
    bm = bmesh.new()
    bas, haut = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        bas.append(bm.verts.new((rayon * math.cos(a), rayon * math.sin(a), -1.0)))
        haut.append(bm.verts.new((rayon * math.cos(a), rayon * math.sin(a), hauteur)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new((bas[i], bas[j], haut[j], haut[i]))
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    sortie = nt.nodes[0]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")            # z : 0 → 1, hauteur → 0
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = hauteur
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.8
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = opacite
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*BRUME, 1.0)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mul.inputs[0])
    nt.links.new(mul.outputs[0], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], sortie.inputs["Surface"])
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"          # pas de grain de tramage sur un grand aplat
    m.use_backface_culling = False
    me.materials.append(m)
    o = bpy.data.objects.new(nom, me)
    o.visible_shadow = False                         # sinon le soleil rasant projetterait l'anneau sur tout le pré
    return o


def nuages(rng):
    """Nuages d'orage en blocs, bas et lourds, au-dessus de la foule (nord) : masses violet noir un peu plus sombres
    que le ciel (silhouettes), dessous rougeoyant (lueur du soleil couchant : émission selon la normale vers le bas).
    Sans ombre portée. Pavés biseautés allongés face à l'origine."""
    m = f.materiau("Pre_nuage", (0.012, 0.003, 0.01), rugosite=1.0)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (0.32, 0.015, 0.02, 1.0)
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")            # normale z : -1 (dessous) → 0,3 ; -0,2 et plus → 0,04
    mr.inputs["From Min"].default_value = -1.0
    mr.inputs["From Max"].default_value = -0.2
    mr.inputs["To Min"].default_value = 0.3
    mr.inputs["To Max"].default_value = 0.04
    nt.links.new(geo.outputs["Normal"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], bsdf.inputs["Emission Strength"])
    bm = bmesh.new()
    # Plafond bas : bandes de pavés plats qui se chevauchent sur tout le secteur nord (la foule), en trois rangs de
    # distance ; chaque bande est une suite de pavés décalés en hauteur (dessous en escalier).
    for rang, (r0, r1, e0, e1, n) in enumerate(((380, 480, 16, 25, 9), (520, 660, 10, 17, 16), (700, 860, 7, 12, 20))):
        for k in range(n):
            az = math.radians(-5 + 190 * (k + rng.uniform(0.0, 0.8)) / n)
            r = rng.uniform(r0, r1)
            elev = math.radians(rng.uniform(e0, e1))
            cx, cy, cz = r * math.cos(az), r * math.sin(az), r * math.tan(elev)
            rot = az + math.pi / 2
            larg = r * math.radians(190 / n) * rng.uniform(1.2, 1.8)         # bandes qui se recouvrent
            for j in range(rng.randint(2, 4)):
                t = (larg * rng.uniform(0.45, 0.85), rng.uniform(60, 140), r * rng.uniform(0.035, 0.07))
                dx, dy = rng.uniform(-0.35, 0.35) * larg, rng.uniform(-40, 40)
                dz = rng.uniform(-0.5, 1.0) * t[2] * (j > 0)
                tmp = bmesh.ops.create_cube(bm, size=1.0)
                vs = tmp["verts"]
                for v in vs:
                    x, y, z = v.co.x * t[0] + dx, v.co.y * t[1] + dy, v.co.z * t[2] + dz
                    v.co = Vector((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot),
                                   cz + z))
                aretes = list({e for v in vs for e in v.link_edges})
                bmesh.ops.bevel(bm, geom=aretes, offset=min(t) * 0.18, segments=1, affect="EDGES", profile=0.5)
    me = bpy.data.meshes.new("Pre_nuages")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m)
    o = bpy.data.objects.new("Pre_nuages", me)
    o.visible_shadow = False
    return o


# ----- touffes ---------------------------------------------------------------------------------------
def lame(bm, base, hauteur, largeur, inclinaison, azimut, mat):
    """Brin d'herbe en bloc effilé (base carrée, sommet pointu), penché vers l'extérieur."""
    d = Vector((math.sin(inclinaison) * math.cos(azimut), math.sin(inclinaison) * math.sin(azimut), math.cos(inclinaison)))
    cote = Vector((-math.sin(azimut), math.cos(azimut), 0)) * (largeur / 2)
    epais = d.cross(cote).normalized() * (largeur * 0.18)
    b = Vector(base)
    haut = b + d * hauteur
    milieu = b + d * hauteur * 0.55
    anneaux = [[b - cote - epais, b + cote - epais, b + cote + epais, b - cote + epais],
               [milieu - cote * 0.75 - epais * 0.8, milieu + cote * 0.75 - epais * 0.8,
                milieu + cote * 0.75 + epais * 0.8, milieu - cote * 0.75 + epais * 0.8]]
    vs = [[bm.verts.new(p) for p in a] for a in anneaux]
    pointe = bm.verts.new(haut + Vector((0, 0, 0)))
    faces = []
    for i in range(4):
        j = (i + 1) % 4
        faces.append(bm.faces.new((vs[0][i], vs[0][j], vs[1][j], vs[1][i])))
        faces.append(bm.faces.new((vs[1][i], vs[1][j], pointe)))
    for fa in faces:
        fa.material_index = mat


def bloc_bm(bm, c, t, mat, rot_z=0.0):
    tmp = bmesh.ops.create_cube(bm, size=1.0)
    for v in tmp["verts"]:
        x, y, z = v.co.x * t[0], v.co.y * t[1], v.co.z * t[2]
        v.co = Vector((c[0] + x * math.cos(rot_z) - y * math.sin(rot_z), c[1] + x * math.sin(rot_z) + y * math.cos(rot_z),
                       c[2] + z))
    for fa in {fa for v in tmp["verts"] for fa in v.link_faces}:
        fa.material_index = mat


def touffe(nom, mats, rng, n, h0, h1, fleur=None, epis=False):
    bm = bmesh.new()
    for i in range(n):
        az = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        r = rng.uniform(0.0, 0.13)
        h = rng.uniform(h0, h1)
        lame(bm, (r * math.cos(az), r * math.sin(az), 0), h, rng.uniform(0.04, 0.07), rng.uniform(0.12, 0.45), az,
             rng.choice((0, 0, 1, 1, 2)))
    if epis:                                     # tiges dorées à épi (contre-jour de fin d'après-midi)
        for i in range(3):
            az = rng.uniform(0, 2 * math.pi)
            h = rng.uniform(h1 * 1.05, h1 * 1.3)
            lame(bm, (0.03 * math.cos(az), 0.03 * math.sin(az), 0), h, 0.02, rng.uniform(0.05, 0.2), az, 3)
            inc = 0.12
            top = Vector((math.sin(inc) * math.cos(az), math.sin(inc) * math.sin(az), math.cos(inc))) * h
            for k in range(4):
                bloc_bm(bm, top + Vector((0, 0, 0.05 * k - 0.05)), (0.035, 0.035, 0.05), 3, az)
    if fleur:
        couleur_petale, couleur_coeur, hauteur, nb = fleur
        lame(bm, (0, 0, 0), hauteur, 0.02, 0.05, 0.0, 0)
        haut = (math.sin(0.05) * hauteur, 0, math.cos(0.05) * hauteur)
        if nb == 0:                              # pissenlit en graines : une boule blanche en bloc
            bloc_bm(bm, haut, (0.08, 0.08, 0.08), couleur_petale)
        else:
            for k in range(nb):
                a = 2 * math.pi * k / nb
                bloc_bm(bm, (haut[0] + 0.045 * math.cos(a), haut[1] + 0.045 * math.sin(a), haut[2]), (0.06, 0.035, 0.015),
                        couleur_petale, a)
            bloc_bm(bm, (haut[0], haut[1], haut[2] + 0.01), (0.04, 0.04, 0.025), couleur_coeur)
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    return bpy.data.objects.new(nom, me)


def main():
    f.vider()
    sc = bpy.context.scene
    col = bpy.data.collections.new("Pre")
    sc.collection.children.link(col)
    src = bpy.data.collections.new("Pre_sources")
    sc.collection.children.link(src)
    rng = random.Random(19)

    # Sol.
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=1200.0, segments=64)
    me = bpy.data.meshes.new("Pre_sol")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(materiau_sol())
    sol = bpy.data.objects.new("Pre_sol", me)
    col.objects.link(sol)

    # Modèles de touffes (Pre_sources), matériaux : vert, vert clair, vert jaune, paille, fleurs.
    # Tons d'orage : herbe très foncée (le liseré rouge du soleil en contre-jour fait le reste), fleurs éteintes ;
    # les coquelicots rouge sang, plus nombreux, font écho aux yeux des serpents.
    mats = [brume(f.materiau("Herbe_vert", (0.005, 0.04, 0.003), 0.6)),
            brume(f.materiau("Herbe_clair", (0.014, 0.075, 0.004), 0.6)),
            brume(f.materiau("Herbe_jaune", (0.04, 0.06, 0.007), 0.6)),
            brume(f.materiau("Herbe_paille", (0.14, 0.07, 0.025), 0.6)),
            brume(f.materiau("Fleur_blanc", (0.24, 0.21, 0.2), 0.5)),
            brume(f.materiau("Fleur_jaune", (0.3, 0.14, 0.0), 0.5)),
            brume(f.materiau("Fleur_rouge", (0.42, 0.006, 0.005), 0.5)),
            brume(f.materiau("Fleur_noir", (0.012, 0.008, 0.008), 0.5))]
    variantes = [
        touffe("V00_courte", mats, rng, 9, 0.14, 0.3),
        touffe("V01_moyenne", mats, rng, 9, 0.35, 0.6),
        touffe("V02_haute", mats, rng, 11, 0.7, 1.1),
        touffe("V03_epis", mats, rng, 8, 0.55, 0.85, epis=True),
        touffe("V04_marguerite", mats, rng, 4, 0.1, 0.2, fleur=(4, 5, 0.36, 7)),
        touffe("V05_coquelicot", mats, rng, 4, 0.12, 0.25, fleur=(6, 7, 0.55, 4)),
        touffe("V06_pissenlit", mats, rng, 5, 0.08, 0.16, fleur=(5, 5, 0.24, 6)),
        touffe("V07_graines", mats, rng, 4, 0.1, 0.18, fleur=(4, 4, 0.42, 0)),
    ]
    for v in variantes:
        src.objects.link(v)
    tri_variantes = [sum(len(p.vertices) - 2 for p in v.data.polygons) for v in variantes]

    # Nuage de points : zones (rayon min, rayon max, densité / m², poids des variantes, échelle min, max).
    zones = [
        (0.0, CLAIRIERE, 3.2, (10, 0, 0, 0, 0.4, 0.9, 0.4, 0.15), 0.9, 1.4),  # clairière : herbe rase, coquelicots
        (CLAIRIERE, 40.0, 2.6, (3, 5, 3, 1.2, 0.15, 0.6, 0.1, 0.06), 0.9, 1.3),
        (40.0, 150.0, 0.22, (0, 4, 4, 2, 0.3, 0.4, 0, 0), 1.3, 1.9),
        (150.0, 600.0, 0.012, (0, 2, 5, 3, 0, 0, 0, 0), 2.2, 3.2),
    ]
    pts, var, rotz, ech = [], [], [], []
    for r0, r1, dens, poids, e0, e1 in zones:
        n = int(dens * math.pi * (r1 * r1 - r0 * r0))
        for _ in range(n):
            r = math.sqrt(rng.uniform(r0 * r0, r1 * r1))
            a = rng.uniform(0, 2 * math.pi)
            x, y = r * math.cos(a), r * math.sin(a)
            if math.hypot(x + 2.6, y - 1.8) < 0.9 or math.hypot(x - 1.7, y - 1.1) < 0.45:
                continue                         # pas d'herbe sur le terrier ni sur le tas de graines
            pts.append((x, y, 0.0))
            var.append(rng.choices(range(8), weights=poids)[0])
            rotz.append(rng.uniform(0, 2 * math.pi))
            ech.append(rng.uniform(e0, e1))
    nuage = ins.nuage("Pre_touffes", pts, {"variante": ("INT", var), "rotz": ("FLOAT", rotz), "echelle": ("FLOAT", ech)},
                      materiau=mats[0])
    col.objects.link(nuage)
    a = ins.Arbre("GN_pre_touffes")
    a.sortie_geo(ins.instancier_variantes(a, a.entree_geo(), src))
    a.poser(nuage, "Touffes")

    # Détails qui racontent.
    terre = f.materiau("Pre_terre", (0.2, 0.1, 0.04), 0.95)
    trou = f.materiau("Pre_trou", (0.012, 0.006, 0.004), 1.0)
    caillou = f.materiau("Pre_caillou", (0.3, 0.27, 0.22), 0.85)
    graine = f.materiau("Pre_graine", (0.05, 0.05, 0.055), 0.5)
    rayure = f.materiau("Pre_graine_rayure", (0.7, 0.68, 0.6), 0.5)
    pieces = []
    # Terrier : butte de terre ouverte vers la caméra, trou sombre.
    tx, ty = -2.6, 1.8
    for i, (dx, dy, sx, sy, sz) in enumerate(((0, 0.25, 1.5, 0.9, 0.32), (-0.55, -0.1, 0.6, 0.9, 0.22),
                                              (0.6, -0.05, 0.6, 0.8, 0.25), (0.1, 0.6, 1.0, 0.5, 0.2))):
        pieces.append(f.boite(f"terrier_{i}", (tx + dx, ty + dy, sz / 2 - 0.04), (sx, sy, sz), terre, biseau=0.12, segments=3))
    pieces.append(f.boite("terrier_trou", (tx, ty - 0.18, 0.16), (0.62, 0.08, 0.36), trou, biseau=0.12, segments=3))
    for i in range(6):                                           # mottes éparpillées devant
        pieces.append(f.boite(f"motte_{i}", (tx + rng.uniform(-0.9, 0.9), ty - rng.uniform(0.6, 1.2), 0.03),
                              (rng.uniform(0.12, 0.2),) * 2 + (0.07,), terre, biseau=0.03, segments=2,
                              rotation=(0, 0, rng.uniform(0, 3))))
    # Tas de graines de tournesol (rayées) : la réserve du hamster.
    gx, gy = 1.7, 1.1
    for i in range(16):
        r = rng.uniform(0, 0.28) * (1 - i / 20)
        a_ = rng.uniform(0, 2 * math.pi)
        z = 0.03 + (0.06 if i > 9 else 0.0) + (0.05 if i > 13 else 0.0)
        rot = (rng.uniform(-0.4, 0.4), rng.uniform(-0.4, 0.4), rng.uniform(0, 3.1))
        pieces.append(f.boite(f"graine_{i}", (gx + r * math.cos(a_), gy + r * math.sin(a_), z), (0.07, 0.16, 0.05), graine,
                              biseau=0.02, segments=2, rotation=rot))
        pieces.append(f.boite(f"graine_r_{i}", (gx + r * math.cos(a_), gy + r * math.sin(a_), z + 0.026),
                              (0.018, 0.14, 0.006), rayure, biseau=0.0, rotation=rot))
    # Cailloux et taupinière.
    for i, (x, y, t) in enumerate(((-7.5, 4.0, 0.7), (8.2, -2.5, 0.5), (5.0, 13.0, 1.1))):
        pieces.append(f.boite(f"caillou_{i}", (x, y, t * 0.3), (t, t * 0.8, t * 0.6), caillou, biseau=t * 0.2, segments=3,
                              rotation=(0.1, -0.08, rng.uniform(0, 3))))
    pieces.append(f.boite("taupiniere", (4.5, 3.5, 0.08), (0.7, 0.6, 0.22), terre, biseau=0.1, segments=3))
    details = f.fusionner(pieces, "Pre_details")
    for c in list(details.users_collection):
        c.objects.unlink(details)
    col.objects.link(details)
    col.objects.link(nuages(random.Random(66)))       # ciel d'orage : nuages en blocs au-dessus de la foule
    for k, (r, h, op) in enumerate(ANNEAUX):        # brume basse rougeâtre : cache la fin de la foule
        col.objects.link(anneau_brume(f"Pre_brume_{k}", r, h, op))
    for nom, p in (("REP_hamster", (0, 0, 0)), ("REP_terrier", (tx, ty, 0)), ("REP_graines", (gx, gy, 0))):
        e = bpy.data.objects.new(nom, None)
        e.location = p
        col.objects.link(e)
    for o in list(sc.collection.objects):         # rien ne doit traîner hors des collections
        sc.collection.objects.unlink(o)

    chemin = f.MODELES / "pre_hamster" / "pre_hamster.blend"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    n_inst = len(pts)
    tri_inst = sum(tri_variantes[v] for v in var)
    tri_fixes = sum(len(p.vertices) - 2 for p in details.data.polygons) + 64
    bpy.ops.wm.save_as_mainfile(filepath=str(chemin), compress=True)
    print(f"MODELE_EXPORTE pre_hamster : {chemin} ({n_inst} touffes en instances, {tri_inst} triangles instanciés, "
          f"{tri_fixes} triangles fixes ; variantes : {tri_variantes})")


main()
