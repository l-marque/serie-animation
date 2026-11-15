"""Effets sonores synthétisés (aucun fichier externe, donc aucune licence à gérer).

Deux sons, générés une fois puis mis en cache :
    pop     apparition d'un objet (actions 'apparaitre' et 'grandir')
    souffle transition entre deux plans (début de chaque beat, sauf le premier)

Les Reels de référence ponctuent chaque apparition et chaque coupe d'un son court : c'est ce qui
donne le rythme, même avec une voix calme. Le volume reste bas pour ne jamais couvrir la voix.
"""

from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path
from typing import Any

from . import chemins

FREQUENCE = 48000
DOSSIER = chemins.RACINE / "renders" / "_cache_sons"
ACTIONS_POP = {"apparaitre", "grandir"}
VOLUME_POP = 0.35
VOLUME_SOUFFLE = 0.22
ECART_MIN_S = 0.12  # deux sons plus proches que cela sont fusionnés (vague d'apparitions d'un module)


def _ecrire(chemin: Path, echantillons: list[float]) -> Path:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(chemin), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(FREQUENCE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, e)) * 32767)) for e in echantillons))
    return chemin


def _pop() -> list[float]:
    """Glissando sinusoïdal 900 -> 300 Hz, attaque instantanée, décroissance rapide (≈ 0,12 s)."""
    n = int(0.12 * FREQUENCE)
    sortie, phase = [], 0.0
    for i in range(n):
        t = i / FREQUENCE
        f = 300 + 600 * math.exp(-t * 40)
        phase += 2 * math.pi * f / FREQUENCE
        sortie.append(math.sin(phase) * math.exp(-t * 32) * 0.9)
    return sortie


def _souffle() -> list[float]:
    """Bruit filtré dont le filtre s'ouvre puis se referme (≈ 0,35 s), effet « whoosh »."""
    rng = random.Random(7)  # reproductible : même son d'un rendu à l'autre
    n = int(0.35 * FREQUENCE)
    sortie, y = [], 0.0
    for i in range(n):
        x = i / n
        enveloppe = math.sin(math.pi * x) ** 2
        alpha = 0.02 + 0.25 * enveloppe  # passe-bas d'ordre 1 à fréquence de coupure variable
        y += alpha * (rng.uniform(-1, 1) - y)
        sortie.append(y * enveloppe * 2.2)
    return sortie


def fichiers() -> dict[str, Path]:
    sons = {"pop": _pop, "souffle": _souffle}
    return {nom: (DOSSIER / f"{nom}.wav") if (DOSSIER / f"{nom}.wav").is_file() else _ecrire(DOSSIER / f"{nom}.wav", f())
            for nom, f in sons.items()}


def evenements(timeline: dict[str, Any]) -> list[tuple[str, float, float]]:
    """Liste (son, instant en s, volume) déduite de la timeline."""
    bruts: list[tuple[str, float, float]] = []
    for i, b in enumerate(timeline["beats"]):
        if i > 0:
            bruts.append(("souffle", max(0.0, b["debut_s"] - 0.12), VOLUME_SOUFFLE))
        for a in b["actions"]:
            if a["type"] in ACTIONS_POP:
                bruts.append(("pop", a["t_debut_s"], VOLUME_POP))
    bruts.sort(key=lambda e: e[1])
    sortie: list[tuple[str, float, float]] = []
    for e in bruts:
        if sortie and sortie[-1][0] == e[0] and e[1] - sortie[-1][1] < ECART_MIN_S:
            continue
        sortie.append(e)
    return sortie
