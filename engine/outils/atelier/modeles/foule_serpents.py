"""Foule « foule_serpents » : 10 000 serpents en INSTANCES qui remplissent l'horizon (série « 10 000 serpents contre
1 hamster », création du projet ; révision « désert » du 2026-11-19 pour le décor desert_hamster).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/foule_serpents.py

Écrit engine/assets/modeles/foule_serpents/foule_serpents.blend, collection « Foule » (à placer en [0, 0, 0] avec
desert_hamster, le hamster à l'origine) : un seul objet « Foule_serpents », nuage de 10 000 points (un point = un
serpent) porteur d'un modificateur Geometry Nodes qui instancie trois niveaux de détail du serpent de serpent_bloc.py :
- proches (1 400, de 9 à 40 m) : serpent_bloc complet (816 triangles), réalisés puis ONDULÉS sommet par sommet
  (vague latérale qui remonte le corps, tête qui se balance et dodeline ; phase différente pour chaque serpent),
  animés par le numéro d'image (aucune clé : ça tourne tout seul dans le moteur) ;
- milieu (4 600, de 40 à 180 m, échelle 1 à 2) : version sans biseau, restent des instances, balancement propre à
  chacun (rotation de l'instance) ;
- horizon (4 000, de 180 à 650 m, échelle 2 à 3,6) : silhouette (4 segments, crâne, gros yeux ; détail bas
  seulement très loin).
Disposition : demi-anneau au nord (angles de -12° à 192°, vers +y), tous tournés vers le hamster, POSÉS SUR LE SABLE
(z = desert_hamster.hauteur(x, y) : dunes basses, presque plat près du hamster), à l'écart des rochers du décor :
chaque serpent se découpe sur le sable clair. Corps vert foncé / violet (pas noirs) avec liseré rouge-orangé de
contre-jour, YEUX ROUGES très émissifs à halo. Brume claire rose-orangé (desert_hamster.BRUME) intégrée aux
matériaux : nulle avant 60 m, elle monte vers l'horizon et noie la fin de la foule ; les yeux ne s'y fondent qu'au
tiers (des milliers de points rouges jusqu'au fond), les halos pas du tout.
Les modèles sources sont dans la collection « Foule_sources » (hors de « Foule »).
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import bpy

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent))
sys.path.insert(0, str(ICI))
import formes as f  # noqa: E402
import instances as ins  # noqa: E402
import serpent_bloc as sb  # noqa: E402
import desert_hamster as dh  # noqa: E402

ZONES = [
    # (variante, nombre, rayon min, rayon max, exposant de densité α (densité ∝ r^-α), distance mini au rayon min,
    #  échelle au rayon min, au rayon max, écart d'orientation °). Densités et échelles raccordées d'une zone à l'autre
    # (sinon on voit des anneaux) : environ 0,5 serpent/m² à 40 m, 0,03 à 180 m.
    (0, 1400, 9.0, 40.0, 0.0, 1.15, 1.0, 1.0, 25),
    (1, 4600, 40.0, 180.0, 1.9, 1.15, 1.0, 2.0, 40),
    (2, 4000, 180.0, 650.0, 2.0, 4.4, 2.0, 3.6, 60),
]
BRUME = dh.BRUME
ANGLE_MIN, ANGLE_MAX = math.radians(-12), math.radians(192)


def tirer(rng, n, r0, r1, alpha, dmin0):
    """Tirage dans le demi-anneau, densité ∝ r^-α, distance minimale qui grandit avec r (dmin0 · (r/r0)^(α/2))."""
    beta = 2.0 - alpha

    def rayon(u):
        if abs(beta) < 1e-6:
            return r0 * (r1 / r0) ** u
        return (r0 ** beta + u * (r1 ** beta - r0 ** beta)) ** (1 / beta)

    def dmin(r):
        return dmin0 * (r / r0) ** (alpha / 2)

    cell = dmin(r1)
    grille = {}
    pts = []
    essais = 0
    while len(pts) < n and essais < n * 80:
        essais += 1
        r = rayon(rng.random())
        a = rng.uniform(ANGLE_MIN, ANGLE_MAX)
        x, y = r * math.cos(a), r * math.sin(a)
        d = dmin(r)
        gx, gy = int(math.floor(x / cell)), int(math.floor(y / cell))
        ok = all((qx - x) ** 2 + (qy - y) ** 2 >= d * d
                 for i in range(gx - 1, gx + 2) for j in range(gy - 1, gy + 2) for (qx, qy) in grille.get((i, j), ()))
        if ok and any((x - rx) ** 2 + (y - ry) ** 2 < (1.1 * t + 1.3) ** 2 for rx, ry, t, _ in dh.ROCHERS):
            ok = False                                 # pas de serpent dans un rocher
        if ok:
            grille.setdefault((gx, gy), []).append((x, y))
            pts.append((x, y))
    while len(pts) < n:                                # zone saturée : on complète sans contrainte
        r = rayon(rng.random())
        a = rng.uniform(ANGLE_MIN, ANGLE_MAX)
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def champ_camera(a):
    """Champ booléen « ce serpent est dans le champ de la caméra active » (sur les points du nuage).

    Test de sphère contre les quatre plans latéraux du cône de vue (matrice de projection de la caméra active,
    donc la focale et le format du plan en cours) : centre du serpent à 0,4 × échelle au-dessus du sol, rayon
    MARGE × échelle (serpent de 2,9 × 1,5 × 1,6 m à l'échelle 1, ondulation comprise : 2,6 × échelle). Les ombres n'en
    souffrent pas : le soleil est derrière la foule (nord) et les ombres filent vers la caméra, donc un serpent
    hors champ projette son ombre encore plus hors champ. Sans caméra active (vue 3D sans caméra), focale nulle :
    tout est gardé."""
    cam = a.noeud("GeometryNodeInputActiveCamera").outputs[0]
    info = a.noeud("GeometryNodeObjectInfo", {"Object": cam}, transform_space="RELATIVE")
    cinfo = a.noeud("GeometryNodeCameraInfo", {"Camera": cam})
    inv = a.noeud("FunctionNodeInvertMatrix", {"Matrix": info.outputs["Transform"]}).outputs[0]
    e = a.attr("echelle")
    pos = a.noeud("GeometryNodeInputPosition").outputs[0]
    centre = a.noeud("ShaderNodeVectorMath", {0: pos, 1: a.xyz(0.0, 0.0, a.math("MULTIPLY", e, 0.4))},
                     operation="ADD").outputs[0]
    v = a.noeud("FunctionNodeTransformPoint", {"Vector": centre, "Transform": inv}).outputs[0]
    vx, vy, vz = a.noeud("ShaderNodeSeparateXYZ", {0: v}).outputs[:3]
    proj = a.noeud("FunctionNodeSeparateMatrix", {"Matrix": cinfo.outputs["Projection Matrix"]})
    rayon = a.math("MULTIPLY", e, MARGE)
    w = a.math("MULTIPLY", vz, -1.0)                        # profondeur devant la caméra
    ok = a.math("GREATER_THAN", a.math("ADD", w, rayon), 0.0)
    for s, comp in ((proj.outputs["Column 1 Row 1"], vx), (proj.outputs["Column 2 Row 2"], vy)):
        # distance au plan latéral : (s·|v| − w) / √(s² + 1) < rayon
        d = a.math("SUBTRACT", a.math("MULTIPLY", s, a.math("ABSOLUTE", comp)), w)
        lim = a.math("MULTIPLY", rayon, a.math("SQRT", a.math("MULTIPLY_ADD", s, s, 1.0)))
        ok = a.math("MULTIPLY", ok, a.math("LESS_THAN", d, lim))
    sans_cam = a.math("LESS_THAN", cinfo.outputs["Focal Length"], 0.001)
    return a.math("GREATER_THAN", a.math("ADD", ok, sans_cam), 0.5)


MARGE = 2.6
CULLING = True


def main():
    f.vider()
    sc = bpy.context.scene
    col = bpy.data.collections.new("Foule")
    sc.collection.children.link(col)
    src = bpy.data.collections.new("Foule_sources")
    sc.collection.children.link(src)

    base = sb.SERPENTS["serpent_bloc"]
    niveaux = [dict(base, detail=2), dict(base, detail=1, segments=8, biseau=0.0),
               dict(base, detail=0, segments=4, biseau=0.0)]
    sources, tris = [], []
    for k, p in enumerate(niveaux):
        o, _ = sb.construire_maillage(p, f"V{k:02d}_serpent")
        for m in o.data.materials:
            if any(k in m.name for k in ("_corps_", "_bande_", "_ventre_")):
                sb.contour(m)                            # liseré rouge-orangé de contre-jour
            if "_halo_" in m.name:
                continue                                 # disque translucide : la brume le rendrait opaque
            oeil = "_oeil_" in m.name
            ins.brume(m, BRUME, debut=60.0, fin=900.0, force=0.35 if oeil else 0.95)
        for c in list(o.users_collection):
            c.objects.unlink(o)
        src.objects.link(o)
        o.vertex_groups.clear()
        sources.append(o)
        print("DIMENSIONS", o.name, tuple(round(c, 2) for c in o.dimensions))
        tris.append(sum(len(q.vertices) - 2 for q in o.data.polygons))

    rng = random.Random(10000)
    pts, var, rotz, ech, phase = [], [], [], [], []
    for v, n, r0, r1, alpha, dmin0, e0, e1, ecart in ZONES:
        for (x, y) in tirer(rng, n, r0, r1, alpha, dmin0):
            r = math.hypot(x, y)
            u = math.log(r / r0) / math.log(r1 / r0)
            pts.append((x, y, dh.hauteur(x, y)))
            var.append(v)
            # face au hamster (l'avant du serpent est -y local) : rotation θ telle que (sin θ, -cos θ) = -p/|p|
            rotz.append(math.atan2(-x / r, y / r) + math.radians(rng.uniform(-ecart, ecart)))
            ech.append(rng.uniform(0.85, 1.15) * (e0 + (e1 - e0) * u))
            phase.append(rng.uniform(0, 2 * math.pi))
    assert len(pts) == 10000, len(pts)
    nuage = ins.nuage("Foule_serpents", pts, {"variante": ("INT", var), "rotz": ("FLOAT", rotz),
                                               "echelle": ("FLOAT", ech), "phase": ("FLOAT", phase)},
                      materiau=sources[0].data.materials[0])
    col.objects.link(nuage)

    a = ins.Arbre("GN_foule_serpents")
    points = a.entree_geo()
    var_f = a.attr("variante", "INT")
    rot = a.noeud("FunctionNodeEulerToRotation", {"Euler": a.xyz(0, 0, a.attr("rotz"))}).outputs[0]
    t = a.temps()
    w = 2 * math.pi / 40.0                                   # une ondulation toutes les 40 images (1,3 s à 30 i/s)
    vu = champ_camera(a) if CULLING else None
    sorties = []
    for k, o in enumerate(sources):
        sel = a.math("COMPARE", var_f, float(k), 0.1)
        if vu is not None:
            sel = a.math("MULTIPLY", sel, vu)                 # hors champ : ni instancié, ni réalisé, ni ondulé
        info = a.noeud("GeometryNodeObjectInfo", {"Object": o, "As Instance": True})
        inst = a.noeud("GeometryNodeInstanceOnPoints", {"Points": points, "Selection": sel,
                                                        "Instance": info.outputs["Geometry"], "Rotation": rot,
                                                        "Scale": a.attr("echelle")}).outputs[0]
        if k == 0:
            # Proches : on réalise les instances puis on ondule chaque sommet (attribut « s » du serpent).
            geo = a.noeud("GeometryNodeRealizeInstances", {"Geometry": inst}).outputs[0]
            s = a.attr("s")
            ph = a.attr("phase")
            e = a.attr("echelle")
            rz = a.attr("rotz")
            arg = a.math("ADD", a.math("SUBTRACT", a.math("MULTIPLY", t, w), a.math("MULTIPLY", s, 6.5)), ph)
            amp = a.math("MULTIPLY", e, a.math("MULTIPLY_ADD", a.math("SUBTRACT", 1.0, s), 0.12, 0.025))
            lat = a.math("MULTIPLY", amp, a.math("SINE", arg))
            cou = a.math("MAXIMUM", 0.0, a.math("MULTIPLY", a.math("SUBTRACT", s, 0.7), 3.33))   # 0 → 1 sur le cou
            tete = a.math("MULTIPLY", a.math("MULTIPLY", cou, e),
                          a.math("MULTIPLY", 0.07, a.math("SINE", a.math("ADD", a.math("MULTIPLY", t, w * 0.5), ph))))
            lat = a.math("ADD", lat, tete)                    # la tête se balance plus lentement
            dz = a.math("MULTIPLY", a.math("MULTIPLY", cou, e),
                        a.math("MULTIPLY", 0.05, a.math("SINE", a.math("ADD", a.math("MULTIPLY", t, w), a.math("ADD", ph, 1.3)))))
            off = a.xyz(a.math("MULTIPLY", lat, a.math("COSINE", rz)), a.math("MULTIPLY", lat, a.math("SINE", rz)), dz)
            geo = a.noeud("GeometryNodeSetPosition", {"Geometry": geo, "Offset": off}).outputs[0]
        else:
            # Milieu et horizon : instances balancées (lacet ± 6°, tangage ± 3°), sans réaliser la géométrie.
            ph = a.attr("phase")
            lacet = a.math("MULTIPLY", 0.1, a.math("SINE", a.math("ADD", a.math("MULTIPLY", t, w * 0.7), ph)))
            tangage = a.math("MULTIPLY", 0.05, a.math("SINE", a.math("ADD", a.math("MULTIPLY", t, w), ph)))
            r_inst = a.noeud("FunctionNodeEulerToRotation", {"Euler": a.xyz(tangage, 0.0, lacet)}).outputs[0]
            geo = a.noeud("GeometryNodeRotateInstances", {"Instances": inst, "Rotation": r_inst,
                                                          "Local Space": True}).outputs[0]
        sorties.append(geo)
    join = a.noeud("GeometryNodeJoinGeometry")
    for g in reversed(sorties):
        a.ng.links.new(g, join.inputs[0])
    a.sortie_geo(join.outputs[0])
    a.poser(nuage, "Foule")

    for o in list(sc.collection.objects):
        sc.collection.objects.unlink(o)
    chemin = f.MODELES / "foule_serpents" / "foule_serpents.blend"
    if "--" in sys.argv[1:]:                               # essai : autre chemin de sortie (après « -- »)
        chemin = Path(sys.argv[sys.argv.index("--") + 1])
    chemin.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(chemin), compress=True)
    total = sum(tris[v] for v in var)
    print(f"MODELE_EXPORTE foule_serpents : {chemin} (10 000 serpents ; triangles par niveau {tris} ; "
          f"{total} triangles au total, dont {tris[0] * var.count(0)} réalisés et ondulés)")


main()
