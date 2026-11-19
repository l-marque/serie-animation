"""Hamsters en blocs et cochon d'Inde géant (série « 10 000 serpents contre 1 hamster », création du projet).

    blender --background --factory-startup -noaudio --python engine/outils/atelier/modeles/hamster_bloc.py [-- hamster_bloc ...]

Même style que perso_bloc.py (forme « rond » : gros biseaux, plastique lisse, couleurs franches, visage en
petits blocs) ; chaque modèle est un maillage unique à membres rigides sur un squelette maison.

- `hamster_bloc` (1,0 m aux oreilles) : le héros. Boule dorée au ventre et aux joues crème, grands yeux noirs
  à deux reflets, petites dents, joues roses, pattes roses serrées contre la poitrine, épi de poils sur le
  crâne, sourcils relevés au centre (air inquiet et attachant). Animations : Idle (respire, penche la tête,
  cligne des yeux à l'image 30), Tremble (b02 : accroupi, pattes devant la bouche, tremblement rapide),
  Run, Jump, Wave.
- `hamster_soldat_bloc` : le soldat (commentaire sans tag). Dé à coudre en guise de casque (avec un plumet
  rouge), épée cure-dent dans la patte droite, capsule de bouteille comme bouclier, air décidé. En plus :
  Attack (coup d'épée, touche à l'image 8) et Cheer (épée levée, en boucle).
- `hamster_archer_bloc` : l'archer (1 ami tagué). Bandeau feuille, arc en brindille, carquois d'allumettes,
  un œil plissé pour viser. En plus : Shoot (bande l'arc, flèche lâchée à l'image 14, elle réapparaît à 32).
- `hamster_boule_bloc` (1,75 m) : le hamster pilote (lunettes d'aviateur) dans sa boule d'exercice
  transparente blindée : bandes de chenille rivetées, moyeux, arceau fixe avec tourelle et canon (paille),
  fanion. Roll : la boule fait un tour en 48 images pendant que le hamster court dedans ; avancer de 4,52 m
  par cycle (2,83 m/s à 30 i/s) pour qu'elle roule sans glisser. Idle : boule immobile.
- `cochon_inde_bloc` (3,0 m, trois fois le hamster) : cochon d'Inde géant tricolore (crème, roux, brun)
  asymétrique, rosette de poils en bataille (comme les cochons d'Inde abyssins), harnais de cuir avec un
  écusson. Animations : Idle, Walk, Run, Popcorn (le saut de joie des cochons d'Inde, sommet à l'image 10).

Convention : regard vers -y, base à z = 0, droite du personnage du côté -x. Animations à 24 i/s, lues image
pour image par le moteur.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Quaternion, Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

COULEURS = {
    "Dore": (0.5, 0.32, 0.12),         # pelage beige doré chaud (AgX : plus sombre et saturé que l'intuition)
    "Creme": (0.85, 0.8, 0.7),
    "Rose": (0.78, 0.26, 0.3),
    "Joue": (0.85, 0.2, 0.22),
    "Yeux": (0.015, 0.012, 0.015),
    "Reflet": (0.97, 0.97, 0.97),
    "Nez": (0.6, 0.12, 0.18),
    "Dents": (0.95, 0.93, 0.86),
    "Bouche": (0.2, 0.05, 0.05),
    "Brun": (0.16, 0.07, 0.025),       # sourcils, épi
}
X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
# Révision « désert » (2026-11-19) : sous le ciel rouge-magenta du pack desert_hamster, un pelage seulement éclairé
# vire au rose saumon. Il brille donc un peu dans une couleur dorée à lui (nom : (couleur, force)) : les héros
# restent dorés et l'élément le plus lisible de l'image. Yeux, bouche, sourcils, transparents : non.
LUEUR = {"Dore": ((0.8, 0.5, 0.14), 0.45), "Creme": ((0.9, 0.78, 0.5), 0.35), "Rose": ((0.85, 0.35, 0.3), 0.25),
         "Joue": ((0.9, 0.3, 0.25), 0.25), "Nez": ((0.7, 0.2, 0.2), 0.2)}


class Modele:
    """Pièces (objet, os) + squelette + actions. Rotations des clés : autour d'axes du MONDE au repos."""

    def __init__(self, asset_id):
        f.vider()
        self.id = asset_id
        self.parties = []
        self.mats = {}
        self.os = {}             # nom -> (tete, queue, parent)
        # Préfixe des actions : le moteur (bibliotheque._jouer_animation) prend la PREMIÈRE action du fichier .blend
        # en cours qui porte le nom demandé, quel que soit l'asset : deux rigs différents ne doivent jamais partager un
        # nom d'action (sinon le cochon d'Inde jouerait l'« Idle » du hamster).
        self.prefixe = {"hamster_boule_bloc": "Boule_", "cochon_inde_bloc": "Cochon_"}.get(asset_id, "Hamster_")

    def m(self, nom, couleur=None, rugosite=0.32, metal=0.0, alpha=1.0):
        if nom not in self.mats:
            if nom == "Yeux":
                rugosite = 0.75           # yeux mats : le ciel orangé ne s'y reflète pas (ils restaient bruns)
            mat = f.materiau(nom, couleur or COULEURS[nom], rugosite=rugosite, metal=metal)
            if nom in LUEUR and alpha >= 1.0:
                lc, lf = LUEUR[nom]
                b_ = mat.node_tree.nodes["Principled BSDF"]
                b_.inputs["Emission Color"].default_value = (*lc, 1.0)
                b_.inputs["Emission Strength"].default_value = lf
            if alpha < 1.0:
                bsdf = mat.node_tree.nodes["Principled BSDF"]
                bsdf.inputs["Alpha"].default_value = alpha
                mat.surface_render_method = "BLENDED"
                mat.use_backface_culling = False
            self.mats[nom] = mat
        return self.mats[nom]

    def bloc(self, nom, os_, c, t, mat, b=0.0, seg=3, rot=(0, 0, 0)):
        o = f.boite(nom, c, t, self.m(mat) if isinstance(mat, str) else mat, biseau=b, segments=seg, rotation=rot)
        self.parties.append((o, os_))
        return o

    def piece(self, o, os_):
        self.parties.append((o, os_))
        return o

    def os_(self, nom, tete, queue, parent=None):
        self.os[nom] = (tete, queue, parent)

    def finir(self):
        arm_d = bpy.data.armatures.new("Squelette")
        arm = bpy.data.objects.new("Armature", arm_d)
        bpy.context.scene.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        for nom, (t, q, _) in self.os.items():
            e = arm_d.edit_bones.new(nom)
            e.head, e.tail, e.roll = Vector(t), Vector(q), 0.0
        for nom, (_, _, p) in self.os.items():
            if p:
                arm_d.edit_bones[nom].parent = arm_d.edit_bones[p]
        bpy.ops.object.mode_set(mode="OBJECT")
        for o, os_ in self.parties:
            if o.type != "MESH":
                o = f.convertir_en_maillage(o)
            g = o.vertex_groups.new(name=os_)
            g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
        corps = f.fusionner([o for o, _ in self.parties], self.id)
        corps.parent = arm
        corps.modifiers.new("Squelette", "ARMATURE").object = arm
        self.arm, self.corps = arm, corps
        pb = arm.pose.bones
        for b in pb:
            b.rotation_mode = "QUATERNION"
        arm.animation_data_create()
        self.repos = {b.name: arm.data.bones[b.name].matrix_local.to_quaternion() for b in pb}
        return arm

    def action(self, nom, cles, longueur):
        """cles : {image: {os: [(axe_monde, degrés), ...] | os:loc: (x, y, z) monde | os:scale: (sx, sy, sz) local}}."""
        pb = self.arm.pose.bones
        act = bpy.data.actions.new(self.prefixe + nom)
        act.use_fake_user = True
        self.arm.animation_data.action = act
        for img in sorted(cles):
            for b in pb:
                b.rotation_quaternion = (1, 0, 0, 0)
                b.location = (0, 0, 0)
                b.scale = (1, 1, 1)
            for cle, val in cles[img].items():
                if cle.endswith(":loc"):
                    nom_os = cle[:-4]
                    pb[nom_os].location = self.repos[nom_os].inverted() @ Vector(val)
                elif cle.endswith(":scale"):
                    pb[cle[:-6]].scale = val
                else:
                    q0 = self.repos[cle]
                    q = Quaternion((1, 0, 0, 0))
                    for axe, ang in val:
                        q = (q0.inverted() @ Quaternion(Vector(axe), math.radians(ang)) @ q0) @ q
                    pb[cle].rotation_quaternion = q
            for b in pb:
                b.keyframe_insert("rotation_quaternion", frame=img)
                b.keyframe_insert("location", frame=img)
                b.keyframe_insert("scale", frame=img)
        act.frame_range = (0, longueur)
        return act

    def exporter(self, defaut="Idle", hauteur=None):
        """hauteur : mise à l'échelle exacte du modèle (hauteur hors tout au repos, en mètres)."""
        self.arm.animation_data.action = bpy.data.actions[self.prefixe + defaut]
        if hauteur:
            zmax = max((self.corps.matrix_world @ v.co).z for v in self.corps.data.vertices)
            k = hauteur / zmax
            self.arm.scale = (k, k, k)
            print(f"ECHELLE {self.id} : {k:.4f} (hauteur {hauteur} m)")
        chemin = f.MODELES / "hamsters_bloc" / f"{self.id}.glb"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", export_animation_mode="ACTIONS",
                                  export_force_sampling=True)
        n_tri = sum(len(p.vertices) - 2 for p in self.corps.data.polygons)
        print(f"MODELE_EXPORTE {self.id} : {chemin} ({n_tri} triangles)")


