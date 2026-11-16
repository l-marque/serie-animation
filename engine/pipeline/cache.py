"""Cache de rendu : ne re-rendre que les beats dont l'image peut avoir changé.

L'empreinte d'un beat combine :
- tout ce qui définit la scène (décor, objets, modules, pack de DA, format, mode) ;
- toutes les actions de l'épisode (elles déterminent les courbes d'animation, donc
  l'état de la scène dans n'importe quel beat) ;
- l'intervalle de frames et le plan caméra du beat ;
- une empreinte du code Blender (modifier le code invalide tout).

Ce qui n'entre PAS dans l'empreinte (et ne coûte donc aucun rendu) : texte de la voix
quand la durée ne change pas, texte à l'écran, sous-titres, musique. Ces éléments sont
ajoutés au montage, qui est toujours refait (quelques secondes).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import chemins

FICHIER_CACHE = "cache.json"


def _empreinte(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def empreinte_code_blender() -> str:
    h = hashlib.sha256()
    for f in sorted(chemins.SCRIPTS_BLENDER.rglob("*.py")):
        h.update(f.relative_to(chemins.SCRIPTS_BLENDER).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def empreintes_beats(timeline: dict[str, Any]) -> dict[str, str]:
    scene = {
        "decor": timeline["decor"],
        "objets": timeline["objets"],
        "modules": timeline["modules"],
        "textes_3d": timeline.get("textes_3d", []),
        "pack": timeline["pack_da"],
        "fps": timeline["fps"],
        "resolution": timeline["resolution"],
        "mode": timeline["mode"],
        "actions": [a for b in timeline["beats"] for a in b["actions"]],
        "code": empreinte_code_blender(),
    }
    base = _empreinte(scene)
    return {
        b["id"]: _empreinte({"scene": base, "frames": [b["frame_debut"], b["frame_fin"]], "plan": b["plan"]})
        for b in timeline["beats"]
    }


def beats_a_rendre(timeline: dict[str, Any], dossier: Path, forcer: bool = False) -> tuple[list[str], dict[str, str]]:
    """Renvoie (ids des beats à rendre, nouvelles empreintes)."""
    nouvelles = empreintes_beats(timeline)
    if forcer:
        return [b["id"] for b in timeline["beats"]], nouvelles
    fichier = dossier / FICHIER_CACHE
    anciennes = json.loads(fichier.read_text(encoding="utf-8")) if fichier.is_file() else {}
    frames = dossier / "frames"
    a_rendre = []
    for b in timeline["beats"]:
        complet = all((frames / f"f_{n:04d}.png").is_file() for n in range(b["frame_debut"], b["frame_fin"] + 1))
        if anciennes.get(b["id"]) != nouvelles[b["id"]] or not complet:
            a_rendre.append(b["id"])
    return a_rendre, nouvelles


def enregistrer(dossier: Path, empreintes: dict[str, str]) -> None:
    (dossier / FICHIER_CACHE).write_text(json.dumps(empreintes, indent=2), encoding="utf-8")
