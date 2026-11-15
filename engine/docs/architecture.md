# Architecture du pôle Production (v1.1)

## En une phrase

Une **fiche épisode** (JSON) entre, une **vidéo 9:16** sort. Entre les deux, un pipeline **scripté et déterministe** fait le travail ; des **agents Claude** n'interviennent que là où le jugement est utile.

```
   fiche épisode (pôle Storytelling, contrat contracts/fiche-episode.schema.json)
              │
              ▼
┌─────────────────────────── prod-chef (sonnet) ────────────────────────────┐
│  python -m engine.pipeline.run <fiche> [--mode animatique|final]          │
│                                                                           │
│  contrat → continuité → bibliothèque → voix → réalisateur (timeline)     │
│      → cache → Blender [décorateur → look → animateur → caméra → rendu]   │
│      → montage (ffmpeg) → contrôles automatiques + planche contact        │
│  code 3 : prod-chef cherche les assets par API, un humain choisit         │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │  rapport.json, champ « suite »
        ┌───────────────────────┼─────────────────────────┬──────────────────────┐
        ▼                       ▼                         ▼                      ▼
 prod-controle-qualite   prod-realisateur        prod-directeur-artistique   maintenance
 (sonnet)                (sonnet)                (sonnet)                    (session de dév.,
 1 image par épisode     fiche libre/invalide    pack de DA                  engine/docs/maintenance.md)
```

Dans ce dépôt, un sous-agent n'a pas l'outil `Agent` (test du 2026-11-15 : un sous-agent lancé avec tous les outils ne l'a pas reçu). `prod-chef` indique donc dans sa réponse (champ `SUITE`) quel agent appeler ; c'est la session principale (ou l'automatisation de Lucas) qui enchaîne. Si l'imbrication devient disponible, il suffira d'ajouter `Agent` aux outils de `prod-chef`.

Conformément à l'organigramme (`docs/agents.md`), seuls les rôles qui demandent du jugement ont un fichier d'agent ; la bibliothèque et la maintenance n'en ont pas.

## Les modules (scripts, 0 crédit Claude)

| Module | Fichier | Rôle |
|---|---|---|
| Chef d'orchestre | `engine/pipeline/run.py` | enchaîne tout, codes de sortie, rapport, champ `suite` |
| Contrat | `engine/pipeline/contrat.py` | structure (JSON Schema) + cohérence (ids, cibles, paramètres) |
| Continuité | `engine/pipeline/continuite.py` | état persistant d'une série (`series/<id>/etat.json`) |
| Bibliothèque | `engine/pipeline/bibliothecaire.py` | assets disponibles et licites ? |
| Voix | `engine/pipeline/voix.py` + `engine/voix/kyutai_worker.py` | voix off Kyutai, mots horodatés, cache |
| Effets sonores | `engine/pipeline/effets_sonores.py` | pop et souffle synthétisés |
| Sources d'assets | `engine/pipeline/sources_assets.py` | recherche et import par API (Poly Haven, Poly Pizza, Sketchfab), HDRI |
| Packs de DA | `engine/pipeline/pack_da.py` | validation d'un pack (schéma + couleurs distinctes en Oklab) |
| Réalisateur (script) | `engine/pipeline/realisateur.py` | **timeline maître** : durées, mots horodatés, frames des actions |
| Cache | `engine/pipeline/cache.py` | ne re-rend que les beats dont l'image a pu changer |
| Décorateur | `engine/blender/decorateur.py` | sol, éléments, personnages, modules (instances) |
| Look | `engine/blender/look.py` | pack de DA : matériaux par rôle, monde, lumière, moteur, contours |
| Animateur | `engine/blender/animateur.py` | exécute les actions |
| Caméra | `engine/blender/camera.py` | une caméra par beat, mouvements prédéfinis, bascule par marqueurs |
| Rendu | `engine/blender/rendu.py` | frames PNG des beats demandés, bascule de moteur en secours |
| Montage | `engine/pipeline/montage.py` | sous-titres mot à mot, textes à l'écran, voix, musique, MP4 |
| Contrôle auto | `engine/pipeline/qa_auto.py` | frames, images unies, durée, audio + planche contact |

Une seule horloge : la timeline. Animateur, Caméra et Montage la lisent, aucun ne décide du timing.
Un seul module touche aux matériaux : Look.

## Les agents (fichiers `.claude/agents/`, préfixe `prod-`)

| Agent | Modèle | Appelé | Coût |
|---|---|---|---|
| `prod-chef` | sonnet | à chaque épisode | 1 passage |
| `prod-controle-qualite` | sonnet | après chaque rendu | 1 image |
| `prod-realisateur` | sonnet | fiche libre ou invalide | occasionnel |
| `prod-directeur-artistique` | sonnet | nouvelle histoire ou pack absent | 1 à 2 appels par série, le pack sert ensuite gratuitement |

Le statut de chaque agent (prévu, brouillon, testé, en service) est dans son en-tête (`statut`).

**Budget visé par épisode : 2 appels** (prod-chef + contrôle qualité), voire 1 si l'automatisation lance `engine.pipeline.run` directement et lit la ligne `SYNTHESE`.

## Ce qui rend la qualité constante sans coûter de crédits

Les briques construites une fois et réutilisées : vocabulaire d'actions, mouvements de caméra, primitives et kits de décor, modules procéduraux, packs de DA, contrôles automatiques. Chaque amélioration profite à tous les épisodes suivants.

## Ordre de production d'un épisode

1. Fiche reçue → `--valider-seulement` (1 s).
2. **Animatique** (basse définition) → contrôle qualité → validation humaine du rythme.
3. **Final** sur la machine de Guillaume (RTX 5070, EEVEE) → contrôle qualité → validation humaine → publication par un humain.

## Ce qui n'est pas encore fait (état réel au 2026-11-15)

| Élément | État |
|---|---|
| Pipeline complet fiche → MP4 | fait et vérifié (Blender 5.3 sans interface, moteur Workbench, résolution réduite) |
| Rendu EEVEE | fonctionne mais n'a été testé que sur processeur (lent) ; à vérifier sur la RTX 5070 |
| Assets de bibliothèque (`bibliotheque:`) | code écrit, **non testé** (aucun asset au registre) |
| Module Voix (Kyutai TTS) | **prévu** : la timeline accepte déjà `voix_audio` et les horodatages de mots |
| Plus de ~5 000 instances | à passer en Geometry Nodes |
| Personnages animés (squelette Mixamo) | prévu : aujourd'hui les cycles sont procéduraux (flotter, sautiller…) |
