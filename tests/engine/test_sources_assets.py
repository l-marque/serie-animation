"""Tests de engine/pipeline/sources_assets.py avec des réponses d'API simulées (aucun appel réseau)."""

from __future__ import annotations

import csv
import json

import pytest

from engine.pipeline import chemins, sources_assets as sa

POLYHAVEN_ASSETS = {
    "lighthouse_01": {"name": "Lighthouse", "tags": ["coast", "tower"], "categories": ["buildings"],
                      "authors": {"Jane Doe": "All"}, "download_count": 50, "polycount": 12000,
                      "thumbnail_url": "https://cdn/x.png"},
    "rock_02": {"name": "Rock", "tags": ["stone"], "categories": ["nature"], "authors": {}, "download_count": 900},
}
POLYHAVEN_FILES = {"gltf": {"1k": {"gltf": {"url": "https://dl/lighthouse_01_1k.gltf", "include": {
    "textures/lighthouse_diff_1k.jpg": {"url": "https://dl/diff.jpg"}}}}},
    "hdri": {"2k": {"hdr": {"url": "https://dl/sky_2k.hdr"}}}}


@pytest.fixture
def depot_temporaire(tmp_path, monkeypatch):
    registre = tmp_path / "registre.json"
    registre.write_text('{"assets": {}}', encoding="utf-8")
    licences = tmp_path / "licences.csv"
    licences.write_text("id,source,auteur,licence,url,date_ajout,attribution_requise,texte_attribution\n",
                        encoding="utf-8")
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    monkeypatch.setattr(chemins, "REGISTRE_ASSETS", registre)
    monkeypatch.setattr(chemins, "LICENCES_ASSETS", licences)
    monkeypatch.setattr(sa, "DOSSIER_MODELES", tmp_path / "engine" / "assets" / "modeles")
    monkeypatch.setattr(sa, "DOSSIER_HDRI", tmp_path / "engine" / "assets" / "hdri")
    telecharges = []

    def faux_telecharger(url, destination, entetes=None):
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"x")
        telecharges.append(url)
        return destination

    monkeypatch.setattr(sa, "_telecharger", faux_telecharger)
    return tmp_path, registre, licences, telecharges


def _faux_json(reponses):
    def f(url, entetes=None):
        for debut, rep in reponses.items():
            if url.startswith(debut):
                return rep
        raise AssertionError(f"appel inattendu : {url}")
    return f


def test_recherche_polyhaven_classe_par_pertinence(monkeypatch):
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.polyhaven.com/assets": POLYHAVEN_ASSETS}))
    res = sa.chercher_polyhaven("coast lighthouse")
    assert [c.id_source for c in res] == ["lighthouse_01"]
    assert res[0].licence_ok and not res[0].attribution_requise and res[0].auteur == "Jane Doe"


def test_sketchfab_ecarte_les_licences_non_commerciales(monkeypatch):
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.sketchfab.com/v3/search": {"results": [
        {"uid": "a", "name": "ok", "license": {"slug": "cc-by"}, "user": {"displayName": "Bob"}},
        {"uid": "b", "name": "nc", "license": {"slug": "by-nc"}},
        {"uid": "c", "name": "nd", "license": {"slug": "by-nd"}},
        {"uid": "d", "name": "inconnue"}]}}))
    res = sa.chercher_sketchfab("tree")
    assert [c.id_source for c in res] == ["a"]
    assert res[0].attribution_requise


def test_polypizza_sans_cle_donne_une_erreur_actionnable(monkeypatch, tmp_path):
    monkeypatch.delenv("POLY_PIZZA_KEY", raising=False)
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    with pytest.raises(sa.SourceErreur, match="POLY_PIZZA_KEY"):
        sa.chercher_polypizza("tree")


def test_chercher_agrege_et_rapporte_les_erreurs(monkeypatch, tmp_path):
    monkeypatch.delenv("POLY_PIZZA_KEY", raising=False)
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.polyhaven.com/assets": POLYHAVEN_ASSETS}))
    res = sa.chercher("rock", ["polyhaven", "polypizza"])
    assert [c["id_source"] for c in res["candidats"]] == ["rock_02"]
    assert "polypizza" in res["erreurs"]


