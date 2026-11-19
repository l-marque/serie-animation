"""Décor « desert_hamster » : désert de sable ocre clair sous un ciel rouge-magenta (série « 10 000 serpents contre
1 hamster », création du projet, 2026-11-19 ; remplace le pré de pre_hamster pour hamster-jour-0).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/desert_hamster.py

Écrit engine/assets/modeles/desert_hamster/desert_hamster.blend, collection « Desert » (à placer en [0, 0, 0],
le hamster à l'origine, "sol": false dans la fiche). Pensé pour le pack desert_hamster v1.1 (lumineux : la peur
vient du rouge, du contre-jour et des yeux rouges, pas du noir) :
- sol de sable (disque de 1 200 m) en longues dunes BASSES : crêtes presque nord-sud (vues de face depuis le sud,
  elles fuient vers l'horizon au lieu de cacher la foule), hauteur nulle dans la zone du hamster (rayon 8 m,
  parfaitement plane), 0,3 à 0,6 m vers 30 m, 1,5 m au plus à l'horizon ; pentes < 5° (soleil à 6°). La hauteur
  est donnée par hauteur(x, y), réutilisée par foule_serpents.py pour poser chaque serpent sur le sable ;
- matériau de sable procédural ocre clair (crêtes plus claires, creux plus chauds) qui se
  fond, au loin seulement (60 à 900 m), dans une brume claire rose-orangé (0,9 ; 0,35 ; 0,25) ;
- brume d'horizon : trois anneaux émissifs translucides (420, 650, 950 m) de la même couleur, qui noient la fin
  de la foule dans une bande lumineuse au ras de l'horizon (jamais au premier plan) ;
- soleil en blocs : grand disque octogonal orange très lumineux au nord, bas sur l'horizon, exactement dans la
  direction du soleil du pack (contre-jour derrière la foule), à moitié voilé par la brume ;
- détails qui racontent : terrier du hamster (trou sombre au pied d'un rocher en strates, sable déblayé en
  éventail, trois graines de tournesol qu'il a laissé tomber, empreintes de pattes du trou jusqu'à lui) ; deux os
  blanchis au premier plan (un fémur à moitié ensablé, une cage thoracique enterrée : d'autres n'ont pas eu sa
  chance) ; quelques rochers en blocs sur les côtés. Pas d'herbe, pas de particules (rendu rapide).
Repères (empties) : REP_hamster (0, 0, 0), REP_terrier.
"""
from __future__ import annotations

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

BRUME = (0.9, 0.35, 0.25)            # brume claire rose-orangé (demande de prod-chef, pack desert_hamster v1.1)
SABLE = (0.5, 0.25, 0.065)           # = rôle « sol » du pack (matériaux d'origine gardés : on reprend sa couleur)
SABLE_CLAIR = (0.62, 0.34, 0.1)      # crêtes
SABLE_CREUX = (0.42, 0.18, 0.045)    # creux, plus chauds
ZONE_PLATE = 8.0                     # rayon de la zone du hamster, parfaitement plane
# Rochers : (x, y, taille, graine). Hors du demi-anneau de la foule ou à l'écart (foule_serpents évite leur rayon).
ROCHERS = [(-3.1, 3.0, 1.0, 1), (-7.8, -1.6, 0.8, 2), (8.4, -2.4, 0.6, 3), (16.0, 24.0, 1.6, 4), (-22.0, 31.0, 2.2, 5),
           (48.0, 70.0, 3.5, 6)]
TERRIER = (-2.35, 2.2)
SOLEIL_DIR = Vector((0.0, math.sin(math.radians(84)), math.cos(math.radians(84))))   # pack : rotation (84, 0, 180)


