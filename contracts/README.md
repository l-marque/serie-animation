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
