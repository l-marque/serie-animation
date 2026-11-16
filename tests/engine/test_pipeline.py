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
    noms = set()
    for fichier in ("primitifs.py", "village.py"):
        source = (chemins.SCRIPTS_BLENDER / "kits" / fichier).read_text(encoding="utf-8")
        bloc = source.split("PRIMITIVES = {", 1)[1].split("}", 1)[0]
        noms |= set(re.findall(r'"([a-z_]+)"\s*:', bloc))
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
    # La voix commence AVANCE_VOIX_S après le début du beat (montage) : durée et mots en tiennent compte.
    assert b1["duree_s"] == pytest.approx(realisateur.AVANCE_VOIX_S + 4.0 + realisateur.MARGE_FIN_S)
    assert b1["mots"][1]["debut"] == pytest.approx(0.3 + realisateur.AVANCE_VOIX_S)


def test_duree_imposee_plus_courte_que_la_voix(donnees):
    donnees["beats"][0]["voix_audio"] = {"fichier": "x.wav", "duree_s": 4.0}
    donnees["beats"][0]["duree_s"] = 3
    with pytest.raises(realisateur.TimelineInvalide, match="plus courte que la voix"):
        realisateur.construire_timeline(fiche(donnees))


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


# ----- voix, sous-titres karaoké, effets sonores -----------------------------------------------
def test_voix_aucune_ne_change_rien(donnees):
    from engine.pipeline import voix
    sortie, cr = voix.ajouter_voix(donnees, "aucune")
    assert sortie == donnees and cr["synthetisees"] == []


def test_voix_kyutai_sans_interpreteur(donnees, monkeypatch, tmp_path):
    from engine.pipeline import voix
    monkeypatch.delenv("TTS_PYTHON", raising=False)
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    with pytest.raises(voix.VoixErreur, match="TTS_PYTHON"):
        voix.ajouter_voix(donnees, "kyutai")


