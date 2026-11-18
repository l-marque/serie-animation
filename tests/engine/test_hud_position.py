"""Position des compteurs et coexistence avec le texte à l'écran."""

from __future__ import annotations

import pytest

pytest.importorskip("PIL")

from engine.pipeline import hud, montage

L, H, FPS = 540, 960, 10


def _compteur(debut, fin, **k):
    return {"type": "compteur", "beat": "b1", "valeur": 5, "debut_s": debut, "fin_s": fin, **k}


def test_defaut_haut_gauche(tmp_path):
    (s,) = hud.preparer([_compteur(0, 2)], FPS, L, H, tmp_path)
    assert s.x < L * 0.1 and s.y < H * 0.2 and s.hauteur > 0


@pytest.mark.parametrize("ancre,cote,haut", [("haut_droite", "droite", True), ("bas_gauche", "gauche", False),
                                              ("haut_centre", "centre", True), ("bas_droite", "droite", False)])
def test_ancres(tmp_path, ancre, cote, haut):
    (s,) = hud.preparer([_compteur(0, 2, position=ancre)], FPS, L, H, tmp_path)
    centre_x, centre_y = s.x + s.largeur / 2, s.y + s.hauteur / 2
    assert (centre_y < H / 3) if haut else (H / 2 < centre_y < H * 0.75)
    assert {"gauche": centre_x < L / 3, "centre": L / 3 < centre_x < 2 * L / 3, "droite": centre_x > 2 * L / 3}[cote]


def test_position_libre_et_empilement_par_ancre(tmp_path):
    seqs = hud.preparer([_compteur(0, 3), _compteur(0, 3, icone="habitant"), _compteur(0, 3, position="haut_droite"),
                         _compteur(0, 3, position=[0.5, 0.5])], FPS, L, H, tmp_path)
    a, b, c, d = seqs
    assert b.y > a.y            # deux compteurs en haut à gauche : empilés
    assert c.y == a.y           # haut_droite a sa propre pile
    assert abs(d.x + d.largeur / 2 - L / 2) <= 1 and abs(d.y + d.hauteur / 2 - H / 2) <= 1


def test_texte_ecran_descend_sous_les_compteurs(tmp_path):
    seqs = hud.preparer([_compteur(0, 2), _compteur(0, 2, icone="habitant")], FPS, L, H, tmp_path)
    t = {"pack_da": {}, "beats": [
        {"debut_s": 0, "fin_s": 2, "texte_ecran": "AVEC COMPTEURS", "mots": []},
        {"debut_s": 3, "fin_s": 4, "texte_ecran": "SANS COMPTEUR", "mots": []}]}
    chemin = tmp_path / "s.ass"
    montage.ecrire_ass(t, L, H, chemin, sequences_hud=seqs)
    lignes = [l for l in chemin.read_text(encoding="utf-8").splitlines() if l.startswith("Dialogue: 1")]
    marge_avec = int(lignes[0].split(",")[7])
    marge_sans = int(lignes[1].split(",")[7])
    assert marge_avec >= max(s.y + s.hauteur for s in seqs) and marge_sans == 0


def test_badge_permanent_en_haut_a_droite(tmp_path):
    (s,) = hud.preparer([{"type": "badge", "texte": "JOUR *2*", "beat": "b1", "debut_s": 0, "fin_s": 3}],
                        FPS, L, H, tmp_path)
    assert s.x + s.largeur / 2 > 2 * L / 3 and s.y < H / 3
    assert s.nb_images == 30 and s.fin_s == pytest.approx(3)


def test_banniere_une_ligne_dans_l_image():
    for texte in ("#PELOUSE *RÉPARÉE*", "#ON EST *11*"):
        im = hud.titre(texte, 1080, 1.0)
        assert im.width * 1.2 <= 1080          # marge d'animation comprise
        assert im.height < 260                 # une seule ligne


def test_sons_ignore_le_badge():
    specs = [{"type": "badge", "texte": "JOUR *2*", "beat": "b1", "debut_s": 0, "fin_s": 3},
             {"type": "compteur", "beat": "b1", "valeur": 0, "vers": 10, "debut_s": 1, "fin_s": 3}]
    assert [nom for nom, _ in hud.sons(specs)] == ["piece"]
