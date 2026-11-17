"""Module Voix : produit la voix off de chaque beat et ses mots horodatés, avant la timeline.

Moteurs :
    kyutai   Kyutai TTS (kyutai/tts-1.6b-en_fr, CC-BY 4.0), dans l'environnement Python qui a PyTorch
             et moshi (variable TTS_PYTHON ou option --python-tts). Mots horodatés par le modèle.
    qwen     Qwen3-TTS (Alibaba Qwen, Apache 2.0), voix « dylan » du modèle CustomVoice : jeu dirigé phrase par
             phrase par des consignes en français (prod-directeur-voix), débit visé en mots par minute ;
             environnement QWEN_PYTHON (.env) ou ~/venvs/qwen-tts. Réglages : pack de DA (voix_off.qwen).
             Voix choisie le 2026-11-17 à la place de Zonos. Mots estimés.
    zonos    Zonos (Zyphra, Zonos-v0.1-transformer, Apache 2.0) : voix expressive réglée par émotions,
             timbre copié d'un court enregistrement de référence ; environnement ZONOS_PYTHON (.env) ou
             ~/venvs/zonos-tts. Réglages dans le pack de DA (voix_off.zonos). Mots estimés.
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

MOTEURS = ("kyutai", "qwen", "zonos", "windows", "aucune")
VOIX_KYUTAI_DEFAUT = "unmute-prod-website/fabieng-enhanced-v2.wav"
WORKER_KYUTAI = chemins.MOTEUR / "voix" / "kyutai_worker.py"
WORKER_ZONOS = chemins.MOTEUR / "voix" / "zonos_worker.py"
WORKER_QWEN = chemins.MOTEUR / "voix" / "qwen_worker.py"
QWEN_DEFAUT = {"modele": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "locuteur": "dylan", "langue": "French",
               "consigne": ("Narrateur de Reel en français, énergique et captivant : ton vivant, intonations très marquées, "
                            "la voix monte et descend, appuie les mots importants, enchaîne les phrases sans traîner."),
               "essais": 6, "seuil_transcription": 0.9, "mots_par_minute": 180, "expressivite_min": 4.8, "graine": 7}
# Émotions nommées du directeur de voix -> consignes de jeu Qwen (en français).
CONSIGNES_EMOTION = {
    "conteur": "Ton de conteur chaleureux, vivant, qui captive.",
    "neutre": "Ton neutre et clair.",
    "joyeux": "Ton joyeux et souriant, on entend le sourire.",
    "enthousiaste": "Avec beaucoup d'enthousiasme et d'énergie, la voix monte sur la fin.",
    "triste": "Ton triste et doux, la voix retombe sur la fin.",
    "nostalgique": "Ton nostalgique, un peu suspendu, comme un souvenir.",
    "mysterieux": "Ton mystérieux, en retenue, qui crée du suspense.",
    "surpris": "Ton surpris et émerveillé.",
    "determine": "Ton déterminé et assuré, qui relance l'histoire.",
    "complice": "Ton complice et chaleureux, comme si on parlait à un ami.",
}
ZONOS_DEFAUT = {"reference": "engine/voix/references/narrateur_fr.wav", "langue": "fr-fr",
                "emotion": [0.45, 0.15, 0.02, 0.05, 0.2, 0.02, 0.1, 0.35], "debit": 16.0,
                "variation_hauteur": 110.0, "graine": 3, "essais": 8,
                "syllabes_par_s": 6.0, "seuil_transcription": 0.8}
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


def python_zonos() -> str | None:
    """Interpréteur qui a zonos : ZONOS_PYTHON (environnement ou .env), sinon ~/venvs/zonos-tts."""
    if os.environ.get("ZONOS_PYTHON"):
        return os.environ["ZONOS_PYTHON"]
    env = chemins.RACINE / ".env"
    if env.is_file():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            if ligne.strip().startswith("ZONOS_PYTHON="):
                return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    defaut = Path.home() / "venvs" / "zonos-tts" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    return str(defaut) if defaut.is_file() else None


_ENV_MSVC: dict[str, str] | None = None


def env_msvc() -> dict[str, str] | None:
    """Variables d'environnement du compilateur C++ de Visual Studio (vcvars64), si Build Tools est installé.

    Zonos les utilise pour compiler son décodeur (torch.compile + Triton) : génération bien plus rapide."""
    global _ENV_MSVC
    if _ENV_MSVC is not None or sys.platform != "win32":
        return _ENV_MSVC or None
    vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft Visual Studio/Installer/vswhere.exe"
    if not vswhere.is_file():
        _ENV_MSVC = {}
        return None
    res = subprocess.run([str(vswhere), "-latest", "-products", "*", "-requires",
                          "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"],
                         capture_output=True, text=True)
    racine_vs = res.stdout.strip().splitlines()[0] if res.stdout.strip() else ""
    vcvars = Path(racine_vs) / "VC/Auxiliary/Build/vcvars64.bat"
    if not vcvars.is_file():
        _ENV_MSVC = {}
        return None
    res = subprocess.run(f'"{vcvars}" >nul && set', shell=True, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    _ENV_MSVC = dict(l.split("=", 1) for l in res.stdout.splitlines() if "=" in l) if res.returncode == 0 else {}
    return _ENV_MSVC or None


def python_qwen() -> str | None:
    """Interpréteur qui a qwen-tts : QWEN_PYTHON (environnement ou .env), sinon ~/venvs/qwen-tts."""
    if os.environ.get("QWEN_PYTHON"):
        return os.environ["QWEN_PYTHON"]
    env = chemins.RACINE / ".env"
    if env.is_file():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            if ligne.strip().startswith("QWEN_PYTHON="):
                return ligne.split("=", 1)[1].strip().strip('"').strip("'")
    defaut = Path.home() / "venvs" / "qwen-tts" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    return str(defaut) if defaut.is_file() else None


def reglages_qwen(nom_pack: str) -> dict[str, Any]:
    chemin = chemins.PACKS_DA / f"{nom_pack}.json"
    pack = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
    return {**QWEN_DEFAUT, **((pack.get("voix_off") or {}).get("qwen") or {})}


def nom_voix_qwen(reglages: dict[str, Any]) -> str:
    son = {k: reglages.get(k) for k in ("modele", "locuteur", "langue", "consigne", "graine")}
    return "qwen:" + hashlib.sha256(json.dumps(son, sort_keys=True).encode()).hexdigest()[:12]


def _synthese_qwen(phrases: list[dict[str, Any]], reglages: dict[str, Any], interpreteur: str,
                   dossier: Path) -> dict[str, dict]:
    with tempfile.TemporaryDirectory() as tmp:
        travail = Path(tmp) / "travail.json"
        travail.write_text(json.dumps({**reglages, "dossier": str(dossier), "phrases": phrases}, ensure_ascii=False),
                           encoding="utf-8")
        res = subprocess.run([interpreteur, "-I", str(WORKER_QWEN), str(travail)], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    if res.returncode != 0:
        raise VoixErreur(f"Qwen a échoué (code {res.returncode}) : {res.stderr.strip()[-1200:]}")
    resultat = json.loads((dossier / "resultat.json").read_text(encoding="utf-8"))
    return {p["id"]: p for p in resultat["phrases"]}


def reglages_zonos(nom_pack: str) -> dict[str, Any]:
    chemin = chemins.PACKS_DA / f"{nom_pack}.json"
    pack = json.loads(chemin.read_text(encoding="utf-8")) if chemin.is_file() else {}
    return {**ZONOS_DEFAUT, **((pack.get("voix_off") or {}).get("zonos") or {})}


REGLAGES_SON_ZONOS = ("reference", "langue", "emotion", "debit", "variation_hauteur", "graine")


def nom_voix_zonos(reglages: dict[str, Any]) -> str:
    """Identifiant de voix pour le cache : seuls les réglages qui changent le son comptent. Les réglages
    de sélection (essais, seuil_transcription, syllabes_par_s, verificateur) n'invalident pas le cache."""
    son = {k: reglages.get(k) for k in REGLAGES_SON_ZONOS}
    return "zonos:" + hashlib.sha256(json.dumps(son, sort_keys=True).encode()).hexdigest()[:12]


