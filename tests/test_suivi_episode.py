"""Tests du schéma episodes/suivi/suivi.schema.json (fichier de suivi de /episode)."""

import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

RACINE = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((RACINE / "episodes" / "suivi" / "suivi.schema.json").read_text(encoding="utf-8"))
VALIDATEUR = Draft202012Validator(SCHEMA)

ATTENTE = {"statut": "en_attente", "par": None, "date": None, "reponse": None}

SUIVI = {
    "id": "essai",
    "titre": None,
    "demande_initiale": "une vidéo où un phare s'allume",
    "branche": "episode/essai",
    "etape_courante": "idee",
    "fichiers": {k: None for k in ("idee", "scenario", "beats", "decoupage", "fiche", "animatique", "video")},
    "arrets": {f"arret_{i}": dict(ATTENTE) for i in range(1, 6)},
    "machine_requise": "n'importe laquelle",
    "blocage": None,
    "historique": [{"date": "2026-11-16T11:00:00+01:00", "etape": "idee", "evenement": "épisode créé"}],
}


def _erreurs(suivi):
    return list(VALIDATEUR.iter_errors(suivi))


def test_schema_valide():
    Draft202012Validator.check_schema(SCHEMA)


def test_suivi_minimal_valide():
    assert _erreurs(SUIVI) == []


def test_arret_valide_avec_reponse():
    s = copy.deepcopy(SUIVI)
    s["arrets"]["arret_1"] = {"statut": "valide", "par": "Lucas", "date": "2026-11-16", "reponse": "idée 2"}
    s["etape_courante"] = "scenario"
    assert _erreurs(s) == []


@pytest.mark.parametrize("modif", [
    lambda s: s["arrets"]["arret_1"].update(statut="valide"),            # validé sans réponse ni auteur
    lambda s: s["arrets"]["arret_2"].update(statut="ok"),                # statut hors liste
    lambda s: s.update(etape_courante="publication"),                    # étape inconnue
    lambda s: s.update(branche="main"),                                  # jamais main
    lambda s: s.update(machine_requise="cloud"),                         # machine hors liste
    lambda s: s["arrets"].pop("arret_5"),                                # un arrêt manquant
    lambda s: s.update(historique=[]),                                   # historique vide
    lambda s: s.update(blocage={"raison": "code 3"}),                    # blocage incomplet
])
def test_suivi_refuse(modif):
    s = copy.deepcopy(SUIVI)
    modif(s)
    assert _erreurs(s)


def test_suivi_factice_essai_orchestrateur_valide():
    """Suivi factice de l'essai du passage de machine (2026-11-16), avant l'arrêt faute de Blender."""
    chemin = RACINE / "tests" / "fixtures" / "suivi" / "essai-orchestrateur.json"
    assert _erreurs(json.loads(chemin.read_text(encoding="utf-8"))) == []


PLAQUETTE_VALIDEE = {
    "lien": "https://www.figma.com/design/4jgvjoxBzwQDQfoXgwW0Fs",
    "statut": "valide",
    "par": "Guillaume",
    "date": "2026-11-16T15:00:00+01:00",
    "reponse": "validé",
}


def test_plaquette_en_attente_valide():
    s = copy.deepcopy(SUIVI)
    s["etape_courante"] = "plaquette"
    s["plaquette"] = {"lien": None, "statut": "en_attente", "par": None, "date": None, "reponse": None}
    assert _erreurs(s) == []


def test_plaquette_validee_par_guillaume():
    s = copy.deepcopy(SUIVI)
    s["etape_courante"] = "animatique"
    s["plaquette"] = dict(PLAQUETTE_VALIDEE)
    assert _erreurs(s) == []


@pytest.mark.parametrize("modif", [
    {"par": "Lucas"},                      # seul Guillaume valide la plaquette
    {"par": "Lucas et Guillaume"},         # accord rapporté ou commun : refusé
    {"reponse": None},                     # validé sans réponse mot pour mot
    {"lien": None},                        # validé sans plaquette créée
    {"statut": "ok"},                      # statut hors liste
])
def test_plaquette_refusee(modif):
    s = copy.deepcopy(SUIVI)
    s["plaquette"] = {**PLAQUETTE_VALIDEE, **modif}
    assert _erreurs(s)


AUDIENCE_RECUE = {
    "premier_episode": False,
    "statut": "recu",
    "par": "Lucas",
    "date": "2026-11-18T09:00:00+01:00",
    "reponse": "12 abonnés, 40 likes, choix gagnant : les filets",
    "mise_a_jour_etat": {"statut": "acceptee", "par": "Lucas", "date": "2026-11-18T09:05:00+01:00", "reponse": "ok"},
}

FILTRE = {
    "commentaires_transmis": ["Construisez des filets !"],
    "pseudos_transmis": ["@kevin_75"],
    "refuses": ["commentaire 2 : mot refusé (liste de modération : « connard »)"],
    "pseudos_a_valider": ["@kevin_75"],
}

PREMIER_EPISODE = {
    "premier_episode": True,
    "statut": "sans_objet",
    "par": None,
    "date": None,
    "reponse": None,
    "mise_a_jour_etat": {"statut": "sans_objet", "par": None, "date": None, "reponse": None},
}


@pytest.mark.parametrize("audience", [
    PREMIER_EPISODE,
    AUDIENCE_RECUE,
    {**AUDIENCE_RECUE, "mise_a_jour_etat": {"statut": "en_attente", "par": None, "date": None, "reponse": None}},
    {**AUDIENCE_RECUE, "statut": "en_attente", "par": None, "date": None, "reponse": None,
     "mise_a_jour_etat": {"statut": "en_attente", "par": None, "date": None, "reponse": None}},
    {**AUDIENCE_RECUE, "filtre": FILTRE},
])
def test_audience_valide(audience):
    s = copy.deepcopy(SUIVI)
    s["etape_courante"] = "audience"
    s["audience"] = copy.deepcopy(audience)
    assert _erreurs(s) == []


@pytest.mark.parametrize("modif", [
    {"reponse": None},                                       # reçu sans les chiffres mot pour mot
    {"par": "agent"},                                        # chiffres donnés par un agent
    {"par": "Instagram"},                                    # aucun accès automatique
    {"statut": "sans_objet"},                                # sans objet hors premier épisode
    {"premier_episode": True},                               # premier épisode : on ne demande rien
    {"mise_a_jour_etat": {"statut": "acceptee", "par": None, "date": None, "reponse": None}},   # accord sans réponse
    {"mise_a_jour_etat": {"statut": "acceptee", "par": "story-chef", "date": "2026-11-18", "reponse": "ok"}},
    {"filtre": {k: v for k, v in FILTRE.items() if k != "refuses"}},              # trace incomplète
    {"filtre": {**FILTRE, "pseudos_transmis": ["kevin_75"]}},                     # pseudo sans @
    {"filtre": {**FILTRE, "pseudos_a_valider": ["@kévin 75"]}},                   # hors format Instagram
])
def test_audience_refusee(modif):
    s = copy.deepcopy(SUIVI)
    s["audience"] = {**copy.deepcopy(AUDIENCE_RECUE), **modif}
    assert _erreurs(s)
