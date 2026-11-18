"""Bibliothèque de sons : bruitages par nom (marteau, pas, pièces, cartes…) et ambiance de fond.

- Le registre `engine/assets/sons/registre.json` (versionné) associe un nom à un ou plusieurs
  fichiers (variantes jouées tour à tour), un volume et une catégorie.
- Les fichiers Kenney (CC0) sont téléchargés par `python -m engine.pipeline.sons telecharger`
  dans `engine/assets/sons/kenney/` (non versionné, comme les modèles 3D).
- Les sons « synth:… » (ambiances) sont générés par le code : aucune licence, aucun fichier à fournir.

L'habillage d'un épisode (`<fiche>.habillage.json`) les place :
    "ambiance": {"son": "ambiance_village", "volume": 0.18}
    "sons": [{"son": "marteau", "beat": "p2_vous", "mot": "aider", "repeter": 3, "intervalle": 0.35}]
Un son absent de la machine n'arrête pas le montage : il est ignoré et signalé dans le rapport.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import io
import json
import math
import random
import struct
import sys
import urllib.request
import wave
import zipfile
from pathlib import Path
from typing import Any

from . import chemins

REGISTRE = chemins.ASSETS / "sons" / "registre.json"
DOSSIER_KENNEY = chemins.ASSETS / "sons" / "kenney"
CACHE = chemins.RACINE / "renders" / "_cache_sons"
FREQUENCE = 48000


class SonInvalide(Exception):
    pass


def registre() -> dict[str, Any]:
    return json.loads(REGISTRE.read_text(encoding="utf-8"))["sons"] if REGISTRE.is_file() else {}


# ----- ambiances synthétisées ------------------------------------------------------------------
def _ecrire_wav(chemin: Path, echantillons: list[float]) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FREQUENCE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, e)) * 32767)) for e in echantillons))
    return chemin


def _vent(n: int, rng: random.Random) -> list[float]:
    """Bruit filtré passe-bas dont l'intensité ondule lentement (rafales douces)."""
    sortie, y, y2 = [], 0.0, 0.0
    for i in range(n):
        t = i / FREQUENCE
        rafale = 0.55 + 0.3 * math.sin(2 * math.pi * 0.11 * t) + 0.15 * math.sin(2 * math.pi * 0.37 * t + 1.3)
        y += 0.02 * (rng.uniform(-1, 1) - y)
        y2 += 0.05 * (y - y2)
        sortie.append(y2 * 5.0 * rafale)
    return sortie


def _oiseaux(n: int, rng: random.Random) -> list[float]:
    """Gazouillis : séries de 2 à 5 notes glissées entre 2,5 et 5 kHz, toutes les 1,2 à 3,5 s."""
    sortie = [0.0] * n
    t = rng.uniform(0.3, 1.0)
    duree = n / FREQUENCE
    while t < duree - 0.6:
        base = rng.uniform(2500, 4200)
        for k in range(rng.randint(2, 5)):
            debut = int((t + k * rng.uniform(0.07, 0.12)) * FREQUENCE)
            longueur = int(rng.uniform(0.04, 0.09) * FREQUENCE)
            montee = rng.choice([1, -1]) * rng.uniform(300, 1200)
            phase, amp = 0.0, rng.uniform(0.15, 0.3)
            for j in range(longueur):
                if debut + j >= n:
                    break
                u = j / longueur
                f = base + montee * u + 120 * math.sin(2 * math.pi * 35 * j / FREQUENCE)
                phase += 2 * math.pi * f / FREQUENCE
                sortie[debut + j] += amp * math.sin(phase) * math.sin(math.pi * u) ** 2
        t += rng.uniform(1.2, 3.5)
    return sortie


def _alarme() -> list[float]:
    """Sirène d'alerte : deux montées-descentes de 650 à 1 300 Hz (1,2 s chacune), timbre carré adouci."""
    n, sortie, phase = int(2.4 * FREQUENCE), [], 0.0
    for i in range(n):
        u = (i / FREQUENCE) % 1.2 / 1.2
        f = 650 + 650 * math.sin(math.pi * u)
        phase += 2 * math.pi * f / FREQUENCE
        s = math.sin(phase) + 0.33 * math.sin(3 * phase) + 0.2 * math.sin(5 * phase)
        sortie.append(0.45 * s)
    fondu = int(0.04 * FREQUENCE)
    for i in range(fondu):
        sortie[i] *= i / fondu
        sortie[-1 - i] *= i / fondu
    return sortie


def ambiance(nom: str, duree_s: float) -> Path:
    """Fichier d'ambiance synthétisée (mis en cache par nom et durée arrondie à la seconde).
    « alarme » est un effet ponctuel de durée fixe (2,4 s)."""
    if nom == "alarme":
        chemin = CACHE / "effet_alarme.wav"
        return chemin if chemin.is_file() else _ecrire_wav(chemin, _alarme())
    duree = int(math.ceil(duree_s)) + 1
    chemin = CACHE / f"ambiance_{nom}_{duree}s.wav"
    if chemin.is_file():
        return chemin
    n, rng = duree * FREQUENCE, random.Random(f"{nom}-{duree}")
    if nom == "vent":
        mix = _vent(n, rng)
    elif nom == "village":
        vent, oiseaux = _vent(n, rng), _oiseaux(n, rng)
        mix = [0.6 * a + b for a, b in zip(vent, oiseaux)]
    else:
        raise SonInvalide(f"ambiance synthétisée inconnue : {nom}")
    fondu = int(0.8 * FREQUENCE)
    for i in range(fondu):
        mix[i] *= i / fondu
        mix[-1 - i] *= i / fondu
    return _ecrire_wav(chemin, mix)