def _lisse(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def hauteur(x: float, y: float) -> float:
    """Hauteur du sable (m). 0 dans la zone du hamster ; longues dunes basses aux crêtes presque nord-sud."""
    r = math.hypot(x, y)
    if r < ZONE_PLATE:
        return 0.0
    amp = _lisse(ZONE_PLATE, 45.0, r) * (0.45 + 0.55 * _lisse(45.0, 350.0, r))
    a1 = math.radians(18)                       # direction perpendiculaire aux crêtes : presque est-ouest
    u = (x * math.cos(a1) + y * math.sin(a1)) / 85.0 + 0.35 * math.sin(y / 160.0)
    d1 = (0.5 + 0.5 * math.sin(2 * math.pi * u)) ** 1.6          # dos doux, crête un peu plus marquée
    a2 = math.radians(-40)
    v = (x * math.cos(a2) + y * math.sin(a2)) / 33.0
    d2 = 0.5 + 0.5 * math.sin(2 * math.pi * v + 1.3)
    return amp * (1.25 * d1 + 0.3 * d2)


def materiau_sable():
    m = f.materiau("Desert_sable", SABLE, rugosite=0.95)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 0.04
    bruit.inputs["Detail"].default_value = 3.0
    fac = nt.nodes.new("ShaderNodeMath")              # z / 1,6 + bruit × 0,35 : crêtes claires, creux chauds
    fac.operation = "MULTIPLY_ADD"
    fac.inputs[1].default_value = 1 / 1.6
    fac2 = nt.nodes.new("ShaderNodeMath")
    fac2.operation = "MULTIPLY_ADD"
    fac2.inputs[1].default_value = 0.35
    rampe = nt.nodes.new("ShaderNodeValToRGB")
    cr = rampe.color_ramp
    cr.elements[0].position, cr.elements[0].color = 0.2, (*SABLE_CREUX, 1)
    cr.elements[1].position, cr.elements[1].color = 0.95, (*SABLE_CLAIR, 1)
    e = cr.elements.new(0.42)
    e.color = (*SABLE, 1)
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(geo.outputs["Position"], bruit.inputs["Vector"])
    nt.links.new(bruit.outputs["Fac"], fac2.inputs[0])
    nt.links.new(sep.outputs["Z"], fac.inputs[0])
    nt.links.new(fac2.outputs[0], fac.inputs[2])
    fac2.inputs[2].default_value = 0.25
    nt.links.new(fac.outputs[0], rampe.inputs["Fac"])
    nt.links.new(rampe.outputs["Color"], bsdf.inputs["Base Color"])
    return ins.brume(m, BRUME, debut=60.0, fin=900.0, force=0.95)


def sol():
    """Disque de sable en anneaux de plus en plus larges (fin près du hamster, grossier au loin)."""
    rayons = [0.0, 2.0, 4.0, 6.0, ZONE_PLATE]
    while rayons[-1] < 1200.0:
        rayons.append(min(1200.0, rayons[-1] * 1.05 + 0.6))
    n = 256
    bm = bmesh.new()
    centre = bm.verts.new((0, 0, 0))
    prec = None
    for r in rayons[1:]:
        anneau = []
        for i in range(n):
            a = 2 * math.pi * i / n
            x, y = r * math.cos(a), r * math.sin(a)
            anneau.append(bm.verts.new((x, y, hauteur(x, y))))
        for i in range(n):
            j = (i + 1) % n
            if prec is None:
                bm.faces.new((centre, anneau[i], anneau[j]))
            else:
                bm.faces.new((prec[i], anneau[i], anneau[j], prec[j]))
        prec = anneau
    me = bpy.data.meshes.new("Desert_sol")
    bm.to_mesh(me)
    bm.free()
    me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    me.materials.append(materiau_sable())
    return bpy.data.objects.new("Desert_sol", me)


def anneau_brume(nom, rayon, haut, opacite, segments=128):
    """Cylindre émissif translucide vu de l'intérieur : opacité `opacite` au pied, nulle en haut."""
    bm = bmesh.new()
    bas, sommet = [], []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        bas.append(bm.verts.new((rayon * math.cos(a), rayon * math.sin(a), -2.0)))
        sommet.append(bm.verts.new((rayon * math.cos(a), rayon * math.sin(a), haut)))
    for i in range(segments):
        j = (i + 1) % segments
        bm.faces.new((bas[i], bas[j], sommet[j], sommet[i]))
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(nd)
    sortie = nt.nodes[0]
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = haut
    mr.inputs["To Min"].default_value = 1.0
    mr.inputs["To Max"].default_value = 0.0
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 1.6
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
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    me.materials.append(m)
    o = bpy.data.objects.new(nom, me)
    o.visible_shadow = False
    return o


def soleil():
    """Disque octogonal émissif dans la direction du soleil du pack, à 900 m (la caméra coupe à 1 000 m), avec une
    couronne plus large et plus pâle (lueur) : le contre-jour a une source visible derrière la foule."""
    centre = SOLEIL_DIR * 900.0
    fwd = -SOLEIL_DIR                      # la face regarde l'origine
    side = Vector((1, 0, 0))
    up = fwd.cross(side).normalized()
    up = -up if up.z < 0 else up
    pieces = []
    for nom, rayon, coul, force, recul in (("Soleil_coeur", 32.0, (1.0, 0.42, 0.1), 3.5, 0.0),
                                           ("Soleil_couronne", 60.0, (1.0, 0.25, 0.08), 2.0, 2.0)):
        bm = bmesh.new()
        c0 = bm.verts.new(centre + SOLEIL_DIR * recul)
        bord = [bm.verts.new(centre + SOLEIL_DIR * recul + (side * math.cos(a) + up * math.sin(a)) * rayon)
                for a in (math.pi / 8 + k * math.pi / 4 for k in range(8))]
        for k in range(8):
            bm.faces.new((c0, bord[k], bord[(k + 1) % 8]))
        me = bpy.data.meshes.new(nom)
        bm.to_mesh(me)
        bm.free()
        m = bpy.data.materials.new(nom)
        m.use_nodes = True
        nt = m.node_tree
        for nd in list(nt.nodes):
            if nd.type != "OUTPUT_MATERIAL":
                nt.nodes.remove(nd)
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (*coul, 1.0)
        em.inputs["Strength"].default_value = force
        if recul > 0:                      # couronne : lueur translucide, pas un anneau opaque
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mix = nt.nodes.new("ShaderNodeMixShader")
            mix.inputs["Fac"].default_value = 0.35
            nt.links.new(tr.outputs[0], mix.inputs[1])
            nt.links.new(em.outputs[0], mix.inputs[2])
            nt.links.new(mix.outputs[0], nt.nodes[0].inputs["Surface"])
            m.surface_render_method = "BLENDED"
        else:
            nt.links.new(em.outputs[0], nt.nodes[0].inputs["Surface"])
        me.materials.append(m)
        o = bpy.data.objects.new(nom, me)
        o.visible_shadow = False
        pieces.append(o)
    return pieces


def rocher(x, y, t, graine, mats):
    """Rocher en strates : 2 à 4 blocs biseautés empilés et décalés, une strate plus claire."""
    rng = random.Random(graine)
    z0 = hauteur(x, y) - 0.08 * t
    pieces = []
    z = z0
    for k in range(rng.randint(2, 4) if t > 0.7 else 2):
        sx = t * rng.uniform(0.9, 1.5) * (1 - 0.18 * k)
        sy = t * rng.uniform(0.8, 1.2) * (1 - 0.18 * k)
        sz = t * rng.uniform(0.35, 0.6)
        mat = mats[1] if k % 2 == 1 else mats[0]
        pieces.append(f.boite(f"roc_{graine}_{k}", (x + rng.uniform(-0.15, 0.15) * t, y + rng.uniform(-0.15, 0.15) * t,
                                                     z + sz / 2), (sx, sy, sz), mat, biseau=0.12 * t, segments=2,
                              rotation=(rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), rng.uniform(0, 3.1))))
        z += sz * 0.92
    if t > 0.7:                              # éboulis au pied
        for k in range(3):
            a = rng.uniform(0, 2 * math.pi)
            s = t * rng.uniform(0.15, 0.3)
            pieces.append(f.boite(f"eboulis_{graine}_{k}", (x + math.cos(a) * t * 0.9, y + math.sin(a) * t * 0.9,
                                                            z0 + s * 0.4), (s, s * 0.8, s * 0.7), mats[0],
                                  biseau=s * 0.2, segments=1, rotation=(0.2, 0.1, a)))
    return pieces


