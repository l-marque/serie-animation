"""Tests d'intégration Blender (nécessitent le module bpy : pip install bpy==5.3.*). Ignorés sinon."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from engine.pipeline import chemins, contrat, realisateur

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


def test_materiaux_origine_et_hdri_absente():
    """Un asset texturé garde ses matériaux si le registre dit "origine" ; une HDRI manquante ne casse rien."""
    sys.path.insert(0, str(chemins.SCRIPTS_BLENDER))
    import look  # noqa: E402

    pack = json.loads((chemins.PACKS_DA / "test_lowpoly.json").read_text(encoding="utf-8"))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    maillage = bpy.data.meshes.new("m")
    obj = bpy.data.objects.new("asset", maillage)
    origine = bpy.data.materials.new("Texture_origine")
    maillage.materials.append(origine)
    look.appliquer_role(obj, "batiment", pack, garder_materiaux=True)
    assert maillage.materials[0] is origine
    look.appliquer_role(obj, "batiment", pack)
    assert maillage.materials[0] is not origine
    pack["monde"]["hdri"] = "engine/assets/hdri/inexistante.hdr"
    look.monde_et_lumiere(bpy.context.scene, pack)
    assert bpy.context.scene.world is not None


def test_hdri_branchee_sur_le_monde(tmp_path):
    sys.path.insert(0, str(chemins.SCRIPTS_BLENDER))
    import look  # noqa: E402

    img = bpy.data.images.new("ciel", 8, 4, float_buffer=True)
    img.filepath_raw = str(tmp_path / "ciel.hdr")
    img.file_format = "HDR"
    img.save()
    pack = json.loads((chemins.PACKS_DA / "test_lowpoly.json").read_text(encoding="utf-8"))
    pack["monde"]["hdri"] = str(tmp_path / "ciel.hdr")  # un chemin absolu est accepté
    look.monde_et_lumiere(bpy.context.scene, pack)
    noeuds = bpy.context.scene.world.node_tree.nodes
    tex = next(n for n in noeuds if n.type == "TEX_ENVIRONMENT")
    assert tex.outputs["Color"].is_linked


def test_materiau_pbr_branche_les_textures(tmp_path):
    sys.path.insert(0, str(chemins.SCRIPTS_BLENDER))
    import look  # noqa: E402

    for nom in ("c.png", "n.png", "r.png"):
        img = bpy.data.images.new(nom, 4, 4)
        img.filepath_raw = str(tmp_path / nom)
        img.file_format = "PNG"
        img.save()
    (tmp_path / "cartes.json").write_text(json.dumps({"couleur": "c.png", "normale": "n.png", "rugosite": "r.png"}),
                                          encoding="utf-8")
    pack = json.loads((chemins.PACKS_DA / "test_lowpoly.json").read_text(encoding="utf-8"))
    pack["materiaux"]["carrelage"] = dict(pack["materiaux"]["sol"], textures=str(tmp_path))  # chemin absolu accepté
    mat = look.materiau_role(pack, "carrelage")
    types = {n.type for n in mat.node_tree.nodes}
    assert {"TEX_IMAGE", "NORMAL_MAP", "MAPPING"} <= types
