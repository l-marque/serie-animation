"""Tests des modules hors Blender (rapides, sans Blender ni ffmpeg obligatoires)."""

from __future__ import annotations

import copy
import json
import re
import shutil
from pathlib import Path

import pytest

from engine.pipeline import bibliothecaire, cache, chemins, continuite, contrat, montage, realisateur

EXEMPLE = chemins.RACINE / "episodes" / "exemples" / "demo_001.json"


@pytest.fixture
def donnees() -> dict:
    return json.loads(EXEMPLE.read_text(encoding="utf-8"))


def fiche(d: dict) -> contrat.Fiche:
    return contrat.valider_donnees(d)


# ----- contrat -------------------------------------------------------------------------------
def test_exemple_valide(donnees):
    f = fiche(donnees)
    assert f.episode_id == "demo_001"
    assert f.donnees["format"]["fps"] == 30


def test_erreurs_collectees_ensemble(donnees):
    donnees["beats"][0]["plan"]["cible"] = "inexistant"
    donnees["beats"][1]["actions"][0]["cible"] = "fantome"
    with pytest.raises(contrat.FicheInvalide) as e:
        fiche(donnees)
    assert len(e.value.erreurs) == 2
    assert any("inexistant" in m for m in e.value.erreurs)


def test_schema_refuse_champ_inconnu(donnees):
    donnees["champ_inconnu"] = 1
    with pytest.raises(contrat.FicheInvalide):
        fiche(donnees)


def test_action_objet_refusee_sur_module(donnees):
    donnees["beats"][2]["actions"].append({"type": "deplacer", "cible": "village", "params": {"vers": [0, 0, 0]}})
    with pytest.raises(contrat.FicheInvalide, match="module"):
        fiche(donnees)


def test_pack_inconnu(donnees):
    donnees["pack_da"] = "nexiste_pas"
    with pytest.raises(contrat.FicheInvalide, match="pack"):
        fiche(donnees)


def test_primitives_concordent_avec_le_kit():
    source = (chemins.SCRIPTS_BLENDER / "kits" / "primitifs.py").read_text(encoding="utf-8")
    bloc = source.split("PRIMITIVES = {", 1)[1].split("}", 1)[0]
    noms = set(re.findall(r'"([a-z_]+)"\s*:', bloc))
    assert noms == set(chemins.PRIMITIVES)


# ----- réalisateur ---------------------------------------------------------------------------
def test_timeline_continue_et_coherente(donnees):
    t = realisateur.construire_timeline(fiche(donnees))
    beats = t["beats"]
    assert beats[0]["frame_debut"] == 1
    for a, b in zip(beats, beats[1:]):
        assert b["frame_debut"] == a["frame_fin"] + 1
        assert b["debut_s"] == pytest.approx(a["fin_s"])
    assert t["nb_frames"] == beats[-1]["frame_fin"]


def test_action_calee_sur_le_mot(donnees):
    t = realisateur.construire_timeline(fiche(donnees))
    b2 = t["beats"][1]
    action = b2["actions"][0]
    mot = next(m for m in b2["mots"] if realisateur.normaliser_mot(m["mot"]).startswith("allume"))
    assert action["t_debut_s"] == pytest.approx(mot["debut"], abs=1e-3)
    assert action["declencheur"] == "mot:allumé"


def test_mot_absent_refuse(donnees):
    donnees["beats"][1]["actions"][0]["mot"] = "dragon"
    with pytest.raises(realisateur.TimelineInvalide, match="dragon"):
        realisateur.construire_timeline(fiche(donnees))


def test_voix_reelle_prioritaire(donnees):
    donnees["beats"][0]["voix_audio"] = {
        "fichier": "x.wav", "duree_s": 4.0,
        "mots": [{"mot": "Au", "debut": 0.1, "fin": 0.3}, {"mot": "début,", "debut": 0.3, "fin": 0.9}],
    }
    t = realisateur.construire_timeline(fiche(donnees))
    b1 = t["beats"][0]
    assert b1["origine_timing"] == "voix_reelle"
    assert b1["duree_s"] == pytest.approx(4.0 + realisateur.MARGE_FIN_S)
    assert b1["mots"][1]["debut"] == pytest.approx(0.3)


def test_duree_imposee(donnees):
    donnees["beats"][0]["duree_s"] = 5
    assert realisateur.construire_timeline(fiche(donnees))["beats"][0]["duree_s"] == 5


# ----- cache ---------------------------------------------------------------------------------
def test_cache_ne_rerend_que_le_beat_modifie(donnees, tmp_path):
    t1 = realisateur.construire_timeline(fiche(donnees))
    e1 = cache.empreintes_beats(t1)
    d2 = copy.deepcopy(donnees)
    d2["beats"][1]["plan"]["distance"] = 9  # seule la caméra du beat 2 change
    e2 = cache.empreintes_beats(realisateur.construire_timeline(fiche(d2)))
    assert [b for b in e1 if e1[b] != e2[b]] == ["b2"]


def test_cache_ignore_texte_ecran(donnees):
    t1 = realisateur.construire_timeline(fiche(donnees))
    d2 = copy.deepcopy(donnees)
    d2["beats"][0]["texte_ecran"] = "AUTRE TEXTE"
    assert cache.empreintes_beats(t1) == cache.empreintes_beats(realisateur.construire_timeline(fiche(d2)))


# ----- bibliothécaire ------------------------------------------------------------------------
def test_asset_bibliotheque_absent_signale(donnees):
    donnees["elements"][0]["asset"] = "bibliotheque:phare_01"
    v = bibliothecaire.verifier(fiche(donnees).donnees)
    assert not v.ok
    assert v.manquants[0]["asset"] == "bibliotheque:phare_01"


