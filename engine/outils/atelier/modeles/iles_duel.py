"""Décor « iles_duel » (série « 7 Jours avant l'Attaque », création du projet) : mer turquoise et deux îles vides.

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/iles_duel.py

Écrit engine/assets/modeles/iles_duel/iles_duel.blend, collection « Iles », lue par le moteur comme
un asset de bibliothèque (.blend + collection), placé en [0, 0, 0] dans la fiche.

Repère (brief iles-jour-1) : île Instagram centrée en (-20, 0, 0), île YouTube en (20, 0, 0), environ
18 m de diamètre au niveau de l'eau ; dessus de l'herbe PLAT à z = 0 (rayon 6,5 m au moins), sable en
pente douce jusqu'à l'eau (z = -0,3) ; mer de 3 km de côté, horizon propre. Rayon de 5 m libre au centre.
Un mât au bord arrière (y = +6) : drapeau dégradé rose-violet (Instagram), rouge (YouTube), sans logo ;
les drapeaux ondulent tout seuls (modificateur Onde, animé par le numéro d'image).
Détails : lagon plus clair autour des îles (couleur de l'eau calculée dans le matériau), liseré
d'écume, rochers en blocs, un palmier par île, une étoile de mer sur la plage d'Instagram, un seau
oublié sur celle de YouTube. Repères « REP_* » (empties) pour viser les plans de caméra.
"""
import math
import random
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

DOSSIER = f.MODELES / "iles_duel"
NIVEAU_EAU = -0.3
ILES = {"instagram": -20.0, "youtube": 20.0}
rng = random.Random(7)

f.vider()
sc = bpy.context.scene

M = {
    "herbe": f.materiau("Ile_herbe", (0.1, 0.5, 0.02), 0.9),
    "herbe_bord": f.materiau("Ile_herbe_bord", (0.06, 0.33, 0.015), 0.9),
    "sable": f.materiau("Ile_sable", (0.8, 0.58, 0.28), 0.95),
    "sable_mouille": f.materiau("Ile_sable_mouille", (0.5, 0.36, 0.17), 0.55),
    "roche": f.materiau("Ile_roche", (0.3, 0.3, 0.32), 0.9),
    "roche_claire": f.materiau("Ile_roche_claire", (0.48, 0.46, 0.44), 0.9),
    "tronc": f.materiau("Palmier_tronc", (0.32, 0.18, 0.07), 0.85),
    "tronc_bague": f.materiau("Palmier_bague", (0.22, 0.12, 0.04), 0.85),
    "palme": f.materiau("Palmier_palme", (0.08, 0.55, 0.05), 0.6),
    "coco": f.materiau("Noix_coco", (0.17, 0.09, 0.03), 0.6),
    "mat": f.materiau("Mat_blanc", (0.85, 0.85, 0.82), 0.35),
    "or": f.materiau("Mat_pommeau_or", (0.9, 0.62, 0.08), 0.3, metal=0.8),
    "rouge_yt": f.materiau("Drapeau_rouge", (0.75, 0.01, 0.01), 0.55),
    "ecume": f.materiau("Ecume", (0.9, 0.95, 0.95), 0.6),
    "etoile": f.materiau("Etoile_de_mer", (0.85, 0.2, 0.05), 0.6),
    "seau": f.materiau("Seau_bleu", (0.02, 0.2, 0.75), 0.4),
}


