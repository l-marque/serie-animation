"""Stade en ruine, pelouse neuve (création du projet) : état `pelouse_neuve` de l'épisode jour-2.

Part du stade du jour 1 tel qu'il est sur le disque (engine/assets/modeles/terrain_boueux/stade_ruine.blend,
y compris les retouches faites à la main par Guillaume) et ne change QUE la pelouse :

- sol aplani à z = 0 (plus d'ornières ni de flaques en creux) et nouveau matériau « Pelouse_neuve » :
  herbe verte uniforme, bandes de tonte alternées (largeur 105 / 18 m), grain fin ;
- lignes neuves : les lignes complètes du terrain source (avant effacement), aplanies, blanc net ;
- retirés : les 350 mottes de boue, les pneus, plots et planches posés sur le terrain, et les touffes
  d'herbes folles situées à l'intérieur des barrières.

Tout le reste (cages rouillées sans filet, restes de filet, tribune effondrée, pylônes, tableau, abris,
barrières, gravats, ville, monde) est conservé tel quel, aux mêmes positions. Le fichier d'origine n'est
jamais réenregistré : la sortie est un nouveau .blend, même collection « Stade ».

    blender --background --factory-startup --python engine/outils/atelier/modeles/stade_ruine_pelouse.py

Si Guillaume retouche stade_ruine.blend, relancer ce script pour reporter ses retouches.
"""
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

SOURCE = f.MODELES / "terrain_boueux" / "stade_ruine.blend"
TERRAIN_SOURCE = f.MODELES / "terrain_boueux" / "terrain_boueux_source.blend"
SORTIE = f.MODELES / "stade_ruine_pelouse" / "stade_ruine_pelouse.blend"

BANDE = 105.0 / 18           # largeur d'une bande de tonte (m) : 18 bandes d'une ligne de but à l'autre
VERT_CLAIR = (0.05, 0.215, 0.016)
VERT_FONCE = (0.026, 0.125, 0.009)
BLANC_LIGNE = (0.86, 0.86, 0.83)
BARRIERES = (56.7, 38.2)     # demi-dimensions du rectangle des barrières

bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
stade = bpy.data.collections["Stade"]
retires = {}


def retirer(o, motif):
    retires[motif] = retires.get(motif, 0) + 1
    bpy.data.objects.remove(o, do_unlink=True)


# ----- 1. tout ce qui salit le terrain --------------------------------------------------------------
for o in list(bpy.data.objects):
    base = o.name.split(".")[0]
    if base == "Motte":
        retirer(o, "mottes de boue")
    elif base.startswith(("pneu_", "plot_", "planche_")):
        retirer(o, "débris sur le terrain")
    elif base.startswith("herbes_"):
        coins = [o.matrix_world @ Vector(c) for c in o.bound_box]
        c = sum(coins, Vector()) / 8
        if abs(c.x) < BARRIERES[0] and abs(c.y) < BARRIERES[1]:
            retirer(o, "herbes folles dans l'enceinte")

# ----- 2. sol aplani + pelouse neuve -------------------------------------------------------------------
sol = bpy.data.objects["Sol"]
for v in sol.data.vertices:
    v.co.z = 0.0
sol.data.update()