def moteur_du_pack(nom_pack: str) -> str | None:
    """Moteur de voix choisi pour la série (`voix_off.moteur` du pack de DA), s'il est indiqué."""
    chemin = chemins.PACKS_DA / f"{nom_pack}.json"
    if not chemin.is_file():
        return None
    return (json.loads(chemin.read_text(encoding="utf-8")).get("voix_off") or {}).get("moteur")


def _synthese_zonos(phrases: list[dict[str, str]], reglages: dict[str, Any], interpreteur: str,
                    dossier: Path) -> dict[str, dict]:
    ref = Path(reglages["reference"])
    if not ref.is_absolute():
        ref = chemins.RACINE / ref
    with tempfile.TemporaryDirectory() as tmp:
        travail = Path(tmp) / "travail.json"
        msvc = env_msvc()
        travail.write_text(json.dumps({**reglages, "reference": str(ref), "dossier": str(dossier),
                                       "compiler": bool(msvc), "phrases": phrases}, ensure_ascii=False),
                           encoding="utf-8")
        env = dict(msvc or os.environ, PYTHONIOENCODING="utf-8")
        res = subprocess.run([interpreteur, "-I", str(WORKER_ZONOS), str(travail)], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", env=env)
    if res.returncode != 0:
        raise VoixErreur(f"Zonos a échoué (code {res.returncode}) : {res.stderr.strip()[-1200:]}")
    resultat = json.loads((dossier / "resultat.json").read_text(encoding="utf-8"))
    return {p["id"]: p for p in resultat["phrases"]}


# Émotions nommées -> vecteur Zonos [bonheur, tristesse, dégoût, peur, surprise, colère, autre, neutre].
EMOTIONS = {
    "conteur": [0.45, 0.15, 0.02, 0.05, 0.2, 0.02, 0.1, 0.35],
    "neutre": [0.15, 0.05, 0.02, 0.02, 0.05, 0.02, 0.1, 0.8],
    "joyeux": [0.85, 0.02, 0.02, 0.02, 0.25, 0.02, 0.1, 0.15],
    "enthousiaste": [0.8, 0.02, 0.02, 0.02, 0.5, 0.05, 0.1, 0.1],
    "triste": [0.05, 0.75, 0.02, 0.05, 0.02, 0.02, 0.1, 0.3],
    "nostalgique": [0.3, 0.5, 0.02, 0.02, 0.05, 0.02, 0.15, 0.4],
    "mysterieux": [0.1, 0.15, 0.02, 0.3, 0.3, 0.02, 0.2, 0.4],
    "surpris": [0.4, 0.02, 0.02, 0.1, 0.8, 0.02, 0.1, 0.1],
    "determine": [0.4, 0.02, 0.02, 0.02, 0.1, 0.3, 0.1, 0.3],
    "complice": [0.65, 0.05, 0.02, 0.02, 0.2, 0.02, 0.2, 0.3],
}
CHAMPS_VOIX_BEAT = ("emotion", "debit", "variation_hauteur", "mots_par_minute")


def fichier_reglages_voix(source: Path | None) -> Path | None:
    """`<fiche>.voix.json` à côté de la fiche : réglages de voix phrase par phrase (prod-directeur-voix)."""
    if source is None:
        return None
    chemin = Path(source).with_name(f"{Path(source).stem}.voix.json")
    return chemin if chemin.is_file() else None


def charger_reglages_voix(source: Path | None) -> dict[str, dict[str, Any]]:
    """Lit `<fiche>.voix.json` : {"version": "1.0", "mots_par_minute": 120 (facultatif, tout l'épisode),
    "beats": {"b02": {"intention": "...", "emotion": "triste" | [8 nombres], "debit": 14, "variation_hauteur": 80,
    "mots_par_minute": 110, "pause_apres_s": 0.2}}}. Les émotions nommées sont converties en vecteur ;
    le débit de tout l'épisode est rendu sous la clé "*"."""
    chemin = fichier_reglages_voix(source)
    if chemin is None:
        return {}
    contenu = json.loads(chemin.read_text(encoding="utf-8"))
    brut = contenu.get("beats", {})
    sortie = {}
    if contenu.get("mots_par_minute"):               # débit cible de tout l'épisode
        sortie["*"] = {"mots_par_minute": float(contenu["mots_par_minute"])}
    for bid, r in brut.items():
        r = dict(r)
        emo = r.get("emotion")
        if isinstance(emo, str):
            r["emotion_nom"] = emo
            if emo not in EMOTIONS:
                raise VoixErreur(f"{chemin.name} : beat {bid} : émotion inconnue « {emo} » ({', '.join(EMOTIONS)})")
            r["emotion"] = EMOTIONS[emo]
        elif emo is not None and (len(emo) != 8 or not all(0 <= float(x) <= 1 for x in emo)):
            raise VoixErreur(f"{chemin.name} : beat {bid} : « emotion » = un nom ou 8 nombres entre 0 et 1")
        sortie[bid] = r
    return sortie


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
                 interpreteur: str | None = None,
                 reglages_beats: dict[str, dict[str, Any]] | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
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
    elif moteur == "qwen":
        reglages = reglages_qwen(donnees.get("pack_da", ""))
        voix = voix or nom_voix_qwen(reglages)
        interpreteur = python_qwen()
        if not interpreteur:
            raise VoixErreur("Qwen : interpréteur introuvable ; indique QWEN_PYTHON=<python.exe avec qwen-tts> dans .env")
    elif moteur == "zonos":
        reglages = reglages_zonos(donnees.get("pack_da", ""))
        voix = voix or nom_voix_zonos(reglages)
        interpreteur = python_zonos()
        if not interpreteur:
            raise VoixErreur("Zonos : interpréteur introuvable ; indique ZONOS_PYTHON=<python.exe avec zonos> dans .env")
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
        fusion = {**(reglages_beats or {}).get("*", {}), **(reglages_beats or {}).get(b["id"], {})}
        if moteur == "zonos":
            propres = {k: v for k, v in fusion.items() if k in CHAMPS_VOIX_BEAT}
        elif moteur == "qwen":
            propres = {k: v for k, v in fusion.items() if k in ("mots_par_minute", "expressivite_min")}
            consigne = fusion.get("consigne") or CONSIGNES_EMOTION.get(fusion.get("emotion_nom", ""), "")
            if consigne:
                propres["consigne"] = (reglages["consigne"] + " " + consigne).strip()
        else:
            propres = {}
        cle = _cle(moteur, voix + ("|" + json.dumps(propres, sort_keys=True) if propres else ""), texte)
        meta = DOSSIER_CACHE / f"{cle}.json"
        if meta.is_file() and (DOSSIER_CACHE / f"{cle}.wav").is_file():
            b["voix_audio"] = json.loads(meta.read_text(encoding="utf-8"))
            compte_rendu["depuis_cache"].append(b["id"])
        else:
            a_synthetiser.append({"id": cle, "texte": texte, "beat": b["id"], **propres})

    if a_synthetiser:
        phrases = [{k: v for k, v in p.items() if k != "beat"} for p in a_synthetiser]
        if moteur == "kyutai":
            resultats = _synthese_kyutai(phrases, voix, interpreteur, DOSSIER_CACHE)
        elif moteur == "qwen":
            resultats = _synthese_qwen(phrases, reglages, interpreteur, DOSSIER_CACHE)
        elif moteur == "zonos":
            resultats = _synthese_zonos(phrases, reglages, interpreteur, DOSSIER_CACHE)
        else:
            resultats = _synthese_windows(phrases, DOSSIER_CACHE)
        par_beat = {b["id"]: b for b in sortie["beats"]}
        for p in a_synthetiser:
            r = resultats[p["id"]]
            audio = {"fichier": str(DOSSIER_CACHE / f"{p['id']}.wav"), "duree_s": r["duree_s"], "mots": r["mots"]}
            (DOSSIER_CACHE / f"{p['id']}.json").write_text(json.dumps(audio, ensure_ascii=False), encoding="utf-8")
            par_beat[p["beat"]]["voix_audio"] = audio
            entree = {"beat": p["beat"], "duree_s": r["duree_s"], "mots": r.get("origine_mots", "estimation")}
            for champ in ("mots_par_minute", "expressivite_st"):
                if champ in r:
                    entree[champ] = r[champ]
            if "transcription" in r:
                entree.update(transcription=r["transcription"], similarite=r["similarite"])
            compte_rendu["synthetisees"].append(entree)

    # Pause voulue après une phrase (prod-directeur-voix) : durée du plan = avance + voix + pause,
    # sauf si la fiche impose déjà duree_s.
    for b in sortie["beats"]:
        pause = (reglages_beats or {}).get(b["id"], {}).get("pause_apres_s")
        if pause is not None and b.get("voix_audio") and "duree_s" not in b:
            b["duree_s"] = round(0.15 + b["voix_audio"]["duree_s"] + float(pause), 3)
    vitesse = vitesse_du_pack(donnees.get("pack_da", ""))
    if abs(vitesse - 1.0) > 1e-3:
        compte_rendu["vitesse"] = vitesse
        for b in sortie["beats"]:
            if b.get("voix_audio") and b["id"] not in compte_rendu["deja_fournies"]:
                b["voix_audio"] = _accelerer(b["voix_audio"], vitesse)
    return sortie, compte_rendu


def vitesse_du_pack(nom_pack: str) -> float:
    """Débit de la voix (`voix_off.vitesse` du pack de DA) : 1,0 = débit du modèle, 1,2 = 20 % plus rapide."""
    chemin = chemins.PACKS_DA / f"{nom_pack}.json"
    if not chemin.is_file():
        return 1.0
    return float((json.loads(chemin.read_text(encoding="utf-8")).get("voix_off") or {}).get("vitesse", 1.0))


def _accelerer(audio: dict[str, Any], vitesse: float) -> dict[str, Any]:
    """Version accélérée (sans changer la hauteur, filtre ffmpeg atempo) d'une voix du cache, elle-même
    mise en cache ; les instants des mots sont divisés par la vitesse."""
    source = Path(audio["fichier"])
    cle = hashlib.sha256(f"{source.name}|{vitesse:.3f}".encode("utf-8")).hexdigest()[:16]
    wav, meta = DOSSIER_CACHE / f"{cle}.wav", DOSSIER_CACHE / f"{cle}.json"
    if meta.is_file() and wav.is_file():
        return json.loads(meta.read_text(encoding="utf-8"))
    res = subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(source), "-filter:a", f"atempo={vitesse:.3f}",
                          str(wav)], capture_output=True, text=True)
    if res.returncode != 0 or not wav.is_file():
        raise VoixErreur(f"accélération de la voix impossible ({source.name}) : {res.stderr.strip()[-400:]}")
    accelere = {"fichier": str(wav), "duree_s": round(_duree_wav(wav), 3),
                "mots": [{**m, "debut": round(m["debut"] / vitesse, 3), "fin": round(m["fin"] / vitesse, 3)}
                         for m in audio.get("mots", [])]}
    meta.write_text(json.dumps(accelere, ensure_ascii=False), encoding="utf-8")
    return accelere


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