# ----- hamster ------------------------------------------------------------------------------------
def hamster(M: Modele, k=1.0, o=(0.0, 0.0, 0.0), humeur="inquiet", bras="poitrine", prefixe=""):
    """Construit un hamster (hauteur 1,0 m × k aux oreilles), pieds à o. Renvoie la fonction P de position."""
    ox, oy, oz = o

    def P(x, y, z):
        return (ox + k * x, oy + k * y, oz + k * z)

    def T(*t):
        return tuple(k * v for v in t)

    def b(nom, os_, c, t, mat, bis=0.0, seg=3, rot=(0, 0, 0)):
        return M.bloc(prefixe + nom, os_, P(*c), T(*t), mat, k * bis, seg, rot)

    # Corps : une boule dorée, ventre crème qui dépasse devant, petite queue.
    b("corps", "Body", (0, 0.04, 0.33), (0.86, 0.8, 0.58), "Dore", 0.22, 4)
    b("ventre", "Body", (0, -0.31, 0.29), (0.58, 0.16, 0.42), "Creme", 0.12, 3)
    b("queue", "Body", (0, 0.45, 0.2), (0.1, 0.08, 0.08), "Rose", 0.035, 2)
    # Tête : large, un peu en avant ; joues gonflées crème (abajoues), museau, nez, dents.
    b("tete", "Head", (0, -0.07, 0.69), (0.82, 0.66, 0.46), "Dore", 0.2, 4)
    for s in (-1, 1):
        b(f"joue_{s}", "Head", (s * 0.235, -0.33, 0.6), (0.32, 0.2, 0.25), "Creme", 0.1, 3)
        b(f"rose_{s}", "Head", (s * 0.3, -0.435, 0.64), (0.11, 0.02, 0.055), "Joue", 0.02, 2)
    b("museau", "Head", (0, -0.42, 0.615), (0.22, 0.14, 0.15), "Creme", 0.06, 3)
    b("nez", "Head", (0, -0.495, 0.675), (0.085, 0.04, 0.055), "Nez", 0.02, 2)
    for s in (-1, 1):
        b(f"dent_{s}", "Head", (s * 0.023, -0.475, 0.525), (0.04, 0.025, 0.065), "Dents", 0.008, 1)
        b(f"moustache_{s}", "Head", (s * 0.2, -0.49, 0.64), (0.16, 0.006, 0.006), "Brun", 0.0, 1,
          rot=(0, s * 0.12, 0))
    b("bouche_g", "Head", (-0.03, -0.493, 0.57), (0.05, 0.012, 0.014), "Bouche", 0.0, 1, rot=(0, 0.5, 0))
    b("bouche_d", "Head", (0.03, -0.493, 0.57), (0.05, 0.012, 0.014), "Bouche", 0.0, 1, rot=(0, -0.5, 0))
    # Grands yeux noirs (os Yeux : clignement) avec deux reflets ; sourcils.
    for s in (-1, 1):
        b(f"oeil_{s}", "Yeux", (s * 0.19, -0.4, 0.77), (0.15, 0.04, 0.19), "Yeux", 0.05, 3)
        b(f"reflet_{s}", "Yeux", (s * 0.19 + 0.035, -0.423, 0.815), (0.055, 0.012, 0.055), "Reflet", 0.012, 1)
        b(f"reflet2_{s}", "Yeux", (s * 0.19 - 0.035, -0.423, 0.725), (0.026, 0.012, 0.026), "Reflet", 0.0, 1)
        if humeur == "inquiet":        # coins intérieurs relevés : inquiet, pas fâché
            ang = s * 0.32
            zc = 0.9
        elif humeur == "decide":       # légèrement vers le centre : concentré, décidé (soldats)
            ang = s * -0.22
            zc = 0.895
        else:
            ang, zc = 0.0, 0.9
        b(f"sourcil_{s}", "Head", (s * 0.19, -0.405, zc), (0.13, 0.025, 0.035), "Brun", 0.01, 1, rot=(0, ang, 0))
    # Oreilles rondes, intérieur rose, un peu écartées.
    for s in (-1, 1):
        b(f"oreille_{s}", "Head", (s * 0.28, -0.02, 0.93), (0.17, 0.07, 0.15), "Dore", 0.06, 3, rot=(0, s * 0.35, 0))
        b(f"oreille_in_{s}", "Head", (s * 0.28 + s * 0.005, -0.058, 0.925), (0.1, 0.012, 0.09), "Rose", 0.03, 2,
          rot=(0, s * 0.35, 0))
    # Épi de poils sur le crâne (trois mèches de travers).
    for i, (x, h, r) in enumerate(((-0.04, 0.09, -0.4), (0.03, 0.12, 0.1), (0.09, 0.07, 0.6))):
        b(f"epi_{i}", "Head", (x, -0.05, 0.92 + h / 2 - 0.02), (0.06, 0.06, h), "Dore", 0.02, 2, rot=(0.15, r, 0))
    # Bras (os Arm) : petites pattes roses serrées contre la poitrine.
    if bras == "poitrine":
        for s, cote in ((-1, "R"), (1, "L")):
            b(f"bras_{cote}", f"Arm.{cote}", (s * 0.2, -0.37, 0.43), (0.14, 0.13, 0.17), "Dore", 0.06, 3)
            b(f"patte_{cote}", f"Arm.{cote}", (s * 0.17, -0.42, 0.355), (0.12, 0.1, 0.07), "Rose", 0.03, 2)
    # Pieds roses (os Leg) qui dépassent sous le ventre.
    for s, cote in ((-1, "R"), (1, "L")):
        b(f"pied_{cote}", f"Leg.{cote}", (s * 0.21, -0.22, 0.035), (0.17, 0.22, 0.07), "Rose", 0.03, 2)
        b(f"jambe_{cote}", f"Leg.{cote}", (s * 0.21, -0.12, 0.12), (0.18, 0.18, 0.14), "Dore", 0.06, 3)
    # Squelette.
    M.os_("Root", P(0, 0, 0), P(0, 0, 0.2))
    M.os_("Body", P(0, 0, 0.12), P(0, 0, 0.52), "Root")
    M.os_("Head", P(0, -0.05, 0.5), P(0, -0.05, 0.95), "Body")
    M.os_("Yeux", P(0, -0.4, 0.77), P(0, -0.5, 0.77), "Head")
    for s, cote in ((-1, "R"), (1, "L")):
        M.os_(f"Arm.{cote}", P(s * 0.22, -0.33, 0.5), P(s * 0.22, -0.33, 0.33), "Body")
        M.os_(f"Leg.{cote}", P(s * 0.2, -0.12, 0.2), P(s * 0.2, -0.12, 0.0), "Root")
    return P, T


