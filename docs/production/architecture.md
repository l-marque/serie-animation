# Architecture de l'agent Production (v1.0)

## En une phrase

Une **fiche épisode** (JSON) entre, une **vidéo 9:16** sort. Entre les deux, un pipeline **scripté et déterministe** fait le travail ; des **sous-agents Claude** n'interviennent que là où le jugement est utile.

```
   fiche épisode (des autres agents)
              │
              ▼
┌──────────────────────── agent production (sonnet) ────────────────────────┐
│  python -m scripts.production.run <fiche> [--mode animatique|final]      │
│                                                                           │
│  contrat → continuité → bibliothécaire → réalisateur (timeline maître)    │
│      → cache → Blender [décorateur → look → animateur → caméra → rendu]   │
│      → montage (ffmpeg) → contrôles automatiques + planche contact        │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │  rapport.json, champ « suite »
          ┌─────────────────────┼──────────────────────┬─────────────────────┐
          ▼                     ▼                      ▼                     ▼
 production-controle-   production-realisateur  production-bibliothecaire  production-technicien
 qualite (sonnet)       (sonnet)                (haiku)                    (opus)
 1 image par épisode    fiche invalide/libre    assets manquants           échec, nouvelle brique
```

Dans Claude Code, un sous-agent ne peut pas en lancer un autre. L'agent `production` lance le pipeline et indique dans sa réponse (champ `SUITE`) quel spécialiste appeler ; c'est la session principale (ou l'automatisation de Lucas) qui enchaîne.

## Les modules (scripts, 0 crédit Claude)

| Module | Fichier | Rôle |
|---|---|---|
| Chef d'orchestre | `scripts/production/run.py` | enchaîne tout, codes de sortie, rapport, champ `suite` |
| Contrat | `scripts/production/contrat.py` | structure (JSON Schema) + cohérence (ids, cibles, paramètres) |
| Continuité | `scripts/production/continuite.py` | état persistant d'une série (`series/<id>/etat.json`) |
| Bibliothécaire (script) | `scripts/production/bibliothecaire.py` | assets disponibles et licites ? |
| Réalisateur (script) | `scripts/production/realisateur.py` | **timeline maître** : durées, mots horodatés, frames des actions |
| Cache | `scripts/production/cache.py` | ne re-rend que les beats dont l'image a pu changer |
| Décorateur | `blender/scripts/production/decorateur.py` | sol, éléments, personnages, modules (instances) |
| Look | `blender/scripts/production/look.py` | pack de DA : matériaux par rôle, monde, lumière, moteur, contours |
| Animateur | `blender/scripts/production/animateur.py` | exécute les actions |
| Caméra | `blender/scripts/production/camera.py` | une caméra par beat, mouvements prédéfinis, bascule par marqueurs |
| Rendu | `blender/scripts/production/rendu.py` | frames PNG des beats demandés, bascule de moteur en secours |
| Montage | `scripts/production/montage.py` | sous-titres mot à mot, textes à l'écran, voix, musique, MP4 |
| Contrôle auto | `scripts/production/qa_auto.py` | frames, images unies, durée, audio + planche contact |

Une seule horloge : la timeline. Animateur, Caméra et Montage la lisent, aucun ne décide du timing.
Un seul module touche aux matériaux : Look.

## Les sous-agents (fichiers `.claude/agents/`)

| Agent | Modèle | Appelé | Coût |
|---|---|---|---|
| `production` | sonnet | à chaque épisode | 1 passage |
| `production-controle-qualite` | sonnet | après chaque rendu | 1 image |
| `production-realisateur` | sonnet | fiche libre ou invalide | occasionnel |
| `production-bibliothecaire` | haiku | asset manquant | occasionnel, tâche simple |
| `production-technicien` | opus | échec ou nouvelle brique | rare, la brique sert ensuite à chaque épisode |

**Budget visé par épisode : 2 appels** (production + contrôle qualité). Le modèle le plus cher n'intervient que pour construire des briques durables.

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
