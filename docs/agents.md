# Carte des agents

Source : « 2026-11-15_claude-lucas_organigramme-agents-v0.1 » (Drive, `01_Claude_Lucas`). Ce qui touche la production attend la validation de Guillaume.

## Principe

- **Un chef par pôle.** Le chef reçoit la demande, la découpe et confie le travail à ses sous-agents ou à des modules en code.
- **Un module qui n'a pas besoin de jugement reste du code** (Python, dans `engine/`) plutôt qu'un agent : moins d'appels Claude, résultat reproductible.
- **Propriétaire** : la personne qui écrit et maintient les fichiers du pôle. Chaque PR est relue par l'autre.

## Statuts

| Statut | Sens |
|---|---|
| prévu | décidé, aucun fichier d'agent |
| brouillon | fichier écrit, jamais lancé sur un cas réel |
| testé | lancé au moins une fois sur un cas réel, résultat vérifié par un humain |
| en service | utilisé régulièrement dans la chaîne |

Le statut d'un agent est aussi indiqué dans l'en-tête de son fichier (champ `statut`).

## Les pôles

### Pilotage — propriétaire : Lucas

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `pilotage` | Chef de cabinet : suivi GitHub et Drive, compte rendu tous les 3 jours, registre des décisions, relances en brouillon | `.claude/agents/pilotage.md` | brouillon (v2 fusionnée, jamais lancée) |

Un seul agent, sans sous-agent.

### Storytelling — propriétaire : Lucas

Pôle séparé, **en amont** de la production. Il transforme une idée en fiche épisode JSON, que la production consomme.

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `story-chef` | Chef du pôle : enchaîne les étapes ci-dessous | aucun | prévu |
| `story-idees` | Idées d'épisodes | aucun | prévu |
| `story-scenario` | Scénario | aucun | prévu |
| `story-beats` | Découpage en beats, avec le texte dit par la voix | aucun | prévu |
| `story-scenes` | Séquencement en scènes | aucun | prévu |
| `story-fiche` | Fiche épisode JSON conforme à `contracts/fiche-episode.schema.json` | aucun | prévu |

### Production — propriétaire : Guillaume

| Agent ou module | Rôle | Forme | Statut |
|---|---|---|---|
| `prod-chef` | Chef du pôle : pilote les modules et les deux agents ci-dessous | agent ; aujourd'hui `.claude/agents/production.md` (v1) | brouillon (v1, renommage à décider) |
| `prod-realisateur` | Construit la timeline à partir de la fiche épisode quand elle n'est pas assez structurée | agent | prévu |
| `prod-controle-qualite` | Juge le contenu du rendu final | agent | prévu |
| voix, bibliothécaire, décorateur, animateur, caméra, look, rendu et montage, chef d'orchestre déterministe | Modules de la chaîne de fabrication, sans appel à Claude | code Python dans `engine/` | prévu (architecture v0.2 de Guillaume) |

Objectif : 1 à 2 appels Claude par épisode. La liste exacte des modules est à confirmer par Guillaume.

### Communication — propriétaire : à définir

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `com-chef` | Chef du pôle : légendes, visuels, calendrier, retours de l'audience | aujourd'hui `.claude/agents/communication.md` (v1) | prévu, repoussé après les premières vidéos |

## Convention de nommage dans `.claude/agents/`

- Dossier **plat** : pas de sous-dossiers.
- Un préfixe par pôle : `pilotage`, `story-`, `prod-`, `com-`.
- Nom de fichier = champ `name` de l'en-tête, en minuscules, mots séparés par des tirets, sans accent (exemple : `prod-controle-qualite.md`).
- Les fichiers v1 `production.md` et `communication.md` gardent leur nom tant que Lucas et Guillaume n'ont pas décidé du renommage en `prod-chef` et `com-chef`.

## Hiérarchie entre agents : ce que permet Claude Code

D'après la documentation de Claude Code (page « sub-agents », consultée le 2026-11-15), un sous-agent **peut** lancer ses propres sous-agents, jusqu'à trois niveaux sous la conversation principale, à condition que l'outil `Agent` figure dans sa liste `tools`. La limite se règle avec `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. Un chef de pôle peut donc piloter ses sous-agents directement. Non testé dans ce dépôt : à vérifier par un petit essai avant de figer l'arborescence.
