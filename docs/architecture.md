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
| Agent Pilotage | défini, à tester |
| Agent Communication | défini, à tester |
| Agent Production | brouillon (attend Blender et le MCP) |
| Collecte Instagram | **à vérifier** : ce que l'API permet réellement de détecter |
| Mécanique « action d'abonné → élément de la ville » | à concevoir après la vérification ci-dessus |

## Décisions

Les décisions importantes sont consignées ici, datées.

- **2026-11-15** : objectif prioritaire = apprentissage et valorisation CV ; le lucratif est secondaire.
- **2026-11-15** : un seul dépôt partagé, une branche par tâche, PR relue par l'autre ; pas de fork entre nous.
- **2026-11-15** : trois agents pour commencer (Pilotage, Communication, Production) ; validation humaine avant toute publication.
- **2026-11-15** : coordination entre les deux Claude par le Drive partagé.