# ----- matériaux à nœuds : eau (lagon clair près des îles) et drapeau dégradé ----------------------
def materiau_eau():
    m = bpy.data.materials.new("Mer_turquoise")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.14
    if "Specular IOR Level" in bsdf.inputs:  # reflet du ciel atténué : la mer reste turquoise même de loin
        bsdf.inputs["Specular IOR Level"].default_value = 0.22
    coord = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(coord.outputs["Object"], sep.inputs[0])
    # distance au centre de l'île la plus proche : |x| - 20 et y
    absx = nt.nodes.new("ShaderNodeMath"); absx.operation = "ABSOLUTE"
    nt.links.new(sep.outputs["X"], absx.inputs[0])
    dx = nt.nodes.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = 20.0
    nt.links.new(absx.outputs[0], dx.inputs[0])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(dx.outputs[0], comb.inputs["X"])
    nt.links.new(sep.outputs["Y"], comb.inputs["Y"])
    long_ = nt.nodes.new("ShaderNodeVectorMath"); long_.operation = "LENGTH"
    nt.links.new(comb.outputs[0], long_.inputs[0])
    # bruit pour casser le cercle parfait du lagon
    bruit = nt.nodes.new("ShaderNodeTexNoise")
    bruit.inputs["Scale"].default_value = 0.15
    nt.links.new(coord.outputs["Object"], bruit.inputs["Vector"])
    ajout = nt.nodes.new("ShaderNodeMath"); ajout.operation = "MULTIPLY_ADD"
    ajout.inputs[1].default_value = 3.0
    nt.links.new(bruit.outputs["Fac"], ajout.inputs[0])
    nt.links.new(long_.outputs["Value"], ajout.inputs[2])
    rampe = nt.nodes.new("ShaderNodeMapRange")
    rampe.inputs["From Min"].default_value = 12.0
    rampe.inputs["From Max"].default_value = 34.0
    nt.links.new(ajout.outputs[0], rampe.inputs["Value"])
    couleurs = nt.nodes.new("ShaderNodeValToRGB")
    cr = couleurs.color_ramp
    cr.elements[0].color = (0.0, 0.62, 0.52, 1)   # lagon turquoise clair
    cr.elements[1].color = (0.0, 0.1, 0.36, 1)    # large, bleu profond
    e = cr.elements.new(0.35)
    e.color = (0.0, 0.33, 0.5, 1)
    nt.links.new(rampe.outputs["Result"], couleurs.inputs["Fac"])
    nt.links.new(couleurs.outputs["Color"], bsdf.inputs["Base Color"])
    # vaguelettes : relief de bruit (reflets du soleil)
    vag = nt.nodes.new("ShaderNodeTexNoise")
    vag.inputs["Scale"].default_value = 1.6
    vag.inputs["Detail"].default_value = 4.0
    nt.links.new(coord.outputs["Object"], vag.inputs["Vector"])
    relief = nt.nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.12
    nt.links.new(vag.outputs["Fac"], relief.inputs["Height"])
    nt.links.new(relief.outputs["Normal"], bsdf.inputs["Normal"])
    m.diffuse_color = (0.02, 0.4, 0.5, 1)
    return m


def materiau_degrade(nom, c1, c2, c3):
    """Dégradé en diagonale sur les UV du drapeau (couleurs seulement, aucun motif)."""
    m = bpy.data.materials.new(nom)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.55
    uv = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uv.outputs["UV"], sep.inputs[0])
    somme = nt.nodes.new("ShaderNodeMath"); somme.operation = "ADD"
    nt.links.new(sep.outputs["X"], somme.inputs[0])
    nt.links.new(sep.outputs["Y"], somme.inputs[1])
    moitie = nt.nodes.new("ShaderNodeMath"); moitie.operation = "MULTIPLY"; moitie.inputs[1].default_value = 0.5
    nt.links.new(somme.outputs[0], moitie.inputs[0])
    rampe = nt.nodes.new("ShaderNodeValToRGB")
    cr = rampe.color_ramp
    cr.elements[0].color = (*c1, 1)
    cr.elements[1].color = (*c3, 1)
    cr.elements.new(0.5).color = (*c2, 1)
    nt.links.new(moitie.outputs[0], rampe.inputs["Fac"])
    nt.links.new(rampe.outputs["Color"], bsdf.inputs["Base Color"])
    m.diffuse_color = (*c2, 1)
    return m


M["eau"] = materiau_eau()
M["degrade_ig"] = materiau_degrade("Drapeau_rose_violet", (1.0, 0.45, 0.02), (0.85, 0.02, 0.32), (0.28, 0.02, 0.7))


# ----- mer -------------------------------------------------------------------------------------------
bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, NIVEAU_EAU))
mer = bpy.context.object
mer.name = "Mer"
mer.data.materials.append(M["eau"])
# fond marin sombre sous les îles (évite de voir le vide à travers les bords)


# ----- îles : disque radial en bmesh, herbe plate à z = 0, sable en pente douce ----------------------
def rayon_herbe(a, graine):
    return 6.9 + 0.35 * math.sin(3 * a + graine) + 0.25 * math.sin(5 * a + 2 * graine)


