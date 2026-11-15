"""Montage : assemble les frames rendues, la voix, la musique, les sous-titres et les textes
à l'écran en un MP4 vertical prêt à publier (H.264 + AAC).

Tout le timing vient de la timeline : sous-titres mot à mot et textes à l'écran sont
synchronisés par construction. ffmpeg est lancé avec le dossier de sortie comme dossier
courant, pour éviter les problèmes d'échappement de chemins Windows dans le filtre 'ass'.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from PIL import Image

from . import chemins, effets_sonores
from .realisateur import AVANCE_VOIX_S

MOTS_PAR_SOUS_TITRE = 3
PONCTUATION_COUPURE = (".", ",", ";", ":", "!", "?", "…")


class MontageErreur(Exception):
    pass


def ffmpeg_disponible() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise MontageErreur("ffmpeg introuvable : installe-le et ajoute-le au PATH (https://ffmpeg.org/download.html)")
    return exe


def _ass_temps(t: float) -> str:
    t = max(0.0, t)
    h, reste = divmod(t, 3600)
    m, s = divmod(reste, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _echapper_ass(texte: str) -> str:
    return texte.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", " ")


def _blocs(mots: list[dict[str, Any]], fin_beat: float) -> list[tuple[float, float, list[dict[str, Any]]]]:
    """Regroupe les mots en blocs courts (lisibles sur mobile), coupés à la ponctuation."""
    blocs, courant = [], []
    for i, m in enumerate(mots):
        courant.append(m)
        coupe = len(courant) >= MOTS_PAR_SOUS_TITRE or m["mot"].endswith(PONCTUATION_COUPURE)
        if coupe or i == len(mots) - 1:
            blocs.append(courant)
            courant = []
    sortie = []
    for i, bloc in enumerate(blocs):
        debut = bloc[0]["debut"]
        suivant = blocs[i + 1][0]["debut"] if i + 1 < len(blocs) else fin_beat
        fin = min(max(bloc[-1]["fin"] + 0.25, debut + 0.4), suivant)
        sortie.append((debut, fin, bloc))
    return sortie


def blocs_sous_titres(mots: list[dict[str, Any]], fin_beat: float) -> list[tuple[float, float, str]]:
    return [(d, f, " ".join(m["mot"] for m in bloc)) for d, f, bloc in _blocs(mots, fin_beat)]


def evenements_sous_titres(mots: list[dict[str, Any]], fin_beat: float,
                           style: dict[str, Any]) -> list[tuple[float, float, str]]:
    """Sous-titres « karaoké » : le bloc de mots reste affiché, le mot prononcé est surligné
    (couleur `surlignage` du pack) et grossit légèrement. Le surlignage suit les mots horodatés,
    donc la voix réelle quand elle existe. `majuscules` (par défaut oui) met le texte en capitales,
    comme les Reels de référence."""
    surlignage = style.get("surlignage", "&H0000D7FF")  # jaune or (format ASS : &HAABBGGRR)
    majuscules = style.get("majuscules", True)
    ouvre = "{\\1c" + surlignage + "&\\fscx112\\fscy112}"
    ferme = "{\\r}"  # retour au style SousTitre
    sortie = []
    for debut_bloc, fin_bloc, bloc in _blocs(mots, fin_beat):
        textes = [_echapper_ass(m["mot"].upper() if majuscules else m["mot"]) for m in bloc]
        for i, m in enumerate(bloc):
            debut = debut_bloc if i == 0 else m["debut"]
            fin = bloc[i + 1]["debut"] if i + 1 < len(bloc) else fin_bloc
            if fin <= debut:
                continue
            ligne = " ".join(ouvre + t + ferme if j == i else t for j, t in enumerate(textes))
            sortie.append((debut, fin, ligne))
    return sortie


def ecrire_ass(timeline: dict[str, Any], largeur: int, hauteur: int, chemin: Path) -> None:
    pack = timeline["pack_da"]
    st, te = pack.get("sous_titres", {}), pack.get("texte_ecran", {})
    taille_st = max(12, int(hauteur * st.get("taille_relative", 0.042)))
    taille_te = max(14, int(hauteur * te.get("taille_relative", 0.055)))
    contour = max(1, int(hauteur * 0.004))
    # Zones sûres 9:16 : le haut (~12 %) et le bas (~20 %) sont recouverts par l'interface des applis.
    marge_st = int(hauteur * 0.27)   # sous-titres vers 70 % de la hauteur
    marge_te = int(hauteur * 0.15)   # texte à l'écran vers 15 % de la hauteur
    lignes = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {largeur}",
        f"PlayResY: {hauteur}",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
        "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: SousTitre,{st.get('police', 'Arial')},{taille_st},{st.get('couleur', '&H00FFFFFF')},&H00FFFFFF,"
        f"{st.get('contour', '&H00141018')},&H64000000,-1,0,0,0,100,100,0,0,1,{contour},0,2,60,60,{marge_st},1",
        f"Style: TexteEcran,{te.get('police', 'Arial')},{taille_te},{te.get('couleur', '&H00FFFFFF')},&H00FFFFFF,"
        f"{te.get('contour', '&H00141018')},&H64000000,-1,0,0,0,100,100,2,0,1,{contour + 1},0,8,60,60,{marge_te},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for b in timeline["beats"]:
        if b.get("texte_ecran"):
            lignes.append(f"Dialogue: 1,{_ass_temps(b['debut_s'])},{_ass_temps(b['fin_s'])},TexteEcran,,0,0,0,,"
                          f"{{\\fad(150,150)}}{_echapper_ass(b['texte_ecran'])}")
        for evt in evenements_sous_titres(b["mots"], b["fin_s"], st):
            lignes.append(f"Dialogue: 0,{_ass_temps(evt[0])},{_ass_temps(evt[1])},SousTitre,,0,0,0,,{evt[2]}")
    chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")


def taille_frames(dossier_frames: Path) -> tuple[int, int]:
    premiere = dossier_frames / "f_0001.png"
    if not premiere.is_file():
        raise MontageErreur(f"aucune frame rendue dans {dossier_frames}")
    with Image.open(premiere) as im:
        l, h = im.size
    return l - l % 2, h - h % 2  # H.264 exige des dimensions paires


def commande_ffmpeg(timeline: dict[str, Any], dossier: Path, largeur: int, hauteur: int,
                    nom_sortie: str = "episode.mp4") -> list[str]:
    fps, duree = timeline["fps"], timeline["duree_totale_s"]
    cmd = [ffmpeg_disponible(), "-y", "-hide_banner", "-loglevel", "error",
           "-framerate", str(fps), "-start_number", "1", "-i", "frames/f_%04d.png"]
    entrees_audio, filtres = [], []
    index = 1
    for b in timeline["beats"]:
        f = b.get("voix_fichier")
        if f:
            chemin = Path(f) if Path(f).is_absolute() else chemins.RACINE / f
            if not chemin.is_file():
                raise MontageErreur(f"fichier de voix introuvable pour le beat {b['id']} : {chemin}")
            cmd += ["-i", str(chemin)]
            ms = int(round((b["debut_s"] + AVANCE_VOIX_S) * 1000))
            filtres.append(f"[{index}:a]aresample=48000,adelay={ms}|{ms}[a{index}]")
            entrees_audio.append(f"[a{index}]")
            index += 1
    voix_presentes = list(entrees_audio)
    if timeline["pack_da"].get("effets_sonores", True):
        sons = effets_sonores.fichiers()
        for nom, instant, volume in effets_sonores.evenements(timeline):
            cmd += ["-i", str(sons[nom])]
            ms = int(round(instant * 1000))
            filtres.append(f"[{index}:a]aresample=48000,volume={volume},adelay={ms}|{ms}[a{index}]")
            entrees_audio.append(f"[a{index}]")
            index += 1
    musique = timeline.get("audio", {}).get("musique")
    if musique:
        chemin = Path(musique) if Path(musique).is_absolute() else chemins.RACINE / musique
        if not chemin.is_file():
            raise MontageErreur(f"musique introuvable : {chemin}")
        vol = timeline["audio"].get("volume_musique", 0.25)
        cmd += ["-stream_loop", "-1", "-i", str(chemin)]
        filtres.append(f"[{index}:a]aresample=48000,volume={vol}[m{index}]")
        if voix_presentes:
            # La musique baisse automatiquement quand la voix parle (compression déclenchée par la voix).
            filtres.append(f"{''.join(voix_presentes)}amix=inputs={len(voix_presentes)}:normalize=0,asplit=2[vx][vd]")
            filtres.append(f"[m{index}][vd]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[a{index}]")
            entrees_audio = [e for e in entrees_audio if e not in voix_presentes] + ["[vx]"]
        else:
            filtres.append(f"[m{index}]anull[a{index}]")
        entrees_audio.append(f"[a{index}]")
        index += 1
    # Piste silencieuse : garantit une piste audio de la bonne durée (exigée par certaines plateformes).
    cmd += ["-f", "lavfi", "-t", f"{duree:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    entrees_audio.append(f"[{index}:a]")
    filtres.insert(0, f"[0:v]scale={largeur}:{hauteur}:flags=lanczos,ass=sous_titres.ass,format=yuv420p[v]")
    # Volume final normalisé à -14 LUFS (niveau visé par Instagram, TikTok et YouTube), crêtes à -1,5 dBTP.
    filtres.append(f"{''.join(entrees_audio)}amix=inputs={len(entrees_audio)}:duration=longest:normalize=0,"
                   f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    cmd += ["-filter_complex", ";".join(filtres), "-map", "[v]", "-map", "[a]",
            "-t", f"{duree:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", nom_sortie]
    return cmd


def monter(timeline: dict[str, Any], dossier: Path) -> Path:
    largeur, hauteur = taille_frames(dossier / "frames")
    ecrire_ass(timeline, largeur, hauteur, dossier / "sous_titres.ass")
    cmd = commande_ffmpeg(timeline, dossier, largeur, hauteur)
    res = subprocess.run(cmd, cwd=dossier, capture_output=True, text=True)
    if res.returncode != 0:
        raise MontageErreur(f"ffmpeg a échoué (code {res.returncode}) : {res.stderr.strip()[-1500:]}")
    return dossier / "episode.mp4"
