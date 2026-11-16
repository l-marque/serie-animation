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
# Temps minimal pendant lequel le résultat d'une action doit rester à l'écran avant la coupe.
MARGE_LISIBILITE_S = 1.0
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
        # Le montage place le fichier de voix à AVANCE_VOIX_S après le début du beat : les mots du
        # fichier (relatifs à son début) sont décalés d'autant.
        if audio.get("mots"):
            mots = [{"mot": m["mot"], "debut": round(m["debut"] + AVANCE_VOIX_S, 3),
                     "fin": round(m["fin"] + AVANCE_VOIX_S, 3)} for m in audio["mots"]]
        else:
            mots = _mots_estimes(texte, audio["duree_s"])
        duree = beat.get("duree_s", AVANCE_VOIX_S + audio["duree_s"] + MARGE_FIN_S)
        if duree < AVANCE_VOIX_S + audio["duree_s"]:
            raise TimelineInvalide(f"beat {beat['id']} : duree_s ({duree} s) plus courte que la voix "
                                   f"({audio['duree_s']:.2f} s) : retire duree_s ou allonge-la")
        return duree, mots, "voix_reelle"
    if texte:
        parole = len(texte) / CARACTERES_PAR_SECONDE
        duree = beat.get("duree_s", max(DUREE_MIN_S, AVANCE_VOIX_S + parole + MARGE_FIN_S))
        parole_effective = max(0.3, min(parole, duree - AVANCE_VOIX_S - 0.1))
        return duree, _mots_estimes(texte, parole_effective), "estimation_texte"
    return beat.get("duree_s", DUREE_BEAT_MUET_S), [], "muet"


NOMBRES_DIFFICILES = re.compile(r"\b(cents?|mille|quatre-vingts?|soixante-(?:dix|onze|douze|treize|quatorze|quinze|seize))\b", re.I)


def lint_voix(texte: str, beat_id: str) -> list[str]:
    """Défauts fréquents de la synthèse vocale, repérés sur le texte (avant tout calcul) :
    phrase trop courte (intonation plate ou coupée) et grands nombres dits en toutes lettres ou en
    chiffres (prononciation souvent heurtée). La production le signale ; le texte reste celui validé
    par le pôle Storytelling."""
    texte = (texte or "").strip()
    if not texte:
        return []
    avert = []
    nb_mots = len(_decouper_mots(texte))
    if nb_mots < 3:
        avert.append(f"beat {beat_id} : voix de {nb_mots} mot(s) (« {texte} ») : la synthèse vocale rend mal les "
                     "phrases très courtes ; les regrouper avec la phrase voisine ou laisser le beat muet")
    if re.search(r"\d{3,}", texte) or NOMBRES_DIFFICILES.search(texte):
        avert.append(f"beat {beat_id} : grand nombre dans la voix (« {texte} ») : prononciation souvent heurtée ; "
                     "le montrer à l'écran (compteur) et le dire autrement (« deux fois plus », « des centaines »)")
    return avert


def _instant_mot(mots: list[dict[str, Any]], cible: str, beat_id: str) -> float:
    n = normaliser_mot(cible)
    for m in mots:
        # Élision française : « m'aider », « l'eau », « qu'on » se déclenchent aussi sur « aider », « eau », « on ».
        formes = {normaliser_mot(m["mot"]), normaliser_mot(re.split(r"['’]", m["mot"])[-1])}
        if any(f.startswith(n) for f in formes if f):
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

    for b in d["beats"]:
        fiche.avertissements += lint_voix(b.get("voix", ""), b["id"])

    nb_frames = beats_sortie[-1]["frame_fin"]
    for b in beats_sortie:
        for a in b["actions"]:
            court_et_muet = not (b.get("voix") or "").strip() and b["duree_s"] < 1.5  # pops rapides voulus
            if a["type"] != "cycle" and not court_et_muet and b["fin_s"] - a["t_fin_s"] < MARGE_LISIBILITE_S:
                fiche.avertissements.append(
                    f"beat {b['id']} : '{a['type']}' sur '{a['cible']}' finit à {b['fin_s'] - a['t_fin_s']:.2f} s "
                    f"de la fin du beat (< {MARGE_LISIBILITE_S} s) : le résultat sera à peine visible ; "
                    "choisir un mot plus tôt dans la phrase"
                )
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