def pelouse_neuve():
    m = bpy.data.materials.new("Pelouse_neuve")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    N, L = nt.nodes.new, nt.links.new
    sortie = N("ShaderNodeOutputMaterial")
    bsdf = N("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.82
    L(bsdf.outputs["BSDF"], sortie.inputs["Surface"])
    geo = N("ShaderNodeNewGeometry")
    sep = N("ShaderNodeSeparateXYZ")
    L(geo.outputs["Position"], sep.inputs["Vector"])

    # Bandes de tonte : floor((x + 52,5) / BANDE) modulo 2, bord très légèrement adouci par un bruit.
    decale = N("ShaderNodeMath"); decale.operation = "ADD"; decale.inputs[1].default_value = 52.5
    L(sep.outputs["X"], decale.inputs[0])
    div = N("ShaderNodeMath"); div.operation = "DIVIDE"; div.inputs[1].default_value = BANDE
    L(decale.outputs[0], div.inputs[0])
    bruit_bord = N("ShaderNodeTexNoise"); bruit_bord.inputs["Scale"].default_value = 3.0
    L(geo.outputs["Position"], bruit_bord.inputs["Vector"])
    bord = N("ShaderNodeMapRange")
    bord.inputs["To Min"].default_value, bord.inputs["To Max"].default_value = 0.0, 0.0   # bords droits (tonte)
    L(bruit_bord.outputs["Fac"], bord.inputs["Value"])
    plus = N("ShaderNodeMath"); plus.operation = "ADD"
    L(div.outputs[0], plus.inputs[0]); L(bord.outputs[0], plus.inputs[1])
    sol_ = N("ShaderNodeMath"); sol_.operation = "FLOOR"
    L(plus.outputs[0], sol_.inputs[0])
    mod = N("ShaderNodeMath"); mod.operation = "FLOORED_MODULO"; mod.inputs[1].default_value = 2.0
    L(sol_.outputs[0], mod.inputs[0])
    bandes = N("ShaderNodeMix"); bandes.data_type = "RGBA"
    bandes.inputs["A"].default_value = (*VERT_FONCE, 1)
    bandes.inputs["B"].default_value = (*VERT_CLAIR, 1)
    L(mod.outputs[0], bandes.inputs["Factor"])

    # Légère variation de teinte (grandes taches à peine visibles) + grain fin de l'herbe.
    bruit_large = N("ShaderNodeTexNoise"); bruit_large.inputs["Scale"].default_value = 0.35
    bruit_large.inputs["Detail"].default_value = 3.0
    L(geo.outputs["Position"], bruit_large.inputs["Vector"])
    teinte = N("ShaderNodeMix"); teinte.data_type = "RGBA"; teinte.blend_type = "MULTIPLY"
    teinte.inputs["Factor"].default_value = 1.0
    plage = N("ShaderNodeMapRange")
    plage.inputs["From Min"].default_value, plage.inputs["From Max"].default_value = 0.3, 0.7
    plage.inputs["To Min"].default_value, plage.inputs["To Max"].default_value = 0.93, 1.06
    L(bruit_large.outputs["Fac"], plage.inputs["Value"])
    L(bandes.outputs["Result"], teinte.inputs["A"])
    gris = N("ShaderNodeCombineXYZ")
    for k in ("X", "Y", "Z"):
        L(plage.outputs[0], gris.inputs[k])
    L(gris.outputs[0], teinte.inputs["B"])
    bruit_fin = N("ShaderNodeTexNoise"); bruit_fin.inputs["Scale"].default_value = 70.0
    bruit_fin.inputs["Detail"].default_value = 4.0
    L(geo.outputs["Position"], bruit_fin.inputs["Vector"])
    grain = N("ShaderNodeMix"); grain.data_type = "RGBA"; grain.blend_type = "MULTIPLY"
    plage2 = N("ShaderNodeMapRange")
    plage2.inputs["From Min"].default_value, plage2.inputs["From Max"].default_value = 0.35, 0.65
    plage2.inputs["To Min"].default_value, plage2.inputs["To Max"].default_value = 0.78, 1.18
    L(bruit_fin.outputs["Fac"], plage2.inputs["Value"])
    gris2 = N("ShaderNodeCombineXYZ")
    for k in ("X", "Y", "Z"):
        L(plage2.outputs[0], gris2.inputs[k])
    grain.inputs["Factor"].default_value = 1.0
    L(teinte.outputs["Result"], grain.inputs["A"]); L(gris2.outputs[0], grain.inputs["B"])
    L(grain.outputs["Result"], bsdf.inputs["Base Color"])

    # Relief : brins très fins (bump discret), pas de creux.
    bruit_brins = N("ShaderNodeTexNoise"); bruit_brins.inputs["Scale"].default_value = 420.0
    L(geo.outputs["Position"], bruit_brins.inputs["Vector"])
    relief = N("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.45
    relief.inputs["Distance"].default_value = 0.01
    L(bruit_brins.outputs["Fac"], relief.inputs["Height"])
    L(relief.outputs["Normal"], bsdf.inputs["Normal"])
    return m


sol.data.materials.clear()
sol.data.materials.append(pelouse_neuve())

# ----- 3. lignes neuves et complètes ------------------------------------------------------------------
ancienne = bpy.data.objects.get("Lignes")
if ancienne:
    bpy.data.objects.remove(ancienne, do_unlink=True)
with bpy.data.libraries.load(str(TERRAIN_SOURCE), link=False) as (src, dst):
    dst.objects = ["Lignes"]
lignes = dst.objects[0]
lignes.name = "Lignes"
stade.objects.link(lignes)
for v in lignes.data.vertices:
    v.co.z = 0.008
lignes.data.update()
lignes.data.materials.clear()
lignes.data.materials.append(f.materiau("Lignes_neuves", BLANC_LIGNE, 0.55))

# ----- 4. nettoyage des données orphelines et enregistrement d'une COPIE -------------------------------
for _ in range(3):
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
SORTIE.parent.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(SORTIE), compress=True, copy=True)
n_tri = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in stade.all_objects if o.type == "MESH")
print(f"STADE_PELOUSE_OK {SORTIE} : {len(stade.all_objects)} objets, {n_tri} triangles, retirés : {retires}")
