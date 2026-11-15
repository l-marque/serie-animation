"""Tests d'intégration Blender (nécessitent le module bpy : pip install bpy==5.3.*). Ignorés sinon."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from scripts.production import chemins, contrat, realisateur

bpy = pytest.importorskip("bpy")

EXEMPLE = chemins.RACINE / "episodes" / "exemples" / "demo_001.json"


@pytest.fixture(scope="module")
def scene_construite(tmp_path_factory):
    dossier = tmp_path_factory.mktemp("scene")
    t = realisateur.construire_timeline(contrat.charger(EXEMPLE))
    (dossier / "timeline.json").write_text(json.dumps(t), encoding="utf-8")
    res = subprocess.run([sys.executable, str(chemins.SCRIPT_CONSTRUCTION), "--", "--timeline",
                          str(dossier / "timeline.json"), "--sortie", str(dossier), "--sans-rendu"],
                         capture_output=True, text=True, timeout=300)
    assert res.returncode == 0, res.stdout[-2000:] + res.stderr[-2000:]
    return dossier, t


def _valeurs(dossier, objets_frames):
    """Lit des valeurs animées dans la scène enregistrée, dans un processus séparé."""
    code = f"""
import bpy, json
bpy.ops.wm.open_mainfile(filepath={str(dossier / 'scene.blend')!r})
s = bpy.context.scene
sortie = {{}}
for nom, attr, frames in {objets_frames!r}:
    o = s.objects[nom]
    for f in frames:
        s.frame_set(f)
        v = getattr(o, attr)
        sortie[f"{{nom}}.{{attr}}@{{f}}"] = list(v) if hasattr(v, "__len__") else v
s.frame_set(1); sortie["camera@1"] = s.camera.name
s.frame_set(200); sortie["camera@200"] = s.camera.name
print("VALEURS" + json.dumps(sortie))
"""
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    ligne = next(l for l in res.stdout.splitlines() if l.startswith("VALEURS"))
    return json.loads(ligne[len("VALEURS"):])


def test_scene_et_animation(scene_construite):
    dossier, t = scene_construite
    b2 = t["beats"][1]
    pop = b2["actions"][0]
    v = _valeurs(dossier, [
        ("EP_phare", "scale", [1, pop["frame_debut"] - 1, pop["frame_fin"] + 5]),
        ("EP_heros", "location", [1, t["nb_frames"]]),
    ])
    assert v["EP_phare.scale@1"][0] == pytest.approx(0)
    assert v[f"EP_phare.scale@{pop['frame_debut'] - 1}"][0] == pytest.approx(0)
    assert v[f"EP_phare.scale@{pop['frame_fin'] + 5}"][0] == pytest.approx(1.4, abs=0.01)
    assert v[f"EP_heros.location@{t['nb_frames']}"][:2] == pytest.approx([-2, -3], abs=0.01)
    assert v["camera@1"] == "CAM_b1"
    assert v["camera@200"] == "CAM_b3"