def avant(a):
    """Membre pendant (os vers le bas) : a > 0 l'envoie vers l'avant (-y)."""
    return (X, -a)


def anims_hamster(M: Modele, k=1.0, extra=()):
    def respire(i, n=48):
        ph = 2 * math.pi * i / n
        return {"Body": [(X, 1.5 * math.sin(ph))], "Head": [(Y, 5 * math.sin(ph)), (X, -1.5 * math.sin(ph))],
                "Arm.R": [avant(4 * math.sin(ph))], "Arm.L": [avant(4 * math.sin(ph + 0.5))]}

    def cligne(i, debut=30):
        return {"Yeux:scale": (1, 1, 0.12)} if debut <= i <= debut + 3 else {}

    M.action("Idle", {i: {**respire(i), **cligne(i)} for i in range(0, 49, 1)}, 48)
    # Tremble (b02) : accroupi, tête rentrée, pattes devant la bouche, tremblement rapide (2 images).
    def tremble(i):
        s = 1 if i % 2 == 0 else -1
        r = (1 if i % 4 < 2 else -1)
        return {"Root:loc": (0, 0, -0.03 * k), "Body": [(Y, 2.2 * s), (X, 3 + 0.8 * r)],
                "Head": [(Y, -1.8 * s), (X, 9), (Z, 1.5 * r)],
                "Arm.R": [avant(55 + 4 * s), (Y, 8)], "Arm.L": [avant(55 - 4 * s), (Y, -8)],
                "Leg.R": [avant(-4)], "Leg.L": [avant(-4)]}
    M.action("Tremble", {i: tremble(i) for i in range(0, 25)}, 24)

    def course(i):
        s = math.sin(2 * math.pi * i / 16)
        return {"Leg.R": [avant(38 * s)], "Leg.L": [avant(-38 * s)], "Arm.R": [avant(-30 * s)],
                "Arm.L": [avant(30 * s)], "Body": [(X, 10)], "Head": [(X, -6)],
                "Root:loc": (0, 0, 0.07 * k * abs(math.cos(2 * math.pi * i / 16)))}
    M.action("Run", {i: course(i) for i in range(0, 17)}, 16)
    M.action("Jump", {0: {}, 5: {"Root:loc": (0, 0, -0.05 * k), "Body": [(X, 8)], "Arm.R": [avant(-20)],
                                 "Arm.L": [avant(-20)]},
                      11: {"Root:loc": (0, 0, 0.45 * k), "Arm.R": [(Y, 150)], "Arm.L": [(Y, -150)],
                           "Arm.R:loc": (-0.17 * k, -0.05 * k, 0.1 * k), "Arm.L:loc": (0.17 * k, -0.05 * k, 0.1 * k),
                           "Leg.R": [avant(20)], "Leg.L": [avant(-15)], "Head": [(X, -10)]},
                      18: {"Root:loc": (0, 0, -0.04 * k), "Body": [(X, 6)]}, 24: {}}, 24)

    # Bras très courts : pour un grand geste, l'os se décale aussi (sinon la patte reste cachée dans la joue).
    def salut(a):
        return {"Arm.R": [(Y, 140 + a)], "Arm.R:loc": (-0.24 * k, -0.06 * k, 0.2 * k), "Head": [(Y, -8)],
                "Body": [(Y, 3)]}
    M.action("Wave", {0: salut(0), 7: salut(35), 15: salut(0), 22: salut(35), 30: salut(0)}, 30)
    if "attack" in extra:
        # Attack : coup d'estoc au cure-dent. Bras ramené en arrière (image 4), détente : épée à l'horizontale,
        # pointe vers l'avant (image 8 = touche), retour (20). L'os Epee (poignet) tourne en plus du bras.
        M.action("Attack", {0: {}, 4: {"Arm.R": [avant(-10)], "Arm.R:loc": (0, 0.06 * k, 0.04 * k), "Epee": [(X, 40)],
                                       "Body": [(Z, -12)], "Head": [(X, -4)]},
                            8: {"Arm.R": [avant(60)], "Arm.R:loc": (0, -0.12 * k, 0.02 * k), "Epee": [(X, 112)],
                                "Body": [(X, 10), (Z, 10)], "Root:loc": (0, -0.1 * k, 0)},
                            12: {"Arm.R": [avant(55)], "Arm.R:loc": (0, -0.1 * k, 0.02 * k), "Epee": [(X, 106)],
                                 "Body": [(X, 8), (Z, 6)], "Root:loc": (0, -0.1 * k, 0)},
                            20: {}}, 20)
        # Cheer : épée levée bien droite au-dessus de la tête, qui pompe ; petits sauts ; en boucle (24 images).
        def cheer(i):
            s = math.sin(2 * math.pi * i / 12)
            return {"Arm.R": [avant(40 + 8 * s)], "Arm.R:loc": (-0.04 * k, -0.04 * k, (0.16 + 0.04 * s) * k),
                    "Arm.L": [avant(30)], "Root:loc": (0, 0, 0.08 * k * max(0, s)), "Head": [(X, -8)]}
        M.action("Cheer", {i: cheer(i) for i in range(0, 25, 2)}, 24)
    if "shoot" in extra:
        # Shoot : bande l'arc (0-12), tient (12-14), lâche à 14 (flèche partie), recharge (32-36).
        def shoot(i):
            if i <= 12:
                a = i / 12
            elif i <= 14:
                a = 1.0
            else:
                a = max(0.0, 1 - (i - 14) / 6)
            c = {"Arm.R:loc": (-0.02 * a * k, 0.16 * a * k, 0.0), "Body": [(Z, 6 * a)],
                 "Head": [(Z, -4 * a), (Y, 4 * a)]}
            if 14 < i < 32:
                c["Fleche:scale"] = (0.001, 0.001, 0.001)
                c["Arm.R:loc"] = (-0.04 * k, 0.2 * max(0.0, 1 - (i - 14) / 6) * k, 0.03 * k)   # main qui part en arrière
            return c
        M.action("Shoot", {i: shoot(i) for i in range(0, 37)}, 36)


