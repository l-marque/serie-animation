"""Synthétise un fond de piano doux (création du projet, aucune licence tierce).

Arpèges lents sur do - sol - la mineur - fa (60 s, 84 BPM), timbre de piano approché par quelques
harmoniques à décroissance exponentielle, léger écho. Destiné à être mixé très bas sous la voix.

    <python avec numpy> engine/outils/piano_doux.py   (ex. environnement Kyutai : venvs/kyutai-tts)
Sortie : engine/assets/musique/piano_doux.wav (mono, 44,1 kHz, 16 bits)
"""
import math
import wave
from pathlib import Path

import numpy as np

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "engine" / "assets" / "musique" / "piano_doux.wav"
FE = 44100
DUREE = 60.0
BPM = 84
NOIRE = 60 / BPM

# Accords (notes MIDI) : do, sol/si, la mineur, fa ; arpège montant puis redescente.
ACCORDS = [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 52, 57, 60, 64], [41, 53, 57, 60, 65]]
MOTIF = [0, 1, 2, 3, 4, 3, 2, 1]


def frequence(midi: int) -> float:
    return 440.0 * 2 ** ((midi - 69) / 12)


def note(midi: int, duree: float, velocite: float) -> np.ndarray:
    t = np.arange(int(duree * FE)) / FE
    f = frequence(midi)
    son = np.zeros_like(t)
    for k, a in ((1, 1.0), (2, 0.42), (3, 0.18), (4, 0.08), (5, 0.04)):
        son += a * np.sin(2 * math.pi * f * k * t) * np.exp(-t * (1.6 + 0.9 * k))
    attaque = np.minimum(1.0, t / 0.008)
    return velocite * son * attaque


def main() -> None:
    piste = np.zeros(int((DUREE + 4) * FE))
    pas = NOIRE / 2  # croches
    t, i = 0.0, 0
    while t < DUREE:
        accord = ACCORDS[(i // len(MOTIF)) % len(ACCORDS)]
        n = accord[MOTIF[i % len(MOTIF)]]
        v = 0.55 if i % len(MOTIF) == 0 else 0.35
        s = note(n, 3.0, v)
        d = int(t * FE)
        piste[d:d + len(s)] += s[: len(piste) - d]
        if i % len(MOTIF) == 0:  # basse tenue au début de chaque accord
            b = note(accord[0] - 12, 4.0, 0.4)
            piste[d:d + len(b)] += b[: len(piste) - d]
        t += pas
        i += 1
    retard = int(0.23 * FE)  # léger écho
    piste[retard:] += 0.25 * piste[:-retard]
    piste = piste[: int(DUREE * FE)]
    fondu = int(2.0 * FE)
    piste[-fondu:] *= np.linspace(1, 0, fondu)
    piste *= 0.8 / np.max(np.abs(piste))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(SORTIE), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FE)
        w.writeframes((piste * 32767).astype(np.int16).tobytes())
    print(f"écrit : {SORTIE}")


if __name__ == "__main__":
    main()
