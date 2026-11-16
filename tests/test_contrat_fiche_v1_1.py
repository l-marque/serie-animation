"""Tests du schéma contracts/fiche-episode.schema.json, version 1.1.

On teste le schéma seul (structure), sans passer par engine/pipeline/contrat.py :
la prise en charge de la v1.1 par le moteur revient à la production.
"""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

RACINE = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((RACINE / "contracts" / "fiche-episode.schema.json").read_text(encoding="utf-8"))
VALIDATEUR = Draft202012Validator(SCHEMA)

# Fiches 1.0 déjà présentes dans le dépôt : elles doivent rester valides sans changement
FICHES_1_0 = [
    "episodes/exemples/demo_001.json",
    "episodes/pilote/canard_001.json",
    "episodes/tests/pip_001.json",
    "episodes/tests/six_seven_001.json",
]

HABILLAGE = {
    "textes_3d": [
        {"id": "nom_ville", "texte": "SIX SEVEN", "parent": "panneau",
         "position": [0, -0.06, 1.85], "taille": 0.3, "role": "accent"},
        {"id": "legende_a", "texte": "FONTAINE", "parent": "carte_a", "visible_au_debut": False},
    ]
}


def _erreurs(fiche):
    return list(VALIDATEUR.iter_errors(fiche))


def _fiche_min(version):
    return {
        "version": version,
        "episode_id": "essai",
        "elements": [
            {"id": "panneau", "asset": "primitif:panneau_entree"},
            {"id": "carte_a", "asset": "primitif:carte_choix"},
        ],
        "beats": [{"id": "b1", "voix": "Bienvenue chez toi, dans ce village.",
                   "plan": {"camera": "plan_fixe", "cible": "panneau"}}],
    }


def test_schema_valide():
    Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("chemin", FICHES_1_0)
def test_fiche_1_0_existante_reste_valide(chemin):
    fiche = json.loads((RACINE / chemin).read_text(encoding="utf-8"))
    assert fiche["version"] == "1.0"
    assert _erreurs(fiche) == []


def test_fiche_1_1_avec_habillage_et_descente_valide():
    fiche = _fiche_min("1.1")
    fiche["habillage"] = copy.deepcopy(HABILLAGE)
    fiche["beats"][0]["plan"] = {"camera": "descente", "cible": "panneau", "distance": 8, "hauteur": 60}
    assert _erreurs(fiche) == []


def test_fiche_1_1_sans_nouveaute_valide():
    assert _erreurs(_fiche_min("1.1")) == []


def test_habillage_refuse_en_1_0():
    fiche = _fiche_min("1.0")
    fiche["habillage"] = copy.deepcopy(HABILLAGE)
    assert _erreurs(fiche)


def test_descente_refusee_en_1_0():
    fiche = _fiche_min("1.0")
    fiche["beats"][0]["plan"]["camera"] = "descente"
    assert _erreurs(fiche)


def test_version_inconnue_refusee():
    assert _erreurs(_fiche_min("1.2"))


@pytest.mark.parametrize("texte", [
    {"id": "t1"},                                         # texte manquant
    {"id": "t1", "texte": ""},                            # texte vide
    {"id": "t1", "texte": "X" * 41},                      # plus de 40 caractères
    {"id": "T1", "texte": "X"},                           # id hors motif
    {"id": "t1", "texte": "X", "role": "inconnu"},        # rôle hors liste
    {"id": "t1", "texte": "X", "position": [0, 0]},       # position à 2 coordonnées
    {"id": "t1", "texte": "X", "couleur": "rouge"},       # propriété inconnue
])
def test_contraintes_des_textes_3d(texte):
    fiche = _fiche_min("1.1")
    fiche["habillage"] = {"textes_3d": [texte]}
    assert _erreurs(fiche)


def test_habillage_identique_au_schema_engine():
    """Le champ du contrat reprend exactement engine/schemas/habillage.schema.json."""
    engine = json.loads((RACINE / "engine" / "schemas" / "habillage.schema.json").read_text(encoding="utf-8"))
    assert SCHEMA["properties"]["habillage"]["properties"]["textes_3d"] == engine["properties"]["textes_3d"]
