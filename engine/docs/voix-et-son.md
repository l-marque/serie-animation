# Voix off et son

## Ce que contient la piste audio

| Couche | Source | Réglage |
|---|---|---|
| Voix off | module `engine/pipeline/voix.py` : Kyutai TTS (`kyutai/tts-1.6b-en_fr`, CC-BY 4.0), ou voix système de Windows en secours | `--voix auto\|kyutai\|windows\|aucune`, `--voix-nom` |
| Effets de rythme | `engine/pipeline/effets_sonores.py` : « pop » à chaque apparition, « souffle » à chaque changement de plan, synthétisés (aucune licence) | `effets_sonores` dans le pack de DA (oui par défaut) |
| Musique | fichier indiqué par la fiche (`audio.musique`) ; baisse automatiquement quand la voix parle | `audio.volume_musique` |

Les sous-titres sont calés sur la **vraie voix** : chaque mot est horodaté par Kyutai, et le mot prononcé est surligné (style karaoké, comme les Reels de référence).

## Installation de Kyutai (une fois, sur la machine de rendu)

1. Un Python 3.10 à 3.12 avec `torch` et `moshi` (`pip install moshi`). Le modèle (≈ 4 Go) et la voix se téléchargent au premier appel dans le cache Hugging Face.
2. Dans `.env` à la racine du dépôt (jamais versionné) : `TTS_PYTHON=C:\chemin\vers\python.exe`.
3. Test : `python -m engine.pipeline.run episodes/exemples/demo_001.json --voix kyutai`.

Sur la machine de Guillaume (installé et vérifié le 2026-11-15) : environnement dédié `C:\Users\guill\venvs\kyutai-tts` avec PyTorch **2.9.1+cu128** (version CUDA compatible RTX 50 ; moshi 0.2.13 exige torch < 2.10) et moshi 0.2.13. Sur la RTX 5070 : 3,4 s de voix en 3,8 s de calcul (environ 1 fois le temps réel), plus 12 s de chargement du modèle par épisode. À titre de comparaison, la version CPU demandait 35 s pour 2,3 s de voix.

Installation reproductible :

```powershell
py -3.12 -m venv C:\Users\<toi>\venvs\kyutai-tts
C:\Users\<toi>\venvs\kyutai-tts\Scripts\python.exe -m pip install "torch==2.9.1" --index-url https://download.pytorch.org/whl/cu128
C:\Users\<toi>\venvs\kyutai-tts\Scripts\python.exe -m pip install moshi==0.2.13
```

puis `TTS_PYTHON=C:\Users\<toi>\venvs\kyutai-tts\Scripts\python.exe` dans `.env`.

Points techniques réglés dans `engine/voix/kyutai_worker.py` : `torch.compile` désactivé (il exige le compilateur C++ de Visual Studio sous Windows) ; bfloat16 sur GPU, float32 sur CPU ; carte graphique choisie automatiquement si elle est disponible.

## Choisir la voix de la série (audition)

```bash
python -m engine.pipeline.voix audition "Une phrase typique de la série." --sortie renders/audition_voix
```

Synthétise la phrase avec les 38 voix françaises du dépôt Kyutai (environ 7 s par voix sur la RTX 5070), écrit un fichier par voix (`v01.wav` …), la correspondance numéro → voix (`correspondance.json`) et un fichier `audition.wav` qui les enchaîne (un bip avant chaque voix). Une fois la voix choisie par un humain, on l'inscrit dans le pack de DA de la série : `"voix_off": {"kyutai": "<identifiant>"}`. Le pipeline l'utilise alors automatiquement (sauf `--voix-nom`).

## Voix

Voix par défaut (si le pack n'en indique pas) : `unmute-prod-website/fabieng-enhanced-v2.wav` (dépôt `kyutai/tts-voices`). Les voix françaises sont dans `cml-tts/fr/` (469 fichiers) et `unmute-prod-website/`. Licences (README du dépôt `kyutai/tts-voices`) : `cml-tts/` CC-BY 4.0 (crédit à prévoir), `voice-donations/` CC0, `expresso/` **non commercial : interdit**. Licence de `unmute-prod-website/` non précisée dans le README : à éviter pour une publication tant qu'elle n'est pas vérifiée. Jamais la voix d'une personne réelle identifiable (le dépôt en contient, par exemple `degaulle-2`).

## Précision et limites

- Horodatage des mots : précision d'environ ±0,2 s (pas de 80 ms du modèle). Si le découpage du modèle ne correspond pas aux mots du texte, le module revient à une répartition au prorata des lettres (`origine_mots: estimation` dans le rapport).
- Une phrase inchangée n'est jamais resynthétisée (cache `renders/_cache_voix`, clé = moteur + voix + texte) ; les fichiers sont recopiés dans `renders/<épisode>/<mode>/voix/`.
- `--valider-seulement` ne synthétise rien (timings estimés), pour rester instantané.

## Son de pièce (HUD)

`piece` : deux notes aiguës en onde carrée adoucie (si 5 puis mi 6, ≈ 0,4 s), synthétisées comme les autres effets (aucune licence). Joué à chaque gain « +10 » et quand un compteur de pièces commence à défiler (`engine/pipeline/hud.py`).