def soldat(M):
    P, T = hamster(M, humeur="decide", bras="aucun")
    # Bras droit levant l'épée cure-dent devant lui ; bras gauche portant la capsule de bouteille.
    M.bloc("bras_R", "Arm.R", P(-0.24, -0.38, 0.43), T(0.14, 0.13, 0.17), "Dore", 0.06, 3)
    M.bloc("patte_R", "Arm.R", P(-0.25, -0.44, 0.36), T(0.12, 0.11, 0.08), "Rose", 0.03, 2)
    bois = M.m("Bois", (0.6, 0.38, 0.15), 0.6)
    epee = f.revolution("epee", [(0.0, -0.06), (0.022, 0.0), (0.022, 0.56), (0.0, 0.66)], bois, cotes=8)
    epee.location = P(-0.25, -0.46, 0.3)
    epee.rotation_euler = (math.radians(22), math.radians(-14), 0)   # pointe vers l'avant et vers le haut
    M.piece(epee, "Epee")
    fil = M.m("Rouge_fil", (0.6, 0.02, 0.02), 0.6)          # fil rouge enroulé : la garde
    M.bloc("garde", "Epee", P(-0.275, -0.5, 0.395), T(0.15, 0.04, 0.035), fil, 0.01, 1,
           rot=(math.radians(22), math.radians(-14), 0))
    M.bloc("bras_L", "Arm.L", P(0.24, -0.36, 0.43), T(0.14, 0.13, 0.17), "Dore", 0.06, 3)
    M.bloc("patte_L", "Arm.L", P(0.25, -0.42, 0.36), T(0.12, 0.1, 0.07), "Rose", 0.03, 2)
    rouge = M.m("Capsule", (0.62, 0.02, 0.015), 0.3, metal=0.5)
    cap = f.revolution("capsule", [(0.0, 0.0), (0.2, 0.0), (0.21, 0.05), (0.0, 0.05)], rouge, cotes=20)
    cap.location = P(0.33, -0.47, 0.42)
    cap.rotation_euler = (math.radians(90), 0, math.radians(-18))
    M.piece(cap, "Arm.L")
    centre = f.revolution("capsule_centre", [(0.0, 0.0), (0.12, 0.0), (0.12, 0.012), (0.0, 0.012)], M.m("Creme"), cotes=20)
    centre.location = P(0.315, -0.525, 0.42)
    centre.rotation_euler = (math.radians(90), 0, math.radians(-18))
    M.piece(centre, "Arm.L")
    for i in range(14):                                    # bord cranté de la capsule
        a = 2 * math.pi * i / 14
        c = Vector((0.33, -0.47, 0.42)) + Vector((math.cos(math.radians(-18)), math.sin(math.radians(-18)), 0)) \
            * (0.215 * math.cos(a)) + Vector((0, 0, 0.215 * math.sin(a)))
        M.bloc(f"cran_{i}", "Arm.L", P(*c), T(0.045, 0.06, 0.045), rouge, 0.008, 1,
               rot=(math.radians(90), a, math.radians(-18)))
    # Dé à coudre en casque (un peu de travers), petits creux, plumet rouge.
    metal = M.m("De", (0.62, 0.62, 0.66), 0.28, metal=0.9)
    de = f.revolution("de", [(0.24, 0.0), (0.245, 0.17), (0.22, 0.25), (0.13, 0.29), (0.0, 0.3)], metal, cotes=16)
    de.location = P(0.02, -0.08, 0.86)
    de.rotation_euler = (math.radians(-6), math.radians(10), 0)
    M.piece(de, "Head")
    creux = M.m("De_creux", (0.18, 0.18, 0.2), 0.5, metal=0.6)
    for r_, z_ in ((0, 0.06), (1, 0.13), (0, 0.2)):
        for j in range(5):
            a = math.radians(-90 - 40 + j * 20 + r_ * 10)
            M.bloc(f"creux_{r_}_{z_}_{j}", "Head", P(0.02 + 0.248 * math.cos(a) + 0.017 * z_ * 5, -0.08 + 0.248 * math.sin(a), 0.86 + z_),
                   T(0.035, 0.035, 0.035), creux, 0.0, 1, rot=(0, 0, a))
    M.bloc("plumet", "Head", P(0.065, -0.07, 1.2), T(0.07, 0.16, 0.14), "Plumet", 0.035, 2, rot=(0.5, 0.2, 0)) \
        if M.m("Plumet", (0.75, 0.03, 0.02), 0.7) else None
    M.bloc("plumet_2", "Head", P(0.07, 0.0, 1.24), T(0.06, 0.12, 0.1), "Plumet", 0.03, 2, rot=(0.9, 0.2, 0))
    M.os_("Epee", P(-0.25, -0.46, 0.33), P(-0.33, -0.58, 0.62), "Arm.R")
    M.finir()
    anims_hamster(M, extra=("attack",))
    M.exporter()


