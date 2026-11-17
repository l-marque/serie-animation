"""Synthèse Qwen3-TTS (Alibaba Qwen, Apache 2.0), exécutée dans l'environnement qui a qwen-tts.

    python -I qwen_worker.py travail.json

travail.json : {"dossier": ..., "modele": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "locuteur": "dylan",
                "langue": "French", "consigne": "<consigne de jeu par défaut>", "essais": 4,
                "seuil_transcription": 0.9, "mots_par_minute": 180, "verificateur": "openai/whisper-small",
                "phrases": [{"id": ..., "texte": ..., "consigne": "...", "mots_par_minute": 170}]}

Rapidité : le modèle est chargé une seule fois, et toutes les phrases sont générées **ensemble** (une seule
passe sur la carte graphique) ; seules les phrases ratées sont refaites, une par une.
Contrôle : chaque version est retranscrite par Whisper (texte exact, dernier mot bien entendu, pas de trou).
Débit : si une phrase s'écarte de plus de 12 % du débit visé, elle est refaite avec une consigne de débit,
puis une retouche de vitesse de ±12 % au plus (sans changer la hauteur).
Écrit <dossier>/<id>.wav et <dossier>/resultat.json ; code 3 si une phrase reste incompréhensible.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
sys.path.insert(0, str(Path(__file__).resolve().parent))      # -I n'ajoute pas le dossier du script

import numpy as np  # noqa: E402
import torch  # noqa: E402
from outils_voix import (dernier_mot_entendu, ecrire_wav, etirer, mots_estimes, mots_par_minute,  # noqa: E402
                         nombre_mots, plus_long_silence_s, rogner, similarite, variation_hauteur_st)

MOTS_MIN_DEBIT = 5   # sous 5 mots, un débit par phrase n'a pas de sens (« Ça, c'est Kevin » sortait à 391 mots/min)
MOTS_MIN_EXPRESSIVITE = 4
# Expressivité visée : médiane des Reels de référence ≈ 4,8 demi-tons à l'échelle d'une phrase (engine/docs/references-videos.md)


def main() -> int:
    travail = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    dossier = Path(travail["dossier"])
    from qwen_tts import Qwen3TTSModel
    from transformers import pipeline as hf_pipeline

    modele = Qwen3TTSModel.from_pretrained(travail.get("modele", "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice"),
                                           device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa")
    transcripteur = hf_pipeline("automatic-speech-recognition", model=travail.get("verificateur", "openai/whisper-small"),
                                device=0, dtype=torch.float16)
    langue = travail.get("langue", "French")
    locuteur = travail.get("locuteur", "dylan")
    seuil = float(travail.get("seuil_transcription", 0.9))
    essais = int(travail.get("essais", 6))

    def entendre(audio, sr):
        return transcripteur({"raw": audio.astype(np.float32), "sampling_rate": sr},
                             generate_kwargs={"language": "french", "task": "transcribe"})["text"].strip()

    def generer(textes, consignes, graine):
        torch.manual_seed(graine)
        wavs, sr = modele.generate_custom_voice(text=textes, language=[langue] * len(textes),
                                                speaker=[locuteur] * len(textes), instruct=consignes)
        return [np.asarray(w, dtype=np.float32) for w in wavs], sr

    def juger(p, audio, sr):
        entendu = entendre(audio, sr)
        sim = similarite(p["texte"], entendu)
        if len(audio) > sr and not dernier_mot_entendu(p["texte"], entendre(audio[int(len(audio) * 0.55):], sr)):
            sim = min(sim, 0.5)                          # fin avalée : Whisper l'avait devinée d'après le contexte
        if plus_long_silence_s(audio, sr) > 0.6:
            sim = min(sim, 0.7)                          # trou anormal au milieu de la phrase
        return sim, entendu

    phrases = travail["phrases"]
    consignes = [p.get("consigne") or travail.get("consigne", "") for p in phrases]
    # 1. Toutes les phrases ensemble (rapide)
    wavs, sr = generer([p["texte"] for p in phrases], consignes, int(travail.get("graine", 7)))
    resultats, echecs = [], []
    for i, (p, brut) in enumerate(zip(phrases, wavs)):
        cible = p.get("mots_par_minute", travail.get("mots_par_minute"))
        if nombre_mots(p["texte"]) < MOTS_MIN_DEBIT:
            cible = None
        audio = rogner(brut, sr)
        sim, entendu = juger(p, audio, sr)
        consigne = consignes[i]
        # 2. Phrase ratée ou débit trop loin de la cible : on la refait seule
        expr_cible = float(p.get("expressivite_min", travail.get("expressivite_min", 4.8)))
        juge_expr = nombre_mots(p["texte"]) >= MOTS_MIN_EXPRESSIVITE
        expr = variation_hauteur_st(audio, sr)
        for k in range(1, essais):
            mpm = mots_par_minute(p["texte"], audio, sr)
            hors_debit = bool(cible) and abs(mpm / cible - 1) > 0.12
            plat = juge_expr and expr < expr_cible
            if sim >= 0.95 and not hors_debit and not plat:
                break
            ajouts = []
            if hors_debit:
                ajouts.append("Parle nettement plus vite, débit soutenu." if mpm < cible
                              else "Parle plus lentement, en posant les mots.")
            if plat:
                ajouts.append("Beaucoup plus expressif : la voix monte et descend franchement, appuie les mots importants.")
            consigne = (consignes[i] + " " + " ".join(ajouts)).strip()
            autre, sr = generer([p["texte"]], [consigne], int(travail.get("graine", 7)) + 100 * k + i)
            autre = rogner(autre[0], sr)
            s2, e2 = juger(p, autre, sr)
            x2 = variation_hauteur_st(autre, sr)
            meilleur_debit = (not cible) or abs(mots_par_minute(p["texte"], autre, sr) / cible - 1) < abs(mpm / cible - 1)
            plus_vivant = juge_expr and x2 > expr
            # texte exact d'abord ; à fidélité suffisante, la version la plus vivante et la mieux rythmée
            if s2 > sim + 0.02 or (s2 >= min(sim, 0.95) and (plus_vivant or meilleur_debit)):
                audio, sim, entendu, expr = autre, s2, e2, x2
        # 3. Retouche fine du débit (±12 % au plus, hauteur inchangée)
        if cible:
            facteur = min(1.12, max(0.88, mots_par_minute(p["texte"], audio, sr) / cible))
            if abs(facteur - 1) > 0.01:
                audio = etirer(audio, sr, facteur)
        mpm = mots_par_minute(p["texte"], audio, sr)
        expr = variation_hauteur_st(audio, sr)
        print(f"qwen : {p['texte']!r} -> entendu {entendu!r} (similarité {sim:.2f}), {mpm:.0f} mots/min, "
              f"expressivité {expr:.1f} demi-tons", flush=True)
        if sim < seuil:
            echecs.append(f"{p['texte']!r} : meilleure version entendue {entendu!r} ({sim:.2f})")
        ecrire_wav(str(dossier / f"{p['id']}.wav"), audio, sr)
        duree = len(audio) / sr
        resultats.append({"id": p["id"], "duree_s": round(duree, 3), "mots": mots_estimes(p["texte"], duree),
                          "origine_mots": "estimation", "transcription": entendu, "similarite": round(sim, 3),
                          "mots_par_minute": round(mpm), "expressivite_st": round(expr, 1)})
    (dossier / "resultat.json").write_text(json.dumps({"phrases": resultats}, ensure_ascii=False), encoding="utf-8")
    if echecs:
        print("Qwen : phrases incompréhensibles après tous les essais :\n  " + "\n  ".join(echecs), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
