"""Personnages « en blocs » de la série (création du projet) : style de toute l'histoire.

Corps en blocs biseautés (plastique lisse, couleurs franches), visage simple et expressif, squelette
maison à membres rigides et animations faites ici : Idle, Idle_Neutral, Run, Kick_Right, Wave, Jump,
Clapping, et depuis jour-2 Walk, Control_Right, Point_Down (mêmes noms que les anciens modèles : les fiches et le registre n'ont pas à changer).
Style inspiré des jeux à avatars en blocs ; aucun élément repris d'un jeu existant.

    blender --background --factory-startup --python engine/outils/atelier/modeles/perso_bloc.py -- kevin_bloc
    blender ... -- abonne_bloc_rouge        (voir PERSONNAGES)

Convention : le personnage regarde vers -y ; sa droite est du côté -x. Animations à 24 i/s.
Kick_Right : contact du pied droit avec le ballon à l'image 4 de l'action.
Walk (jour-2) : marche lente et nonchalante, cycle de 48 images (deux pas). Vitesse au sol pour que les pieds
ne glissent pas : environ 0,46 m par pas, soit 0,57 m/s pour un abonné (1,75 m) et 0,47 m/s pour Kevin
(1,45 m) à 30 i/s (les actions sont lues image pour image par le moteur).
Control_Right (jour-2) : contrôle du ballon du pied droit, ballon amorti au pied à l'image 8.
Point_Down (jour-2) : montre le bas de l'image (les commentaires), en boucle.
"""
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import formes as f  # noqa: E402

PEAU = (0.78, 0.46, 0.3)

PERSONNAGES = {
    # Kevin au départ : t-shirt moutarde délavé et rapiécé, short usé, chaussettes tombées, vieilles baskets,
    # cheveux en bataille, mine triste. Il évoluera (nouvelles tenues = nouvelles entrées ici).
    "kevin_bloc": dict(hauteur=1.45, tshirt=(0.42, 0.28, 0.04), bas=(0.07, 0.1, 0.2), short=True,
                       chaussures=(0.13, 0.12, 0.11), semelle=(0.4, 0.38, 0.35), chaussettes=(0.6, 0.58, 0.52),
                       cheveux=(0.09, 0.045, 0.02), coiffure="bataille", humeur="triste", piece=(0.2, 0.16, 0.12),
                       chaussette_tombee=True),
    # Kevin heureux (jour-2) : même modèle, même tenue, seule l'expression change (grand sourire, sourcils
    # détendus et levés, joues roses). Les épisodes passés gardent kevin_bloc.
    "kevin_bloc_heureux": dict(hauteur=1.45, tshirt=(0.42, 0.28, 0.04), bas=(0.07, 0.1, 0.2), short=True,
                               chaussures=(0.13, 0.12, 0.11), semelle=(0.4, 0.38, 0.35), chaussettes=(0.6, 0.58, 0.52),
                               cheveux=(0.09, 0.045, 0.02), coiffure="bataille", humeur="heureux", piece=(0.2, 0.16, 0.12),
                               chaussette_tombee=True),
    # Abonnés : même bonhomme, seul le t-shirt change.
    **{f"abonne_bloc_{nom}": dict(hauteur=1.75, tshirt=c, bas=(0.04, 0.05, 0.09), short=False,
                                  chaussures=(0.95, 0.95, 0.95), semelle=(0.2, 0.2, 0.2), chaussettes=None,
                                  cheveux=(0.05, 0.035, 0.025), coiffure="courte", humeur="sourire")
       for nom, c in {"rouge": (0.7, 0.03, 0.02), "bleu": (0.02, 0.15, 0.7), "vert": (0.03, 0.45, 0.08),
                      "jaune": (0.9, 0.55, 0.01), "violet": (0.3, 0.05, 0.6), "orange": (0.9, 0.22, 0.01)}.items()},
}


def plastique(nom, couleur, rugosite=0.42):
    return f.materiau(nom, couleur, rugosite=rugosite)