def archer(M):
    P, T = hamster(M, humeur="decide", bras="aucun")
    # Chapeau pointu d'archer vert (de travers), bord plus foncé, plume rouge plantée sur le côté.
    feutre = M.m("Feutre", (0.06, 0.3, 0.03), 0.6)
    bord = M.m("Feutre_bord", (0.03, 0.16, 0.015), 0.6)
    chap = f.prisme("chapeau", (0, 0, 0), 0.7, 0.56, 0.34, feutre, biseau=0.03)
    chap.rotation_euler = (0, math.radians(-8), math.radians(90))
    chap.location = P(0.0, -0.04, 0.86)
    M.piece(chap, "Head")
    M.bloc("chapeau_bord", "Head", P(0.0, -0.04, 0.88), T(0.6, 0.74, 0.05), bord, 0.02, 2, rot=(0, math.radians(-8), 0))
    M.bloc("plume", "Head", P(0.2, 0.12, 1.08), T(0.04, 0.09, 0.32), M.m("Plumet", (0.75, 0.03, 0.02), 0.7), 0.02, 2,
           rot=(-0.55, 0.35, 0))
    # Œil droit plissé pour viser : paupière dorée sur le haut de l'œil.
    M.bloc("paupiere", "Head", P(-0.19, -0.418, 0.83), T(0.16, 0.02, 0.1), "Dore", 0.02, 2)
    # Bras gauche tendu devant qui tient l'arc ; bras droit à la corde, flèche-allumette encochée.
    M.bloc("bras_L", "Arm.L", P(0.2, -0.47, 0.47), T(0.14, 0.26, 0.13), "Dore", 0.06, 3)
    M.bloc("patte_L", "Arm.L", P(0.18, -0.62, 0.47), T(0.1, 0.09, 0.11), "Rose", 0.03, 2)
    M.bloc("bras_R", "Arm.R", P(-0.12, -0.43, 0.47), T(0.22, 0.13, 0.13), "Dore", 0.06, 3)
    M.bloc("patte_R", "Arm.R", P(0.0, -0.47, 0.47), T(0.09, 0.09, 0.1), "Rose", 0.03, 2)
    brindille = M.m("Brindille", (0.3, 0.16, 0.06), 0.7)
    arc = f.tube_courbe("arc", [P(0.18, -0.5, 0.06), P(0.18, -0.6, 0.25), P(0.18, -0.64, 0.47), P(0.18, -0.6, 0.69),
                                P(0.18, -0.5, 0.88)], 0.025 * 1, brindille, cotes=6, resolution=4)
    M.piece(arc, "Arm.L")
    corde = M.m("Corde", (0.85, 0.82, 0.75), 0.6)
    M.piece(f.tube("corde", P(0.18, -0.5, 0.06), P(0.18, -0.5, 0.88), 0.006, corde, cotes=4), "Arm.L")
    allumette = M.m("Allumette", (0.75, 0.58, 0.33), 0.6)
    tete_rouge = M.m("Allumette_tete", (0.7, 0.03, 0.02), 0.5)
    M.piece(f.tube("fleche", P(0.17, -0.46, 0.47), P(0.17, -0.95, 0.47), 0.014, allumette, cotes=4), "Fleche")
    M.bloc("fleche_pointe", "Fleche", P(0.17, -0.97, 0.47), T(0.045, 0.06, 0.045), tete_rouge, 0.015, 2)
    # Carquois (boîte d'allumettes roulée en tube) sur le dos, trois allumettes qui dépassent.
    cuir = M.m("Carquois", (0.25, 0.09, 0.03), 0.6)
    M.bloc("carquois", "Body", P(-0.15, 0.42, 0.6), T(0.16, 0.14, 0.42), cuir, 0.04, 2, rot=(0.25, -0.35, 0))
    for j, dx in enumerate((-0.04, 0.0, 0.04)):
        M.piece(f.tube(f"allumette_{j}", P(-0.15 + dx - 0.05, 0.46, 0.75), P(-0.15 + dx - 0.1, 0.5, 0.97), 0.012,
                       allumette, cotes=4), "Body")
        M.bloc(f"allumette_tete_{j}", "Body", P(-0.15 + dx - 0.1, 0.5, 0.98), T(0.04, 0.04, 0.05), tete_rouge, 0.012, 2)
    M.os_("Fleche", P(0.0, -0.47, 0.47), P(0.0, -0.6, 0.47), "Arm.R")
    M.finir()
    anims_hamster(M, extra=("shoot",))
    M.exporter()