def os_blanchis(mat, rng):
    pieces = []
    # Fémur à moitié ensablé, au premier plan à droite (tige + têtes en blocs).
    cx, cy, ang = 1.15, -1.85, math.radians(28)
    d = Vector((math.cos(ang), math.sin(ang), 0))
    pieces.append(f.boite("femur_tige", (cx, cy, 0.04), (0.78, 0.11, 0.1), mat, biseau=0.03, segments=2,
                          rotation=(0.0, 0.05, ang)))
    for s in (-1, 1):
        for k, (dx, dy) in enumerate(((0.0, 0.06), (0.0, -0.06))):
            p = Vector((cx, cy, 0.05)) + d * (s * 0.42) + Vector((-d.y, d.x, 0)) * dy
            pieces.append(f.boite(f"femur_tete_{s}_{k}", tuple(p), (0.16, 0.13, 0.14), mat, biseau=0.05, segments=2,
                                  rotation=(0, 0, ang + 0.3 * s)))
    # Cage thoracique enterrée derrière à droite : épine dorsale et côtes en arcs de blocs qui sortent du sable.
    bx, by = 1.7, 4.3
    for k in range(5):
        pieces.append(f.boite(f"vertebre_{k}", (bx - 0.6 + k * 0.3, by, 0.04), (0.2, 0.14, 0.12), mat, biseau=0.03,
                              segments=1, rotation=(0, 0, rng.uniform(-0.1, 0.1))))
    for k in range(4):
        x = bx - 0.45 + k * 0.3
        for s in (-1, 1):
            haut = 0.55 - 0.08 * abs(k - 1.5)
            for j, (dy, z, rx) in enumerate(((0.12, 0.12, 0.35), (0.25, 0.33, 0.75), (0.32, haut - 0.1, 1.3))):
                if s == 1 and k == 3 and j == 2:
                    continue                      # une côte cassée
                pieces.append(f.boite(f"cote_{k}_{s}_{j}", (x, by + s * dy, z), (0.05, 0.07, 0.24), mat, biseau=0.015,
                                      segments=1, rotation=(-s * rx, 0, 0)))
    return pieces


