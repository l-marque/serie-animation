"""Contrôle qualité automatique (sans Claude) et planche contact (pour le seul appel Claude).

Contrôles :
- toutes les frames attendues existent ;
- l'image du milieu de chaque beat n'est ni vide ni unie (plan raté, caméra dans un mur) ;
- la vidéo existe, sa durée correspond à la timeline et elle contient une piste audio.

La planche contact rassemble, sur UNE image, la vignette centrale de chaque beat avec sa
phrase de voix off : le sous-agent prod-controle-qualite la juge en un seul appel.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageStat

ECART_TYPE_MIN = 6.0  # en dessous, l'image est considérée comme unie


def _police(taille: int) -> ImageFont.ImageFont:
    for nom in ("DejaVuSans.ttf", "arial.ttf", "Arial.ttf", "LiberationSans-Regular.ttf"):
        try:
            return ImageFont.truetype(nom, taille)
        except OSError:
            continue
    return ImageFont.load_default()


def frame_centrale(beat: dict[str, Any]) -> int:
    return (beat["frame_debut"] + beat["frame_fin"]) // 2


def frame_representative(beat: dict[str, Any]) -> int:
    """Frame qui montre le beat une fois ses actions faites : la fin de la dernière action
    (hors cycles) qui se termine dans le beat, sinon le milieu. Sans cela, une apparition calée
    sur un mot de fin de phrase serait invisible sur la planche contact."""
    fins = [a["frame_fin"] for a in beat.get("actions", [])
            if a.get("type") != "cycle" and beat["frame_debut"] <= a.get("frame_fin", -1) <= beat["frame_fin"]]
    if not fins:
        return frame_centrale(beat)
    return max(frame_centrale(beat), min(max(fins) + 1, beat["frame_fin"]))


def _sonder(video: Path) -> dict[str, Any]:
    exe = shutil.which("ffprobe")
    if not exe:
        return {}
    res = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration:stream=codec_type",
                          "-of", "json", str(video)], capture_output=True, text=True)
    return json.loads(res.stdout) if res.returncode == 0 else {}


def controler(timeline: dict[str, Any], dossier: Path) -> dict[str, Any]:
    frames = dossier / "frames"
    problemes: list[str] = []
    manquantes = [n for n in range(1, timeline["nb_frames"] + 1) if not (frames / f"f_{n:04d}.png").is_file()]
    if manquantes:
        problemes.append(f"{len(manquantes)} frame(s) manquante(s), première : {manquantes[0]}")
    for b in timeline["beats"]:
        f = frames / f"f_{frame_centrale(b):04d}.png"
        if f.is_file():
            with Image.open(f) as im:
                ecart = max(ImageStat.Stat(im.convert("RGB")).stddev)
            if ecart < ECART_TYPE_MIN:
                problemes.append(f"beat {b['id']} : image quasi unie (écart-type {ecart:.1f}), plan probablement raté")
    video = dossier / "episode.mp4"
    infos: dict[str, Any] = {}
    if not video.is_file():
        problemes.append("episode.mp4 absent")
    else:
        sonde = _sonder(video)
        if sonde:
            duree = float(sonde.get("format", {}).get("duration", 0))
            infos["duree_video_s"] = round(duree, 3)
            tolerance = 1 / timeline["fps"] + 0.1
            if abs(duree - timeline["duree_totale_s"]) > tolerance:
                problemes.append(f"durée vidéo {duree:.2f} s au lieu de {timeline['duree_totale_s']:.2f} s")
            types = {s.get("codec_type") for s in sonde.get("streams", [])}
            if "audio" not in types:
                problemes.append("pas de piste audio")
        else:
            infos["avertissement"] = "ffprobe indisponible : durée et audio non vérifiés"
    return {"ok": not problemes, "problemes": problemes, **infos}


def planche_contact(timeline: dict[str, Any], dossier: Path, colonnes: int = 3, largeur_vignette: int = 300) -> Path:
    frames = dossier / "frames"
    vignettes = []
    for b in timeline["beats"]:
        f = frames / f"f_{frame_representative(b):04d}.png"
        if f.is_file():
            with Image.open(f) as im:
                im = im.convert("RGB")
                ratio = largeur_vignette / im.width
                vignettes.append((b, im.resize((largeur_vignette, int(im.height * ratio)))))
        else:
            vignettes.append((b, None))
    hauteur_img = max((v.height for _, v in vignettes if v), default=int(largeur_vignette * 16 / 9))
    police, police_titre = _police(15), _police(17)
    hauteur_texte = 110
    lignes = (len(vignettes) + colonnes - 1) // colonnes
    marge = 12
    largeur = colonnes * (largeur_vignette + marge) + marge
    hauteur = 46 + lignes * (hauteur_img + hauteur_texte + marge) + marge
    planche = Image.new("RGB", (largeur, hauteur), (24, 24, 28))
    dessin = ImageDraw.Draw(planche)
    dessin.text((marge, 12), f"{timeline['episode_id']} · {timeline['mode']} · {timeline['duree_totale_s']:.1f} s",
                fill=(240, 240, 240), font=police_titre)
    for i, (b, v) in enumerate(vignettes):
        x = marge + (i % colonnes) * (largeur_vignette + marge)
        y = 46 + (i // colonnes) * (hauteur_img + hauteur_texte + marge)
        if v:
            planche.paste(v, (x, y))
        else:
            dessin.rectangle([x, y, x + largeur_vignette, y + hauteur_img], outline=(200, 60, 60), width=3)
            dessin.text((x + 10, y + 10), "frame absente", fill=(230, 90, 90), font=police)
        entete = f"{b['id']} · {b['duree_s']:.1f} s · {b['plan']['camera']} · f{frame_representative(b)}"
        if b.get("texte_ecran"):
            entete += f" · « {b['texte_ecran']} »"
        dessin.text((x, y + hauteur_img + 6), entete, fill=(255, 210, 90), font=police)
        voix = textwrap.fill(b.get("voix") or "(sans voix)", width=34)
        dessin.multiline_text((x, y + hauteur_img + 28), voix, fill=(225, 225, 225), font=police, spacing=3)
    sortie = dossier / "planche_contact.png"
    planche.save(sortie)
    return sortie
