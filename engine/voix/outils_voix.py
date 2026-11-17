"""Outils audio communs aux workers de voix (numpy seulement, sans dépendance au modèle).

Rognage des silences, comparaison texte / transcription, débit en mots par minute, changement de vitesse
sans changer la hauteur (ffmpeg), mots estimés. Repris de zonos_worker.py (2026-11-17).
"""
from __future__ import annotations

import difflib
import re
import subprocess
import tempfile
import unicodedata
import wave
from pathlib import Path

import numpy as np

NOMBRES = {"1": "un", "2": "deux", "3": "trois", "10": "dix", "100": "cent"}


def lire_wav(chemin: str):
    with wave.open(chemin, "rb") as w:
        sr, n, canaux = w.getframerate(), w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if canaux > 1:
        a = a.reshape(-1, canaux).mean(axis=1)
    return a, sr


def ecrire_wav(chemin: str, audio: np.ndarray, sr: int) -> None:
    x = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(chemin, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x.tobytes())


def _energie(a: np.ndarray, fen: int) -> np.ndarray:
    """Énergie (RMS) par fenêtres successives de `fen` échantillons, calculée d'un seul bloc (numpy)."""
    n = len(a) // fen
    if n == 0:
        return np.array([float(np.sqrt((a ** 2).mean()))]) if len(a) else np.zeros(1)
    return np.sqrt((a[:n * fen].reshape(n, fen) ** 2).mean(axis=1))


def rogner(a: np.ndarray, sr: int, seuil: float = 0.006, marge_debut_s: float = 0.04,
           marge_fin_s: float = 0.3) -> np.ndarray:
    """Retire les silences de début et de fin ; seuil bas et marge de fin large pour ne pas couper la
    dernière syllabe ; court fondu de sortie."""
    fen = int(0.02 * sr)
    energie = _energie(a, fen)
    parle = np.where(energie > seuil)[0]
    if len(parle) == 0:
        return a
    sortie = a[max(0, parle[0] * fen - int(marge_debut_s * sr)):
               min(len(a), (parle[-1] + 1) * fen + int(marge_fin_s * sr))].copy()
    n = min(len(sortie), int(0.08 * sr))
    sortie[-n:] *= np.linspace(1.0, 0.0, n)
    return sortie


def plus_long_silence_s(a: np.ndarray, sr: int, seuil: float = 0.012) -> float:
    silence = np.concatenate([[0], (_energie(a, int(0.02 * sr)) < seuil).astype(np.int8), [0]])
    bords = np.flatnonzero(np.diff(silence))
    longueurs = bords[1::2] - bords[::2]
    return float(longueurs.max() * 0.02) if len(longueurs) else 0.0


def normaliser(texte: str) -> str:
    """Minuscules, sans accents ni ponctuation, chiffres courants en lettres, sans espaces."""
    texte = " ".join(NOMBRES.get(m, m) for m in re.findall(r"\w+", texte.lower()))
    texte = unicodedata.normalize("NFD", texte)
    return "".join(c for c in texte if c.isalnum() and not unicodedata.combining(c))


def similarite(attendu: str, entendu: str) -> float:
    return difflib.SequenceMatcher(None, normaliser(attendu), normaliser(entendu)).ratio()


def dernier_mot_entendu(texte: str, fin_entendue: str) -> bool:
    """Le dernier mot du texte est-il dans la transcription de la fin seule ? (fins avalées)"""
    mots = [m for m in texte.split() if any(c.isalnum() for c in m)]
    if not mots:
        return True
    dernier = normaliser(mots[-1])
    fin = normaliser(fin_entendue)
    return not dernier or difflib.SequenceMatcher(None, dernier, fin[-len(dernier) - 3:]).ratio() >= 0.6


def nombre_mots(texte: str) -> int:
    return len(re.findall(r"[\w'’-]+", texte))


def mots_par_minute(texte: str, audio: np.ndarray, sr: int) -> float:
    parole = max(len(audio) / sr - 0.34, 0.2)          # sans les marges de début et de fin de rogner()
    return 60.0 * nombre_mots(texte) / parole


def etirer(audio: np.ndarray, sr: int, facteur: float) -> np.ndarray:
    """Change la vitesse sans changer la hauteur (ffmpeg atempo) : facteur > 1 = plus rapide."""
    with tempfile.TemporaryDirectory() as tmp:
        e, s = Path(tmp) / "e.wav", Path(tmp) / "s.wav"
        ecrire_wav(str(e), audio, sr)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(e), "-af", f"atempo={facteur:.4f}", str(s)],
                       check=True)
        a, _ = lire_wav(str(s))
    return a


def variation_hauteur_st(audio: np.ndarray, sr: int) -> float:
    """Expressivité : écart-type de la hauteur de voix, en demi-tons (autocorrélation sur 40 ms).
    Repère : médiane des Reels de référence 5,8 (de 4,5 à 7,4) ; jour-1 5,1 (engine/docs/references-videos.md)."""
    fr, hop = int(0.04 * sr), int(0.01 * sr)
    if len(audio) <= fr:
        return 0.0
    trames = np.lib.stride_tricks.sliding_window_view(audio, fr)[::hop]
    trames = trames[np.sqrt((trames ** 2).mean(axis=1)) >= 0.02]
    if len(trames) < 10:
        return 0.0
    trames = trames - trames.mean(axis=1, keepdims=True)
    # autocorrélation de toutes les trames d'un coup (FFT), identique à np.correlate(s, s, "full")[fr - 1:]
    n = 1 << int(np.ceil(np.log2(2 * fr)))
    spectre = np.fft.rfft(trames, n=n, axis=1)
    c = np.fft.irfft(spectre * np.conj(spectre), n=n, axis=1)[:, :fr]
    lo, hi = sr // 350, sr // 70
    k = lo + np.argmax(c[:, lo:hi], axis=1)
    garde = c[np.arange(len(c)), k] > 0.45 * c[:, 0]
    if garde.sum() < 10:
        return 0.0
    f0 = sr / k[garde]
    return float(np.std(12 * np.log2(f0 / np.median(f0))))


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
