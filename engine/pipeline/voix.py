"""Module Voix : produit la voix off de chaque beat et ses mots horodatés, avant la timeline.

Moteurs :
    kyutai   Kyutai TTS (kyutai/tts-1.6b-en_fr, CC-BY 4.0), dans l'environnement Python qui a PyTorch
             et moshi (variable TTS_PYTHON ou option --python-tts). Mots horodatés par le modèle.
    windows  voix système de Windows (System.Speech), sans installation ; qualité moyenne, mots
             estimés. Secours quand Kyutai n'est pas installé.
    aucune   pas de voix (vidéo muette, comme avant).

Le résultat de chaque beat est mis en cache selon (moteur, voix, texte) : une phrase inchangée
n'est jamais resynthétisée. La fiche n'est pas modifiée sur disque ; le module renvoie une copie
dont chaque beat parlé reçoit `voix_audio` (contrat : fichier, duree_s, mots).
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any

from . import chemins

MOTEURS = ("kyutai", "windows", "aucune")
VOIX_KYUTAI_DEFAUT = "unmute-prod-website/fabieng-enhanced-v2.wav"
WORKER_KYUTAI = chemins.MOTEUR / "voix" / "kyutai_worker.py"
DOSSIER_CACHE = chemins.RACINE / "renders" / "_cache_voix"


class VoixErreur(Exception):
    pass


def python_tts(explicite: str | None = None) -> str | None:
    """Interpréteur Python qui a PyTorch et moshi : option, puis TTS_PYTHON, puis .env."""
    if explicite:
        return explicite
    if os.environ.get("TTS_PYTHON"):
        return os.environ["TTS_PYTHON"]
    env = chemins.RACINE / ".env"
    if env.is_file():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            if ligne.strip().startswith("TTS_PYTHON="):
                return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _cle(moteur: str, voix: str, texte: str) -> str:
    return hashlib.sha256(f"{moteur}|{voix}|{texte.strip()}".encode("utf-8")).hexdigest()[:16]


def _duree_wav(chemin: Path) -> float:
    with wave.open(str(chemin), "rb") as w:
        return w.getnframes() / w.getframerate()


def _mots_estimes(texte: str, duree: float) -> list[dict[str, Any]]:
    mots = texte.split()
    poids = [len(m) + 1 for m in mots]
    total = sum(poids) or 1
    t, sortie = 0.0, []
    for m, p in zip(mots, poids):
        d = duree * p / total
        sortie.append({"mot": m, "debut": round(t, 3), "fin": round(t + d, 3)})
        t += d
    return sortie


def _synthese_kyutai(phrases: list[dict[str, str]], voix: str, interpreteur: str, dossier: Path) -> dict[str, dict]:
    with tempfile.TemporaryDirectory() as tmp:
        travail = Path(tmp) / "travail.json"
        travail.write_text(json.dumps({"voix": voix, "dossier": str(dossier), "appareil": "auto",
                                       "phrases": phrases}, ensure_ascii=False), encoding="utf-8")
        res = subprocess.run([interpreteur, str(WORKER_KYUTAI), str(travail)], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if res.returncode != 0:
        raise VoixErreur(f"Kyutai a échoué (code {res.returncode}) : {res.stderr.strip()[-1200:]}")
    resultat = json.loads((dossier / "resultat.json").read_text(encoding="utf-8"))
    return {p["id"]: p for p in resultat["phrases"]}


_SCRIPT_WINDOWS = r"""
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$fr = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'fr-*' } | Select-Object -First 1
if ($fr) { $s.SelectVoice($fr.VoiceInfo.Name) }
$s.SetOutputToWaveFile($args[1])
$s.Speak([IO.File]::ReadAllText($args[0], [Text.Encoding]::UTF8))
$s.Dispose()
"""


def _synthese_windows(phrases: list[dict[str, str]], dossier: Path) -> dict[str, dict]:
    if sys.platform != "win32":
        raise VoixErreur("le moteur 'windows' ne fonctionne que sous Windows")
    sortie = {}
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "dire.ps1"
        script.write_text(_SCRIPT_WINDOWS, encoding="utf-8")
        for p in phrases:
            texte = Path(tmp) / f"{p['id']}.txt"
            texte.write_text(p["texte"], encoding="utf-8")
            wav = dossier / f"{p['id']}.wav"
            res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                                  str(texte), str(wav)], capture_output=True, text=True)
            if res.returncode != 0 or not wav.is_file():
                raise VoixErreur(f"voix Windows : échec pour {p['id']} : {res.stderr.strip()[-600:]}")
            duree = _duree_wav(wav)
            sortie[p["id"]] = {"fichier": str(wav), "duree_s": round(duree, 3),
                               "mots": _mots_estimes(p["texte"], duree), "origine_mots": "estimation"}
    return sortie


def voix_du_pack(nom_pack: str) -> str | None:
    """Voix choisie pour la série, rangée dans le pack de DA (`voix_off.kyutai`), si elle existe."""
    chemin = chemins.PACKS_DA / f"{nom_pack}.json"
    if not chemin.is_file():
        return None
    return (json.loads(chemin.read_text(encoding="utf-8")).get("voix_off") or {}).get("kyutai")


def ajouter_voix(donnees: dict[str, Any], moteur: str, voix: str | None = None,
                 interpreteur: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Renvoie (copie de la fiche avec voix_audio, compte rendu). Lève VoixErreur si la synthèse échoue.

    Voix utilisée : celle passée en argument, sinon celle du pack de DA, sinon la voix par défaut."""
    if moteur not in MOTEURS:
        raise VoixErreur(f"moteur de voix inconnu : {moteur} ({', '.join(MOTEURS)})")
    sortie = copy.deepcopy(donnees)
    compte_rendu: dict[str, Any] = {"moteur": moteur, "synthetisees": [], "depuis_cache": [], "deja_fournies": []}
    if moteur == "aucune":
        return sortie, compte_rendu
    if moteur == "kyutai":
        voix = voix or voix_du_pack(donnees.get("pack_da", "")) or VOIX_KYUTAI_DEFAUT
    else:
        voix = voix or "systeme"
    if moteur == "kyutai":
        interpreteur = python_tts(interpreteur)
        if not interpreteur:
            raise VoixErreur("Kyutai : interpréteur introuvable ; indique TTS_PYTHON=<chemin de python.exe "
                             "avec torch et moshi> dans .env, ou utilise --voix windows")
    compte_rendu["voix"] = voix
    DOSSIER_CACHE.mkdir(parents=True, exist_ok=True)

    a_synthetiser = []
    for b in sortie["beats"]:
        texte = (b.get("voix") or "").strip()
        if not texte:
            continue
        if b.get("voix_audio"):  # voix enregistrée ou fournie par un humain : on n'y touche pas
            compte_rendu["deja_fournies"].append(b["id"])
            continue
        cle = _cle(moteur, voix, texte)
        meta = DOSSIER_CACHE / f"{cle}.json"
        if meta.is_file() and (DOSSIER_CACHE / f"{cle}.wav").is_file():
            b["voix_audio"] = json.loads(meta.read_text(encoding="utf-8"))
            compte_rendu["depuis_cache"].append(b["id"])
        else:
            a_synthetiser.append({"id": cle, "texte": texte, "beat": b["id"]})

    if a_synthetiser:
        phrases = [{"id": p["id"], "texte": p["texte"]} for p in a_synthetiser]
        if moteur == "kyutai":
            resultats = _synthese_kyutai(phrases, voix, interpreteur, DOSSIER_CACHE)
        else:
            resultats = _synthese_windows(phrases, DOSSIER_CACHE)
        par_beat = {b["id"]: b for b in sortie["beats"]}
        for p in a_synthetiser:
            r = resultats[p["id"]]
            audio = {"fichier": str(DOSSIER_CACHE / f"{p['id']}.wav"), "duree_s": r["duree_s"], "mots": r["mots"]}
            (DOSSIER_CACHE / f"{p['id']}.json").write_text(json.dumps(audio, ensure_ascii=False), encoding="utf-8")
            par_beat[p["beat"]]["voix_audio"] = audio
            compte_rendu["synthetisees"].append({"beat": p["beat"], "duree_s": r["duree_s"],
                                                 "mots": r.get("origine_mots", "estimation")})
    return sortie, compte_rendu


