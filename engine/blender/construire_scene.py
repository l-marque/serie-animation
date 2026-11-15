"""Point d'entrée Blender de l'agent Production : timeline -> scène -> frames.

Lancé par le chef d'orchestre (engine/pipeline/run.py) :
    blender --background --factory-startup --python construire_scene.py -- \
        --timeline renders/<ep>/<mode>/timeline.json --sortie renders/<ep>/<mode> --beats b1,b2
Fonctionne aussi avec le module Python 'bpy' (tests) : python construire_scene.py -- ...

Options :
    --beats        beats à rendre (séparés par des virgules ; vide = aucun rendu)
    --sans-rendu   construit et enregistre la scène sans rendre (pour l'inspecter dans Blender)
    --moteur       force un moteur (BLENDER_EEVEE, CYCLES, BLENDER_WORKBENCH)

La scène construite est toujours enregistrée dans <sortie>/scene.blend : Guillaume peut
l'ouvrir pour inspecter ou retoucher un plan.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
if str(ICI) not in sys.path:
    sys.path.insert(0, str(ICI))

import bpy  # noqa: E402

import look  # noqa: E402
import rendu  # noqa: E402
from animateur import Animateur  # noqa: E402
from camera import Cameraman  # noqa: E402
from commun import journal  # noqa: E402
from decorateur import Decorateur  # noqa: E402

RACINE_DEPOT = ICI.parents[1]  # engine/blender -> racine du dépôt


def arguments() -> argparse.Namespace:
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser(prog="construire_scene")
    p.add_argument("--timeline", required=True)
    p.add_argument("--sortie", required=True)
    p.add_argument("--beats", default="")
    p.add_argument("--sans-rendu", action="store_true")
    p.add_argument("--moteur")
    return p.parse_args(argv)


def scene_vierge() -> bpy.types.Scene:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "PRODUCTION"
    return scene


def construire(timeline: dict, sortie: Path, moteur_force: str | None = None) -> bpy.types.Scene:
    scene = scene_vierge()
    pack = timeline["pack_da"]
    look.monde_et_lumiere(scene, pack)
    look.moteur(scene, pack, timeline["mode"], forcer=moteur_force)
    decorateur = Decorateur(scene, timeline, RACINE_DEPOT)
    decorateur.construire()
    look.adapter_contours(scene.render.engine)
    Animateur(scene, timeline, decorateur).appliquer()
    Cameraman(scene, timeline).appliquer()
    rendu.regler(scene, timeline, sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(sortie / "scene.blend"), compress=True)
    journal(f"scène enregistrée : {sortie / 'scene.blend'}")
    return scene


def main() -> None:
    args = arguments()
    timeline = json.loads(Path(args.timeline).read_text(encoding="utf-8"))
    sortie = Path(args.sortie)
    scene = construire(timeline, sortie, args.moteur)
    beats = [b for b in args.beats.split(",") if b]
    if args.sans_rendu or not beats:
        journal("construction seule, aucun rendu demandé")
        return
    durees = rendu.rendre(scene, timeline, beats)
    (sortie / "durees_rendu.json").write_text(json.dumps(durees, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