def ile(nom, cx, graine):
    """Renvoie l'objet île. Profil : herbe (z = 0) jusqu'à r_h, petite marche de 6 cm, sable
    jusqu'à l'eau vers r = 9, puis talus sous-marin jusqu'à -2,5 m."""
    secteurs = 72
    bm = bmesh.new()
    centre = bm.verts.new((cx, 0, 0))
    # anneaux : (fraction ou rayon absolu, z, matériau de la bande qui suit vers l'extérieur)
    anneaux = []
    for i in range(secteurs):
        a = 2 * math.pi * i / secteurs
        rh = rayon_herbe(a, graine)
        rs = rh + 2.3 + 0.3 * math.sin(4 * a + graine * 1.7)  # bord de l'eau
        prof = [
            (rh * 0.5, 0.0), (rh - 0.02, 0.0),          # herbe plate
            (rh + 0.06, -0.06),                         # petite marche herbe / sable
            (rh + (rs - rh) * 0.5, -0.14),              # sable sec
            (rs - 0.25, -0.25), (rs, NIVEAU_EAU - 0.02),   # sable mouillé
            (rs + 1.6, -1.0), (rs + 4.0, -2.5),         # talus sous l'eau
        ]
        anneaux.append([bm.verts.new((cx + r * math.cos(a), r * math.sin(a), z)) for r, z in prof])
    mats = [0, 1, 2, 2, 3, 3, 3]  # herbe, herbe_bord, sable, sable, mouillé...
    n = len(anneaux[0])
    for i in range(secteurs):
        j = (i + 1) % secteurs
        f0 = bm.faces.new((centre, anneaux[i][0], anneaux[j][0]))
        f0.material_index = 0
        for k in range(n - 1):
            fa = bm.faces.new((anneaux[i][k], anneaux[i][k + 1], anneaux[j][k + 1], anneaux[j][k]))
            fa.material_index = mats[k] if k < len(mats) else 3
    bm.normal_update()
    me = bpy.data.meshes.new(nom)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    sc.collection.objects.link(o)
    for mat in (M["herbe"], M["herbe_bord"], M["sable"], M["sable_mouille"]):
        o.data.materials.append(mat)
    # normales : la face doit regarder vers +z
    f.selectionner([o])
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode="OBJECT")
    for p in o.data.polygons:
        p.use_smooth = p.material_index != 0
    return o


def ecume(nom, cx, graine):
    """Liseré d'écume irrégulier, juste au-dessus de l'eau, là où le sable plonge."""
    secteurs = 72
    bm = bmesh.new()
    interieur, exterieur = [], []
    for i in range(secteurs):
        a = 2 * math.pi * i / secteurs
        rs = rayon_herbe(a, graine) + 2.3 + 0.3 * math.sin(4 * a + graine * 1.7)
        largeur = 0.25 + 0.2 * (0.5 + 0.5 * math.sin(7 * a + graine))
        interieur.append(bm.verts.new((cx + (rs - 0.05) * math.cos(a), (rs - 0.05) * math.sin(a), NIVEAU_EAU + 0.012)))
        exterieur.append(bm.verts.new((cx + (rs + largeur) * math.cos(a), (rs + largeur) * math.sin(a), NIVEAU_EAU + 0.012)))
    for i in range(secteurs):
        j = (i + 1) % secteurs
        bm.faces.new((interieur[i], exterieur[i], exterieur[j], interieur[j]))
    me = bpy.data.meshes.new(nom)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(nom, me)
    sc.collection.objects.link(o)
    o.data.materials.append(M["ecume"])
    return o


def rocher(nom, p, t, mat="roche"):
    o = f.boite(nom, p, t, M[mat], biseau=min(t) * 0.25, segments=1,
                rotation=(rng.uniform(-0.25, 0.25), rng.uniform(-0.25, 0.25), rng.uniform(0, math.pi)))
    return o


