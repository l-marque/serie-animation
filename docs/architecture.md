# Architecture de la chaîne

## Vue d'ensemble

```
Instagram (actions des abonnés)
   │  collecte (API Instagram, compte professionnel)
   ▼
File d'événements à valider  ──►  validation humaine
   │
   ▼
Agent Production ──► Blender (MCP / scripts) ──► rendu (aperçu puis final)
   │
   ▼
Agent Communication ──► brouillons (légende, miniature) ──► validation ──► publication
   │
   ▼
Agent Pilotage ──► issues GitHub, journal, point hebdo, passation Drive
```

## État d'avancement

| Brique | État |
|---|---|
| Dépôt GitHub et règles de travail | fait |
| Drive partagé et protocole Claude vers Claude | fait |
| Agent Pilotage | v2 rédigée (chef de cabinet, 12 missions, compte rendu tous les 3 jours) ; non testée, premier passage après relecture |
| Agent Communication | défini, à tester |
| Agent Production | v1 : pipeline fiche épisode -> vidéo + 4 sous-agents (voir `docs/production/`) ; testé sans GPU, à valider sur la machine de Guillaume |
| Collecte Instagram | **à vérifier** : ce que l'API permet réellement de détecter |
| Mécanique « action d'abonné → élément de la ville » | à concevoir après la vérification ci-dessus |

## Décisions

Les décisions importantes sont consignées ici, datées.

- **2026-11-15** : objectif prioritaire = apprentissage et valorisation CV ; le lucratif est secondaire.
- **2026-11-15** : un seul dépôt partagé, une branche par tâche, PR relue par l'autre ; pas de fork entre nous.
- **2026-11-15** : trois agents pour commencer (Pilotage, Communication, Production) ; validation humaine avant toute publication.
- **2026-11-15** : coordination entre les deux Claude par le Drive partagé.
- **2026-11-15** (proposée par Lucas, à valider par Guillaume en relisant la PR) : agent Pilotage v2 = « chef de cabinet » qui prépare et synchronise sans rien décider. GitHub fait foi pour les statuts des tâches, le Backlog du Drive pour les notes et le contexte. Compte rendu tous les 3 jours, écrit uniquement dans le doc Drive « Comptes rendus de pilotage ». Relances en brouillon Gmail seulement.
- **2026-11-15** (proposée par Guillaume, PR #20) : production pilotée par une fiche épisode JSON (contrat versionné) et un pipeline scripté ; Claude n'intervient que pour le jugement (2 appels visés par épisode).