def terrier(mats, rng):
    sable, sable_clair, trou, graine, rayure, empreinte = mats
    tx, ty = TERRIER
    pieces = []
    # Trou ovale (octogone aplati) un peu enfoncé, bord de sable déblayé derrière et sur les côtés.
    pieces.append(f.boite("terrier_trou", (tx, ty, 0.0), (0.72, 0.5, 0.06), trou, biseau=0.2, segments=2))
    for k, (dx, dy, sx, sy, sz) in enumerate(((0, 0.38, 0.9, 0.3, 0.16), (-0.48, 0.1, 0.3, 0.5, 0.12),
                                               (0.48, 0.12, 0.28, 0.45, 0.13))):
        pieces.append(f.boite(f"terrier_bord_{k}", (tx + dx, ty + dy, sz * 0.35), (sx, sy, sz), sable_clair,
                              biseau=0.06, segments=2))
    # Éventail de sable déblayé devant (vers le hamster), petites mottes plates.
    for k in range(7):
        a = math.radians(rng.uniform(-150, -40))
        r = rng.uniform(0.45, 1.0)
        s = rng.uniform(0.12, 0.22)
        pieces.append(f.boite(f"deblai_{k}", (tx + r * math.cos(a), ty + r * math.sin(a), 0.015), (s, s * 0.8, 0.05),
                              sable_clair, biseau=0.02, segments=1, rotation=(0, 0, rng.uniform(0, 3))))
    # Trois graines de tournesol tombées en chemin (rayées).
    for k, (gx, gy, a) in enumerate(((-1.5, 1.4, 0.4), (-1.15, 1.05, 1.9), (-0.9, 0.55, -0.6))):
        pieces.append(f.boite(f"graine_{k}", (gx, gy, 0.025), (0.07, 0.15, 0.05), graine, biseau=0.02, segments=2,
                              rotation=(0.1, 0, a)))
        pieces.append(f.boite(f"graine_r_{k}", (gx, gy, 0.051), (0.018, 0.13, 0.006), rayure, rotation=(0.1, 0, a)))
    # Empreintes de pattes du trou jusqu'au hamster (pas alternés).
    p0, p1 = Vector((tx + 0.25, ty - 0.35, 0)), Vector((-0.35, 0.45, 0))
    dirn = (p1 - p0).normalized()
    lat = Vector((-dirn.y, dirn.x, 0))
    n = 7
    for k in range(n):
        p = p0.lerp(p1, k / (n - 1)) + lat * (0.07 if k % 2 else -0.07)
        ang = math.atan2(dirn.y, dirn.x) - math.pi / 2
        pieces.append(f.boite(f"empreinte_{k}", (p.x, p.y, 0.002), (0.07, 0.08, 0.006), empreinte, rotation=(0, 0, ang)))
        for j in (-1, 0, 1):
            q = p + dirn * 0.065 + lat * (0.03 * j)
            pieces.append(f.boite(f"doigt_{k}_{j}", (q.x, q.y, 0.002), (0.022, 0.025, 0.006), empreinte))
    return pieces