def test_voix_cache_puis_reutilise(donnees, monkeypatch, tmp_path):
    import wave as _wave
    from engine.pipeline import voix
    monkeypatch.setattr(voix, "DOSSIER_CACHE", tmp_path)
    appels = []

    def faux_kyutai(phrases, nom_voix, interpreteur, dossier):
        sortie = {}
        for p in phrases:
            appels.append(p["id"])
            with _wave.open(str(dossier / f"{p['id']}.wav"), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\0\0" * 24000)
            sortie[p["id"]] = {"duree_s": 1.0, "mots": [{"mot": m, "debut": 0.1 * i, "fin": 0.1 * i + 0.1}
                                                        for i, m in enumerate(p["texte"].split())]}
        return sortie

    monkeypatch.setattr(voix, "_synthese_kyutai", faux_kyutai)
    s1, cr1 = voix.ajouter_voix(donnees, "kyutai", interpreteur="python")
    parles = [b for b in donnees["beats"] if (b.get("voix") or "").strip()]
    assert len(cr1["synthetisees"]) == len(parles) and all(b.get("voix_audio") for b in s1["beats"] if b.get("voix"))
    s2, cr2 = voix.ajouter_voix(donnees, "kyutai", interpreteur="python")
    assert cr2["synthetisees"] == [] and len(cr2["depuis_cache"]) == len(parles)
    assert len(appels) == len(parles)
    t = realisateur.construire_timeline(fiche(s2))
    assert t["beats"][0]["origine_timing"] == "voix_reelle"


def test_karaoke_surligne_le_mot_prononce():
    from engine.pipeline import montage
    mots = [{"mot": "Au", "debut": 0.15, "fin": 0.3}, {"mot": "début,", "debut": 0.3, "fin": 0.8},
            {"mot": "il", "debut": 0.9, "fin": 1.0}]
    evts = montage.evenements_sous_titres(mots, 2.0, {})
    assert [e[2].count("\\1c") for e in evts] == [1, 1, 1]
    assert "DÉBUT," in evts[0][2] and "IL" not in evts[0][2]  # coupure à la ponctuation
    assert evts[1][2].startswith("AU {\\1c")


def test_effets_sonores_fusionnes_et_places():
    from engine.pipeline import effets_sonores
    timeline = {"beats": [
        {"debut_s": 0.0, "actions": [{"type": "apparaitre", "t_debut_s": 1.0}, {"type": "apparaitre", "t_debut_s": 1.05}]},
        {"debut_s": 3.0, "actions": [{"type": "deplacer", "t_debut_s": 3.5}]}]}
    evts = effets_sonores.evenements(timeline)
    assert [e[0] for e in evts] == ["pop", "souffle"]
    assert evts[1][1] == pytest.approx(2.88)


def test_voix_du_pack_et_assemblage_audition(tmp_path, monkeypatch):
    import json as _json
    import wave as _wave
    from engine.pipeline import voix
    pack = _json.loads((chemins.PACKS_DA / "test_lowpoly.json").read_text(encoding="utf-8"))
    pack["voix_off"] = {"kyutai": "cml-tts/fr/296_1028_000022-0001_enhanced.wav"}
    (tmp_path / "p.json").write_text(_json.dumps(pack), encoding="utf-8")
    monkeypatch.setattr(chemins, "PACKS_DA", tmp_path)
    assert voix.voix_du_pack("p") == "cml-tts/fr/296_1028_000022-0001_enhanced.wav"
    assert voix.voix_du_pack("absent") is None
    for vid in ("v01", "v02"):
        with _wave.open(str(tmp_path / f"{vid}.wav"), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(b"\0\0" * 24000)
    chemin = voix._assembler_audition(tmp_path, ["v01", "v02", "v03"])
    with _wave.open(str(chemin)) as w:
        assert w.getnframes() / w.getframerate() == pytest.approx(2 * (1 + 0.35 * 2 + 0.12), abs=0.01)


def test_fiche_completee_reste_valide_apres_revalidation(donnees):
    """La voix revalide la fiche complétée par les valeurs par défaut : celles-ci doivent rester conformes."""
    donnees["elements"].append({"id": "sans_role", "asset": "primitif:caisse"})
    donnees["modules"][0].pop("role", None)
    f = fiche(donnees)
    assert contrat.valider_donnees(f.donnees, source="revalidation").donnees["episode_id"] == f.donnees["episode_id"]


def test_lint_voix():
    assert realisateur.lint_voix("Cinq cent douze canards arrivent.", "b") and "grand nombre" in realisateur.lint_voix("Cinq cent douze canards arrivent.", "b")[0]
    assert "mot(s)" in realisateur.lint_voix("Stop !", "b")[0]
    assert realisateur.lint_voix("Et chaque canard devient deux canards.", "b") == []
    assert realisateur.lint_voix("", "b") == []


def test_mot_declencheur_apres_elision():
    from engine.pipeline.realisateur import _instant_mot
    mots = [{"mot": "Il", "debut": 0.0}, {"mot": "pouvez", "debut": 0.4}, {"mot": "m'aider.", "debut": 0.9},
            {"mot": "l’eau", "debut": 1.5}]
    assert _instant_mot(mots, "aider", "b") == 0.9
    assert _instant_mot(mots, "m'aider", "b") == 0.9
    assert _instant_mot(mots, "eau", "b") == 1.5


def test_habillage_valide_et_controle_les_parents():
    from engine.pipeline import habillage
    fiche_min = {"elements": [{"id": "panneau"}], "personnages": [], "modules": []}
    textes = habillage.valider({"version": "1.0", "textes_3d": [{"id": "t1", "texte": "SIX SEVEN", "parent": "panneau"}]},
                               fiche_min)
    assert textes[0]["taille"] == 0.3 and textes[0]["role"] == "accent"
    with pytest.raises(habillage.HabillageInvalide, match="parent"):
        habillage.valider({"version": "1.0", "textes_3d": [{"id": "t1", "texte": "X", "parent": "absent"}]}, fiche_min)
    with pytest.raises(habillage.HabillageInvalide, match="déjà utilisé"):
        habillage.valider({"version": "1.0", "textes_3d": [{"id": "panneau", "texte": "X"}]}, fiche_min)


def test_habillage_absent_ne_change_rien(tmp_path):
    from engine.pipeline import habillage
    assert habillage.charger(tmp_path / "ep.json", {}) == []


@pytest.mark.parametrize("licence,ok", [("CC0", True), ("CC0 1.0 Universal", True), ("CC-BY 3.0", True),
                                        ("CREATIVE_COMMONS_BY", True), ("Public Domain", True), ("CC-BY-NC", False),
                                        ("CC BY-SA 4.0", False), ("CC-BY-ND 4.0", False), ("Editorial", False),
                                        ("inconnue", False), ("CC Attribution", True), ("CC Attribution-NonCommercial", False), ("CC Attribution-ShareAlike", False), ("CC0 Public Domain", True)])
def test_licences_acceptees(licence, ok):
    from engine.pipeline.sources_assets import licence_acceptee
    assert licence_acceptee(licence) is ok


def _timeline_hud():
    return {"duree_totale_s": 10.0, "fps": 30, "beats": [
        {"id": "b1", "debut_s": 0.0, "fin_s": 4.0, "mots": [{"mot": "chaque", "debut": 0.5, "fin": 0.9},
                                                          {"mot": "like,", "debut": 1.0, "fin": 1.3}]},
        {"id": "b2", "debut_s": 4.0, "fin_s": 8.0, "mots": []}]}


def test_hud_resout_les_instants_et_refuse_un_mot_absent():
    from engine.pipeline import hud
    tl = _timeline_hud()
    r = hud.resoudre([{"type": "compteur", "beat": "b1", "mot": "like", "valeur": 990, "vers": 1000, "jusqu_au_beat": "b2"},
                      {"type": "gain", "beat": "b1", "mot": "like"}], tl)
    assert (r[0]["debut_s"], r[0]["fin_s"]) == (1.0, 8.0)
    assert r[1]["fin_s"] == pytest.approx(1.0 + hud.DUREE_GAIN_S)
    assert hud.sons(r) == [("piece", 1.0 + hud.DUREE_POP_S), ("piece", 1.0)]
    with pytest.raises(hud.HudInvalide, match="apparaît pas"):
        hud.resoudre([{"type": "gain", "beat": "b1", "mot": "abonnement"}], tl)


def test_hud_rend_des_sequences_transparentes(tmp_path):
    from PIL import Image
    from engine.pipeline import hud
    r = hud.resoudre([{"type": "compteur", "icone": "habitant", "beat": "b1", "debut": 0.0, "valeur": 12, "vers": 13},
                      {"type": "gain", "beat": "b1", "mot": "like", "position": [0.5, 0.6]}], _timeline_hud())
    seqs = hud.preparer(r, 30, 540, 960, tmp_path)
    assert len(seqs) == 2 and all(s.nb_images > 0 for s in seqs)
    for s in seqs:
        with Image.open(s.dossier / "0010.png") as im:
            assert im.mode == "RGBA" and s.x + im.width <= 540 and s.y + im.height <= 960


def test_cles_env_tolerantes(tmp_path, monkeypatch):
    from engine.pipeline import chemins, sources_assets
    (tmp_path / ".env").write_text("API_Poly_Pizza=abc\nAPI_3D_Texel :tx_live_123\n", encoding="utf-8")
    monkeypatch.setattr(chemins, "RACINE", tmp_path)
    for nom in ("POLY_PIZZA_KEY", "TEXEL_API_KEY", "SKETCHFAB_TOKEN"):
        monkeypatch.delenv(nom, raising=False)
    assert sources_assets._env("POLY_PIZZA_KEY") == "abc"
    assert sources_assets._env("TEXEL_API_KEY") == "tx_live_123"
    assert sources_assets._env("SKETCHFAB_TOKEN") is None


def test_sons_resolus_avec_repetition_et_ambiance():
    from engine.pipeline import sons
    tl = _timeline_hud()
    r = sons.resoudre({"ambiance": {"son": "ambiance_village"},
                       "sons": [{"son": "marteau", "beat": "b1", "mot": "like", "repeter": 3, "intervalle": 0.5}]}, tl)
    assert [e["t"] for e in r["evenements"]] == [1.0, 1.5, 2.0]
    assert r["ambiance"]["son"] == "ambiance_village" and r["ambiance"]["volume"] > 0
    with pytest.raises(sons.SonInvalide, match="inconnu"):
        sons.resoudre({"sons": [{"son": "dragon", "beat": "b1"}]}, tl)


def test_ambiance_synthetisee(tmp_path, monkeypatch):
    import wave
    from engine.pipeline import sons
    monkeypatch.setattr(sons, "CACHE", tmp_path)
    f = sons.ambiance("village", 2.2)
    with wave.open(str(f)) as w:
        assert w.getnframes() / w.getframerate() >= 2.2
