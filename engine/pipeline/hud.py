"""Habillage 2D animé (« HUD ») : compteurs et gains incrustés au montage, au-dessus de l'image 3D.

Styles repris du kit Figma « Série animation — Outils d'affichage (HUD) » :
- compteur : pastille blanche arrondie, icône (pièce, habitant), valeur en Baloo 2 ExtraBold ;
  il apparaît quand on en parle (pop), compte jusqu'à la nouvelle valeur, puis disparaît ;
- gain : « +10 » doré cerné de bleu nuit avec une pièce, qui monte et s'efface (façon jeu vidéo),
  accompagné du son de pièce.

Décrit dans `<fiche>.habillage.json` (clé "hud"), donc hors contrat v1.0. Chaque élément est rendu
en une courte séquence PNG transparente (Pillow), superposée par ffmpeg à l'instant voulu : rien
n'est re-rendu dans Blender quand on modifie un compteur.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from . import chemins

POLICE = chemins.ASSETS / "polices" / "Baloo2-variable.ttf"
HAUTEUR_REF = 1920  # tailles du kit Figma, pour une vidéo 1080 × 1920
BLANC, NUIT, OR, OR_FONCE, OR_CLAIR, BLEU = (255, 255, 255), (20, 33, 61), (255, 201, 60), (176, 120, 0), (255, 243, 196), (46, 134, 222)
DUREE_POP_S, DUREE_SORTIE_S, DUREE_COMPTAGE_S, DUREE_GAIN_S = 0.18, 0.15, 0.6, 0.9
MARGE_HAUT = 0.13  # sous la zone masquée par l'interface Instagram (≈ 11,5 % du haut)
MARGE_BAS = 0.30   # au-dessus des sous-titres (≈ 70 %) et de la légende Instagram
MARGE_COTE = 0.045
# Ancres des compteurs : (x relatif, y relatif, alignement horizontal, sens d'empilement).
# Défaut : haut_gauche. À droite, l'interface Instagram masque le bas (boutons) : préférer haut_droite.
ANCRES: dict[str, tuple[float, float, str, int]] = {
    "haut_gauche": (MARGE_COTE, MARGE_HAUT, "gauche", 1),
    "haut_centre": (0.5, MARGE_HAUT, "centre", 1),
    "haut_droite": (1 - MARGE_COTE, MARGE_HAUT, "droite", 1),
    "bas_gauche": (MARGE_COTE, 1 - MARGE_BAS, "gauche", -1),
    "bas_centre": (0.5, 1 - MARGE_BAS, "centre", -1),
    "bas_droite": (1 - MARGE_COTE, 1 - MARGE_BAS, "droite", -1),
}
ANCRE_DEFAUT = "haut_gauche"


class HudInvalide(Exception):
    pass


@dataclass
class Sequence:
    """Séquence PNG prête pour ffmpeg : dossier/0000.png… posée en (x, y) de debut_s à fin_s."""
    dossier: Path
    debut_s: float
    fin_s: float
    x: int
    y: int
    nb_images: int
    largeur: int = 0
    hauteur: int = 0


# ----- résolution des instants ---------------------------------------------------------------------
def _instant(beat: dict[str, Any], spec: dict[str, Any], quoi: str) -> float:
    from .realisateur import TimelineInvalide, _instant_mot
    if spec.get("mot"):
        try:
            return _instant_mot(beat["mots"], spec["mot"], beat["id"])
        except TimelineInvalide as e:
            raise HudInvalide(f"{quoi} : {e}") from e
    return beat["debut_s"] + float(spec.get("debut", 0.0))


def resoudre(specs: list[dict[str, Any]], timeline: dict[str, Any]) -> list[dict[str, Any]]:
    """Ajoute à chaque élément ses instants absolus (debut_s, fin_s) à partir des beats et des mots."""
    beats = {b["id"]: b for b in timeline["beats"]}
    sortie = []
    for i, s in enumerate(specs):
        quoi = f"hud[{i}] ({s['type']})"
        if s["beat"] not in beats:
            raise HudInvalide(f"{quoi} : beat '{s['beat']}' absent de la fiche")
        debut = _instant(beats[s["beat"]], s, quoi)
        if s["type"] == "gain":
            fin = debut + DUREE_GAIN_S
        else:
            dernier = s.get("jusqu_au_beat", s["beat"])
            if dernier not in beats:
                raise HudInvalide(f"{quoi} : beat '{dernier}' absent de la fiche")
            fin = beats[dernier]["fin_s"]
            if fin - debut < DUREE_POP_S + DUREE_SORTIE_S + 0.3:
                raise HudInvalide(f"{quoi} : affiché moins de 0,6 s ; prolonge-le avec « jusqu_au_beat »")
        sortie.append({**s, "debut_s": round(debut, 3), "fin_s": round(min(fin, timeline["duree_totale_s"]), 3)})
    return sortie


# ----- dessin ------------------------------------------------------------------------------------
def _police(taille: int) -> ImageFont.FreeTypeFont:
    if not POLICE.is_file():
        raise HudInvalide(f"police absente : {POLICE.relative_to(chemins.RACINE)}")
    f = ImageFont.truetype(str(POLICE), taille)
    f.set_variation_by_name("ExtraBold")
    return f


def _etoile(cx: float, cy: float, r: float) -> list[tuple[float, float]]:
    return [(cx + (r if k % 2 == 0 else r * 0.45) * math.sin(math.pi * k / 5),
             cy - (r if k % 2 == 0 else r * 0.45) * math.cos(math.pi * k / 5)) for k in range(10)]


def icone(nom: str, taille: int) -> Image.Image:
    """Pièce dorée étoilée ou pastille habitant, dessinées à 4× puis réduites (bords lisses)."""
    s = taille * 4
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    e = max(4, s // 16)
    if nom == "piece":
        d.ellipse([e // 2, e // 2, s - e // 2, s - e // 2], fill=OR, outline=OR_FONCE, width=e)
        m = s * 0.19
        d.ellipse([m, m, s - m, s - m], outline=(227, 155, 0), width=max(3, e * 3 // 4))
        d.polygon(_etoile(s / 2, s / 2, s * 0.2), fill=OR_CLAIR)
    elif nom == "habitant":
        d.ellipse([e // 2, e // 2, s - e // 2, s - e // 2], fill=BLEU, outline=NUIT, width=e)
        d.ellipse([s * 0.36, s * 0.24, s * 0.64, s * 0.52], fill=BLANC)
        d.chord([s * 0.22, s * 0.55, s * 0.78, s * 1.05], 180, 360, fill=BLANC)
    else:
        raise HudInvalide(f"icône inconnue : {nom}")
    return im.resize((taille, taille), Image.LANCZOS)


def pastille(valeur: str, nom_icone: str, echelle: float) -> Image.Image:
    """Compteur blanc du kit Figma (taille réelle à l'échelle de la vidéo, sans animation)."""
    h = round(96 * echelle)
    police = _police(round(64 * echelle))
    l_texte = police.getbbox(valeur)[2]
    pad_g, pad_d, ecart, ic = round(14 * echelle), round(32 * echelle), round(16 * echelle), round(72 * echelle)
    l = pad_g + ic + ecart + l_texte + pad_d
    ombre = round(10 * echelle)
    im = Image.new("RGBA", (l + 2 * ombre, h + 3 * ombre), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([ombre, 2 * ombre, ombre + l, 2 * ombre + h], radius=h // 2, fill=(20, 33, 61, 60))
    d.rounded_rectangle([ombre, ombre, ombre + l, ombre + h], radius=h // 2, fill=BLANC,
                        outline=(214, 222, 234), width=max(2, round(3 * echelle)))
    im.alpha_composite(icone(nom_icone, ic), (ombre + pad_g, ombre + (h - ic) // 2))
    haut = police.getbbox(valeur)
    d.text((ombre + pad_g + ic + ecart, ombre + (h - (haut[3] + haut[1])) // 2), valeur, font=police, fill=NUIT)
    return im


def badge_gain(texte: str, nom_icone: str, echelle: float) -> Image.Image:
    police = _police(round(120 * echelle))
    contour = max(3, round(8 * echelle))
    bb = police.getbbox(texte, stroke_width=contour)
    ic = round(96 * echelle)
    l, h = bb[2] + round(10 * echelle) + ic + contour, max(bb[3], ic) + round(12 * echelle)
    im = Image.new("RGBA", (l, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((0, round(6 * echelle)), texte, font=police, fill=(20, 33, 61, 110), stroke_width=contour,
           stroke_fill=(20, 33, 61, 110))  # ombre portée
    d.text((0, 0), texte, font=police, fill=OR, stroke_width=contour, stroke_fill=NUIT)
    im.alpha_composite(icone(nom_icone, ic), (bb[2] + round(10 * echelle), (h - ic) // 2))
    return im


def _format(n: int) -> str:
    return f"{n:,}".replace(",", " ")  # espace des milliers, à la française


def _rebond(u: float) -> float:
    """0 -> 1 avec léger dépassement (pop)."""
    u = min(max(u, 0.0), 1.0)
    c = 1.70158 * 1.4
    return 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2


def _poser(toile: Image.Image, motif: Image.Image, echelle_anim: float, opacite: float,
           ancre: tuple[int, int], dy: int = 0) -> None:
    if echelle_anim <= 0.01 or opacite <= 0.01:
        return
    m = motif.resize((max(1, round(motif.width * echelle_anim)), max(1, round(motif.height * echelle_anim))), Image.LANCZOS)
    if opacite < 1:
        alpha = m.getchannel("A").point(lambda a: round(a * opacite))
        m.putalpha(alpha)
    toile.alpha_composite(m, (ancre[0] - m.width // 2, ancre[1] - m.height // 2 + dy))


# ----- séquences ---------------------------------------------------------------------------------
def _sequence_compteur(e: dict[str, Any], fps: int, echelle: float, dossier: Path) -> tuple[int, int, int]:
    depart, arrivee = int(e["valeur"]), int(e.get("vers", e["valeur"]))
    duree = e["fin_s"] - e["debut_s"]
    n = max(1, round(duree * fps))
    plus_large = pastille(_format(max(depart, arrivee)) + "0", e.get("icone", "piece"), echelle)  # marge pour le rebond
    l, h = round(plus_large.width * 1.2), round(plus_large.height * 1.25)
    for i in range(n):
        t = i / fps
        if t < DUREE_POP_S:
            s = _rebond(t / DUREE_POP_S)
        elif t > duree - DUREE_SORTIE_S:
            s = max(0.0, (duree - t) / DUREE_SORTIE_S)
        else:
            s = 1.0
        u = min(max((t - DUREE_POP_S) / DUREE_COMPTAGE_S, 0.0), 1.0)
        valeur = round(depart + (arrivee - depart) * (1 - (1 - u) ** 3))
        if arrivee != depart and 0 < t - DUREE_POP_S - DUREE_COMPTAGE_S < 0.2:  # petit sursaut à l'arrivée
            s *= 1 + 0.08 * math.sin(math.pi * (t - DUREE_POP_S - DUREE_COMPTAGE_S) / 0.2)
        toile = Image.new("RGBA", (l, h), (0, 0, 0, 0))
        p = pastille(_format(valeur), e.get("icone", "piece"), echelle)
        _poser(toile, p, s, 1.0, (p.width // 2 + round(l * 0.08), h // 2))
        toile.save(dossier / f"{i:04d}.png")
    return n, l, h


def _sequence_gain(e: dict[str, Any], fps: int, echelle: float, hauteur: int, dossier: Path) -> tuple[int, int, int]:
    badge = badge_gain(e.get("texte", "+10"), e.get("icone", "piece"), echelle)
    montee = round(0.06 * hauteur)
    l, h = round(badge.width * 1.3), round(badge.height * 1.3) + montee
    n = max(1, round(DUREE_GAIN_S * fps))
    for i in range(n):
        t = i / fps
        s = _rebond(t / DUREE_POP_S) if t < DUREE_POP_S else 1.0
        opacite = 1.0 if t < DUREE_GAIN_S * 0.55 else max(0.0, (DUREE_GAIN_S - t) / (DUREE_GAIN_S * 0.45))
        dy = -round(montee * min(t / DUREE_GAIN_S, 1.0))
        toile = Image.new("RGBA", (l, h), (0, 0, 0, 0))
        _poser(toile, badge, s, opacite, (l // 2, h - round(badge.height * 0.65)), dy)
        toile.save(dossier / f"{i:04d}.png")
    return n, l, h


def preparer(hud: list[dict[str, Any]], fps: int, largeur: int, hauteur: int, dossier: Path) -> list[Sequence]:
    """Rend chaque élément du HUD en séquence PNG.

    Compteurs : posés à leur `position` (une ancre de ANCRES, ou [x, y] relatifs = centre), par défaut
    en haut à gauche ; les compteurs simultanés sur une même ancre s'empilent (vers le bas en haut de
    l'image, vers le haut en bas). Gains : centrés sur `position` [x, y] (défaut [0.5, 0.55])."""
    echelle = hauteur / HAUTEUR_REF
    racine = dossier / "hud"
    sequences: list[Sequence] = []
    actifs: list[tuple[float, int, str]] = []  # (fin, emplacement, ancre) des compteurs affichés
    for i, e in enumerate(sorted(hud, key=lambda x: x["debut_s"])):
        d = racine / f"{i:02d}_{e['type']}"
        d.mkdir(parents=True, exist_ok=True)
        for ancien in d.glob("*.png"):
            ancien.unlink()
        if e["type"] == "compteur":
            n, l, h = _sequence_compteur(e, fps, echelle, d)
            pos = e.get("position", ANCRE_DEFAUT)
            if isinstance(pos, str):
                actifs = [a for a in actifs if a[0] > e["debut_s"]]
                libres = sorted({0, 1, 2, 3} - {a[1] for a in actifs if a[2] == pos})
                emplacement = libres[0] if libres else 0
                actifs.append((e["fin_s"], emplacement, pos))
                fx, fy, aligne, sens = ANCRES[pos]
                ax = round(largeur * fx)
                # La toile du compteur a une marge (ombre, rebond) : ~8 % à gauche, ~12 % en haut.
                x = {"gauche": ax - round(l * 0.08), "centre": ax - l // 2, "droite": ax - round(l * 0.92)}[aligne]
                pas = emplacement * round(120 * echelle)
                y = (round(hauteur * fy) + pas - round(h * 0.12)) if sens > 0 else (round(hauteur * fy) - pas - round(h * 0.88))
            else:
                fx, fy = pos
                x, y = round(largeur * fx - l / 2), round(hauteur * fy - h / 2)
        else:
            n, l, h = _sequence_gain(e, fps, echelle, hauteur, d)
            fx, fy = e.get("position", [0.5, 0.55])
            x, y = round(largeur * fx - l / 2), round(hauteur * fy - h / 2)
        x, y = min(max(x, 0), largeur - l), min(max(y, 0), hauteur - h)
        sequences.append(Sequence(d, e["debut_s"], e["debut_s"] + n / fps, x, y, n, l, h))
    return sequences


def bas_occupe_en_haut(sequences: list[Sequence], debut_s: float, fin_s: float, hauteur: int) -> int:
    """Ordonnée (px) du bas des éléments du HUD posés dans le tiers haut de l'image et visibles
    entre debut_s et fin_s ; 0 s'il n'y en a pas. Sert à placer le texte à l'écran juste dessous."""
    bas = 0
    for s in sequences:
        if s.debut_s < fin_s and s.fin_s > debut_s and s.y < hauteur / 3:
            bas = max(bas, s.y + s.hauteur)
    return bas


def sons(hud: list[dict[str, Any]]) -> list[tuple[str, float]]:
    """Son de pièce : à chaque gain, et quand un compteur de pièces commence à compter."""
    sortie = []
    for e in hud:
        if e["type"] == "gain":
            sortie.append(("piece", e["debut_s"]))
        elif e.get("icone", "piece") == "piece" and int(e.get("vers", e["valeur"])) != int(e["valeur"]):
            sortie.append(("piece", e["debut_s"] + DUREE_POP_S))
    return sortie
