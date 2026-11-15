"""Caméra : une caméra par beat, animée selon un mouvement prédéfini, calée sur la timeline.

Chaque caméra vise un point (VISEE_<beat>) placé sur la cible du plan. Des marqueurs de
timeline basculent automatiquement d'une caméra à l'autre au début de chaque beat : le
découpage est donc exact à la frame près.

Mouvements disponibles (fiche : plan.camera) :
    plan_fixe            caméra immobile
    survol               glisse latéralement en arc autour de la cible
    revelation           part bas et près, se recule et s'élève : dévoile la scène
    dolly_avant          avance vers la cible
    orbite               tourne d'un tiers de tour autour de la cible
    plongee              vue presque verticale qui descend doucement
    travelling_lateral   translation latérale face à la cible
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector

from commun import cle, journal, lier, nouvelle_collection, objets_par_id

DISTANCE_DEFAUT = 20.0
HAUTEUR_DEFAUT = 10.0
FOCALE_DEFAUT = 35.0
HAUTEUR_VISEE = 1.2
PAS_ARC = 4  # frames entre deux clés sur les trajectoires courbes


def _lisser(u: float) -> float:
    return u * u * (3 - 2 * u)  # départ et arrivée en douceur


def _polaire(centre: Vector, angle_deg: float, rayon: float, z: float) -> Vector:
    a = math.radians(angle_deg)
    return centre + Vector((rayon * math.cos(a), rayon * math.sin(a), z))


def trajectoire(preset: str, c: Vector, d: float, h: float):
    """Renvoie une fonction u (0 -> 1) -> position de la caméra, et un booléen 'courbe'."""
    if preset == "plan_fixe":
        p = _polaire(c, -90, d, h)
        return (lambda u: p), False
    if preset == "survol":
        return (lambda u: _polaire(c, -110 + 40 * u, d * (1 - 0.05 * u), h * (1 - 0.1 * u))), True
    if preset == "revelation":
        a, b = _polaire(c, -90, d * 0.45, max(1.0, h * 0.25)), _polaire(c, -90, d, h)
        return (lambda u: a.lerp(b, u)), False
    if preset == "dolly_avant":
        a, b = _polaire(c, -90, d * 1.3, h * 1.15), _polaire(c, -90, d * 0.8, h * 0.85)
        return (lambda u: a.lerp(b, u)), False
    if preset == "orbite":
        return (lambda u: _polaire(c, -120 + 60 * u, d, h)), True
    if preset == "plongee":
        a, b = _polaire(c, -90, d * 0.25, h * 1.7), _polaire(c, -90, d * 0.15, h * 1.2)
        return (lambda u: a.lerp(b, u)), False
    if preset == "travelling_lateral":
        a, b = c + Vector((-d * 0.4, -d, h)), c + Vector((d * 0.4, -d, h))
        return (lambda u: a.lerp(b, u)), False
    raise ValueError(f"mouvement de caméra inconnu : {preset}")


class Cameraman:
    def __init__(self, scene: bpy.types.Scene, timeline: dict):
        self.scene = scene
        self.timeline = timeline
        self.objets = objets_par_id(scene)
        self.col = nouvelle_collection("CAMERAS", scene.collection)

    def _centre(self, plan: dict, frame: int) -> Vector:
        cible = plan.get("cible")
        if cible and cible in self.objets:
            self.scene.frame_set(frame)
            pos = self.objets[cible].matrix_world.translation.copy()
        else:
            pos = Vector((0, 0, 0))
        return pos + Vector((0, 0, HAUTEUR_VISEE))

    def beat(self, b: dict) -> bpy.types.Object:
        plan = b["plan"]
        f0, f1 = b["frame_debut"], b["frame_fin"]
        centre = self._centre(plan, f0)
        visee = lier(bpy.data.objects.new(f"VISEE_{b['id']}", None), self.col)
        visee.location = centre
        donnees = bpy.data.cameras.new(f"CAM_{b['id']}")
        donnees.lens = plan.get("focale", FOCALE_DEFAUT)
        donnees.clip_end = 1000
        cam = lier(bpy.data.objects.new(f"CAM_{b['id']}", donnees), self.col)
        contrainte = cam.constraints.new("TRACK_TO")
        contrainte.target = visee
        contrainte.track_axis = "TRACK_NEGATIVE_Z"
        contrainte.up_axis = "UP_Y"
        position, courbe = trajectoire(plan["camera"], centre, plan.get("distance", DISTANCE_DEFAUT),
                                       plan.get("hauteur", HAUTEUR_DEFAUT))
        if courbe:
            for f in list(range(f0, f1, PAS_ARC)) + [f1]:
                cam.location = position(_lisser((f - f0) / max(f1 - f0, 1)))
                cle(cam, "location", f, "LINEAR")
        else:
            cam.location = position(0.0)
            cle(cam, "location", f0, "BEZIER")
            cam.location = position(1.0)
            cle(cam, "location", f1, "BEZIER")
        marqueur = self.scene.timeline_markers.new(f"plan_{b['id']}", frame=f0)
        marqueur.camera = cam
        return cam

    def appliquer(self) -> None:
        cams = [self.beat(b) for b in self.timeline["beats"]]
        self.scene.camera = cams[0]
        self.scene.frame_set(1)
        journal(f"{len(cams)} caméra(s) placée(s)")
