# Série d'animation pilotée par des agents IA

> Une ville 3D construite dans Blender, qui évolue au fil des épisodes en fonction des actions de son audience Instagram. Toute la chaîne (production, pilotage, communication) est orchestrée par des agents Claude.

**Statut :** phase de fondations (novembre 2026).

## L'idée

Le produit, c'est une série de vidéos d'animation. Le vrai sujet du projet, c'est **la chaîne qui la fabrique** :

```
Audience Instagram ──► collecte ──► agents Claude ──► Blender ──► rendu ──► validation humaine ──► publication
```

Chaque étape est confiée à un agent spécialisé, avec un humain qui valide avant toute publication.

## Les agents

| Agent | Rôle | Outils |
|---|---|---|
| **Pilotage** | Suivi des tâches, journal de bord, point hebdomadaire | GitHub Issues, Google Drive |
| **Communication** | Légendes, visuels, calendrier de publication | Canva, Google Drive |
| **Production** | Pilotage de Blender : scènes, objets, rendus | Blender MCP, scripts Python |

Les définitions des agents sont dans [`.claude/agents/`](.claude/agents/).

## Organisation du dépôt

```
.claude/agents/    définitions des agents Claude
docs/              architecture, décisions, conventions
blender/scripts/   scripts Python exécutés dans Blender
scripts/           automatisation hors Blender
assets/            petits fichiers uniquement (les lourds sont sur le Drive)
CLAUDE.md          contexte partagé lu par tous les agents
CONTRIBUTING.md    règles de travail à deux
```

## Stack

Blender · Claude (Claude Code, sous-agents, MCP) · GitHub · Google Drive · Canva · API Instagram / YouTube

## Équipe

- **Lucas Marque** : architecture des agents, automatisation, GitHub, pilotage du projet
- **Guillaume** : 3D, modélisation et animation dans Blender
