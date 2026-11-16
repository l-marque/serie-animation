"""Tests du schéma episodes/serie/etat.schema.json (état de la série, bible § 4)."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

RACINE = Path(__file__).resolve().parents[1]
DOSSIER = RACINE / "episodes" / "serie"
SCHEMA = json.loads((DOSSIER / "etat.schema.json").read_text(encoding="utf-8"))
VALIDATEUR = Draft202012Validator(SCHEMA)

# État fictif après quelques épisodes (aucun vrai pseudo).
ETAT_REMPLI = {
    "abonnes": 120,
    "cagnotte_euros": 340,
    "joueurs": [{"pseudo": "joueur_essai", "role": "gardien", "depuis_episode": "episode-2"}],
    "supporters": 120,
    "ameliorations": [{"episode": "episode-1", "nom": "filets neufs", "cout": 50}],
    "choix_en_cours": [
        {"libelle": "PROJECTEURS", "cout": 300, "commentaire_origine": "mettez des projecteurs"},
        {"libelle": "BUVETTE", "cout": 200, "commentaire_origine": "une buvette !"},
    ],
    "mise_a_jour": {"date": "2026-11-18", "par": "Lucas", "episode": "episode-2"},
}


def _erreurs(etat):
    return list(VALIDATEUR.iter_errors(etat))


def test_schema_valide():
    Draft202012Validator.check_schema(SCHEMA)


def test_etat_initial_tout_a_zero():
    etat = json.loads((DOSSIER / "etat.json").read_text(encoding="utf-8"))
    assert _erreurs(etat) == []
    assert etat["abonnes"] == etat["cagnotte_euros"] == etat["supporters"] == 0
    assert etat["joueurs"] == etat["ameliorations"] == etat["choix_en_cours"] == []
    assert etat["mise_a_jour"] is None


def test_etat_rempli_valide():
    assert _erreurs(ETAT_REMPLI) == []


@pytest.mark.parametrize("modif", [
    lambda e: e.update(abonnes=-1),                                     # négatif
    lambda e: e.update(cagnotte_euros=12.5),                            # euros entiers
    lambda e: e.pop("supporters"),                                      # champ manquant
    lambda e: e.update(likes=10),                                       # champ inconnu
    lambda e: e["joueurs"][0].pop("depuis_episode"),                    # joueur incomplet
    lambda e: e["joueurs"][0].update(pseudo=""),                        # pseudo vide
    lambda e: e["ameliorations"][0].update(cout=-5),                    # coût négatif
    lambda e: e["choix_en_cours"].append(dict(e["choix_en_cours"][0])), # plus de 2 choix
    lambda e: e["choix_en_cours"][0].pop("commentaire_origine"),        # choix sans commentaire
    lambda e: e["mise_a_jour"].update(par="agent"),                     # chiffres donnés par un agent
    lambda e: e["mise_a_jour"].update(par="Instagram"),                 # aucun accès automatique
])
def test_etat_refuse(modif):
    e = copy.deepcopy(ETAT_REMPLI)
    modif(e)
    assert _erreurs(e)