def construire(asset_id: str, p: dict):
    f.vider()
    u = p["hauteur"] / 5.25           # unité de bloc
    b = 0.06 * u                      # biseau
    m = {k: plastique(k, v) for k, v in {
        "Peau": PEAU, "Tshirt": p["tshirt"], "Bas": p["bas"], "Chaussures": p["chaussures"],
        "Semelle": p["semelle"], "Cheveux": p["cheveux"], "Yeux": (0.05, 0.05, 0.07),
        "Blanc_yeux": (0.97, 0.97, 0.97), "Bouche": (0.35, 0.1, 0.1)}.items()}
    if p.get("chaussettes"):
        m["Chaussettes"] = plastique("Chaussettes", p["chaussettes"])
    if p.get("piece"):
        m["Piece"] = plastique("Piece", p["piece"], 0.8)
    if p["humeur"] == "heureux":
        m["Dents"] = plastique("Dents", (0.9, 0.88, 0.84), 0.3)
        m["Langue"] = plastique("Langue", (0.55, 0.12, 0.12), 0.5)
        m["Joues"] = plastique("Joues", (0.75, 0.24, 0.2), 0.6)
        m["Gorge"] = plastique("Gorge", (0.09, 0.015, 0.015), 0.7)   # intérieur de la bouche, sombre : lisible au téléphone
    parties = []                      # (objet, os)

    def bloc(nom, os_, centre, taille, mat, biseau=b, rot=(0, 0, 0)):
        o = f.boite(nom, centre, taille, m[mat], biseau=biseau, segments=2, rotation=rot)
        parties.append((o, os_))
        return o

    # Jambes (os Leg.R à -x, Leg.L à +x), pivot à la hanche z = 2u.
    for cote, x in (("R", -0.5 * u), ("L", 0.5 * u)):
        os_ = f"Leg.{cote}"
        if p["short"]:
            bloc(f"short_{cote}", os_, (x, 0, 1.55 * u), (0.98 * u, 1.0 * u, 0.9 * u), "Bas")
            bloc(f"jambe_{cote}", os_, (x, 0, 0.85 * u), (0.82 * u, 0.82 * u, 0.9 * u), "Peau")
        else:
            bloc(f"pantalon_{cote}", os_, (x, 0, 1.1 * u), (0.98 * u, 1.0 * u, 1.8 * u), "Bas")
        if p.get("chaussettes"):
            h = 0.22 * u if (p.get("chaussette_tombee") and cote == "L") else 0.42 * u
            bloc(f"chaussette_{cote}", os_, (x, 0, 0.32 * u + h / 2), (0.86 * u, 0.86 * u, h), "Chaussettes")
        bloc(f"chaussure_{cote}", os_, (x, -0.12 * u, 0.2 * u), (0.96 * u, 1.24 * u, 0.32 * u), "Chaussures")
        bloc(f"semelle_{cote}", os_, (x, -0.12 * u, 0.04 * u), (1.0 * u, 1.28 * u, 0.08 * u), "Semelle", biseau=0.02 * u)

    # Tronc 2u × 1u × 2u, pivot au bassin.
    large = 1.12 if asset_id.startswith("kevin") else 1.0     # t-shirt trop grand
    bloc("tronc", "Torso", (0, 0, 3.0 * u), (2.0 * u * large, 1.0 * u * large, 2.0 * u), "Tshirt")
    bloc("ceinture", "Torso", (0, 0, 2.08 * u), (2.0 * u, 1.0 * u, 0.16 * u), "Bas", biseau=0.03 * u)
    if p.get("piece"):                                         # pièce cousue sur le ventre
        bloc("piece", "Torso", (0.45 * u, -0.56 * u * large, 2.6 * u), (0.42 * u, 0.04 * u, 0.36 * u), "Piece",
             biseau=0.01 * u, rot=(0, math.radians(8), 0))

    # Bras : manche courte + bras + main, pivot à l'épaule.
    for cote, x in (("R", -1.5 * u), ("L", 1.5 * u)):
        os_ = f"Arm.{cote}"
        bloc(f"manche_{cote}", os_, (x * (large if large > 1 else 1), 0, 3.55 * u), (0.98 * u * large, 1.0 * u * large, 0.9 * u), "Tshirt")
        bloc(f"bras_{cote}", os_, (x, 0, 2.65 * u), (0.82 * u, 0.82 * u, 1.1 * u), "Peau")
        bloc(f"main_{cote}", os_, (x, 0, 1.98 * u), (0.86 * u, 0.86 * u, 0.32 * u), "Peau", biseau=0.12 * u)

    # Tête : bloc arrondi 1,25u, cou court.
    zt = 4.68 * u
    bloc("cou", "Head", (0, 0, 4.07 * u), (0.6 * u, 0.6 * u, 0.2 * u), "Peau")
    bloc("tete", "Head", (0, 0, zt), (1.3 * u, 1.18 * u, 1.18 * u), "Peau", biseau=0.22 * u)
    yf = -0.59 * u - 0.01 * u                                   # face avant
    for cote, x in (("R", -0.27 * u), ("L", 0.27 * u)):
        bloc(f"oeil_{cote}", "Head", (x, yf, zt + 0.05 * u), (0.17 * u, 0.04 * u, 0.26 * u), "Yeux", biseau=0.05 * u)
        bloc(f"reflet_{cote}", "Head", (x + 0.03 * u, yf - 0.02 * u, zt + 0.11 * u), (0.06 * u, 0.02 * u, 0.06 * u),
             "Blanc_yeux", biseau=0.0)
        triste = p["humeur"] == "triste"
        angle = (-22 if cote == "R" else 22) if triste else 0
        dz = 0.0                                                # sourcils plats et détendus (plus haut, la frange les cache)
        bloc(f"sourcil_{cote}", "Head", (x, yf, zt + 0.3 * u + dz), (0.28 * u, 0.04 * u, 0.06 * u), "Cheveux",
             biseau=0.0, rot=(0, math.radians(angle), 0))
    if p["humeur"] == "heureux":                                # grand sourire ouvert, dents, langue, joues
        # Sourire en « D » : bande haute large (dents), bande basse plus étroite (langue), coins relevés.
        zb = zt - 0.3 * u
        bloc("bouche_h", "Head", (0, yf, zb + 0.04 * u), (0.54 * u, 0.04 * u, 0.13 * u), "Gorge", biseau=0.03 * u)
        bloc("bouche_b", "Head", (0, yf, zb - 0.06 * u), (0.34 * u, 0.04 * u, 0.13 * u), "Gorge", biseau=0.04 * u)
        bloc("dents", "Head", (0, yf - 0.012 * u, zb + 0.06 * u), (0.44 * u, 0.03 * u, 0.055 * u), "Dents", biseau=0.0)
        bloc("langue", "Head", (0.02 * u, yf - 0.012 * u, zb - 0.075 * u), (0.2 * u, 0.03 * u, 0.06 * u), "Langue",
             biseau=0.02 * u)
        for s in (-1, 1):
            bloc(f"coin_{s}", "Head", (s * 0.29 * u, yf, zb + 0.12 * u), (0.07 * u, 0.04 * u, 0.12 * u), "Gorge",
                 biseau=0.0, rot=(0, math.radians(-30 * s), 0))
            bloc(f"joue_{s}", "Head", (s * 0.43 * u, yf + 0.005 * u, zt - 0.14 * u), (0.16 * u, 0.03 * u, 0.09 * u),
                 "Joues", biseau=0.02 * u)
    elif p["humeur"] == "triste":                                 # bouche en accent circonflexe
        for s in (-1, 1):
            bloc(f"bouche_{s}", "Head", (s * 0.08 * u, yf, zt - 0.3 * u), (0.18 * u, 0.04 * u, 0.05 * u), "Bouche",
                 biseau=0.0, rot=(0, math.radians(18 * s), 0))
    else:                                                       # sourire
        for s in (-1, 1):
            bloc(f"bouche_{s}", "Head", (s * 0.1 * u, yf, zt - 0.27 * u), (0.2 * u, 0.04 * u, 0.05 * u), "Bouche",
                 biseau=0.0, rot=(0, math.radians(-20 * s), 0))
        bloc("bouche_m", "Head", (0, yf, zt - 0.31 * u), (0.12 * u, 0.04 * u, 0.05 * u), "Bouche", biseau=0.0)

    # Cheveux.
    zh = zt + 0.59 * u
    if p["coiffure"] == "courte":
        bloc("cheveux", "Head", (0, 0.04 * u, zh - 0.02 * u), (1.36 * u, 1.24 * u, 0.26 * u), "Cheveux", biseau=0.1 * u)
        bloc("frange", "Head", (0, -0.5 * u, zh - 0.14 * u), (1.3 * u, 0.28 * u, 0.22 * u), "Cheveux", biseau=0.08 * u)
        bloc("nuque", "Head", (0, 0.58 * u, zt + 0.15 * u), (1.34 * u, 0.2 * u, 0.85 * u), "Cheveux", biseau=0.08 * u)
    else:                                                       # en bataille : mèches de travers
        bloc("cheveux", "Head", (0, 0.03 * u, zh - 0.04 * u), (1.36 * u, 1.24 * u, 0.24 * u), "Cheveux", biseau=0.1 * u)
        bloc("nuque", "Head", (0, 0.58 * u, zt + 0.12 * u), (1.34 * u, 0.2 * u, 0.9 * u), "Cheveux", biseau=0.08 * u)
        rng = random.Random(7)
        for i in range(9):
            x, y = rng.uniform(-0.5, 0.5) * u, rng.uniform(-0.45, 0.45) * u
            bloc(f"meche_{i}", "Head", (x, y, zh + 0.12 * u), (0.3 * u, 0.3 * u, rng.uniform(0.25, 0.45) * u),
                 "Cheveux", biseau=0.06 * u,
                 rot=(rng.uniform(-0.5, 0.5), rng.uniform(-0.5, 0.5), rng.uniform(0, 1.5)))
        for i, x in enumerate((-0.42, -0.1, 0.25)):
            bloc(f"frange_{i}", "Head", (x * u, -0.52 * u, zh - 0.1 * u - i * 0.04 * u), (0.36 * u, 0.24 * u, 0.3 * u),
                 "Cheveux", biseau=0.06 * u, rot=(0, rng.uniform(-0.4, 0.4), 0))

    # Squelette : Root, Torso, Head, Arm.L/R, Leg.L/R.
    arm_d = bpy.data.armatures.new("Squelette")
    arm = bpy.data.objects.new("Armature", arm_d)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")

    def os_edit(nom, tete, queue, parent=None):
        e = arm_d.edit_bones.new(nom)
        e.head, e.tail = Vector(tete), Vector(queue)
        e.roll = 0.0
        if parent:
            e.parent = arm_d.edit_bones[parent]
        return e

    os_edit("Root", (0, 0, 0), (0, 0, 0.8 * u))
    os_edit("Torso", (0, 0, 2.0 * u), (0, 0, 4.0 * u), "Root")
    os_edit("Head", (0, 0, 4.0 * u), (0, 0, 5.2 * u), "Torso")
    for cote, x in (("R", -1.5 * u), ("L", 1.5 * u)):
        os_edit(f"Arm.{cote}", (x, 0, 3.75 * u), (x, 0, 2.0 * u), "Torso")
        os_edit(f"Leg.{cote}", (x / 3, 0, 2.0 * u), (x / 3, 0, 0.0), "Root")
    bpy.ops.object.mode_set(mode="OBJECT")

    # Maillage unique, membres rigides (poids 1 sur un seul os).
    for o, os_ in parties:
        g = o.vertex_groups.new(name=os_)
        g.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
    corps = f.fusionner([o for o, _ in parties], asset_id)
    corps.parent = arm
    mod = corps.modifiers.new("Squelette", "ARMATURE")
    mod.object = arm
    animer(arm, u)
    return arm, corps