def boule(M):
    R = 0.72                                   # rayon de la boule
    k = 0.78                                   # hamster pilote, un peu plus petit
    P, T = hamster(M, k=k, o=(0, 0, 0.05), humeur="decide")
    # Lunettes d'aviateur sur le front.
    cuir = M.m("Cuir", (0.2, 0.08, 0.025), 0.6)
    verre = M.m("Lunettes", (0.25, 0.55, 0.6), 0.1, metal=0.3)
    M.bloc("lunettes_sangle", "Head", P(0, -0.07, 0.88), T(0.85, 0.69, 0.06), cuir, 0.03, 2)
    for s in (-1, 1):
        M.bloc(f"lunette_{s}", "Head", P(s * 0.15, -0.42, 0.9), T(0.17, 0.06, 0.13), cuir, 0.04, 2)
        M.bloc(f"verre_{s}", "Head", P(s * 0.15, -0.455, 0.9), T(0.12, 0.02, 0.09), verre, 0.03, 2)
    # Boule transparente (os Boule) : sphère + fentes d'aération + bandes de chenille rivetées.
    plastique = M.m("Boule", (0.75, 0.9, 1.0), 0.05, alpha=0.16)
    prof = [(R * math.sin(math.pi * i / 16), R - R * math.cos(math.pi * i / 16)) for i in range(17)]
    sph = f.revolution("boule", prof, plastique, cotes=32)
    sph.rotation_euler = (0, math.radians(90), 0)       # axe des pôles selon x (les fentes tournent avec la boule)
    sph.location = (-R, 0, R)
    M.piece(sph, "Boule")
    blinde = M.m("Blindage", (0.22, 0.28, 0.12), 0.45, metal=0.6)      # vert kaki
    rivet = M.m("Rivet", (0.7, 0.68, 0.6), 0.3, metal=0.9)
    for sx in (-1, 1):
        for i in range(18):
            a = 2 * math.pi * i / 18
            c = (sx * 0.5, R * 0.73 * math.cos(a) * 1.0, R + R * 0.73 * math.sin(a))
            # bande à x = ±0,5 : rayon local sqrt(R² - 0,5²) = 0,52
            rr = math.sqrt(R * R - 0.5 * 0.5) + 0.02
            c = (sx * 0.5, rr * math.cos(a), R + rr * math.sin(a))
            M.bloc(f"chenille_{sx}_{i}", "Boule", c, (0.12, 0.17, 0.05), blinde, 0.015, 1, rot=(a + math.pi / 2, 0, 0))
            if i % 2 == 0:
                M.bloc(f"rivet_{sx}_{i}", "Boule", (sx * 0.5, (rr + 0.03) * math.cos(a), R + (rr + 0.03) * math.sin(a)),
                       (0.04, 0.04, 0.03), rivet, 0.01, 1, rot=(a + math.pi / 2, 0, 0))
    # Fentes d'aération (bandes plus opaques) entre les chenilles.
    fente = M.m("Fente", (0.35, 0.45, 0.55), 0.2, alpha=0.45)
    for i in range(12):
        a = 2 * math.pi * i / 12 + 0.13
        M.bloc(f"fente_{i}", "Boule", (0, (R + 0.003) * math.cos(a), R + (R + 0.003) * math.sin(a)), (0.45, 0.05, 0.012),
               fente, 0.0, 1, rot=(a + math.pi / 2, 0, 0))
    # Trois plaques de blindage boulonnées sur la boule (os Boule) : on voit la boule tourner quand elle roule.
    orange = M.m("Plaque", (0.85, 0.36, 0.0), 0.45, metal=0.3)
    for j, a_deg in enumerate((25, 235, 320)):
        a = math.radians(a_deg)
        rr = R + 0.02
        M.bloc(f"plaque_{j}", "Boule", (0, rr * math.cos(a), R + rr * math.sin(a)), (0.4, 0.32, 0.04), orange, 0.02, 1,
               rot=(a + math.pi / 2, 0, 0))
        for dx in (-0.14, 0.14):
            M.bloc(f"plaque_rivet_{j}_{dx}", "Boule", (dx, (rr + 0.025) * math.cos(a), R + (rr + 0.025) * math.sin(a)),
                   (0.04, 0.04, 0.03), rivet, 0.01, 1, rot=(a + math.pi / 2, 0, 0))
    # Moyeux et arceau fixe (os Cadre) : tourelle et canon-paille au-dessus, fanion à l'arrière.
    for sx in (-1, 1):
        M.bloc(f"moyeu_{sx}", "Cadre", (sx * (R + 0.04), 0, R), (0.1, 0.3, 0.3), blinde, 0.05, 2)
        M.bloc(f"moyeu_rivet_{sx}", "Cadre", (sx * (R + 0.1), 0, R), (0.04, 0.12, 0.12), rivet, 0.03, 2)
        M.piece(f.tube_courbe(f"arceau_{sx}", [(sx * (R + 0.06), 0, R + 0.1), (sx * (R + 0.06), 0, R + 0.55),
                                                (sx * 0.5, 0, 2 * R + 0.12), (sx * 0.12, 0, 2 * R + 0.17)],
                              0.04, blinde, cotes=8), "Cadre")
    M.bloc("tourelle", "Cadre", (0, 0, 2 * R + 0.2), (0.36, 0.36, 0.2), blinde, 0.07, 3)
    paille = M.m("Paille", (0.9, 0.85, 0.8), 0.4)
    bande_rouge = M.m("Paille_rayure", (0.7, 0.03, 0.03), 0.4)
    M.piece(f.tube("canon", (0, -0.1, 2 * R + 0.22), (0, -0.62, 2 * R + 0.27), 0.045, paille, cotes=10), "Cadre")
    a_, b_ = Vector((0, -0.1, 2 * R + 0.22)), Vector((0, -0.62, 2 * R + 0.27))
    for j in range(3):                                     # rayures rouges de la paille
        t0 = 0.4 + 0.2 * j
        M.piece(f.tube(f"canon_rayure_{j}", a_.lerp(b_, t0), a_.lerp(b_, t0 + 0.07), 0.05, bande_rouge, cotes=10), "Cadre")
    M.piece(f.tube("mat", (0.1, 0.12, 2 * R + 0.28), (0.1, 0.18, 2 * R + 0.62), 0.012, rivet, cotes=4), "Cadre")
    fanion = M.m("Fanion", (0.85, 0.42, 0.0), 0.6)
    M.bloc("fanion", "Cadre", (0.1, 0.27, 2 * R + 0.55), (0.012, 0.18, 0.1), fanion, 0.0, 1, rot=(0.1, 0, 0))
    M.os_("Boule", (0, 0, R), (0.4, 0, R), "Root")
    M.os_("Cadre", (0, 0, R), (0, 0, R + 0.4), "Root")
    M.finir()
    anims_hamster(M, k=k)
    # Roll : un tour de boule en 48 images (sans glisser : avancer de 2πR = 4,52 m), hamster qui court.
    def roll(i):
        s = math.sin(2 * math.pi * i / 16)
        return {"Boule": [(X, 360 * i / 48)], "Leg.R": [avant(40 * s)], "Leg.L": [avant(-40 * s)],
                "Arm.R": [avant(-30 * s)], "Arm.L": [avant(30 * s)], "Body": [(X, 14)], "Head": [(X, -10)],
                "Root:loc": (0, 0, 0.0)}
    M.action("Roll", {i: roll(i) for i in range(0, 49)}, 48)
    M.exporter()


