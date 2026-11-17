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
| abandonné | décidé de ne pas le construire (raison et date indiquées) |

Le statut d'un agent est aussi indiqué dans l'en-tête de son fichier (champ `statut`).

## Orchestrateur de bout en bout — propriétaire : Lucas

| Commande | Rôle | Fichier | Statut |
|---|---|---|---|
| `/episode` | « Une vidéo en un seul prompt » : enchaîne `story-chef` puis `prod-chef` dans la conversation principale, avec 5 arrêts de validation humaine, un fichier de suivi par épisode (`episodes/suivi/<id>.json`) et une branche `episode/<id>` qui passe d'une machine à l'autre. Ne publie jamais. Détails : `docs/orchestrateur.md` | `.claude/commands/episode.md` | brouillon |

```
/episode <demande>
  └─ entrée audience (chiffres donnés par Lucas ; mise à jour de episodes/serie/etat.json après accord)
  └─ story-chef ─ idées ─────── ARRÊT 1 (Lucas choisit l'idée)
                ─ scénario ──── ARRÊT 2 (Lucas valide)
                ─ voix ──────── ARRÊT 3 (Lucas valide le texte)
                ─ découpage ─── ARRÊT 4 (Lucas valide)
  └─ [Blender présent ? sinon : push de episode/<id>, reprise sur le PC de Guillaume]
  └─ prod-chef ─ fiche (prod-realisateur) ─ ARRÊT PLAQUETTE Figma (Guillaume) ─ animatique ─ contrôle qualité ─ corrections (≤ 2)
               ─ rendu final (sur demande explicite) ─ ARRÊT 5 (Lucas ET Guillaume)
  └─ PR episode/<id> → main, jamais fusionnée ; com-legendes seulement proposé
```

C'est une commande et non un agent : un sous-agent lancé dans le cloud ne reçoit pas l'outil `Agent` (voir « Hiérarchie entre agents »), la conversation principale si.

## Les pôles

### Pilotage — propriétaire : Lucas

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `pilotage` | Chef de cabinet : suivi GitHub et Drive, compte rendu tous les 3 jours, registre des décisions, relances en brouillon | `.claude/agents/pilotage.md` | brouillon (v2 fusionnée, jamais lancée) |

Un seul agent, sans sous-agent.

### Storytelling — propriétaire : Lucas

Pôle séparé, **en amont** de la production. Il transforme une idée en **découpage où tout est décidé** (voix, plans, décor chiffré), que la production traduit en fiche épisode JSON (`prod-realisateur`) puis construit. Référence commune : `docs/storytelling/gabarit-realisation.md`.

| Agent | Rôle | Fichier | Statut |
|---|---|---|---|
| `story-chef` | Chef du pôle : enchaîne idées → continuité → scénario → continuité → beats → découpage → continuité, avec 4 arrêts de validation par Lucas (idée, scénario, voix, découpage), puis remet le découpage à `prod-chef` ; repli `SUITE` sans outil `Agent` | `.claude/agents/story-chef.md` | brouillon |
| `story-idees` | 5 idées d'épisodes courts (9:16, 30 à 60 s) : accroche, déroulé, influence de l'audience, difficulté | `.claude/agents/story-idees.md` | brouillon |
| `story-continuite` | Relit les idées (ou un scénario) avant le choix de Lucas : 6 contrôles sourcés (éléments, mémoire de série, cohérence, doublon, faisabilité, compréhension seule) ; lecture seule. Appelé par `story-chef` après `story-idees` | `.claude/agents/story-continuite.md` | brouillon |
| `story-scenario` | Scénario d'épisode complet à partir d'une idée retenue (déroulé en 5 temps, intentions de voix off, contraintes, grille sur 7), proposé à la validation de Lucas dans `docs/storytelling/scenarios/` | `.claude/agents/story-scenario.md` | brouillon |
| `story-beats` | Texte exact de la voix off en beats chronométrés (durées, intonation, mots appuyés, pauses, sous-titres, texte à l'écran, compteur), dans `docs/storytelling/beats/` ; règles de voix Kyutai | `.claude/agents/story-beats.md` | brouillon |
| `story-decoupage` | Découpage technique plan par plan à partir d'une voix validée (décor chiffré, caméra, actions calées sur les mots, zone sûre, sons), dans `docs/storytelling/decoupage/` ; briques manquantes et champs hors contrat v1.0 listés | `.claude/agents/story-decoupage.md` | brouillon |
| `story-scenes` | Séquencement en scènes | aucun | abandonné (décision de Lucas, 2026-11-16 : JSON et validation par prod-realisateur, scènes intégrées au découpage) |
| `story-fiche` | Fiche épisode JSON conforme à `contracts/fiche-episode.schema.json` | aucun | abandonné (décision de Lucas, 2026-11-16 : JSON et validation par prod-realisateur, scènes intégrées au découpage) |

### Production — propriétaire : Guillaume

| Agent ou module | Rôle | Forme | Statut |
|---|---|---|---|
| `prod-chef` | Chef du pôle : lance le pipeline `engine/`, traite les assets manquants (recherche par API, choix humain), indique l'agent suivant | `.claude/agents/prod-chef.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-realisateur` | Transforme un brief libre en fiche épisode, ou corrige une fiche refusée | `.claude/agents/prod-realisateur.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-controle-qualite` | Juge la planche contact d'un rendu (lisibilité, image et voix, défauts) | `.claude/agents/prod-controle-qualite.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-directeur-artistique` | Ajouté à la demande de Guillaume : propose 3 directions artistiques selon l'histoire, écrit le pack de DA choisi par un humain ; enrichit le décor d'un épisode (détails qui ont une raison visuelle) et critique le rendu avec une note chiffrée et des pistes d'amélioration classées par coût | `.claude/agents/prod-directeur-artistique.md` | testé (cas réels le 2026-11-15, résultats validés par Guillaume) |
| `prod-modeleur` | Ajouté à la demande de Guillaume (2026-11-17) : crée lui-même dans Blender les personnages, tenues, décors et ruines de la série (atelier `engine/outils/atelier/`, Blender ouvert en direct), s'autocontrôle sur des rendus, propose des variantes et enregistre le modèle dans la bibliothèque | `.claude/agents/prod-modeleur.md` | nouveau (fondé sur jour-1 v2, pas encore appelé comme agent) |
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

D'après la documentation de Claude Code (page « sub-agents », consultée le 2026-11-15), un sous-agent **peut** lancer ses propres sous-agents, jusqu'à trois niveaux sous la conversation principale, à condition que l'outil `Agent` figure dans sa liste `tools`. La limite se règle avec `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`. Un chef de pôle peut donc piloter ses sous-agents directement.

État réel dans ce dépôt :

- **Fait et vérifié, en local** (Claude Code de Lucas, 2026-11-15) : `story-chef` appelle `story-idees` puis `story-scenario` ; l'imbrication fonctionne.
- **Fait et vérifié par Guillaume, en environnement cloud** (2026-11-15) : un sous-agent ne reçoit pas l'outil `Agent`. Conséquence : `prod-chef` a l'outil `Agent`, mais prévoit un repli, le champ `SUITE` de sa sortie, pour que l'appel suivant soit fait par la conversation principale.
- **Prévu, pas encore testé** : le lien `story-scenario` → `prod-realisateur` (pilote du canard, issue #16).
