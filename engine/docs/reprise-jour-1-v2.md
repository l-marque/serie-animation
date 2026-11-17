# Reprise : épisode jour-1, version « blocs » (état au 2026-11-17)

Note de passation écrite par Claude pour le Claude qui reprend le projet (changement de compte de Guillaume). Branche : `episode/jour-1-v2` (contient aussi `episode/jour-1` et `engine/atelier-modelisation`). Rien n'est publié ; aucune PR n'est ouverte.

## Ce que Guillaume a demandé et validé

- **Personnages en blocs** façon jeux à avatars (type Roblox, sans rien reprendre d'un vrai jeu) : **validés** (« les personnages sont parfaites »). Kevin = enfant qui fait un peu pitié (t-shirt moutarde trop grand rapiécé, short, chaussette tombée, mine triste) ; abonnés = même bonhomme, seul le t-shirt change de couleur. Tous dans un seul dossier.
- **Décor** : son terrain boueux (modélisé par lui dans Blender) + ruines « pro mais épurées » + **ambiance de ville autour** + lignes et barrières abîmées (« trop belles pour un terrain en ruine »).
- **Plus de plans sur les ruines** : fait (17 plans, dont tribune effondrée, pylône penché, tableau d'affichage, boue, cage sans filet).
- **Voix** : Kyutai jugée sans accroche ; Chatterbox « encore pire » ; **choix : Zonos, réglage « conteur »** (`renders/jour-1/essais_voix/4_zonos_conteur.wav`).
- **Kevin tire vraiment dans le ballon** (élan, frappe, contact sur le mot « Kevin », ballon sur la barre).
- **b10** : « Et mettez en commentaires vos suggestions d'amélioration ! » (texte « VOS IDÉES D'AMÉLIORATION ↓ »).
- Ne pas encore remplacer la cage par la cage avec filet (« c'est après »).
- Claude doit **modéliser lui-même** (pas seulement chercher dans les banques) et peut piloter le Blender ouvert de Guillaume.

## Où est quoi

| Élément | Emplacement | Dans Git ? |
|---|---|---|
| Fiche épisode | `episodes/jour-1.json`, `episodes/jour-1.habillage.json` | oui |
| Pack de DA | `engine/packs_da/stade_bloc.json` (AgX, voix Zonos) | oui |
| Générateur des personnages | `engine/outils/atelier/modeles/perso_bloc.py` | oui |
| Personnages (7 GLB + aperçu) | `engine/assets/modeles/personnages_bloc/` | **non** (`.gitignore`) : régénérer avec le script |
| Stade en ruine + ville | script `engine/outils/atelier/modeles/stade_ruine.py` → `engine/assets/modeles/terrain_boueux/stade_ruine.blend` | script oui, `.blend` non |
| Terrain d'origine de Guillaume | `engine/assets/modeles/terrain_boueux/terrain_boueux_source.blend` | **non** : à copier dans le Drive (`06_Rendus et assets lourds`) pour l'autre poste |
| Atelier de modélisation | `engine/outils/atelier/` (`formes.py`, `apercu.py`, `poses.py`, `blender_direct.py`) | oui ; méthode : `engine/docs/modelisation.md` |
| Moteur de voix Zonos | `engine/voix/zonos_worker.py`, `engine/pipeline/voix.py`, référence de timbre `engine/voix/references/narrateur_fr.wav` | oui |
| Environnement Python de Zonos | `C:\Users\guill\venvs\zonos-tts` (relié au PyTorch CUDA de `venvs\kyutai-tts` par un `.pth`) | hors dépôt |
| Aperçus visuels | `renders/jour-1/apercus_v2/` | non (renders/) |
| Essais de voix | `renders/jour-1/essais_voix/` | non |
| Vidéo actuelle | `renders/jour-1/final/episode.mp4` = **ancienne version** (Quaternius, petit terrain) | non |

## Commandes

```bash
# régénérer les personnages (7 GLB)
"C:/Program Files/Blender Foundation/Blender 5.3/blender.exe" --background --factory-startup -noaudio --python engine/outils/atelier/modeles/perso_bloc.py
# régénérer le stade (≈ 10-15 min : la ville a des milliers de fenêtres)
"C:/Program Files/Blender Foundation/Blender 5.3/blender.exe" --background --factory-startup -noaudio --python engine/outils/atelier/modeles/stade_ruine.py
# valider puis rendre l'épisode (voix Zonos choisie par le pack ; 16 voix sur 17 déjà en cache)
.venv/Scripts/python.exe -m engine.pipeline.run episodes/jour-1.json --valider-seulement
.venv/Scripts/python.exe -m engine.pipeline.run episodes/jour-1.json --mode final --blender "C:/Program Files/Blender Foundation/Blender 5.3/blender.exe"
```

## État au 2026-11-17, 15 h 30

- **Vidéo finale de la version blocs rendue** : `renders/jour-1/final/episode.mp4` (41,3 s, code 0, QA automatique sans problème). Planche contact vérifiée : Kevin sur la pelouse, plans sur les ruines, abonnés avec pseudo, fin de b15 non coupée. **Voix validées par Guillaume.**
- Images b01-b11 réutilisées (rendu interrompu, en partie à 32 échantillons pour les ~100 premières images), b12-b15 rendues à 64.
- Corrections du moteur pendant la session : assets `.blend` mal placés au chargement (bibliotheque.py) ; plus de bascule silencieuse vers Cycles si une image est verrouillée (rendu.py) ; Zonos : plusieurs versions par phrase vérifiées par Whisper (zonos_worker.py), clé de cache limitée aux réglages de son, compilation automatique si Visual Studio Build Tools est présent.
- Répliques reformulées pour Zonos : b04 « c'est le premier jour de l'aventure », b14 « La pelouse ou les filets ? », b15 « Rendez-vous au jour deux, pour voir la suite ! ».

## Reste à faire

1. Visual Studio Build Tools : l'installation par winget a été annulée (autorisation administrateur non donnée, code 0x8013153B). La relancer avec Guillaume devant l'écran ; Zonos passera alors en mode compilé (plus rapide) tout seul.
2. Mettre à jour la plaquette Figma « jour-1 — plaquette ».
3. Journal de bord du Drive et copie des assets lourds dans `06_Rendus et assets lourds`.
4. Push : bloqué par la confidentialité de l'adresse e-mail GitHub (voir la session précédente) ; Guillaume a demandé de rester en local pour l'instant.
5. PR et relecture par Lucas ; aucune publication sans validation humaine.

## Points d'attention

- `.env` : la ligne de la clé Sketchfab est mal formée (`API_Sketch_Fab: …`) ; il faut `SKETCHFAB_TOKEN=…`. Guillaume doit la corriger lui-même (modification du `.env` refusée au mode auto). Les clés Sketchfab et 3DTexel ont été affichées dans une sortie de commande de la session précédente : Guillaume peut les régénérer.
- Licences : bonhomme Poly Pizza « Hyper Casual Character » (CC-BY, J-Toastie) et ballon (CC-BY) à créditer dans la légende ; personnages en blocs, stade et ville = créations du projet ; Zonos = Apache 2.0.
- Ne jamais utiliser de dépôts qui contournent l'abonnement ElevenLabs (refusé). Options légales si Zonos ne suffit plus : ElevenLabs Starter (~5-6 $/mois) ou Gemini Flash TTS : décision humaine (dépense).
- Le Blender ouvert de Guillaume a l'extension « MCP » de Blender Lab (pont port 9876) : `engine/outils/atelier/blender_direct.py` permet de l'utiliser.
