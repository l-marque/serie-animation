"""Décorateur : monte le décor (sol, éléments, personnages, modules procéduraux).

Tout objet visible est un EMPTY qui instancie une collection prototype : un même asset
utilisé 5 000 fois n'existe qu'une fois en mémoire (indispensable avec 12 Go de VRAM).
Les positions aléatoires dépendent d'une seed : même fiche = même décor, à chaque fois.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import bpy

import bibliotheque
import look
from commun import PROP_CATEGORIE, PROP_ECHELLE, PROP_ID, journal, lier, nouvelle_collection
from kits import KITS

ANGLE_OR = math.pi * (3 - math.sqrt(5))


class Decorateur:
    def __init__(self, scene: bpy.types.Scene, timeline: dict, racine: Path):
        self.scene = scene
        self.timeline = timeline
        self.pack = timeline["pack_da"]
        self.racine = racine
        self.kit = KITS[timeline["decor"]["kit"]]
        self.prototypes: dict[tuple[str, str | None], bpy.types.Collection] = {}
        self.col_decor = nouvelle_collection("DECOR", scene.collection)
        self.col_personnages = nouvelle_collection("PERSONNAGES", scene.collection)
        self.col_modules = nouvelle_collection("MODULES", scene.collection)

    # ----- prototypes -------------------------------------------------------------------
    def apparition(self, ident: str, visible_au_debut: bool) -> int:
        """Image où l'élément devient visible : 1 s'il l'est dès le début, sinon le début de sa
        première action « apparaitre » (repli : 1)."""
        if visible_au_debut:
            return 1
        debuts = [a["frame_debut"] for b in self.timeline["beats"] for a in b["actions"]
                  if a["type"] == "apparaitre" and a["cible"] == ident]
        return min(debuts) if debuts else 1

    def prototype(self, asset: str, role: str | None, decalage: int = 0) -> bpy.types.Collection:
        """Collection prototype d'un asset, pour un rôle principal donné (mise en cache).

        `decalage` (images) décale l'option « sequence » du registre : ses images comptent à partir
        de l'apparition de l'élément. Il ne compte dans la clé du cache que pour un asset à séquence."""
        espace, nom = asset.split(":", 1)
        a_sequence = espace == "bibliotheque" and bool(
            bibliotheque.charger_registre(self.racine).get(nom, {}).get("sequence"))
        decalage = decalage if a_sequence else 0
        cle = (asset, role, decalage)
        if cle in self.prototypes:
            return self.prototypes[cle]
        suffixe = f"_d{decalage}" if decalage else ""
        col = bpy.data.collections.new(f"PROTO_{nom}_{role or 'defaut'}{suffixe}")
        if espace == "primitif":
            for nom_piece, maillage, pos, rot_z, role_piece, principale in self.kit.PRIMITIVES[nom](seed=7):
                obj = bpy.data.objects.new(f"{nom}_{nom_piece}", maillage.copy())
                obj.location = pos
                obj.rotation_euler.z = rot_z
                look.appliquer_role(obj, role if (principale and role) else role_piece, self.pack)
                col.objects.link(obj)
        else:
            garder = bibliotheque.charger_registre(self.racine).get(nom, {}).get("materiaux") == "origine"
            for obj, role_piece, principale in bibliotheque.pieces_bibliotheque(self.racine, nom, decalage):
                if obj.type == "MESH":
                    look.appliquer_role(obj, role if (principale and role) else role_piece, self.pack, garder)
                col.objects.link(obj)
        self.prototypes[cle] = col
        return col

    # ----- objets -----------------------------------------------------------------------
    def instance(self, nom: str, asset: str, role: str | None, collection: bpy.types.Collection,
                 decalage: int = 0) -> bpy.types.Object:
        e = bpy.data.objects.new(nom, None)
        e.instance_type = "COLLECTION"
        e.instance_collection = self.prototype(asset, role, decalage)
        e.empty_display_size = 0.3
        return lier(e, collection)

    def objet(self, spec: dict) -> bpy.types.Object:
        col = self.col_personnages if spec["categorie"] == "personnage" else self.col_decor
        decalage = self.apparition(spec["id"], spec.get("visible_au_debut", True)) - 1
        e = self.instance(f"EP_{spec['id']}", spec["asset"], spec.get("role"), col, decalage)
        e.location = spec["position"]
        e.rotation_euler.z = math.radians(spec.get("rotation_z", 0))
        s = spec.get("echelle", 1)
        e.scale = (s, s, s)
        e[PROP_ID], e[PROP_CATEGORIE], e[PROP_ECHELLE] = spec["id"], spec["categorie"], s
        if not spec.get("visible_au_debut", True):
            e.scale = (0, 0, 0)
        return e

    def positions(self, m: dict) -> list[tuple[float, float]]:
        n, esp, rng = m["nombre"], m["espacement"], random.Random(m["seed"])
        if m["motif"] == "spirale":
            return [(0.75 * esp * math.sqrt(i + 1) * math.cos(i * ANGLE_OR),
                     0.75 * esp * math.sqrt(i + 1) * math.sin(i * ANGLE_OR)) for i in range(n)]
        if m["motif"] == "grille":
            cote = max(1, math.ceil(math.sqrt(n)))
            dec = (cote - 1) * esp / 2
            return [((i % cote) * esp - dec, (i // cote) * esp - dec) for i in range(n)]
        if m["motif"] == "cercle":
            r = max(esp, n * esp / (2 * math.pi))
            return [(r * math.cos(2 * math.pi * i / max(n, 1)), r * math.sin(2 * math.pi * i / max(n, 1))) for i in range(n)]
        # aleatoire : 'espacement' = rayon de la zone, 'rayon_interieur' = zone laissée libre au centre ;
        # tirage avec distance minimale entre instances (rendu plus naturel).
        rayon, r_int = esp, min(m.get("rayon_interieur", 0.0), esp * 0.95)
        surface = math.pi * (rayon ** 2 - r_int ** 2)
        dmin = max(math.sqrt(surface / max(n, 1)) * 0.55, 0.5)
        pts: list[tuple[float, float]] = []
        essais = 0
        while len(pts) < n and essais < n * 60:
            essais += 1
            r = math.sqrt(r_int ** 2 + (rayon ** 2 - r_int ** 2) * rng.random())
            a = rng.random() * 2 * math.pi
            p = (r * math.cos(a), r * math.sin(a))
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 >= dmin ** 2 for q in pts):
                pts.append(p)
        if len(pts) < n:
            journal(f"module {m['id']} : zone trop petite, {len(pts)}/{n} instances placées")
        return pts

    def module(self, m: dict) -> bpy.types.Object:
        racine = bpy.data.objects.new(f"MOD_{m['id']}", None)
        racine.location = m["centre"]
        racine.empty_display_size = 1.0
        racine[PROP_ID], racine[PROP_CATEGORIE] = m["id"], "module"
        lier(racine, self.col_modules)
        rng = random.Random(m["seed"] + 1)
        smin, smax = m["variation_echelle"]
        for i, (x, y) in enumerate(self.positions(m)):
            e = self.instance(f"MOD_{m['id']}_{i:04d}", m["asset"], m.get("role"), self.col_modules)
            e.parent = racine
            e.location = (x, y, 0)
            e.rotation_euler.z = rng.random() * 2 * math.pi
            s = rng.uniform(smin, smax)
            e.scale = (s, s, s) if m.get("visible_au_debut", True) else (0, 0, 0)
            e[PROP_ID], e[PROP_CATEGORIE], e[PROP_ECHELLE] = f"{m['id']}_{i:04d}", "instance", s
        journal(f"module {m['id']} : {len(racine.children)} instance(s) de {m['asset']}")
        return racine

    def sol(self) -> None:
        decor = self.timeline["decor"]
        if not decor.get("sol", True):
            return
        obj = bpy.data.objects.new("SOL", self.kit.sol(decor.get("taille_sol", 40)))
        look.appliquer_role(obj, "sol", self.pack)
        obj.modifiers.clear()  # pas de contour sur le sol
        if obj.data.materials and obj.data.materials[-1].name == "MAT_contour":
            obj.data.materials.pop()
        lier(obj, self.col_decor)

    def texte_3d(self, t: dict, objets: dict[str, bpy.types.Object]) -> bpy.types.Object:
        """Texte en relief (habillage) : nom de ville, légende de carte… converti en maillage pour
        recevoir le matériau de son rôle et le contour du pack, comme les autres assets."""
        courbe = bpy.data.curves.new(f"TXT_{t['id']}", "FONT")
        courbe.body = t["texte"]
        courbe.align_x, courbe.align_y = "CENTER", "CENTER"
        courbe.size = t["taille"]
        courbe.extrude = t["epaisseur"] / 2
        tmp = bpy.data.objects.new(f"_TXT_{t['id']}", courbe)
        self.scene.collection.objects.link(tmp)
        bpy.context.view_layer.update()
        maillage = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(tmp, do_unlink=True)
        bpy.data.curves.remove(courbe)
        obj = lier(bpy.data.objects.new(f"TXT_{t['id']}", maillage), self.col_decor)
        look.appliquer_role(obj, t["role"], self.pack)
        # Debout, face à -y : le texte est lisible depuis la caméra par défaut.
        obj.rotation_euler = (math.radians(90), 0, math.radians(t["rotation_z"]))
        obj.location = t["position"]
        parent = objets.get(t["parent"]) if t.get("parent") else None
        if parent is not None:
            obj.parent = parent  # repère du parent : le texte suit ses apparitions et déplacements
        obj[PROP_ID], obj[PROP_CATEGORIE] = t["id"], "texte"
        if not t.get("visible_au_debut", True):
            obj.scale = (0, 0, 0)
        return obj

    def construire(self) -> None:
        self.sol()
        objets = {}
        for spec in self.timeline["objets"]:
            objets[spec["id"]] = self.objet(spec)
        for m in self.timeline["modules"]:
            self.module(m)
        for t in self.timeline.get("textes_3d", []):
            self.texte_3d(t, objets)
        journal(f"décor monté : {len(self.timeline['objets'])} objet(s), {len(self.timeline['modules'])} module(s), "
                f"{len(self.prototypes)} prototype(s)")