def copier_dans(donnees: dict[str, Any], dossier: Path) -> None:
    """Copie les fichiers de voix à côté du rendu (le cache peut être vidé sans casser un épisode)."""
    cible = dossier / "voix"
    cible.mkdir(parents=True, exist_ok=True)
    for b in donnees["beats"]:
        audio = b.get("voix_audio")
        if audio and Path(audio["fichier"]).is_file() and Path(audio["fichier"]).parent == DOSSIER_CACHE:
            dest = cible / f"{b['id']}.wav"
            shutil.copyfile(audio["fichier"], dest)
            audio["fichier"] = str(dest)


# ----- audition : écouter plusieurs voix sur la même phrase ----------------------------------
VOIX_FR_CANDIDATES = [
    "unmute-prod-website/fabieng-enhanced-v2.wav",
    "unmute-prod-website/developpeuse-3.wav",
    "unmute-prod-website/default_voice.wav",
] + [f"cml-tts/fr/{c}_enhanced.wav" for c in (
    "10087_11650_000028-0002", "10177_10625_000134-0003", "10179_11051_000005-0001", "12080_11650_000047-0001",
    "12205_11650_000004-0002", "12977_10625_000037-0001", "1406_1028_000009-0003", "1591_1028_000108-0004",
    "1770_1028_000036-0002", "2114_1656_000053-0001", "2154_2576_000020-0003", "2216_1745_000007-0001",
    "2223_1745_000009-0002", "2465_1943_000152-0002", "296_1028_000022-0001", "3267_1902_000075-0001",
    "4193_3103_000004-0001", "4482_3103_000063-0001", "4724_3731_000031-0001", "4937_3731_000004-0001",
    "5207_3078_000031-0002", "5476_3103_000072-0001", "577_394_000070-0001", "5790_4893_000052-0001",
    "579_2548_000015-0001", "5830_4703_000037-0001", "6318_7016_000027-0002", "7142_2432_000124-0003",
    "7400_2928_000100-0001", "7591_6742_000149-0002", "7601_7727_000062-0001", "7762_8734_000048-0002",
    "8128_7016_000047-0002", "928_486_000075-0001", "9834_9697_000150-0003")]