def palmier(nom, base, penche, graine):
    """Palmier en blocs : tronc en tronçons décalés (courbe), bagues sombres, palmes en lames pliées, noix."""
    r = random.Random(graine)
    pieces = []
    x, y, z = base
    dx, dy = penche
    h_seg = 0.55
    for k in range(9):
        t = k / 8
        cx = x + dx * t * t * 1.6
        cy = y + dy * t * t * 1.6
        cote = 0.42 - 0.12 * t
        pieces.append(f.boite("tr", (cx, cy, z + h_seg * (k + 0.5)), (cote, cote, h_seg * 0.92),
                              M["tronc"] if k % 2 == 0 else M["tronc_bague"], biseau=0.05, segments=1,
                              rotation=(0, 0, r.uniform(-0.3, 0.3))))
    sommet = Vector((x + dx * 1.6, y + dy * 1.6, z + h_seg * 9))
    for k in range(7):
        a = 2 * math.pi * k / 7 + r.uniform(-0.2, 0.2)
        d = Vector((math.cos(a), math.sin(a), 0))
        # palme en deux lames : la première monte un peu, la seconde retombe
        for s, (l, pente) in enumerate(((1.3, 0.25), (1.3, -0.7))):
            debut = sommet + d * (0.55 + 1.25 * s) + Vector((0, 0, 0.12 if s == 0 else -0.05))
            lame = f.boite("pa", debut, (1.35, 0.55 - 0.15 * s, 0.07), M["palme"], biseau=0.02, segments=1)
            lame.rotation_euler = (0, -math.atan(pente) * 0.8, a)
            lame.location = debut
            pieces.append(lame)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        pieces.append(f.boite("co", sommet + Vector((0.28 * math.cos(a), 0.28 * math.sin(a), -0.28)), (0.26, 0.26, 0.26),
                              M["coco"], biseau=0.07, segments=1))
    for o in pieces:
        f.selectionner([o])
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return f.fusionner(pieces, nom)


