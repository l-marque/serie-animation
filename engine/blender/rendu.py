"""Rendu : produit les frames PNG des beats demandés (les autres sont déjà en cache).

Frames numérotées globalement : <sortie>/frames/f_0001.png … f_NNNN.png. Le montage
les assemble ensuite dans l'ordre. Mode 'animatique' : résolution réduite et peu
d'échantillons, pour valider le rythme vite ; mode 'final' : qualité de publication.
"""

from __future__ import annotations

import time
from pathlib import Path

import bpy

import look
from commun import journal


def regler(scene: bpy.types.Scene, timeline: dict, sortie: Path) -> None:
    largeur, hauteur = timeline["resolution"]
    scene.render.resolution_x, scene.render.resolution_y = largeur, hauteur
    defaut = 50 if timeline["mode"] == "animatique" else 100
    scene.render.resolution_percentage = int(timeline.get("pourcentage_resolution", defaut))
    scene.render.fps = timeline["fps"]
    scene.render.fps_base = 1.0
    scene.frame_start, scene.frame_end = 1, timeline["nb_frames"]
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.use_file_extension = True
    scene.render.use_motion_blur = False
    scene.render.filepath = str(sortie / "frames" / "f_")
    (sortie / "frames").mkdir(parents=True, exist_ok=True)


def rendre(scene: bpy.types.Scene, timeline: dict, beats: list[str]) -> dict[str, float]:
    """Rend les beats demandés. Si le moteur principal échoue (ex. pas de GPU), bascule sur le moteur de secours."""
    durees: dict[str, float] = {}
    par_id = {b["id"]: b for b in timeline["beats"]}
    for ident in beats:
        b = par_id[ident]
        scene.frame_start, scene.frame_end = b["frame_debut"], b["frame_fin"]
        t0 = time.time()
        try:
            bpy.ops.render.render(animation=True, scene=scene.name)
        except RuntimeError as e:
            secours = timeline["pack_da"]["moteur"].get("secours", "CYCLES")
            if scene.render.engine == secours:
                raise
            if "cannot save" in str(e):
                # Image verrouillée (ouverte dans une visionneuse…) : changer de moteur ne règle rien et
                # Cycles est ~20 fois plus lent (incident du 2026-11-17). On s'arrête avec un message clair.
                raise RuntimeError(f"image impossible à écrire, fermer la visionneuse qui l'ouvre : {e}") from e
            journal(f"échec du moteur {scene.render.engine} ({e}) : bascule sur {secours}")
            look.moteur(scene, timeline["pack_da"], timeline["mode"], forcer=secours)
            bpy.ops.render.render(animation=True, scene=scene.name)
        durees[ident] = round(time.time() - t0, 2)
        journal(f"beat {ident} rendu (frames {b['frame_debut']}-{b['frame_fin']}) en {durees[ident]} s")
    scene.frame_start, scene.frame_end = 1, timeline["nb_frames"]
    return durees