def main():
    f.vider()
    sc = bpy.context.scene
    col = bpy.data.collections.new("Desert")
    sc.collection.children.link(col)
    rng = random.Random(7)

    sol_o = sol()
    col.objects.link(sol_o)

    def mat(nom, c, r=0.85, em=0.0):
        return ins.brume(f.materiau(nom, c, r, emission=em), BRUME, debut=60.0, fin=900.0, force=0.95)

    roche = [mat("Desert_roche", (0.3, 0.12, 0.05)), mat("Desert_roche_strate", (0.45, 0.2, 0.07))]
    os_m = mat("Desert_os", (0.72, 0.62, 0.46), 0.6)
    m_terrier = [mat("Desert_sable_tas", SABLE, 0.95), mat("Desert_sable_deblai", SABLE_CLAIR, 0.95),
                 mat("Desert_trou", (0.035, 0.014, 0.008), 1.0), mat("Desert_graine", (0.05, 0.045, 0.05), 0.5),
                 mat("Desert_graine_rayure", (0.7, 0.66, 0.58), 0.5), mat("Desert_empreinte", (0.36, 0.16, 0.04), 1.0)]
    pieces = []
    for x, y, t, g in ROCHERS:
        pieces += rocher(x, y, t, g, roche)
    pieces += os_blanchis(os_m, rng)
    pieces += terrier(m_terrier, rng)
    details = f.fusionner(pieces, "Desert_details")
    for c in list(details.users_collection):
        c.objects.unlink(details)
    col.objects.link(details)

    for k, (r, h, op) in enumerate(((420.0, 14.0, 0.35), (650.0, 28.0, 0.6), (950.0, 55.0, 0.9))):
        col.objects.link(anneau_brume(f"Desert_brume_{k}", r, h, op))
    for o in soleil():
        col.objects.link(o)
    for nom, p in (("REP_hamster", (0, 0, 0)), ("REP_terrier", (*TERRIER, 0))):
        e = bpy.data.objects.new(nom, None)
        e.location = p
        col.objects.link(e)
    for o in list(sc.collection.objects):
        sc.collection.objects.unlink(o)

    tri = sum(len(p.vertices) - 2 for o in col.objects if o.type == "MESH" for p in o.data.polygons)
    chemin = f.MODELES / "desert_hamster" / "desert_hamster.blend"
    chemin.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(chemin), compress=True)
    print(f"MODELE_EXPORTE desert_hamster : {chemin} ({tri} triangles)")


if __name__ == "__main__":
    main()
