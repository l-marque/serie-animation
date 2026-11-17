"""Synthèse Zonos (Zyphra, Zonos-v0.1-transformer, Apache 2.0), exécutée dans l'environnement qui a zonos.

    python zonos_worker.py travail.json

travail.json : {"dossier": ..., "reference": "<wav du timbre>", "langue": "fr-fr",
                "emotion": [bonheur, tristesse, dégoût, peur, surprise, colère, autre, neutre],
                "debit": 16.0, "variation_hauteur": 110.0, "graine": 3,
                "phrases": [{"id": ..., "texte": ...}]}
Écrit <dossier>/<id>.wav (silences de début et de fin retirés) et <dossier>/resultat.json
({"phrases": [{"id", "duree_s", "mots", "origine_mots"}]}). Zonos ne donne pas l'instant des mots :
ils sont estimés sur la partie parlée (proportionnellement à la longueur des mots).
"""
import json
import os
import sys
import wave
from pathlib import Path

import espeakng_loader

os.environ.setdefault("PHONEMIZER_ESPEAK_LIBRARY", espeakng_loader.get_library_path())
os.environ.setdefault("ESPEAK_DATA_PATH", espeakng_loader.get_data_path())

import numpy as np  # noqa: E402
import torch  # noqa: E402
from zonos.conditioning import make_cond_dict  # noqa: E402
from zonos.model import Zonos  # noqa: E402


def lire_wav(chemin: str):
    with wave.open(chemin, "rb") as w:
        sr, n, canaux = w.getframerate(), w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if canaux > 1:
        a = a.reshape(-1, canaux).mean(axis=1)
    return a, sr


def rogner(a: np.ndarray, sr: int, seuil: float = 0.012, marge_s: float = 0.04) -> np.ndarray:
    fen = int(0.02 * sr)
    energie = np.array([np.sqrt((a[i:i + fen] ** 2).mean()) for i in range(0, max(len(a) - fen, 1), fen)])
    parle = np.where(energie > seuil)[0]
    if len(parle) == 0:
        return a
    marge = int(marge_s * sr)
    return a[max(0, parle[0] * fen - marge): min(len(a), (parle[-1] + 1) * fen + marge)]


def mots_estimes(texte: str, duree: float) -> list[dict]:
    mots = texte.split()
    poids = [len(m) + 1 for m in mots]
    total = sum(poids) or 1
    t, sortie = 0.0, []
    for m, p in zip(mots, poids):
        d = duree * p / total
        sortie.append({"mot": m, "debut": round(t, 3), "fin": round(t + d, 3)})
        t += d
    return sortie


def main() -> int:
    travail = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dossier = Path(travail["dossier"])
    appareil = "cuda" if torch.cuda.is_available() else "cpu"
    modele = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=appareil)
    ref, sr_ref = lire_wav(travail["reference"])
    locuteur = modele.make_speaker_embedding(torch.from_numpy(ref)[None], sr_ref)
    sr = modele.autoencoder.sampling_rate
    resultats = []
    for p in travail["phrases"]:
        torch.manual_seed(int(travail.get("graine", 3)))
        cond = make_cond_dict(text=p["texte"], speaker=locuteur, language=travail.get("langue", "fr-fr"),
                              emotion=travail["emotion"], speaking_rate=float(travail.get("debit", 16.0)),
                              pitch_std=float(travail.get("variation_hauteur", 110.0)))
        codes = modele.generate(modele.prepare_conditioning(cond), disable_torch_compile=True)
        audio = modele.autoencoder.decode(codes).cpu().squeeze().float().numpy()
        audio = rogner(audio, sr)
        x = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(dossier / f"{p['id']}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(x.tobytes())
        duree = len(x) / sr
        resultats.append({"id": p["id"], "duree_s": round(duree, 3), "mots": mots_estimes(p["texte"], duree),
                          "origine_mots": "estimation"})
        print(f"zonos : {p['id']} ({duree:.2f} s)", flush=True)
    (dossier / "resultat.json").write_text(json.dumps({"phrases": resultats}, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