# ----- résolution ------------------------------------------------------------------------------
def fichier(nom_son: str, variante: int, duree_s: float = 0.0) -> Path | None:
    """Chemin du fichier à jouer, ou None s'il manque sur cette machine."""
    entree = registre().get(nom_son)
    if entree is None:
        raise SonInvalide(f"son inconnu : '{nom_son}' (voir engine/assets/sons/registre.json)")
    choix = entree["fichiers"][variante % len(entree["fichiers"])]
    if choix.startswith("synth:"):
        return ambiance(choix.split(":", 1)[1], duree_s)
    chemin = chemins.RACINE / choix
    return chemin if chemin.is_file() else None


def valider_noms(donnees: dict[str, Any]) -> None:
    connus = registre()
    noms = [s["son"] for s in donnees.get("sons", [])]
    if donnees.get("ambiance"):
        noms.append(donnees["ambiance"]["son"])
    inconnus = sorted({n for n in noms if n not in connus})
    if inconnus:
        raise SonInvalide(f"son(s) inconnu(s) : {', '.join(inconnus)} ; disponibles : {', '.join(sorted(connus))}")


def resoudre(donnees: dict[str, Any] | None, timeline: dict[str, Any]) -> dict[str, Any]:
    """Instants absolus des bruitages de l'habillage + ambiance : {"evenements": [...], "ambiance": {...}}."""
    from .hud import HudInvalide, _instant
    if not donnees:
        return {"evenements": [], "ambiance": None}
    valider_noms(donnees)
    beats = {b["id"]: b for b in timeline["beats"]}
    connus = registre()
    evenements = []
    for i, s in enumerate(donnees.get("sons", [])):
        if s["beat"] not in beats:
            raise SonInvalide(f"sons[{i}] : beat '{s['beat']}' absent de la fiche")
        try:
            t0 = _instant(beats[s["beat"]], s, f"sons[{i}] ({s['son']})")
        except HudInvalide as e:
            raise SonInvalide(str(e)) from e
        volume = s.get("volume", connus[s["son"]]["volume"])
        for k in range(int(s.get("repeter", 1))):
            evenements.append({"son": s["son"], "t": round(t0 + k * float(s.get("intervalle", 0.4)), 3),
                               "volume": volume, "variante": i + k})
    amb = donnees.get("ambiance")
    if amb:
        amb = {"son": amb["son"], "volume": amb.get("volume", connus[amb["son"]]["volume"])}
    return {"evenements": evenements, "ambiance": amb}


# ----- téléchargement des packs Kenney (CC0) ----------------------------------------------------
def telecharger_kenney(packs: list[str] | None = None) -> dict[str, int]:
    """Télécharge les packs audio Kenney par le même chemin que le bouton « Continue without donating »."""
    packs = packs or json.loads(REGISTRE.read_text(encoding="utf-8"))["sources"]["kenney"]["packs"]
    ua = {"User-Agent": "serie-animation-pipeline/1.0 (github.com/l-marque/serie-animation)"}
    ouvreur = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    bilan = {}
    for pack in packs:
        page = f"https://kenney.nl/assets/{pack}"
        ouvreur.open(urllib.request.Request(page, headers=ua), timeout=30).read()
        lien = json.loads(ouvreur.open(urllib.request.Request(
            f"https://kenney.nl/download-link/{('assets/' + pack).encode().hex()}", headers={**ua, "Referer": page}),
            timeout=30).read())["url"]
        archive = zipfile.ZipFile(io.BytesIO(ouvreur.open(urllib.request.Request(lien, headers=ua), timeout=120).read()))
        dossier = DOSSIER_KENNEY / pack
        dossier.mkdir(parents=True, exist_ok=True)
        n = 0
        for nom in archive.namelist():
            p = Path(nom)
            if ".." in p.parts or not (p.suffix.lower() in (".ogg", ".wav") or p.name.lower().startswith("license")):
                continue
            (dossier / p.name).write_bytes(archive.read(nom))  # à plat : aucun chemin de l'archive n'est suivi
            n += 1
        bilan[pack] = n
    return bilan


def verifier() -> dict[str, list[str]]:
    """Sons du registre dont un fichier manque sur cette machine."""
    manquants = {}
    for nom, e in registre().items():
        absents = [f for f in e["fichiers"] if not f.startswith("synth:") and not (chemins.RACINE / f).is_file()]
        if absents:
            manquants[nom] = absents
    return manquants


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sons", description="Bibliothèque de sons du pipeline.")
    sp = p.add_subparsers(dest="cmd", required=True)
    sp.add_parser("telecharger", help="télécharge les packs audio Kenney (CC0)")
    sp.add_parser("verifier", help="liste les fichiers manquants")
    sp.add_parser("liste", help="liste les sons disponibles")
    args = p.parse_args(argv)
    if args.cmd == "telecharger":
        print(json.dumps(telecharger_kenney(), indent=2))
    elif args.cmd == "verifier":
        manquants = verifier()
        print(json.dumps(manquants, ensure_ascii=False, indent=2) if manquants else "tous les sons sont présents")
        return 1 if manquants else 0
    else:
        for nom, e in sorted(registre().items()):
            print(f"{nom:18} {e['categorie']:11} {e['description']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
