"""Synthèse vocale Kyutai TTS (kyutai/tts-1.6b-en_fr), exécutée dans l'environnement Python qui a
PyTorch et moshi. Script autonome : il n'importe rien du dépôt, car le pipeline tourne dans un autre
environnement (sans PyTorch).

Entrée : un fichier JSON de travail
    {"voix": "unmute-prod-website/fabieng-enhanced-v2.wav", "dossier": "<sortie>",
     "appareil": "auto" | "cuda" | "cpu", "cfg": 2.0,
     "phrases": [{"id": "b1", "texte": "..."}]}
Sortie : <dossier>/<id>.wav (mono, fréquence de Mimi) pour chaque phrase, et <dossier>/resultat.json
    {"frequence": 24000, "appareil": "cpu", "phrases": [{"id", "fichier", "duree_s", "mots": [...],
     "origine_mots": "kyutai" | "estimation", "secondes_calcul"}]}

Les mots sont horodatés à partir de `TTSResult.all_transcripts` (étape de génération de chaque mot,
convertie en secondes à la fréquence d'images de Mimi), puis recalés sur le début réel de la parole.
"""

from __future__ import annotations

import json
import os
import sys
import time
import wave
from pathlib import Path

# moshi compile certaines fonctions avec torch.compile, qui exige un compilateur C++ (cl.exe sous
# Windows). Sans gain notable ici : on le désactive avant d'importer moshi.
os.environ.setdefault("NO_TORCH_COMPILE", "1")
os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")  # certaines fonctions de moshi utilisent torch.compile directement

import numpy as np  # noqa: E402
import torch  # noqa: E402

from moshi.models.loaders import CheckpointInfo  # noqa: E402
from moshi.models.tts import DEFAULT_DSM_TTS_REPO, TTSModel  # noqa: E402

SEUIL_SILENCE = 0.02  # amplitude sous laquelle un échantillon est considéré comme du silence


def _ecrire_wav(chemin: Path, pcm: np.ndarray, frequence: int) -> None:
    donnees = (np.clip(pcm, -1.0, 1.0) * 32767).astype("<i2")
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(frequence)
        w.writeframes(donnees.tobytes())


def _rogner(pcm: np.ndarray, frequence: int) -> tuple[np.ndarray, float]:
    """Retire le silence au début et à la fin (en gardant 50 ms) ; renvoie aussi le décalage de début."""
    actifs = np.flatnonzero(np.abs(pcm) > SEUIL_SILENCE)
    if actifs.size == 0:
        return pcm, 0.0
    marge = int(0.05 * frequence)
    debut = max(0, actifs[0] - marge)
    fin = min(pcm.size, actifs[-1] + marge)
    return pcm[debut:fin], debut / frequence


def _mots_estimes(texte: str, duree: float) -> list[dict]:
    mots = texte.split()
    poids = [len(m) + 1 for m in mots]
    total = sum(poids) or 1
    t, sortie = 0.0, []
    for m, p in zip(mots, poids):
        d = duree * p / total
        sortie.append({"mot": m, "debut": round(t, 3), "fin": round(t + d, 3)})
        t += d
    return sortie


def _mots_kyutai(transcript, texte: str, frame_rate: float, decalage: float, duree: float) -> list[dict] | None:
    """Convertit [(mot, étape), ...] en horodatage ; None si le résultat n'est pas exploitable."""
    if not transcript:
        return None
    paires = [(str(m).strip(), float(e) / frame_rate - decalage) for m, e in transcript if str(m).strip()]
    if len(paires) != len(texte.split()):
        return None  # découpage différent du texte : on ne peut pas associer mot à mot de façon sûre
    mots_texte = texte.split()
    sortie = []
    for i, ((_, debut), mot) in enumerate(zip(paires, mots_texte)):
        fin = paires[i + 1][1] if i + 1 < len(paires) else duree
        debut = min(max(0.0, debut), duree)
        sortie.append({"mot": mot, "debut": round(debut, 3), "fin": round(max(debut + 0.05, min(fin, duree)), 3)})
    return sortie


def main(chemin_travail: str) -> int:
    travail = json.loads(Path(chemin_travail).read_text(encoding="utf-8"))
    dossier = Path(travail["dossier"])
    dossier.mkdir(parents=True, exist_ok=True)
    appareil = travail.get("appareil", "auto")
    if appareil == "auto":
        appareil = "cuda" if torch.cuda.is_available() else "cpu"
    # bfloat16 est mal accéléré sur la plupart des processeurs : float32 sur CPU.
    dtype = torch.bfloat16 if appareil == "cuda" else torch.float32

    t0 = time.time()
    info = CheckpointInfo.from_hf_repo(travail.get("depot", DEFAULT_DSM_TTS_REPO))
    modele = TTSModel.from_checkpoint_info(info, n_q=32, temp=0.6, device=torch.device(appareil), dtype=dtype)
    chemin_voix = modele.get_voice_path(travail["voix"])
    conditions = modele.make_condition_attributes([chemin_voix], cfg_coef=travail.get("cfg", 2.0))
    chargement = time.time() - t0
    frequence = int(modele.mimi.sample_rate)
    frame_rate = float(modele.mimi.frame_rate)

    resultats = []
    for phrase in travail["phrases"]:
        t1 = time.time()
        entrees = modele.prepare_script([phrase["texte"]], padding_between=1)
        morceaux: list[np.ndarray] = []

        def _sur_image(image: torch.Tensor) -> None:
            if (image != -1).all():
                pcm = modele.mimi.decode(image[:, 1:, :]).float().cpu().numpy()
                morceaux.append(np.clip(pcm[0, 0], -1, 1))

        with modele.mimi.streaming(1):
            res = modele.generate([entrees], [conditions], on_frame=_sur_image)
        pcm = np.concatenate(morceaux) if morceaux else np.zeros(1, dtype=np.float32)
        pcm, decalage = _rogner(pcm, frequence)
        duree = pcm.size / frequence
        transcript = res.all_transcripts[0] if getattr(res, "all_transcripts", None) else None
        mots = _mots_kyutai(transcript, phrase["texte"], frame_rate, decalage, duree)
        origine = "kyutai"
        if mots is None:
            mots, origine = _mots_estimes(phrase["texte"], duree), "estimation"
        fichier = dossier / f"{phrase['id']}.wav"
        _ecrire_wav(fichier, pcm, frequence)
        resultats.append({"id": phrase["id"], "fichier": str(fichier), "duree_s": round(duree, 3), "mots": mots,
                          "origine_mots": origine, "secondes_calcul": round(time.time() - t1, 1)})
        print(f"[voix] {phrase['id']} : {duree:.2f} s d'audio en {time.time() - t1:.1f} s ({origine})", flush=True)

    (dossier / "resultat.json").write_text(json.dumps(
        {"frequence": frequence, "appareil": appareil, "chargement_s": round(chargement, 1), "phrases": resultats},
        ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
