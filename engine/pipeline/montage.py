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

from . import chemins, effets_sonores, hud, sons
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


POLICES_WINDOWS = {"arial": "arialbd.ttf", "arial black": "ariblk.ttf", "verdana": "verdanab.ttf"}


def _mesureur(police: str, taille_ass: int):
    """Fonction largeur(texte) en px, avec la police réelle si elle est trouvée (gras), sinon estimée.
    Facteur 1,075 mesuré sur un rendu libass réel (Arial gras), 2026-11-17."""
    from PIL import ImageFont
    fichier = Path("C:/Windows/Fonts") / POLICES_WINDOWS.get(police.lower(), "arialbd.ttf")
    try:
        f = ImageFont.truetype(str(fichier), max(1, round(taille_ass / 1.075)))
        return lambda t: f.getlength(t)
    except OSError:
        return lambda t: len(t) * taille_ass * 0.58


def _couper(texte: str, largeur_max: float, mesurer) -> list[str]:
    mots, lignes, courante = texte.split(), [], ""
    for m in mots:
        essai = f"{courante} {m}".strip()
        if courante and mesurer(essai) > largeur_max:
            lignes.append(courante)
            courante = m
        else:
            courante = essai
    return lignes + [courante] if courante else lignes


def _ass_couleur(c: str) -> str:
    """'&H00BBGGRR' (style) -> '&HBBGGRR&' (balise de ligne)."""
    return f"&H{c[4:]}&"


def _texte_encadre(texte: str, debut: str, fin: str, cadre: dict[str, Any], te: dict[str, Any], taille: int,
                   largeur: int, hauteur: int, haut: int) -> list[str]:
    """Texte à l'écran dans UN rectangle ajusté à la phrase : liseré, fond plein, texte centré, apparition
    en « pop » depuis le centre. Le rectangle est dessiné (\\p1), pas déduit des lignes, pour rester
    rectangulaire quand la phrase tient sur plusieurs lignes."""
    k = hauteur / 1920
    marge_px = max(2, round(cadre.get("marge_px", 20) * k))
    bordure_px = max(1, round(cadre.get("bordure_px", 9) * k))
    mesurer = _mesureur(te.get("police", "Arial"), taille)
    lignes_txt = _couper(texte, largeur * 0.84 - 2 * marge_px, mesurer)
    interligne = round(taille * 1.0)
    l_int = round(max(mesurer(t) for t in lignes_txt) + 2 * marge_px)
    h_int = round(len(lignes_txt) * interligne + 2 * marge_px)
    l_ext, h_ext = l_int + 2 * bordure_px, h_int + 2 * bordure_px
    cx, cy = largeur // 2, haut + h_ext // 2
    pop = "\\fscx0\\fscy0\\t(0,140,\\fscx115\\fscy115)\\t(140,240,\\fscx100\\fscy100)" if cadre.get("pop", True) else ""
    commun = f"\\an5\\pos({cx},{cy})\\bord0\\shad0\\fad(0,150){pop}"
    couleur_texte = cadre.get("texte", te.get("couleur", "&H00FFFFFF"))
    return [
        f"Dialogue: 1,{debut},{fin},TexteEcranCadre,,0,0,0,,{{{commun}\\1c{_ass_couleur(cadre['bordure'])}\\p1}}"
        f"m 0 0 l {l_ext} 0 {l_ext} {h_ext} 0 {h_ext}{{\\p0}}",
        f"Dialogue: 2,{debut},{fin},TexteEcranCadre,,0,0,0,,{{{commun}\\1c{_ass_couleur(cadre['fond'])}\\p1}}"
        f"m 0 0 l {l_int} 0 {l_int} {h_int} 0 {h_int}{{\\p0}}",
        f"Dialogue: 3,{debut},{fin},TexteEcranCadre,,0,0,0,,{{{commun}\\q2\\1c{_ass_couleur(couleur_texte)}}}"
        + "\\N".join(_echapper_ass(t) for t in lignes_txt),
    ]