def audition(texte: str, dossier: Path, voix: list[str] | None = None, interpreteur: str | None = None) -> Path:
    """Synthétise `texte` avec chaque voix (par défaut : les voix françaises du dépôt Kyutai) dans
    `dossier/vNN.wav`, écrit `dossier/correspondance.json` et `dossier/audition.wav` (toutes les voix
    à la suite, séparées par un bip : 1 bip avant la voix 1, etc. ; le numéro est dans la liste)."""
    voix = voix or VOIX_FR_CANDIDATES
    interpreteur = python_tts(interpreteur)
    if not interpreteur:
        raise VoixErreur("audition : TTS_PYTHON introuvable")
    dossier.mkdir(parents=True, exist_ok=True)
    corr = {f"v{i:02d}": v for i, v in enumerate(voix, 1)}
    phrases = [{"id": vid, "texte": texte, "voix": v} for vid, v in corr.items()]
    _synthese_kyutai(phrases, voix[0], interpreteur, dossier)
    (dossier / "correspondance.json").write_text(json.dumps(corr, ensure_ascii=False, indent=2), encoding="utf-8")
    return _assembler_audition(dossier, list(corr))


def _assembler_audition(dossier: Path, ids: list[str]) -> Path:
    import math
    import struct
    frequence = None
    sortie = bytearray()
    for vid in ids:
        f = dossier / f"{vid}.wav"
        if not f.is_file():
            continue
        with wave.open(str(f), "rb") as w:
            frequence = frequence or w.getframerate()
            donnees = w.readframes(w.getnframes())
        bip = b"".join(struct.pack("<h", int(8000 * math.sin(2 * math.pi * 880 * i / frequence)))
                       for i in range(int(0.12 * frequence)))
        silence = b"\0\0" * int(0.35 * frequence)
        sortie += silence + bip + silence + donnees
    chemin = dossier / "audition.wav"
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(frequence or 24000)
        w.writeframes(bytes(sortie))
    return chemin


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="voix", description="Outils voix off (Kyutai).")
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("audition", help="écouter plusieurs voix sur la même phrase")
    a.add_argument("texte")
    a.add_argument("--sortie", type=Path, default=chemins.RACINE / "renders" / "audition_voix")
    a.add_argument("--voix", nargs="*", help="voix à comparer (défaut : toutes les voix françaises)")
    a.add_argument("--python-tts")
    args = p.parse_args(argv)
    try:
        chemin = audition(args.texte, args.sortie, args.voix, args.python_tts)
    except VoixErreur as e:
        print(json.dumps({"erreur": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps({"audition": str(chemin), "correspondance": str(args.sortie / "correspondance.json")},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