def test_primitives_toujours_disponibles(donnees):
    assert bibliothecaire.verifier(fiche(donnees).donnees).ok


# ----- continuité ----------------------------------------------------------------------------
def test_continuite_reprend_et_remplace(donnees, tmp_path, monkeypatch):
    monkeypatch.setattr(chemins, "SERIES", tmp_path)
    donnees["serie"] = {"id": "test", "continuite": True}
    t = realisateur.construire_timeline(fiche(donnees))
    etat = continuite.etat_final(t)
    assert next(e for e in etat["elements"] if e["id"] == "phare")["visible_au_debut"] is True
    assert next(p for p in etat["personnages"] if p["id"] == "heros")["position"] == [-2, -3, 0]
    continuite.enregistrer("test", etat)

    suivant = {"version": "1.0", "episode_id": "demo_002", "serie": {"id": "test", "continuite": True},
               "modules": [{"id": "village", "type": "disperser", "asset": "primitif:maison", "nombre": 55}],
               "beats": [{"id": "b1", "voix": "Le village grandit.", "plan": {"camera": "survol", "cible": "phare"}}]}
    fusion, notes = continuite.fusionner(suivant)
    ids = {o["id"] for o in fusion["elements"]}
    assert {"phare", "rocher_1"} <= ids
    village = next(m for m in fusion["modules"] if m["id"] == "village")
    assert village["nombre"] == 55  # redéclaré : la nouvelle valeur l'emporte
    assert notes
    fiche(fusion)  # la fiche fusionnée reste valide


# ----- montage -------------------------------------------------------------------------------
def test_sous_titres_courts_et_ordonnes(donnees):
    t = realisateur.construire_timeline(fiche(donnees))
    for b in t["beats"]:
        blocs = montage.blocs_sous_titres(b["mots"], b["fin_s"])
        assert all(len(texte.split()) <= montage.MOTS_PAR_SOUS_TITRE for _, _, texte in blocs)
        assert all(d < f <= b["fin_s"] + 1e-6 for d, f, _ in blocs)
        assert all(blocs[i][1] <= blocs[i + 1][0] + 1e-6 for i in range(len(blocs) - 1))


def test_fichier_ass(donnees, tmp_path):
    t = realisateur.construire_timeline(fiche(donnees))
    chemin = tmp_path / "st.ass"
    montage.ecrire_ass(t, 1080, 1920, chemin)
    texte = chemin.read_text(encoding="utf-8")
    assert "PlayResY: 1920" in texte and "JOUR 1" in texte and "Style: SousTitre" in texte


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg absent")
def test_commande_ffmpeg_piste_audio(donnees, tmp_path):
    t = realisateur.construire_timeline(fiche(donnees))
    cmd = montage.commande_ffmpeg(t, tmp_path, 540, 960)
    assert "anullsrc=r=48000:cl=stereo" in cmd
    assert cmd[-1] == "episode.mp4"


# ----- packs de direction artistique ------------------------------------------------------------
def test_pack_de_test_valide_sans_avertissement():
    from engine.pipeline import pack_da
    _, avertissements = pack_da.charger(chemins.PACKS_DA / "test_lowpoly.json")
    assert avertissements == []


def test_pack_invalide_et_couleurs_indistinctes():
    import copy as _copy
    import json as _json
    from engine.pipeline import pack_da
    base = _json.loads((chemins.PACKS_DA / "test_lowpoly.json").read_text(encoding="utf-8"))
    casse = _copy.deepcopy(base)
    casse["materiaux"]["sol"]["couleur"] = [1.4, 0, 0]
    del casse["sous_titres"]
    with pytest.raises(pack_da.PackInvalide) as e:
        pack_da.valider(casse, "test_lowpoly")
    assert len(e.value.erreurs) == 2
    terne = _copy.deepcopy(base)
    terne["materiaux"]["personnage"]["couleur"] = terne["materiaux"]["sol"]["couleur"]
    assert any("personnage et sol" in a for a in pack_da.valider(terne, "test_lowpoly"))


def test_pack_absent_route_vers_le_directeur_artistique(tmp_path):
    import json as _json
    import subprocess as _sp
    import sys as _sys
    fiche = _json.loads((chemins.RACINE / "episodes/exemples/demo_001.json").read_text(encoding="utf-8"))
    fiche["pack_da"] = "pack_qui_n_existe_pas"
    chemin = tmp_path / "f.json"
    chemin.write_text(_json.dumps(fiche), encoding="utf-8")
    res = _sp.run([_sys.executable, "-m", "engine.pipeline.run", str(chemin), "--valider-seulement"],
                  cwd=chemins.RACINE, capture_output=True, text=True)
    synthese = _json.loads(res.stdout.strip().splitlines()[-1].removeprefix("SYNTHESE "))
    assert res.returncode == 2 and synthese["suite"] == "prod-directeur-artistique"


def test_planche_montre_le_beat_apres_ses_actions():
    from engine.pipeline import qa_auto
    beat = {"frame_debut": 100, "frame_fin": 200, "actions": [
        {"type": "cycle", "frame_debut": 100, "frame_fin": 400},
        {"type": "apparaitre", "frame_debut": 170, "frame_fin": 185}]}
    assert qa_auto.frame_representative(beat) == 186
    assert qa_auto.frame_representative({"frame_debut": 0, "frame_fin": 60, "actions": []}) == 30
    tardive = {"frame_debut": 0, "frame_fin": 60, "actions": [{"type": "deplacer", "frame_debut": 50, "frame_fin": 90}]}
    assert qa_auto.frame_representative(tardive) == 30  # action qui déborde : milieu du beat
