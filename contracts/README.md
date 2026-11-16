# Contrats entre pôles

Un contrat fixe le format des données échangées entre deux pôles. Tant qu'un contrat est respecté, chaque pôle peut changer son fonctionnement interne sans casser les autres.

## Règles

- Un contrat est **validé par Lucas ET Guillaume** avant d'être utilisé. Toute modification passe par une PR relue par les deux.
- Un contrat versionné ici fait foi ; les brouillons et discussions restent sur le Drive.
- Propriétaire du dossier : Lucas (rédaction). La validation reste commune.

## Contrats prévus

Les deux contrats ci-dessous ont une **proposition de Guillaume** (PR #20), déjà implémentée et testée par la production. Ils restent à valider par Lucas et Guillaume.

| Fichier | Entre | Rôle | Source de départ | Statut | Tâche |
|---|---|---|---|---|---|
| `fiche-episode.schema.json` | Storytelling → Production | Schéma JSON de la fiche épisode produite par `story-fiche` et lue par la production | proposition de Guillaume « architecture-blender-v0.1 » (Drive, `02_Claude_Guillaume`) | proposition de Guillaume v1.0 (PR #20), à valider | Backlog 13 |
| `vocabulaire-actions.md` | Storytelling → Production | Liste fermée des actions qu'une fiche épisode peut demander à la production | architecture Production v0.2 de Guillaume | proposition de Guillaume v1.0 (PR #20), à valider | Backlog 24 |

## Historique des versions

| Version | Date | Contrats touchés | Changement | Compatibilité | Décidé par |
|---|---|---|---|---|---|
| 1.0 | 2026-11-15 | `fiche-episode.schema.json`, `vocabulaire-actions.md` | Proposition initiale de Guillaume (PR #20) | — | proposition de Guillaume, à valider |
| 1.1 | 2026-11-16 | `fiche-episode.schema.json`, `vocabulaire-actions.md` | Champ facultatif `habillage.textes_3d` (textes 3D, cartes de choix), repris de `engine/schemas/habillage.schema.json` ; mouvement de caméra `descente` (prévu : à implémenter dans `engine/` par la production). Ces deux ajouts exigent `"version": "1.1"`. | **Rétrocompatible** : une fiche 1.0 reste valide telle quelle ; rien n'est retiré ni renommé | Lucas (2026-11-16, 10 h 23) ; répartition du travail moteur à confirmer par Guillaume |
