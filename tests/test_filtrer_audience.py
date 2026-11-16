"""Filtre d'entrée des commentaires et pseudos de l'audience (scripts/filtrer_audience.py)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts import filtrer_audience

RACINE = Path(__file__).resolve().parents[1]


def test_texte_refuse_jamais_dans_les_acceptes():
    r = filtrer_audience.filtrer(["Construisez une fontaine !", "vous êtes des connards"], ["kevin_75", "@kevin_fuuck"])
    assert r["commentaires_transmis"] == ["Construisez une fontaine !"]
    assert r["pseudos_transmis"] == ["@kevin_75"]
    assert [m.split(" : ")[0] for m in r["refuses"]] == ["commentaire 2", "pseudo 2"]
    # Le motif d'un commentaire cite l'origine et l'entrée de la liste, pas le texte de l'abonné.
    assert "connards" not in r["refuses"][0]


def test_pseudos_acceptes_restent_a_valider():
    r = filtrer_audience.filtrer(["Bravo @marie.b pour l'idée"], ["@kevin_75", "kevin_75"])
    assert r["pseudos_a_valider"] == ["@marie.b", "@kevin_75"]


def test_pseudo_au_format_invalide_refuse():
    r = filtrer_audience.filtrer([], ["kévin 75", "a" * 31, "kevin​75"])
    assert r["pseudos_transmis"] == [] and len(r["refuses"]) == 3


def test_lien_dans_un_commentaire_refuse():
    r = filtrer_audience.filtrer(["allez voir monsite.fr"], [])
    assert r["commentaires_transmis"] == [] and r["refuses"]


def test_sortie_conforme_au_suivi():
    import jsonschema
    schema = json.loads((RACINE / "episodes/suivi/suivi.schema.json").read_text(encoding="utf-8"))
    filtre = schema["properties"]["audience"]["properties"]["filtre"]
    r = filtrer_audience.filtrer(["Une fontaine @marie.b", "connard"], ["kevin_75", "kévin"])
    jsonschema.validate(r, filtre)


def _lancer(tmp_path, donnees) -> subprocess.CompletedProcess:
    entree = tmp_path / "audience.json"
    entree.write_text(donnees if isinstance(donnees, str) else json.dumps(donnees), encoding="utf-8")
    return subprocess.run([sys.executable, "scripts/filtrer_audience.py", str(entree)],
                          cwd=RACINE, capture_output=True, text=True, encoding="utf-8")


def test_ligne_de_commande_codes_retour(tmp_path):
    ok = _lancer(tmp_path, {"commentaires": ["Une fontaine !"], "pseudos": ["kevin_75"]})
    assert ok.returncode == 0 and json.loads(ok.stdout)["pseudos_a_valider"] == ["@kevin_75"]
    refus = _lancer(tmp_path, {"commentaires": ["PUT41N"], "pseudos": []})
    assert refus.returncode == 8 and json.loads(refus.stdout)["refuses"]
    assert _lancer(tmp_path, {"commentaires": "pas une liste"}).returncode == 2
    assert _lancer(tmp_path, "{json cassé").returncode == 2
