"""Tests de scripts/recuperer_audience.py, sans réseau (API YouTube simulée)."""

import json

import pytest

from scripts import recuperer_audience as ra


def _commentaire(auteur, texte, likes=0, date="2026-11-17T10:00:00Z", video="v2"):
    return {
        "snippet": {"topLevelComment": {"snippet": {
            "authorDisplayName": auteur, "textOriginal": texte, "likeCount": likes, "publishedAt": date,
        }}}
    }


REPONSES = {
    "channels": {"items": [{
        "contentDetails": {"relatedPlaylists": {"uploads": "UU_test"}},
        "statistics": {"subscriberCount": "42", "hiddenSubscriberCount": False},
    }]},
    "playlistItems": {"items": [
        {"contentDetails": {"videoId": "v2", "videoPublishedAt": "2026-11-17T18:00:00Z"}},
        {"contentDetails": {"videoId": "v1", "videoPublishedAt": "2026-11-15T18:00:00Z"}},
    ]},
    "videos": {"items": [{
        "id": "v2", "snippet": {"title": "Jour 2", "publishedAt": "2026-11-17T18:00:00Z"},
        "statistics": {"viewCount": "500", "likeCount": "37", "commentCount": "4"},
    }]},
    "commentThreads": {"items": [
        _commentaire("@marie_75", "Pelouse !!", likes=5),
        _commentaire("@tom", "les FILETS", likes=12),
        _commentaire("@tom", "finalement pelouse", likes=1, date="2026-11-17T12:00:00Z"),
        _commentaire("@zoe", "pelouse ou filets je sais pas", likes=0),
    ]},
}


def appel_simule(ressource, params):
    return REPONSES[ressource]


def test_releve_complet():
    r = ra.faire_releve(appel_simule, "UC_test", ra.date(2026, 11, 16), ["pelouse", "filets"])
    assert r["abonnes"] == 42
    assert [v["id"] for v in r["videos"]] == ["v2"]  # v1 publiée avant --depuis
    assert r["likes_total"] == 37
    assert len(r["commentaires"]) == 4
    assert r["plus_likes"][0]["texte"] == "les FILETS"


def test_votes_un_par_auteur_dernier_commentaire_et_ambigus():
    commentaires = [ra.lire_commentaires(appel_simule, "v2")][0]
    v = ra.compter_votes(commentaires, ["pelouse", "filets"])
    # @tom a changé d'avis : seul son dernier commentaire compte ; @zoe cite les deux : ignoré.
    assert v["options"] == {"pelouse": 2, "filets": 0}
    assert v["gagnant"] == "pelouse"
    assert v["commentaires_ambigus"] == 1


def test_egalite_pas_de_gagnant():
    c = [{"auteur": "a", "texte": "pelouse", "date": "1", "likes": 0},
         {"auteur": "b", "texte": "filets", "date": "1", "likes": 0}]
    assert ra.compter_votes(c, ["pelouse", "filets"])["gagnant"] is None


def test_abonnes_masques():
    reponses = json.loads(json.dumps(REPONSES))
    reponses["channels"]["items"][0]["statistics"] = {"hiddenSubscriberCount": True}
    chaine = ra.lire_chaine(lambda res, p: reponses[res], "UC_test")
    assert chaine["abonnes"] is None


def test_entree_filtre_sans_doublon():
    c = [{"auteur": "@tom", "texte": "pelouse"}, {"auteur": "@tom", "texte": "pelouse"},
         {"auteur": "@zoe", "texte": "  "}]
    assert ra.entree_filtre(c) == {"commentaires": ["pelouse"], "pseudos": ["@tom", "@zoe"]}


def test_commentaires_desactives():
    def appel(res, p):
        raise ra.ErreurYouTube("commentThreads : HTTP 403 (The video has disabled comments.)")
    assert ra.lire_commentaires(appel, "v2") == []


def test_ligne_de_commande(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("YOUTUBE_CHANNEL_ID", "UC_test")
    sortie, filtre = tmp_path / "releve.json", tmp_path / "entree.json"
    code = ra.main(["--depuis", "2026-11-16", "--options", "pelouse", "filets",
                    "--sortie", str(sortie), "--entree-filtre", str(filtre)], appel=appel_simule)
    assert code == 0
    releve = json.loads(sortie.read_text(encoding="utf-8"))
    assert releve["votes"]["gagnant"] == "pelouse"
    assert set(json.loads(filtre.read_text(encoding="utf-8"))) == {"commentaires", "pseudos"}


@pytest.mark.parametrize("args, env", [
    (["--depuis", "hier"], {"YOUTUBE_CHANNEL_ID": "UC_test"}),
    ([], {}),
])
def test_configuration_invalide(args, env, monkeypatch):
    monkeypatch.delenv("YOUTUBE_CHANNEL_ID", raising=False)
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    assert ra.main(args, appel=appel_simule) == 2


def test_cle_absente(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    monkeypatch.setenv("YOUTUBE_CHANNEL_ID", "UC_test")
    assert ra.main([]) == 2


def test_erreur_api(monkeypatch):
    monkeypatch.setenv("YOUTUBE_CHANNEL_ID", "UC_test")
    def appel(res, p):
        raise ra.ErreurYouTube("channels : HTTP 400 (API key not valid)")
    assert ra.main([], appel=appel) == 3