def test_integrer_polyhaven_ecrit_registre_et_licences(monkeypatch, depot_temporaire):
    racine, registre, licences, telecharges = depot_temporaire
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.polyhaven.com/files/": POLYHAVEN_FILES,
                                                     "https://api.polyhaven.com/info/": {"authors": {"Jane Doe": "All"}}}))
    sortie = sa.integrer("polyhaven", "lighthouse_01", "phare_01", role_defaut="batiment", materiaux="origine")
    assert sortie["fichier"] == "engine/assets/modeles/phare_01/lighthouse_01_1k.gltf"
    assert (racine / "engine/assets/modeles/phare_01/textures/lighthouse_diff_1k.jpg").is_file()
    assert len(telecharges) == 2
    entree = json.loads(registre.read_text(encoding="utf-8"))["assets"]["phare_01"]
    assert entree["materiaux"] == "origine" and entree["echelle_verifiee"] is False
    lignes = list(csv.reader(licences.open(encoding="utf-8")))
    assert lignes[-1][:4] == ["phare_01", "polyhaven", "Jane Doe", "CC0"]
    with pytest.raises(sa.SourceErreur, match="existe déjà"):
        sa.integrer("polyhaven", "lighthouse_01", "phare_01")


def test_integrer_refuse_une_licence_non_acceptee(depot_temporaire, monkeypatch):
    _, registre, _, _ = depot_temporaire
    monkeypatch.setattr(sa, "url_glb_sketchfab", lambda uid: "https://dl/m.glb")
    c = sa.Candidat("sketchfab", "u1", "Arbre", "Bob", "by-nc", "https://sketchfab.com/m/u1")
    with pytest.raises(sa.SourceErreur, match="licence refusée"):
        sa.integrer("sketchfab", "u1", "arbre_01", candidat=c)
    assert json.loads(registre.read_text(encoding="utf-8"))["assets"] == {}


def test_hdri_polyhaven(monkeypatch, depot_temporaire):
    racine, *_ = depot_temporaire
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.polyhaven.com/files/": POLYHAVEN_FILES}))
    chemin = sa.telecharger_hdri_polyhaven("sky", "2k")
    assert chemin == racine / "engine/assets/hdri/sky_2k.hdr"
    with pytest.raises(sa.SourceErreur, match="4k"):
        sa.telecharger_hdri_polyhaven("sky", "4k")


def test_cli_chercher_code_1_si_aucune_source_ne_repond(monkeypatch, tmp_path, capsys):
    monkeypatch.delenv("POLY_PIZZA_KEY", raising=False)
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    assert sa.main(["chercher", "lighthouse", "--sources", "polypizza"]) == 1
    assert "POLY_PIZZA_KEY" in capsys.readouterr().out


def test_3dtexel_ne_garde_que_le_cc0_gratuit(monkeypatch):
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://3dtexel.com/wp-json/3dtexel-api/v1/assets/search": {"items": [
        {"id": 1, "title": "Carrelage", "type": "pbr", "source": "handmade", "license": "CC0 1.0 (public domain)",
         "price": {"credits": 0, "free": True}, "url": "https://3dtexel.com/p/1"},
        {"id": 2, "title": "Carrelage IA", "type": "ai-pbr", "source": "ai", "license": "3DTexel License",
         "price": {"credits": 10, "free": False}},
        {"id": 3, "title": "Rocher premium", "type": "premium-3d", "source": "premium", "license": "3DTexel License",
         "price": {"credits": None, "free": True}}]}}))
    res = sa.chercher_3dtexel("tile")
    assert [c.id_source for c in res] == ["1"] and res[0].licence_ok


def test_3dtexel_telechargement_sans_cle(monkeypatch, tmp_path):
    monkeypatch.delenv("TEXEL_API_KEY", raising=False)
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    with pytest.raises(sa.SourceErreur, match="TEXEL_API_KEY"):
        sa.telecharger_3dtexel("1", tmp_path)


def test_texture_polyhaven(monkeypatch, depot_temporaire):
    racine, *_ = depot_temporaire
    monkeypatch.setattr(sa, "DOSSIER_TEXTURES", racine / "engine" / "assets" / "textures")
    monkeypatch.setattr(sa, "_get_json", _faux_json({"https://api.polyhaven.com/files/": {
        "Diffuse": {"1k": {"jpg": {"url": "https://dl/d.jpg"}}}, "nor_gl": {"1k": {"jpg": {"url": "https://dl/n.jpg"}}},
        "Rough": {"1k": {"jpg": {"url": "https://dl/r.jpg"}}}}}))
    dossier = sa.telecharger_texture_polyhaven("white_tiles")
    import json as _json
    cartes = _json.loads((dossier / "cartes.json").read_text(encoding="utf-8"))
    assert set(cartes) == {"couleur", "normale", "rugosite"}