def ecrire_ass(timeline: dict[str, Any], largeur: int, hauteur: int, chemin: Path,
               sequences_hud: list[hud.Sequence] | None = None) -> None:
    """Sous-titres et texte à l'écran. Le texte à l'écran peut coexister avec des compteurs : s'il
    y en a dans le haut de l'image pendant le beat, il descend juste sous eux."""
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
        f"Style: TexteEcranCadre,{te.get('police', 'Arial')},{taille_te},{te.get('couleur', '&H00FFFFFF')},&H00FFFFFF,"
        f"&H00FFFFFF,&H00000000,-1,0,0,0,100,100,2,0,3,{contour + 1},0,8,60,60,{marge_te},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for b in timeline["beats"]:
        if b.get("texte_ecran"):
            bas_hud = hud.bas_occupe_en_haut(sequences_hud or [], b["debut_s"], b["fin_s"], hauteur)
            marge = max(marge_te, bas_hud + int(hauteur * 0.01)) if bas_hud else 0  # 0 = marge du style
            debut, fin, texte = _ass_temps(b["debut_s"]), _ass_temps(b["fin_s"]), _echapper_ass(b["texte_ecran"])
            cadre = te.get("cadre")
            if cadre:
                lignes += _texte_encadre(b["texte_ecran"], debut, fin, cadre, te, taille_te, largeur, hauteur,
                                         marge or marge_te)
            else:
                lignes.append(f"Dialogue: 1,{debut},{fin},TexteEcran,,0,0,{marge},,"
                              f"{{\\fad(150,150)}}{texte}")
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
                    nom_sortie: str = "episode.mp4", sequences_hud: list[hud.Sequence] | None = None) -> list[str]:
    fps, duree = timeline["fps"], timeline["duree_totale_s"]
    cmd = [ffmpeg_disponible(), "-y", "-hide_banner", "-loglevel", "error",
           "-framerate", str(fps), "-start_number", "1", "-i", "frames/f_%04d.png"]
    entrees_audio, filtres = [], []
    index = 1
    # Habillage 2D (HUD) : chaque séquence PNG est décalée à son instant puis superposée.
    chaine_video, etiquette = [f"[0:v]scale={largeur}:{hauteur}:flags=lanczos,format=rgba[b0]"], "b0"
    for k, seq in enumerate(sequences_hud or []):
        cmd += ["-framerate", str(fps), "-start_number", "0", "-i", (seq.dossier / "%04d.png").relative_to(dossier).as_posix()]
        chaine_video.append(f"[{index}:v]format=rgba,setpts=PTS-STARTPTS+{seq.debut_s:.3f}/TB[h{k}]")
        chaine_video.append(f"[{etiquette}][h{k}]overlay=x={seq.x}:y={seq.y}:eof_action=pass:"
                            f"enable='between(t,{seq.debut_s:.3f},{seq.fin_s:.3f})'[b{k + 1}]")
        etiquette = f"b{k + 1}"
        index += 1
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
        synthes = effets_sonores.fichiers()
        evenements = effets_sonores.evenements(timeline) + [
            (nom, t, effets_sonores.VOLUME_PIECE) for nom, t in hud.sons(timeline.get("hud", []))]
        for nom, instant, volume in sorted(evenements, key=lambda e: e[1]):
            cmd += ["-i", str(synthes[nom])]
            ms = int(round(instant * 1000))
            filtres.append(f"[{index}:a]aresample=48000,volume={volume},adelay={ms}|{ms}[a{index}]")
            entrees_audio.append(f"[a{index}]")
            index += 1
    manquants: set[str] = set()
    bruitages = list(timeline.get("sons", {}).get("evenements", []))
    if "pieces" in sons.registre():
        bruitages += [{"son": "pieces", "t": t, "volume": sons.registre()["pieces"]["volume"], "variante": k}
                      for k, (nom, t) in enumerate(hud.sons(timeline.get("hud", []))) if nom == "piece"]
    for ev in sorted(bruitages, key=lambda e: e["t"]):
        f = sons.fichier(ev["son"], ev["variante"])
        if f is None:
            manquants.add(ev["son"])
            continue
        cmd += ["-i", str(f)]
        ms = int(round(ev["t"] * 1000))
        filtres.append(f"[{index}:a]aresample=48000,volume={ev['volume']},adelay={ms}|{ms}[a{index}]")
        entrees_audio.append(f"[a{index}]")
        index += 1
    amb = timeline.get("sons", {}).get("ambiance")
    if amb:
        f = sons.fichier(amb["son"], 0, duree)
        if f is None:
            manquants.add(amb["son"])
        else:
            cmd += ["-i", str(f)]
            filtres.append(f"[{index}:a]aresample=48000,atrim=0:{duree:.3f},volume={amb['volume']}[a{index}]")
            entrees_audio.append(f"[a{index}]")
            index += 1
    timeline["_sons_manquants"] = sorted(manquants)
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
    chaine_video.append(f"[{etiquette}]ass=sous_titres.ass,format=yuv420p[v]")
    filtres = chaine_video + filtres
    # Volume final normalisé à -14 LUFS (niveau visé par Instagram, TikTok et YouTube), crêtes à -1,5 dBTP.
    filtres.append(f"{''.join(entrees_audio)}amix=inputs={len(entrees_audio)}:duration=longest:normalize=0,"
                   f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
    cmd += ["-filter_complex", ";".join(filtres), "-map", "[v]", "-map", "[a]",
            "-t", f"{duree:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", nom_sortie]
    return cmd


def monter(timeline: dict[str, Any], dossier: Path) -> Path:
    largeur, hauteur = taille_frames(dossier / "frames")
    try:
        sequences = hud.preparer(timeline.get("hud", []), timeline["fps"], largeur, hauteur, dossier)
    except hud.HudInvalide as e:
        raise MontageErreur(str(e)) from e
    ecrire_ass(timeline, largeur, hauteur, dossier / "sous_titres.ass", sequences_hud=sequences)
    cmd = commande_ffmpeg(timeline, dossier, largeur, hauteur, sequences_hud=sequences)
    res = subprocess.run(cmd, cwd=dossier, capture_output=True, text=True)
    if res.returncode != 0:
        raise MontageErreur(f"ffmpeg a échoué (code {res.returncode}) : {res.stderr.strip()[-1500:]}")
    return dossier / "episode.mp4"
