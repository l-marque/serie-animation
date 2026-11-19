"""Supporters en blocs (création du projet) : la foule de la tribune réparée (jour-3, plans b10-b11 et suivants).

Volontairement PLUS SIMPLES que les joueurs (perso_bloc.py) pour qu'on ne les confonde jamais avec l'équipe :
10 blocs, pas de visage, gros volumes lisibles de loin. Debout, les deux bras levés en V, l'écharpe rayée tendue
au-dessus de la tête, bonnet à pompon aux couleurs. Hauteur hors tout 1,86 m (tête à 1,52 m : plus petits que
les joueurs, l'écharpe dépasse).

    blender --background --factory-startup --python engine/outils/atelier/modeles/supporter_bloc.py [-- supporter_bloc_rouge ...]

Convention : regarde vers -y (le terrain et les caméras), base à z = 0. Pour le poser dans la tribune de
`stade_repare` : debout sur la marche du rang k, devant son siège : position (x ; 41,28 + 1,4 k ; 0,55 (k + 1)),
rotation_z 0, où x = -29,5 + 0,62 i (i = n° du siège). Étiquette « @pseudo » au-dessus : z + 2,0 m.
Squelette : Root (pieds) et Haut (bassin -> tête, porte bras et écharpe). Animations (24 i/s) :
Idle = balancement gauche-droite de chant de supporter (48 images, en boucle) ;
Jump = sauts de joie, deux sauts de 0,3 m (24 images, en boucle).
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

BAS = (0.04, 0.08, 0.2)                                   # jean
SUPPORTERS = {
    # couleur du club, couleur des rayures, peau (variété de carnations)
    "supporter_bloc_rouge": ((0.7, 0.03, 0.02), (0.82, 0.82, 0.8), (0.78, 0.46, 0.3)),
    "supporter_bloc_bleu": ((0.02, 0.15, 0.7), (0.82, 0.82, 0.8), (0.33, 0.17, 0.09)),
    "supporter_bloc_jaune": ((0.9, 0.55, 0.01), (0.03, 0.04, 0.12), (0.86, 0.56, 0.4)),
    "supporter_bloc_noir": ((0.015, 0.015, 0.02), (0.85, 0.42, 0.0), (0.55, 0.3, 0.17)),   # aux couleurs du FC Élite
}


def construire(asset_id, couleur, rayure, peau):
    f.vider()
    m = {k: f.materiau(k, c, 0.45) for k, c in {"Club": couleur, "Rayure": rayure, "Peau": peau, "Bas": BAS,
                                                  "Semelle": (0.75, 0.75, 0.72)}.items()}
    parties = []

    def bloc(nom, os_, centre, taille, mat, biseau=0.03, rot=(0, 0, 0)):
        o = f.boite(nom, centre, taille, m[mat], biseau=biseau, segments=2, rotation=rot)
        parties.append((o, os_))
        return o

    # Bas du corps (os Root) : jambes d'un seul bloc fendu par deux blocs, semelles claires.
    for s in (-1, 1):
        bloc(f"jambe_{s}", "Root", (s * 0.1, 0, 0.42), (0.19, 0.24, 0.76), "Bas")
        bloc(f"pied_{s}", "Root", (s * 0.1, -0.03, 0.04), (0.2, 0.3, 0.08), "Semelle", biseau=0.02)
    # Haut du corps (os Haut) : maillot, tête sans visage, bonnet à pompon, bras en V, écharpe tendue.
    bloc("maillot", "Haut", (0, 0, 1.05), (0.5, 0.28, 0.56), "Club", biseau=0.05)
    bloc("tete", "Haut", (0, 0, 1.47 - 0.17), (0.32, 0.3, 0.32), "Peau", biseau=0.07)
    bloc("bonnet", "Haut", (0, 0.01, 1.47), (0.34, 0.32, 0.12), "Club", biseau=0.04)
    bloc("bonnet_bord", "Haut", (0, 0.01, 1.42), (0.35, 0.33, 0.05), "Rayure", biseau=0.015)
    bloc("pompon", "Haut", (0, 0.01, 1.57), (0.11, 0.11, 0.1), "Rayure", biseau=0.04)
    for s in (-1, 1):
        angle = math.radians(28 * s)                            # bras levés en V
        epaule = Vector((s * 0.21, 0, 1.25))
        d = Vector((math.sin(angle), 0, math.cos(angle)))
        bloc(f"bras_{s}", "Haut", epaule + d * 0.26, (0.13, 0.13, 0.48), "Club", biseau=0.03, rot=(0, angle, 0))
        bloc(f"main_{s}", "Haut", epaule + d * 0.54, (0.13, 0.13, 0.12), "Peau", biseau=0.04, rot=(0, angle, 0))
    # écharpe tendue entre les mains, au-dessus de la tête : 7 bandes alternées + franges qui pendent
    zm, xm = 1.25 + 0.54 * math.cos(math.radians(28)), 0.21 + 0.54 * math.sin(math.radians(28))
    n = 7
    for i in range(n):
        x = -xm + (i + 0.5) * 2 * xm / n
        bloc(f"echarpe_{i}", "Haut", (x, -0.07, zm + 0.04), (2 * xm / n + 0.002, 0.03, 0.17),
             "Club" if i % 2 == 0 else "Rayure", biseau=0.0)
    for s in (-1, 1):                                           # bouts qui pendent sous les poings
        bloc(f"echarpe_bout_{s}", "Haut", (s * (xm + 0.02), -0.07, zm - 0.14), (0.12, 0.03, 0.28), "Club", biseau=0.0)
        bloc(f"frange_{s}", "Haut", (s * (xm + 0.02), -0.07, zm - 0.31), (0.12, 0.025, 0.06), "Rayure", biseau=0.0)

    arm_d = bpy.data.armatures.new("Squelette")
    arm = bpy.data.objects.new("Armature", arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    r = arm_d.edit_bones.new("Root")
    r.head, r.tail = (0, 0, 0), (0, 0, 0.4)
    h = arm_d.edit_bones.new("Haut")
    h.head, h.tail, h.parent = (0, 0, 0.8), (0, 0, 1.5), r
    bpy.ops.object.mode_set(mode="OBJECT")
    for o, os_ in parties:
        g = o.vertex_groups.new(name=os_)
        g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    corps = f.fusionner([o for o, _ in parties], asset_id)
    corps.parent = arm
    corps.modifiers.new("Squelette", "ARMATURE").object = arm

    pb = arm.pose.bones
    for b in pb:
        b.rotation_mode = "XYZ"
    arm.animation_data_create()

    def action(nom, cles, longueur):
        """cles : {image: {"Root": (z, roulis_deg), "Haut": (roulis_deg, rx_deg)}} ; os vers le haut : y local = z monde."""
        act = bpy.data.actions.new(nom)
        act.use_fake_user = True
        arm.animation_data.action = act
        for img in sorted(cles):
            z, roulis = cles[img].get("Root", (0, 0))
            pb["Root"].location = (0, z, 0)
            pb["Root"].rotation_euler = (0, 0, math.radians(roulis))   # z local = -y monde : roulis latéral
            ry, rx = cles[img].get("Haut", (0, 0))
            pb["Haut"].rotation_euler = (math.radians(rx), 0, math.radians(ry))   # rx > 0 : penché en avant
            for b in pb:
                b.keyframe_insert("location", frame=img)
                b.keyframe_insert("rotation_euler", frame=img)
        act.frame_range = (0, longueur)

    # Idle : chant de tribune, tout le corps se balance de gauche à droite (pivot aux pieds), petit rebond.
    action("Idle", {0: {"Haut": (0, 0)}, 12: {"Haut": (0, 0), "Root": (0.03, 6)}, 24: {"Haut": (0, 0)},
                    36: {"Haut": (0, 0), "Root": (0.03, -6)}, 48: {"Haut": (0, 0)}}, 48)
    # Jump : accroupi (image 0), en l'air (5), réception (10), accroupi (12), en l'air (17), réception (22).
    action("Jump", {0: {"Root": (-0.06, 0), "Haut": (0, 8)}, 5: {"Root": (0.3, 4), "Haut": (0, -6)},
                    10: {"Root": (0, 0), "Haut": (0, 4)}, 12: {"Root": (-0.06, 0), "Haut": (0, 8)},
                    17: {"Root": (0.3, -4), "Haut": (0, -6)}, 22: {"Root": (0, 0), "Haut": (0, 4)},
                    24: {"Root": (-0.06, 0), "Haut": (0, 8)}}, 24)
    arm.animation_data.action = bpy.data.actions["Idle"]
    return corps


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(SUPPORTERS)
    for asset_id in args:
        corps = construire(asset_id, *SUPPORTERS[asset_id])
        chemin = f.MODELES / "supporters_bloc" / f"{asset_id}.glb"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", export_animation_mode="ACTIONS",
                                  export_force_sampling=True)
        n_tri = sum(len(p.vertices) - 2 for p in corps.data.polygons)
        print(f"MODELE_EXPORTE {asset_id} : {chemin} ({n_tri} triangles)")


main()
