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


def ajouter_voix(donnees: dict[str, Any], moteur: str, voix: str | None = None,
                 interpreteur: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """Renvoie (copie de la fiche avec voix_audio, compte rendu). Lève VoixErreur si la synthèse échoue."""
    if moteur not in MOTEURS:
        raise VoixErreur(f"moteur de voix inconnu : {moteur} ({', '.join(MOTEURS)})")
    sortie = copy.deepcopy(donnees)
    compte_rendu: dict[str, Any] = {"moteur": moteur, "synthetisees": [], "depuis_cache": [], "deja_fournies": []}
    if moteur == "aucune":
        return sortie, compte_rendu
    voix = voix or (VOIX_KYUTAI_DEFAUT if moteur == "kyutai" else "systeme")
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
