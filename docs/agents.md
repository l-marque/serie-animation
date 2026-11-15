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
| `story-chef` | Chef du pôle : fait proposer des idées par `story-idees`, les fait relire par `story-continuite`, les présente à Lucas avec leur verdict, consigne l'idée choisie dans `docs/storytelling/idees-retenues.md` | `.claude/agents/story-chef.md` | brouillon |
| `story-idees` | 5 idées d'épisodes courts (9:16, 30 à 60 s) : accroche, déroulé, influence de l'audience, difficulté | `.claude/agents/story-idees.md` | brouillon |
| `story-continuite` | Relit les idées (ou un scénario) avant le choix de Lucas : 6 contrôles sourcés (éléments, mémoire de série, cohérence, doublon, faisabilité, compréhension seule) ; lecture seule. Appelé par `story-chef` après `story-idees` | `.claude/agents/story-continuite.md` | brouillon |
| `story-scenario` | Scénario d'épisode complet à partir d'une idée retenue (déroulé en 5 temps, intentions de voix off, contraintes, grille sur 7), proposé à la validation de Lucas dans `docs/storytelling/scenarios/` | `.claude/agents/story-scenario.md` | brouillon |
| `story-beats` | Découpage en beats, avec le texte dit par la voix | aucun | prévu |
| `story-scenes` | Séquencement en scènes | aucun | prévu |
| `story-fiche` | Fiche épisode JSON conforme à `contracts/fiche-episode.schema.json` | aucun | prévu |

### Production — propriétaire : Guillaume

| Agent ou module | Rôle | Forme | Statut |
|---|---|---|---|
| `prod-chef` | Chef du pôle : lance le pipeline `engine/`, traite les assets manquants (recherche par API, choix humain), indique l'agent suivant | `.claude/agents/prod-chef.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-realisateur` | Transforme un brief libre en fiche épisode, ou corrige une fiche refusée | `.claude/agents/prod-realisateur.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-controle-qualite` | Juge la planche contact d'un rendu (lisibilité, image et voix, défauts) | `.claude/agents/prod-controle-qualite.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-directeur-artistique` | Ajouté à la demande de Guillaume : propose 3 directions artistiques selon l'histoire, écrit le pack de DA choisi par un humain ; enrichit le décor d'un épisode (détails qui ont une raison visuelle) et critique le rendu avec une note chiffrée et des pistes d'amélioration classées par coût | `.claude/agents/prod-directeur-artistique.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| contrat, continuité, bibliothèque et sources d'assets, timeline, cache, décorateur, look, animateur, caméra, rendu, montage, contrôles automatiques, chef d'orchestre `run.py` | Modules de la chaîne de fabrication, sans appel à Claude | code Python dans `engine/` (voir `engine/README.md`) | testés (34 tests ; EEVEE validé sur la RTX 5070) |
| voix (Kyutai TTS) et son | Voix off avec mots horodatés, sous-titres karaoké, effets de rythme, musique baissée sous la voix | code dans `engine/` (`engine/docs/voix-et-son.md`) | testé sur le PC de Guillaume (Kyutai sur CPU) |
| module habillage | Sous-titres mot par mot, cartes de commentaires, compteurs | code Python | idée à confirmer par Guillaume |

Objectif : 1 à 2 appels Claude par épisode (prod-chef + contrôle qualité ; 1 seul si l'automatisation lance `python -m engine.pipeline.run` et lit la ligne `SYNTHESE`). La maintenance du code n'a pas d'agent : elle suit `engine/docs/maintenance.md`.

### Communication — propriétaire : à définir

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `com-chef` | Chef du pôle : légendes, visuels, calendrier, retours de l'audience | aujourd'hui `.claude/agents/communication.md` (v1) | prévu, repoussé après les premières vidéos |
| `com-legendes` | Brouillons de publication à partir d'un scénario : légende Instagram (2 variantes), titre et description YouTube Shorts, texte d'accroche, en français et en anglais, dans `docs/communication/brouillons/`. Ne publie rien, sans accès réseau. Sous-agent appelé à la main par Lucas tant que `com-chef` n'existe pas | `.claude/agents/com-legendes.md` | brouillon |

## Convention de nommage dans `.claude/agents/`

- Dossier **plat** : pas de sous-dossiers.
- Un préfixe par pôle : `pilotage`, `story-`, `prod-`, `com-`.
- Nom de fichier = champ `name` de l'en-tête, en minuscules, mots séparés par des tirets, sans accent (exemple : `prod-controle-qualite.md`).
- `production.md` est devenu `prod-chef.md` (décision de Guillaume, 2026-11-15). `communication.md` garde son nom tant que le renommage en `com-chef` n'est pas décidé.

## Hiérarchie entre agents : ce que permet Claude Code

D'après la documentation de Claude Code (page « sub-agents », consultée le 2026-11-15), un sous-agent **peut** lancer ses propres sous-agents, jusqu'à trois niveaux sous la conversation principale, à condition que l'outil `Agent` figure dans sa liste `tools`. La limite se règle avec `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. Un chef de pôle peut donc piloter ses sous-agents directement. Non testé dans ce dépôt : à vérifier par un petit essai avant de figer l'arborescence.
