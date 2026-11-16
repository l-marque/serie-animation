"""Modération des textes affichés ou lus (engine/pipeline/textes_ecran.py)."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

from engine.pipeline import chemins, textes_ecran


@pytest.mark.parametrize("texte", [
    "CONNARDS", "Va te faire f.u.c.k", "fuuuuck", "PUT41N", "sh1t", "Bravo @nazi_du_75",
    "@marie.connasse", "@kevin_fuuck",
])
def test_mots_refuses(texte):
    assert not textes_ecran.verifier_texte("t", texte).ok


@pytest.mark.parametrize("texte", [
    "Un retard de cinq minutes", "Le stade est unique", "Un sentier pédestre",
    "Merci à tous, mille pièces !", "Kevin rénove le stade", "Conseil municipal",
])
def test_pas_de_faux_positif_courant(texte):
    assert textes_ecran.verifier_texte("t", texte).ok


def test_lien_et_caractere_invisible_refuses():
    assert not textes_ecran.verifier_texte("t", "go sur www.site.com").ok
    assert not textes_ecran.verifier_texte("t", "abonne-toi sur monsite.fr").ok
    assert not textes_ecran.verifier_texte("t", "co​nnard").ok
    assert not textes_ecran.verifier_texte("t", "Kevin‮gagne").ok


def test_pseudo_liste_pour_validation_humaine():
    r = textes_ecran.verifier_texte("beat b1 / voix", "Bravo @kevin_75 pour ton idée")
    assert r.ok and r.pseudos == [{"origine": "beat b1 / voix", "pseudo": "@kevin_75"}]


def test_exception_autorisee_par_un_humain(tmp_path):
    mots = tmp_path / "mots.txt"
    mots.write_text("cunt*\n", encoding="utf-8")
    exc = tmp_path / "exc.txt"
    assert not textes_ecran.verifier_texte("t", "@scunthorpe_fan", textes_ecran.charger_liste(mots, exc)).ok
    exc.write_text("# relu par Guillaume\nscunthorpe_fan\n", encoding="utf-8")
    assert textes_ecran.verifier_texte("t", "@scunthorpe_fan", textes_ecran.charger_liste(mots, exc)).ok


def test_textes_episode_couvre_voix_habillage_et_hud():
    fiche = {"titre": "T", "beats": [{"id": "b1", "voix": "V", "texte_ecran": "E"}]}
    hab = {"textes_3d": [{"id": "panneau", "texte": "P"}], "hud": [{"id": "g", "texte": "+10"}]}
    origines = [o for o, _ in textes_ecran.textes_episode(fiche, hab)]
    assert origines == ["titre", "beat b1 / voix", "beat b1 / texte_ecran", "texte 3D panneau", "hud g / texte"]


def test_pipeline_refuse_un_texte_avec_code_8(tmp_path):
    fiche = json.loads((chemins.RACINE / "episodes/exemples/demo_001.json").read_text(encoding="utf-8"))
    fiche["beats"][0]["voix"] = "Merci à @kevin_fuuck pour son idée"
    chemin = tmp_path / "f.json"
    chemin.write_text(json.dumps(fiche), encoding="utf-8")
    res = subprocess.run([sys.executable, "-m", "engine.pipeline.run", str(chemin), "--valider-seulement",
                          "--sortie", str(tmp_path / "sortie")],
                         cwd=chemins.RACINE, capture_output=True, text=True)
    synthese = json.loads(res.stdout.strip().splitlines()[-1].removeprefix("SYNTHESE "))
    assert res.returncode == 8 and synthese["suite"] == "humain" and synthese["etape_bloquante"] == "textes"