def cochon(M):
    """Cochon d'Inde géant, 3,0 m (trois fois le hamster), quadrupède, regarde vers -y."""
    crem, roux, brun = (M.m("Cochon_creme", (0.82, 0.74, 0.6), 0.35), M.m("Cochon_roux", (0.6, 0.22, 0.04), 0.35),
                        M.m("Cochon_brun", (0.09, 0.045, 0.02), 0.4))

    def b(nom, os_, c, t, mat, bis=0.0, seg=3, rot=(0, 0, 0)):
        return M.bloc(nom, os_, c, t, mat, bis, seg, rot)

    # Corps : avant crème, arrière roux (tricolore), tache brune sur le flanc gauche.
    b("corps_avant", "Body", (0, -0.45, 1.33), (2.3, 1.9, 2.2), crem, 0.72, 4)
    b("corps_arriere", "Body", (0, 0.75, 1.3), (2.36, 1.95, 2.25), roux, 0.75, 4)
    b("tache", "Body", (1.1, 0.25, 1.65), (0.22, 1.0, 0.8), brun, 0.2, 3)
    # Tête : moitié droite brune (tache sur l'œil), moitié gauche crème, liseré roux au milieu ; museau crème.
    b("tete_d", "Head", (-0.45, -1.55, 1.6), (1.0, 1.4, 1.6), brun, 0.45, 4)
    b("tete_g", "Head", (0.45, -1.55, 1.6), (1.0, 1.4, 1.6), crem, 0.45, 4)
    b("liseré", "Head", (0, -1.6, 2.1), (0.3, 1.25, 0.6), roux, 0.12, 3)
    b("museau", "Head", (0, -2.2, 1.28), (1.15, 0.5, 0.75), crem, 0.3, 3)
    b("nez", "Head", (0, -2.47, 1.48), (0.32, 0.08, 0.2), M.m("Nez"), 0.06, 2)
    for s in (-1, 1):
        b(f"dent_{s}", "Head", (s * 0.07, -2.43, 0.97), (0.12, 0.07, 0.2), M.m("Dents"), 0.025, 1)
        b(f"bouche_{s}", "Head", (s * 0.08, -2.46, 1.18), (0.16, 0.03, 0.04), M.m("Bouche"), 0.0, 1, rot=(0, -s * 0.5, 0))
        b(f"joue_{s}", "Head", (s * 0.75, -2.15, 1.38), (0.3, 0.06, 0.15), M.m("Joue"), 0.05, 2)
        # Grands yeux noirs (os Yeux) avec reflets.
        b(f"oeil_{s}", "Yeux", (s * 0.52, -2.24, 1.86), (0.4, 0.1, 0.46), M.m("Yeux"), 0.12, 3)
        b(f"reflet_{s}", "Yeux", (s * 0.52 + 0.09, -2.3, 1.98), (0.14, 0.03, 0.14), M.m("Reflet"), 0.03, 2)
        b(f"reflet2_{s}", "Yeux", (s * 0.52 - 0.09, -2.3, 1.75), (0.07, 0.03, 0.07), M.m("Reflet"), 0.0, 1)
        b(f"sourcil_{s}", "Head", (s * 0.52, -2.28, 2.2), (0.34, 0.06, 0.08), brun if s > 0 else roux, 0.02, 1,
          rot=(0, s * -0.15, 0))
        # Oreilles en pétale tombantes, intérieur rose.
        b(f"oreille_{s}", "Head", (s * 0.95, -1.25, 2.3), (0.5, 0.18, 0.4), roux if s > 0 else brun, 0.12, 3,
          rot=(0.1, s * 0.75, 0))
        b(f"oreille_in_{s}", "Head", (s * 0.93, -1.35, 2.27), (0.32, 0.04, 0.26), M.m("Rose"), 0.06, 2,
          rot=(0.1, s * 0.75, 0))
        b(f"moustache_{s}", "Head", (s * 0.8, -2.46, 1.35), (0.6, 0.02, 0.02), brun, 0.0, 1, rot=(0, s * 0.12, 0))
    # Rosette de poils en bataille (cochon d'Inde abyssin) sur le sommet du crâne.
    for i, (x, y, h, rx, ry) in enumerate(((0, -1.4, 0.4, 0.0, 0.0), (-0.25, -1.3, 0.3, -0.3, -0.5),
                                            (0.25, -1.3, 0.32, -0.3, 0.5), (-0.12, -1.6, 0.28, 0.45, -0.3),
                                            (0.14, -1.62, 0.26, 0.45, 0.35), (0, -1.15, 0.3, -0.55, 0.0))):
        b(f"rosette_{i}", "Head", (x, y, 2.42 + h / 2 - 0.05), (0.18, 0.18, h), crem if i % 2 else roux, 0.06, 2,
          rot=(rx, ry, 0))
    # Harnais de cuir (sangle de poitrail et sangle dorsale) avec écusson doré.
    cuir = M.m("Harnais", (0.18, 0.07, 0.02), 0.6)
    or_ = M.m("Ecusson", (0.95, 0.6, 0.05), 0.3, metal=0.9)
    b("sangle_dos", "Body", (0, -0.15, 2.38), (0.3, 1.6, 0.12), cuir, 0.04, 2)
    for s in (-1, 1):
        b(f"sangle_flanc_{s}", "Body", (s * 1.17, -0.8, 1.55), (0.1, 0.25, 1.4), cuir, 0.03, 2, rot=(0.5, 0, 0))
    for s in (-1, 1):                     # écusson doré à cœur rouge sur chaque flanc
        b(f"ecusson_{s}", "Body", (s * 1.22, -0.8, 1.45), (0.08, 0.46, 0.46), or_, 0.1, 3)
        b(f"ecusson_coeur_{s}", "Body", (s * 1.265, -0.8, 1.45), (0.03, 0.22, 0.22),
          M.m("Capsule", (0.62, 0.02, 0.015), 0.3), 0.05, 2)
    # Pattes courtes et pieds roses.
    for nom, x, y in (("FR", -0.75, -1.05), ("FL", 0.75, -1.05), ("BR", -0.8, 1.35), ("BL", 0.8, 1.35)):
        b(f"patte_{nom}", f"Leg.{nom}", (x, y, 0.35), (0.55, 0.55, 0.5), roux if nom.startswith("B") else crem, 0.18, 3)
        b(f"pied_{nom}", f"Leg.{nom}", (x, y - 0.12, 0.08), (0.5, 0.62, 0.16), M.m("Rose"), 0.06, 2)
        M.os_(f"Leg.{nom}", (x, y, 0.7), (x, y, 0.0), "Root")
    M.os_("Root", (0, 0, 0), (0, 0, 0.6))
    M.os_("Body", (0, 0.2, 0.7), (0, 0.2, 2.2), "Root")
    M.os_("Head", (0, -1.0, 1.5), (0, -1.0, 2.5), "Body")
    M.os_("Yeux", (0, -2.24, 1.86), (0, -2.5, 1.86), "Head")
    M.finir()

    def respire(i):
        ph = 2 * math.pi * i / 48
        c = {"Body": [(X, 0.8 * math.sin(ph))], "Head": [(Y, 3 * math.sin(ph)), (X, 1.5 * math.sin(ph))]}
        if 30 <= i <= 33:
            c["Yeux:scale"] = (1, 1, 0.12)
        if 12 <= i <= 22:                                  # renifle : petits coups de tête
            c["Head"] = c["Head"] + [(X, 3 * math.sin((i - 12) * 2.2))]
        return c
    M.action("Idle", {i: respire(i) for i in range(0, 49)}, 48)

    def marche(i, n, amp, rebond):
        s = math.sin(2 * math.pi * i / n)
        return {"Leg.FR": [avant(amp * s)], "Leg.BL": [avant(amp * s)], "Leg.FL": [avant(-amp * s)],
                "Leg.BR": [avant(-amp * s)], "Root:loc": (0, 0, rebond * abs(math.cos(2 * math.pi * i / n))),
                "Body": [(Y, 2 * s)], "Head": [(X, 2 * math.sin(4 * math.pi * i / n)), (Z, -2 * s)]}
    M.action("Walk", {i: marche(i, 32, 18, 0.05) for i in range(0, 33)}, 32)
    M.action("Run", {i: marche(i, 16, 30, 0.2) for i in range(0, 17)}, 16)
    # Popcorn : saut de joie avec torsion (sommet à l'image 10), réception à 18.
    def popcorn(i):
        if i <= 4:
            z, tw = -0.12 * i / 4, 0
        elif i <= 18:
            u = (i - 4) / 14
            z, tw = 1.1 * math.sin(math.pi * u), 22 * math.sin(2 * math.pi * u)
        else:
            z, tw = -0.1 * (1 - (i - 18) / 6), 0
        return {"Root:loc": (0, 0, z), "Body": [(Z, tw), (Y, -tw * 0.4)], "Head": [(X, -8 * max(0, z))],
                "Leg.FR": [avant(20 * max(0, z))], "Leg.FL": [avant(20 * max(0, z))],
                "Leg.BR": [avant(-20 * max(0, z))], "Leg.BL": [avant(-20 * max(0, z))]}
    M.action("Popcorn", {i: popcorn(i) for i in range(0, 25)}, 24)
    M.exporter(hauteur=3.0)


def heros(M):
    hamster(M)
    M.finir()
    anims_hamster(M)
    M.exporter()


CONSTRUCTEURS = {"hamster_bloc": heros, "hamster_soldat_bloc": soldat, "hamster_archer_bloc": archer,
                 "hamster_boule_bloc": boule, "cochon_inde_bloc": cochon}


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(CONSTRUCTEURS)
    for asset_id in args:
        CONSTRUCTEURS[asset_id](Modele(asset_id))


main()