def mat_et_drapeau(nom, cx, mat_drapeau, graine):
    """Mât blanc (6 m) au bord arrière, socle de pierres, pommeau doré, drapeau 2,6 × 1,6 m vers +x
    (vu de face depuis le sud) qui ondule grâce au modificateur Onde (poids nul côté mât)."""
    x, y = cx, 6.0
    h = 6.0
    pieces = [f.tube("mat", (x, y, -0.1), (x, y, h), 0.07, M["mat"], cotes=12),
              f.boite("socle", (x, y, 0.15), (0.7, 0.7, 0.3), M["roche_claire"], biseau=0.08, segments=1,
                      rotation=(0, 0, 0.3)),
              f.boite("socle2", (x + 0.15, y - 0.1, 0.38), (0.4, 0.4, 0.2), M["roche"], biseau=0.06, segments=1,
                      rotation=(0, 0, -0.2))]
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=6, radius=0.14, location=(x, y, h + 0.08))
    boule = bpy.context.object
    boule.data.materials.append(M["or"])
    for p in boule.data.polygons:
        p.use_smooth = True
    pieces.append(boule)
    mat_obj = f.fusionner(pieces, f"Mat_{nom}")

    # drapeau : grille 16 × 8, UV de 0 à 1, sens +x depuis le mât
    largeur, hauteur = 2.6, 1.6
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=8, size=1, location=(0, 0, 0))
    d = bpy.context.object
    d.name = f"Drapeau_{nom}"
    d.scale = (largeur, hauteur, 1)
    d.rotation_euler = (math.pi / 2, 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    d.location = (x + 0.07 + largeur / 2, y, h - 0.15 - hauteur / 2)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    d.data.materials.append(mat_drapeau)
    for p in d.data.polygons:
        p.use_smooth = True
    # légère ondulation figée (le drapeau n'est jamais plat), plus forte loin du mât
    groupe = d.vertex_groups.new(name="flotte")
    for v in d.data.vertices:
        u = (v.co.x - x) / largeur
        v.co.y += 0.12 * u * math.sin(u * 5.0 + graine)
        groupe.add([v.index], min(1.0, u * 1.2), "REPLACE")
    onde = d.modifiers.new("Onde", "WAVE")
    onde.use_normal = True  # le drapeau est vertical : on pousse selon sa normale (axe y)
    onde.use_x = True
    onde.use_y = False
    onde.height = 0.18
    onde.width = 1.1
    onde.speed = 0.06
    onde.narrowness = 1.2
    onde.start_position_x = x
    onde.start_position_y = y
    onde.time_offset = -graine * 10
    onde.vertex_group = "flotte"
    sol = d.modifiers.new("Epaisseur", "SOLIDIFY")
    sol.thickness = 0.02
    return mat_obj, d


def etoile_de_mer(nom, p, rot):
    pieces = [f.boite("c", p, (0.16, 0.16, 0.05), M["etoile"], biseau=0.02, segments=1)]
    for k in range(5):
        a = rot + 2 * math.pi * k / 5
        b = f.boite("b", (p[0] + 0.14 * math.cos(a), p[1] + 0.14 * math.sin(a), p[2]), (0.24, 0.09, 0.045),
                    M["etoile"], biseau=0.02, segments=1, rotation=(0, 0, a))
        pieces.append(b)
    return f.fusionner(pieces, nom)


def seau(nom, p):
    o = f.revolution(nom, [(0.0, 0.0), (0.13, 0.0), (0.17, 0.26), (0.16, 0.26), (0.12, 0.02), (0.0, 0.02)],
                     M["seau"], cotes=14)
    o.location = p
    o.rotation_euler = (0.0, 1.35, 0.4)  # renversé sur le flanc
    return o


def repere(nom, p):
    e = bpy.data.objects.new(f"REP_{nom}", None)
    e.location = p
    sc.collection.objects.link(e)


for i, (nom, cx) in enumerate(ILES.items()):
    graine = 1.3 + 2.1 * i
    ile(f"Ile_{nom}", cx, graine)
    ecume(f"Ecume_{nom}", cx, graine)
    mat_et_drapeau(nom, cx, M["degrade_ig"] if nom == "instagram" else M["rouge_yt"], graine * 3)
    # rochers : sur le sable et dans l'eau, côtés et arrière (le centre et l'avant restent dégagés)
    rochers = []
    for a_deg, r, t in ((150, 8.2, 0.9), (162, 8.6, 0.55), (40, 9.4, 1.1), (55, 8.9, 0.5), (-120, 9.6, 0.7),
                        (-100, 9.1, 0.4), (95, 10.3, 0.8)):
        a = math.radians(a_deg + (25 if nom == "youtube" else 0))
        if nom == "youtube":
            a = math.pi - a  # symétrie miroir entre les deux îles
        z = -0.18 if r < 9 else NIVEAU_EAU
        rochers.append(rocher("ro", (cx + r * math.cos(a), r * math.sin(a), z + t * 0.3), (t, t * 0.85, t * 0.75),
                              "roche" if rng.random() < 0.6 else "roche_claire"))
    f.fusionner(rochers, f"Rochers_{nom}")
    # un palmier, côté extérieur arrière, penché vers le large (ne cache pas le centre)
    sens = -1 if nom == "instagram" else 1
    base = (cx + sens * 6.6, 3.6, -0.02)
    palmier(f"Palmier_{nom}", base, (sens * 0.55, 0.25), graine=11 + i)
    if nom == "instagram":
        etoile_de_mer("Etoile_de_mer", (cx + 5.0, -7.5, -0.16), 0.3)
    else:
        seau("Seau_oublie", (cx - 6.2, -6.2, -0.04))
    repere(f"ile_{nom}", (cx, 0, 1.0))
    repere(f"drapeau_{nom}", (cx + 1.3, 6.0, 5.0))
repere("centre", (0, 0, 1.0))
repere("bras_de_mer", (0, 0, NIVEAU_EAU))

# ----- tout dans la collection « Iles » --------------------------------------------------------------
col = bpy.data.collections.new("Iles")
sc.collection.children.link(col)
for o in list(sc.collection.objects):
    col.objects.link(o)
    sc.collection.objects.unlink(o)
DOSSIER.mkdir(parents=True, exist_ok=True)
sortie = DOSSIER / "iles_duel.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(sortie), compress=True)
dg = bpy.context.evaluated_depsgraph_get()
n_tri = 0
for o in col.all_objects:
    if o.type == "MESH":
        me = o.evaluated_get(dg).to_mesh()
        n_tri += sum(len(p.vertices) - 2 for p in me.polygons)
print(f"ILES_OK {sortie} : {len(col.all_objects)} objets, {n_tri} triangles")
