"""Animateur : exécute les actions de la timeline (tout ce qui bouge, sauf la caméra).

Les actions sont traitées dans l'ordre chronologique. Pour chaque action, l'état de départ
est lu dans la scène à l'instant de déclenchement (frame_set), ce qui permet d'enchaîner
plusieurs actions sur un même objet (déplacer puis tourner, apparaître puis grandir).

Les cycles (flotter, sautiller…) agissent sur les canaux « delta » de l'objet : ils
s'additionnent aux déplacements sans les écraser.
"""

from __future__ import annotations

import math

import bpy

from commun import PROP_ECHELLE, cle, instances_module, journal, objets_par_id


class Animateur:
    def __init__(self, scene: bpy.types.Scene, timeline: dict, decorateur):
        self.scene = scene
        self.timeline = timeline
        self.decorateur = decorateur
        self.fps = timeline["fps"]
        self.objets = objets_par_id(scene)

    # ----- utilitaires ---------------------------------------------------------------------
    def _cibles(self, ident: str) -> tuple[bpy.types.Object, list[bpy.types.Object]]:
        obj = self.objets[ident]
        if obj.get("prod_categorie") == "module":
            return obj, instances_module(obj)
        return obj, [obj]

    @staticmethod
    def _echelle_base(o: bpy.types.Object) -> float:
        return float(o.get(PROP_ECHELLE, 1.0))

    def _masquer_avant(self, o: bpy.types.Object, frame: int) -> None:
        o.scale = (0, 0, 0)
        if frame > 1:
            cle(o, "scale", 1, "CONSTANT")
        cle(o, "scale", frame, "BACK")

    # ----- actions -------------------------------------------------------------------------
    def apparaitre(self, a: dict) -> None:
        racine, objs = self._cibles(a["cible"])
        f0, f1 = a["frame_debut"], a["frame_fin"]
        if len(objs) == 1:
            o = objs[0]
            s = self._echelle_base(o)
            self._masquer_avant(o, f0)
            o.scale = (s, s, s)
            cle(o, "scale", f1, "BEZIER")
            return
        # Module : apparition en vague, du centre vers l'extérieur.
        centre = racine.matrix_world.translation
        tri = sorted(objs, key=lambda o: (o.matrix_world.translation - centre).length)
        etendue = max(f1 - f0, 1)
        duree_pop = max(4, int(etendue * 0.3))
        for i, o in enumerate(tri):
            depart = f0 + int(etendue * 0.7 * i / max(len(tri) - 1, 1))
            s = self._echelle_base(o)
            self._masquer_avant(o, depart)
            o.scale = (s, s, s)
            cle(o, "scale", depart + duree_pop, "BEZIER")

    def disparaitre(self, a: dict) -> None:
        _, objs = self._cibles(a["cible"])
        for o in objs:
            self.scene.frame_set(a["frame_debut"])
            cle(o, "scale", a["frame_debut"], "BEZIER")
            o.scale = (0, 0, 0)
            cle(o, "scale", a["frame_fin"], "CONSTANT")

    def deplacer(self, a: dict) -> None:
        o = self.objets[a["cible"]]
        p = a["params"]
        self.scene.frame_set(a["frame_debut"])
        cle(o, "location", a["frame_debut"], "BEZIER")
        if "vers" in p:
            v = list(p["vers"])
            o.location = v if len(v) == 3 else [*v, o.location.z]
        else:
            o.location = self.objets[p["vers_cible"]].matrix_world.translation.copy()
        cle(o, "location", a["frame_fin"], "BEZIER")

    def tourner(self, a: dict) -> None:
        o = self.objets[a["cible"]]
        self.scene.frame_set(a["frame_debut"])
        cle(o, "rotation_euler", a["frame_debut"], "BEZIER")
        o.rotation_euler.z += math.radians(a["params"].get("degres", 360))
        cle(o, "rotation_euler", a["frame_fin"], "BEZIER")

    def grandir(self, a: dict) -> None:
        _, objs = self._cibles(a["cible"])
        facteur = a["params"].get("facteur", 1.5)
        for o in objs:
            self.scene.frame_set(a["frame_debut"])
            cle(o, "scale", a["frame_debut"], "BEZIER")
            o.scale = [c * facteur for c in o.scale]
            o[PROP_ECHELLE] = self._echelle_base(o) * facteur
            cle(o, "scale", a["frame_fin"], "BACK")

    def transformer(self, a: dict) -> None:
        """L'objet se réduit à zéro pendant que le nouvel asset apparaît au même endroit."""
        ancien = self.objets[a["cible"]]
        f0, f1 = a["frame_debut"], a["frame_fin"]
        milieu = (f0 + f1) // 2
        self.scene.frame_set(f0)
        nouveau = self.decorateur.instance(f"{ancien.name}_transforme", a["params"]["vers_asset"],
                                           a["params"].get("role"), ancien.users_collection[0])
        nouveau.matrix_world = ancien.matrix_world.copy()
        s = list(ancien.scale)
        cle(ancien, "scale", f0, "BEZIER")
        ancien.scale = (0, 0, 0)
        cle(ancien, "scale", milieu, "CONSTANT")
        nouveau.scale = (0, 0, 0)
        cle(nouveau, "scale", 1, "CONSTANT")
        cle(nouveau, "scale", milieu, "BACK")
        nouveau.scale = s
        cle(nouveau, "scale", f1, "BEZIER")

    def cycle(self, a: dict) -> None:
        o = self.objets[a["cible"]]
        nom = a["params"]["nom"]
        amplitude = float(a["params"].get("amplitude", 1.0))
        f0, f1 = a["frame_debut"], a["frame_fin"]
        pas = 2
        for f in range(f0, f1 + 1, pas):
            t = (f - f0) / self.fps
            if nom == "flotter":
                o.delta_location.z = 0.15 * amplitude * math.sin(2 * math.pi * t / 1.6)
                cle(o, "delta_location", f, "LINEAR")
            elif nom == "sautiller":
                o.delta_location.z = 0.35 * amplitude * abs(math.sin(math.pi * t / 0.45))
                cle(o, "delta_location", f, "LINEAR")
            elif nom == "tourner_sur_soi":
                o.delta_rotation_euler.z = 2 * math.pi * t / 1.2
                cle(o, "delta_rotation_euler", f, "LINEAR")
            elif nom == "osciller":
                o.delta_rotation_euler.z = math.radians(12 * amplitude) * math.sin(2 * math.pi * t / 1.0)
                cle(o, "delta_rotation_euler", f, "LINEAR")
        # Retour au repos à la fin du cycle.
        o.delta_location.z = 0.0
        o.delta_rotation_euler.z = 0.0 if nom != "tourner_sur_soi" else o.delta_rotation_euler.z
        canal = "delta_rotation_euler" if nom in ("tourner_sur_soi", "osciller") else "delta_location"
        cle(o, canal, f1 + pas, "LINEAR")

    # ----- exécution -----------------------------------------------------------------------
    def appliquer(self) -> None:
        actions = sorted((a for b in self.timeline["beats"] for a in b["actions"]), key=lambda a: a["frame_debut"])
        for a in actions:
            getattr(self, a["type"])(a)
        self.scene.frame_set(1)
        journal(f"{len(actions)} action(s) animée(s)")
