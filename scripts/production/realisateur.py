"""Réalisateur : construit la timeline maître à partir d'une fiche validée.

La timeline est la seule horloge du pipeline. Décorateur, Animateur, Caméra (dans Blender)
et Montage (ffmpeg) la lisent ; aucun ne décide du timing de son côté.

Règles de durée d'un beat (par ordre de priorité) :
1. 'duree_s' imposée dans la fiche ;
2. durée réelle de la voix ('voix_audio.duree_s', remplie par le futur module Voix) + marge ;
3. estimation à partir du texte (débit moyen d'une voix off française) ;
4. 2 s pour un beat muet.

Les mots de la voix sont horodatés : exactement si 'voix_audio.mots' existe, sinon par
estimation proportionnelle au nombre de caractères. Une action déclenchée sur un mot
('mot': 'lumière') utilise ces horodatages : quand la vraie voix arrivera, rien ne change
dans les fiches, la synchronisation devient simplement exacte.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

from . import chemins
from .contrat import Fiche

CARACTERES_PAR_SECONDE = 14.0  # débit d'une voix off française posée
AVANCE_VOIX_S = 0.15           # silence avant la première syllabe
MARGE_FIN_S = 0.45             # respiration après la dernière syllabe
DUREE_MIN_S = 1.5
DUREE_BEAT_MUET_S = 2.0


class TimelineInvalide(Exception):
    pass


def normaliser_mot(mot: str) -> str:
    """Minuscules, sans accents ni ponctuation : 'Lumière,' -> 'lumiere'."""
    sans_accent = unicodedata.normalize("NFKD", mot).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", sans_accent.lower())


def _decouper_mots(texte: str) -> list[str]:
    return [m for m in re.split(r"\s+", texte.strip()) if m]


def _mots_estimes(texte: str, duree_parole: float) -> list[dict[str, Any]]:
    """Répartit la durée de parole entre les mots, au prorata de leur longueur."""
    mots = _decouper_mots(texte)
    if not mots:
        return []
    poids = [max(len(normaliser_mot(m)), 1) + 1 for m in mots]  # +1 : l'espace / la micro-pause
    total = sum(poids)
    t = AVANCE_VOIX_S
    sortie = []
    for mot, p in zip(mots, poids):
        d = duree_parole * p / total
        sortie.append({"mot": mot, "debut": round(t, 3), "fin": round(t + d, 3)})
        t += d
    return sortie


def _duree_et_mots(beat: dict[str, Any]) -> tuple[float, list[dict[str, Any]], str]:
    """Renvoie (durée du beat, mots horodatés relatifs au beat, origine du timing)."""
    texte = beat.get("voix", "").strip()
    audio = beat.get("voix_audio")
    if audio:
        mots = audio.get("mots") or _mots_estimes(texte, audio["duree_s"])
        duree = beat.get("duree_s", audio["duree_s"] + MARGE_FIN_S)
        return duree, mots, "voix_reelle"
    if texte:
        parole = len(texte) / CARACTERES_PAR_SECONDE
        duree = beat.get("duree_s", max(DUREE_MIN_S, AVANCE_VOIX_S + parole + MARGE_FIN_S))
        parole_effective = max(0.3, min(parole, duree - AVANCE_VOIX_S - 0.1))
        return duree, _mots_estimes(texte, parole_effective), "estimation_texte"
    return beat.get("duree_s", DUREE_BEAT_MUET_S), [], "muet"


def _instant_mot(mots: list[dict[str, Any]], cible: str, beat_id: str) -> float:
    n = normaliser_mot(cible)
    for m in mots:
        if normaliser_mot(m["mot"]).startswith(n):
            return m["debut"]
    dispo = ", ".join(m["mot"] for m in mots)
    raise TimelineInvalide(f"beat {beat_id} : le mot '{cible}' n'apparaît pas dans la voix ({dispo})")


def _seconde_vers_frame(t: float, fps: int) -> int:
    """Frames numérotées à partir de 1 (convention Blender)."""
    return int(round(t * fps)) + 1


def charger_pack(nom: str) -> dict[str, Any]:
    with (chemins.PACKS_DA / f"{nom}.json").open(encoding="utf-8") as f:
        return json.load(f)


def construire_timeline(fiche: Fiche, mode: str = "animatique") -> dict[str, Any]:
    """Construit la timeline complète (dictionnaire sérialisable en JSON)."""
    if mode not in ("animatique", "final"):
        raise ValueError("mode doit valoir 'animatique' ou 'final'")
    d = fiche.donnees
    fps = d["format"]["fps"]
    t = 0.0
    beats_sortie = []
    for b in d["beats"]:
        duree, mots_rel, origine = _duree_et_mots(b)
        debut, fin = t, t + duree
        actions = []
        for a in b["actions"]:
            rel = _instant_mot(mots_rel, a["mot"], b["id"]) if "mot" in a else a.get("debut", 0.0)
            if rel >= duree:
                raise TimelineInvalide(
                    f"beat {b['id']} : action '{a['type']}' déclenchée à {rel:.2f} s, après la fin du beat ({duree:.2f} s)"
                )
            t0 = debut + rel
            t1 = t0 + a["duree_s"]
            actions.append({
                "type": a["type"],
                "cible": a["cible"],
                "t_debut_s": round(t0, 3),
                "t_fin_s": round(t1, 3),
                "frame_debut": _seconde_vers_frame(t0, fps),
                "frame_fin": max(_seconde_vers_frame(t1, fps), _seconde_vers_frame(t0, fps) + 1),
                "params": a["params"],
                "declencheur": f"mot:{a['mot']}" if "mot" in a else "temps",
            })
        frame_debut = _seconde_vers_frame(debut, fps)
        frame_fin = _seconde_vers_frame(fin, fps) - 1
        beats_sortie.append({
            "id": b["id"],
            "debut_s": round(debut, 3),
            "fin_s": round(fin, 3),
            "duree_s": round(duree, 3),
            "frame_debut": frame_debut,
            "frame_fin": frame_fin,
            "voix": b.get("voix", ""),
            "voix_fichier": (b.get("voix_audio") or {}).get("fichier"),
            "origine_timing": origine,
            "mots": [{"mot": m["mot"], "debut": round(debut + m["debut"], 3), "fin": round(debut + m["fin"], 3)}
                     for m in mots_rel],
            "texte_ecran": b.get("texte_ecran"),
            "plan": b["plan"],
            "actions": actions,
        })
        t = fin

    nb_frames = beats_sortie[-1]["frame_fin"]
    for b in beats_sortie:
        for a in b["actions"]:
            if a["frame_fin"] > nb_frames:
                a["frame_fin"] = nb_frames
                a["t_fin_s"] = round((nb_frames - 1) / fps, 3)
                fiche.avertissements.append(
                    f"beat {b['id']} : action '{a['type']}' coupée à la fin de l'épisode"
                )

    return {
        "version_timeline": "1.0",
        "episode_id": d["episode_id"],
        "titre": d["titre"],
        "mode": mode,
        "fps": fps,
        "resolution": d["format"]["resolution"],
        "duree_totale_s": round(t, 3),
        "nb_frames": nb_frames,
        "pack_da": charger_pack(d["pack_da"]),
        "decor": d["decor"],
        "objets": [{**o, "categorie": "element"} for o in d["elements"]]
        + [{**o, "categorie": "personnage"} for o in d["personnages"]],
        "modules": d["modules"],
        "audio": d["audio"],
        "beats": beats_sortie,
    }
