"""Synthèse Zonos (Zyphra, Zonos-v0.1-transformer, Apache 2.0), exécutée dans l'environnement qui a zonos.

    python zonos_worker.py travail.json

travail.json : {"dossier": ..., "reference": "<wav du timbre>", "langue": "fr-fr",
                "emotion": [bonheur, tristesse, dégoût, peur, surprise, colère, autre, neutre],
                "debit": 16.0, "variation_hauteur": 110.0, "graine": 3,
                "phrases": [{"id": ..., "texte": ...}]}
Pour chaque phrase, plusieurs versions sont générées (« essais ») ; chacune est retranscrite par
Whisper (openai/whisper-small, MIT) et comparée au texte, car Zonos invente parfois du charabia sur
les phrases courtes. La version la plus fidèle et la plus propre est gardée ; si aucune n'atteint
« seuil_transcription », le worker échoue (code 3) au lieu de livrer une phrase fausse.
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
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

import difflib  # noqa: E402
import re  # noqa: E402
import unicodedata  # noqa: E402

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


def rogner(a: np.ndarray, sr: int, seuil: float = 0.006, marge_debut_s: float = 0.04,
           marge_fin_s: float = 0.3) -> np.ndarray:
    """Retire les silences de début et de fin. Seuil bas et marge de fin large : la dernière syllabe,
    souvent douce (« la suite »), était coupée avec le silence (b15, 2026-11-17). Fondu de sortie court."""
    fen = int(0.02 * sr)
    energie = np.array([np.sqrt((a[i:i + fen] ** 2).mean()) for i in range(0, max(len(a) - fen, 1), fen)])
    parle = np.where(energie > seuil)[0]
    if len(parle) == 0:
        return a
    sortie = a[max(0, parle[0] * fen - int(marge_debut_s * sr)): min(len(a), (parle[-1] + 1) * fen + int(marge_fin_s * sr))].copy()
    n = min(len(sortie), int(0.08 * sr))
    sortie[-n:] *= np.linspace(1.0, 0.0, n)
    return sortie


VOYELLES = set("aeiouyàâäéèêëîïôöùûüœæ")


def syllabes(texte: str) -> int:
    """Nombre approximatif de syllabes (groupes de voyelles ; e muet final ignoré)."""
    n = 0
    for mot in texte.lower().replace("'", " ").split():
        mot = "".join(c for c in mot if c.isalpha())
        if len(mot) > 2 and mot.endswith(("e", "es", "ent")) and not mot.endswith(("ée", "ées")):
            mot = mot[:-1] if mot.endswith("e") else mot[:-2]
        groupes, avant = 0, False
        for c in mot:
            v = c in VOYELLES
            if v and not avant:
                groupes += 1
            avant = v
        n += max(groupes, 1) if mot else 0
    return max(n, 1)


def noter(audio: np.ndarray, sr: int, attendu: float) -> float:
    """Plus la note est basse, mieux c'est : durée proche de l'attendu, pas de trou au milieu,
    pas de fin qui traîne (babillage), pas de phrase tronquée."""
    duree = len(audio) / sr
    note = abs(np.log(max(duree, 0.05) / attendu)) * 2.0
    if duree < 0.75 * attendu:
        note += 2.0                                   # phrase avalée ou tronquée
    if duree > 1.6 * attendu:
        note += 2.0                                   # bafouillage ou bruit ajouté
    fen = int(0.02 * sr)
    energie = np.array([np.sqrt((audio[i:i + fen] ** 2).mean()) for i in range(0, max(len(audio) - fen, 1), fen)])
    silence = energie < 0.012
    plus_long, courant = 0, 0
    for s in silence:
        courant = courant + 1 if s else 0
        plus_long = max(plus_long, courant)
    trou = plus_long * 0.02
    if trou > 0.3:
        note += (trou - 0.3) * 6.0                    # trou anormal au milieu de la phrase
    # fin avalée : Zonos accélère et faiblit souvent sur les derniers mots (« la suite », b15)
    parle = energie[~silence]
    if len(parle) >= 8:
        dernier_quart = parle[-max(2, len(parle) // 4):]
        rapport = float(np.median(dernier_quart) / max(np.median(parle), 1e-4))
        if rapport < 0.55:
            note += (0.55 - rapport) * 8.0
    if duree < 0.85 * attendu:
        note += (0.85 - duree / attendu) * 6.0        # phrase trop rapide : mots écrasés
    return float(note)


NOMBRES = {"1": "un", "2": "deux", "3": "trois", "10": "dix", "100": "cent"}


def normaliser(texte: str) -> str:
    """Minuscules, sans accents ni ponctuation, chiffres courants en lettres, sans espaces."""
    texte = " ".join(NOMBRES.get(m, m) for m in re.findall(r"\w+", texte.lower()))
    texte = unicodedata.normalize("NFD", texte)
    return "".join(c for c in texte if c.isalnum() and not unicodedata.combining(c))


def similarite(attendu: str, entendu: str) -> float:
    return difflib.SequenceMatcher(None, normaliser(attendu), normaliser(entendu)).ratio()


def etirer(audio: np.ndarray, sr: int, facteur: float) -> np.ndarray:
    """Change la vitesse sans changer la hauteur (ffmpeg atempo) : facteur > 1 = plus rapide."""
    import subprocess
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        e, s = Path(tmp) / "e.wav", Path(tmp) / "s.wav"
        x = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(e), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(x.tobytes())
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(e), "-af", f"atempo={facteur:.4f}", str(s)],
                       check=True)
        a, _ = lire_wav(str(s))
    return a


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
    n_essais = int(travail.get("essais", 8))
    seuil = float(travail.get("seuil_transcription", 0.8))
    from transformers import pipeline as hf_pipeline
    transcripteur = hf_pipeline("automatic-speech-recognition", model=travail.get("verificateur", "openai/whisper-small"),
                                device=0 if appareil == "cuda" else -1,
                                dtype=torch.float16 if appareil == "cuda" else torch.float32)

    def entendre(audio):
        return transcripteur({"raw": audio.astype(np.float32), "sampling_rate": sr},
                             generate_kwargs={"language": "french", "task": "transcribe"})["text"].strip()

    echecs = []
    # Compilation du décodeur (torch.compile + Triton, compilateur C++ de Visual Studio) : bien plus rapide.
    # Si elle échoue (outils absents ou cassés), on repasse en mode non compilé pour la suite.
    etat = {"compiler": bool(travail.get("compiler", False))}

    def generer(prepare):
        if etat["compiler"]:
            try:
                return modele.generate(prepare, disable_torch_compile=False)
            except Exception as e:  # noqa: BLE001
                print(f"zonos : compilation impossible ({type(e).__name__}), mode lent", flush=True)
                etat["compiler"] = False
        return modele.generate(prepare, disable_torch_compile=True)
    def choisir(p, debit):
        """Génère jusqu'à n_essais versions au débit donné et garde la plus fidèle et la plus propre."""
        cond = make_cond_dict(text=p["texte"], speaker=locuteur, language=travail.get("langue", "fr-fr"),
                              emotion=p.get("emotion", travail["emotion"]), speaking_rate=float(debit),
                              pitch_std=float(p.get("variation_hauteur", travail.get("variation_hauteur", 110.0))))
        prepare = modele.prepare_conditioning(cond)
        attendu = syllabes(p["texte"]) / float(travail.get("syllabes_par_s", 6.0))
        meilleur, note_min, notes, sim_meilleur, texte_meilleur = None, 1e9, [], 0.0, ""
        for k in range(n_essais):
            torch.manual_seed(int(travail.get("graine", 3)) + k)
            codes = generer(prepare)
            audio = rogner(modele.autoencoder.decode(codes).cpu().squeeze().float().numpy(), sr)
            entendu = entendre(audio)
            sim = similarite(p["texte"], entendu)
            # Whisper complète les fins de phrase d'après le contexte : on réécoute la fin seule et on
            # exige d'y entendre le dernier mot (« suite » de b15, avalé mais « entendu » en entier).
            mots_t = p["texte"].split()
            dernier = normaliser(mots_t[-1] if mots_t[-1].isalpha() else mots_t[-2])
            fin = normaliser(entendre(audio[int(len(audio) * 0.55):])) if len(audio) > sr else normaliser(entendu)
            if dernier and difflib.SequenceMatcher(None, dernier, fin[-len(dernier) - 3:]).ratio() < 0.6:
                sim = min(sim, 0.5)
            # la transcription prime : une phrase incompréhensible est écartée quelle que soit sa durée
            note = noter(audio, sr, attendu) + (1.0 - sim) * 10.0
            notes.append((round(sim, 2), round(note, 2)))
            if note < note_min:
                meilleur, note_min, sim_meilleur, texte_meilleur = audio, note, sim, entendu
            if sim >= 0.95 and note < 1.0:
                break                                      # version propre trouvée
        return meilleur, sim_meilleur, texte_meilleur, notes

    def mots_par_minute(texte, audio):
        parole = max(len(audio) / sr - 0.34, 0.2)          # sans les marges de début et de fin (rogner)
        return 60.0 * len(re.findall(r"[\w'’-]+", texte)) / parole

    for p in travail["phrases"]:
        # Réglages de la phrase (prod-directeur-voix, <fiche>.voix.json), sinon ceux du pack.
        debit = float(p.get("debit", travail.get("debit", 16.0)))
        meilleur, sim_meilleur, texte_meilleur, notes = choisir(p, debit)
        cible = p.get("mots_par_minute", travail.get("mots_par_minute"))
        if cible:
            # Débit cible : on régénère au débit corrigé (voix naturelle), puis petite retouche (±10 % au plus).
            mpm = mots_par_minute(p["texte"], meilleur)
            if abs(mpm / cible - 1) > 0.1:
                debit2 = min(30.0, max(5.0, debit * cible / mpm))
                autre = choisir(p, debit2)
                if autre[1] >= min(seuil, sim_meilleur):
                    meilleur, sim_meilleur, texte_meilleur, notes = autre
                    debit = debit2
                mpm = mots_par_minute(p["texte"], meilleur)
            facteur = min(1.1, max(0.9, cible / mpm))   # atempo f : débit × f (sens corrigé le 2026-11-17)
            if abs(facteur - 1) > 0.01:
                meilleur = etirer(meilleur, sr, facteur)
            print(f"zonos : débit {mots_par_minute(p['texte'], meilleur):.0f} mots/min (cible {cible}, "
                  f"réglage Zonos {debit:.1f})", flush=True)
        print(f"zonos : {p['texte']!r} -> entendu {texte_meilleur!r} (similarité {sim_meilleur:.2f}) ; "
              f"essais (similarité, note) {notes}", flush=True)
        if sim_meilleur < seuil:
            echecs.append(f"{p['texte']!r} : meilleure version entendue {texte_meilleur!r} ({sim_meilleur:.2f})")
        x = (np.clip(meilleur, -1, 1) * 32767).astype(np.int16)
        with wave.open(str(dossier / f"{p['id']}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(x.tobytes())
        duree = len(x) / sr
        resultats.append({"id": p["id"], "duree_s": round(duree, 3), "mots": mots_estimes(p["texte"], duree),
                          "origine_mots": "estimation", "transcription": texte_meilleur,
                          "similarite": round(sim_meilleur, 3)})
    (dossier / "resultat.json").write_text(json.dumps({"phrases": resultats}, ensure_ascii=False), encoding="utf-8")
    if echecs:
        print("Zonos : phrases incompréhensibles après tous les essais (augmenter « essais » ou reformuler) :\n  "
              + "\n  ".join(echecs), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
