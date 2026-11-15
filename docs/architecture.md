# Architecture de la chaîne

## Vue d'ensemble

La chaîne est organisée en **quatre pôles**, chacun avec un agent chef. Le détail des agents, sous-agents et modules est dans [`agents.md`](agents.md).

```
Idée / actions des abonnés Instagram
   │
   ▼
Storytelling (Lucas) ── idées → scénario → beats → scènes → fiche épisode JSON
   │                       contrats : contracts/fiche-episode.schema.json
   ▼                                + contracts/vocabulaire-actions.md
Production (Guillaume) ── voix → réalisateur (timeline) → Blender → animatique validée
   │                       → rendu → montage → contrôle qualité   (engine/, prod-*)
   ▼
Communication (plus tard) ── brouillons (légende, miniature) → validation humaine → publication

Pilotage (Lucas), transversal ── GitHub, Drive, comptes rendus, registre des décisions
```

L'ordre des étapes de production est **à valider** (tâche 24 du Backlog).

## Pôles et propriétaires

| Pôle | Chef | Propriétaire | Fichiers possédés |
|---|---|---|---|
| Pilotage | `pilotage` | Lucas | `.claude/agents/pilotage.md`, `.claude/skills/compte-rendu-pilotage/` |
| Storytelling | `story-chef` (prévu) | Lucas | agents `story-*` (à créer) |
| Production | `prod-chef` (aujourd'hui `production.md`) | Guillaume | `engine/` (à créer), agents `prod-*` |
| Communication | `com-chef` (aujourd'hui `communication.md`) | à définir | agents `com-*` |

Lucas possède aussi `contracts/`, `docs/` et `scripts/`. Le propriétaire écrit et maintient ; chaque PR est relue par l'autre.

## Contrats

Les pôles échangent par des contrats versionnés dans [`contracts/`](../contracts/README.md) : la fiche épisode (schéma JSON) et le vocabulaire d'actions. Ils sont validés par Lucas **et** Guillaume ; aucun n'est encore rédigé.

## Exécution

La production tourne en local chez Guillaume (RTX 5070, 12 Go de VRAM, 32 Go de RAM). Pour l'instant, les appels Claude de la production passent par l'abonnement de Guillaume.

## État d'avancement

| Brique | État |
|---|---|
| Dépôt GitHub et règles de travail | fait |
| Drive partagé et protocole Claude vers Claude | fait |
| Agent Pilotage | brouillon : v2 fusionnée (PR #18), correctifs en cours, jamais lancée |
| Pôle Storytelling | prévu (aucun fichier d'agent) |
| Pôle Production | `production.md` v1 en brouillon ; architecture v0.2 de Guillaume proposée ; premier test Blender réussi chez Guillaume (connecteur officiel Blender Lab) |
| Pôle Communication | `communication.md` v1 en brouillon ; repoussé après les premières vidéos |
| Contrats (fiche épisode, vocabulaire d'actions) | à rédiger, puis à valider à deux |
| Collecte Instagram | **à vérifier** : ce que l'API permet réellement de détecter |
| Mécanique « action d'abonné → élément de la ville » | à concevoir après la vérification ci-dessus |

## Décisions

Les décisions importantes sont consignées ici, datées.

- **2026-11-15** : objectif prioritaire = apprentissage et valorisation CV ; le lucratif est secondaire.
- **2026-11-15** : un seul dépôt partagé, une branche par tâche, PR relue par l'autre ; pas de fork entre nous.
- **2026-11-15** : trois agents pour commencer (Pilotage, Communication, Production) ; validation humaine avant toute publication.
- **2026-11-15** : coordination entre les deux Claude par le Drive partagé.
- **2026-11-15** (proposée par Lucas, à valider par Guillaume en relisant la PR) : agent Pilotage v2 = « chef de cabinet » qui prépare et synchronise sans rien décider. GitHub fait foi pour les statuts des tâches, le Backlog du Drive pour les notes et le contexte. Compte rendu tous les 3 jours, écrit uniquement dans le doc Drive « Comptes rendus de pilotage ». Relances en brouillon Gmail seulement.
- **2026-11-15** (Lucas) : organisation en pôles, avec un agent chef par pôle : Pilotage, Storytelling, Production, Communication.
- **2026-11-15** (Lucas, sur recommandation de son Claude) : le Storytelling est un pôle séparé, en amont de la production ; il produit la fiche épisode en JSON.
- **2026-11-15** (Lucas) : la Communication est traitée plus tard, une fois les premières vidéos réalisées.
- **2026-11-15** (Lucas ; à confirmer par Guillaume) : Guillaume possède la production (`engine/`, agents `prod-*`) ; Lucas possède le pilotage, le storytelling, `contracts/`, `docs/` et `scripts/`.
- **2026-11-15** (Lucas) : `.claude/agents/` reste plat, avec les préfixes `pilotage`, `story-`, `prod-`, `com-` ; le statut de chaque agent (prévu / brouillon / testé / en service) figure dans son en-tête et dans `docs/agents.md`.
- **2026-11-15** (Lucas) : les contrats (fiche épisode, vocabulaire d'actions) sont validés par Lucas et Guillaume.
- **2026-11-15** (Lucas) : le Drive est l'interface entre les deux Claude ; chaque commit, PR ou fusion est reporté dans le Journal de bord le jour même.
- **2026-11-15** (Lucas) : la production tourne en local chez Guillaume ; ses appels Claude passent pour l'instant par l'abonnement de Guillaume.