# ----- animations --------------------------------------------------------------------------------
def animer(arm, u):
    pb = arm.pose.bones
    for b in pb:
        b.rotation_mode = "XYZ"
    arm.animation_data_create()

    def action(nom, cles, longueur):
        """cles : {image: {os: (rx, ry, rz) en degrés ou ("loc", (x, y, z))}}."""
        act = bpy.data.actions.new(nom)
        act.use_fake_user = True
        arm.animation_data.action = act
        for b in pb:
            b.rotation_euler = (0, 0, 0)
            b.location = (0, 0, 0)
        for img in sorted(cles):
            for b in pb:
                b.rotation_euler = (0, 0, 0)
                b.location = (0, 0, 0)
            for os_, val in cles[img].items():
                if os_.endswith(":loc"):
                    pb[os_[:-4]].location = val
                else:
                    rx, ry, rz = val
                    if os_.startswith(("Arm", "Leg")):
                        rx = -rx   # os orientés vers le bas : x > 0 dans les clés = vers l'avant
                    pb[os_].rotation_euler = [math.radians(a) for a in (rx, ry, rz)]
            for b in pb:
                b.keyframe_insert("rotation_euler", frame=img)
                b.keyframe_insert("location", frame=img)
        act.frame_range = (0, longueur)
        return act

    # Rotation autour de x local : >0 = membre vers l'avant (vers -y) pour les os orientés vers le bas.
    def respire(d):
        return {"Torso": (d, 0, 0), "Arm.R": (0, 0, -3 - d), "Arm.L": (0, 0, 3 + d), "Head": (-d, 0, 0)}

    action("Idle", {0: respire(0), 24: respire(2.5), 48: respire(0)}, 48)
    action("Idle_Neutral", {0: {**respire(0), "Head": (0, 0, 0)}, 12: {**respire(1.5), "Head": (5, 0, 4)},
                            24: {**respire(2.5), "Head": (-3, 0, 0)}, 36: {**respire(1.5), "Head": (5, 0, -4)},
                            48: {**respire(0), "Head": (0, 0, 0)}}, 48)

    def course(s):
        return {"Leg.R": (40 * s, 0, 0), "Leg.L": (-40 * s, 0, 0), "Arm.R": (-45 * s, 0, 0),
                "Arm.L": (45 * s, 0, 0), "Torso": (10, 0, 0), "Head": (6, 0, 0)}
    action("Run", {0: {**course(1), "Root:loc": (0, 0, 0)}, 4: {**course(0), "Root:loc": (0, 0.12 * u, 0)},
                   8: {**course(-1), "Root:loc": (0, 0, 0)}, 12: {**course(0), "Root:loc": (0, 0.12 * u, 0)},
                   16: {**course(1), "Root:loc": (0, 0, 0)}}, 16)

    repos = {}
    action("Kick_Right", {
        0: repos,
        3: {"Leg.R": (-55, 0, 0), "Arm.L": (40, 0, 20), "Arm.R": (-30, 0, -25), "Torso": (8, 0, 0)},
        4: {"Leg.R": (15, 0, 0), "Arm.L": (25, 0, 25), "Arm.R": (-20, 0, -30), "Torso": (2, 0, 0)},   # contact
        8: {"Leg.R": (85, 0, 0), "Arm.L": (-20, 0, 30), "Arm.R": (30, 0, -35), "Torso": (-12, 0, 0),
            "Leg.L": (-8, 0, 0)},
        14: {"Leg.R": (30, 0, 0), "Torso": (-4, 0, 0)},
        22: repos}, 22)

    def salut(a):
        return {"Arm.R": (170, 0, -15 + a), "Head": (0, 0, -6), "Arm.L": (0, 0, 3)}
    action("Wave", {0: salut(0), 7: salut(28), 15: salut(0), 22: salut(28), 30: salut(0)}, 30)

    action("Jump", {0: {}, 5: {"Root:loc": (0, -0.25 * u, 0), "Arm.R": (-20, 0, 0), "Arm.L": (-20, 0, 0)},
                    11: {"Root:loc": (0, 0.9 * u, 0), "Arm.R": (175, 0, -20), "Arm.L": (175, 0, 20),
                         "Leg.R": (15, 0, 0), "Leg.L": (-10, 0, 0)},
                    18: {"Root:loc": (0, -0.15 * u, 0)}, 24: {}}, 24)

    def clap(z):
        return {"Arm.R": (80, z, 0), "Arm.L": (80, -z, 0), "Head": (-5, 0, 0)}
    action("Clapping", {0: clap(-30), 4: clap(8), 8: clap(-30), 12: clap(8), 16: clap(-30)}, 16)

    # Walk (jour-2) : marche lente, traînante. Clés toutes les 2 images pour que les pieds ne glissent pas :
    # angle des jambes LINÉAIRE dans le temps (±20°, le pied d'appui recule à vitesse constante, écart < 2 mm
    # avec un déplacement uniforme) et bassin abaissé de 2u·(1 − cos θ) à chaque image (pied d'appui à z = 0).
    # Nonchalance : épaules qui roulent (torsion du tronc), bras ballants peu amples, tête basse qui dodeline.
    def marche(img):
        t = img / 48
        s = 1 - 4 * abs(((t + 0.5) % 1) - 0.5)          # +1 (jambe droite devant) → −1 à l'image 24 → +1
        c, sn = math.cos(2 * math.pi * t), math.sin(2 * math.pi * t)
        th = math.radians(20 * s)
        return {"Leg.R": (20 * s, 0, 0), "Leg.L": (-20 * s, 0, 0), "Arm.R": (-13 * c, 0, 4), "Arm.L": (13 * c, 0, -4),
                "Torso": (5, 5 * c, 2.5 * c), "Head": (8 - math.cos(4 * math.pi * t), -3 * c, -5 * c + 2 * sn),
                "Root:loc": (0, -2 * u * (1 - math.cos(th)), 0)}
    action("Walk", {i: marche(i) for i in range(0, 49, 2)}, 48)

    # Bras : pour Arm.R, z > 0 écarte le bras du corps (z < 0 le ramène devant le ventre) ; inverse pour Arm.L.
    # Control_Right (jour-2) : la jambe droite vient au-devant du ballon puis recule pour l'amortir
    # (ballon arrêté au pied à l'image 8), bras écartés pour l'équilibre, regard sur le ballon.
    action("Control_Right", {
        0: {},
        5: {"Leg.R": (28, 0, 0), "Arm.R": (15, 0, 28), "Arm.L": (15, 0, -28), "Torso": (-4, 0, 0), "Head": (14, 0, 0)},
        8: {"Leg.R": (8, 0, 0), "Arm.R": (10, 0, 22), "Arm.L": (10, 0, -22), "Torso": (2, 0, 0), "Head": (16, 0, 0)},
        14: {"Leg.R": (0, 0, 0), "Arm.R": (0, 0, 8), "Arm.L": (0, 0, -8), "Head": (10, 0, 0)},
        22: {}}, 22)

    # Point_Down (jour-2) : bras droit tendu vers le bas de l'image, petits coups d'index en boucle.
    # Bras écarté en diagonale (lisible de face : la silhouette dessine une flèche vers le bas), regard qui
    # suit le bras, petits coups vers le bas ; l'autre bras reste le long du corps.
    def montre(a):
        return {"Arm.R": (a, 0, 30), "Arm.L": (0, 0, -3), "Head": (12, 0, -10), "Torso": (4, 0, -3)}
    action("Point_Down", {0: montre(28), 6: montre(40), 12: montre(28), 18: montre(40), 24: montre(28)}, 24)

    arm.animation_data.action = bpy.data.actions["Idle"]


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(PERSONNAGES)
    for asset_id in args:
        construire(asset_id, PERSONNAGES[asset_id])
        chemin = f.MODELES / "personnages_bloc" / f"{asset_id}.glb"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.export_scene.gltf(filepath=str(chemin), export_format="GLB", export_animation_mode="ACTIONS",
                                  export_force_sampling=True)
        print(f"MODELE_EXPORTE {asset_id} : {chemin}")


main()
