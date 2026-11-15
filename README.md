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

La chaîne est découpée en quatre pôles, chacun dirigé par un agent chef. Carte complète et statuts : [`docs/agents.md`](docs/agents.md).

| Pôle | Agent chef | Rôle | Propriétaire | Statut |
|---|---|---|---|---|
| **Pilotage** | `pilotage` | Suivi GitHub et Drive, comptes rendus, registre des décisions | Lucas | brouillon |
| **Storytelling** | `story-chef` | Idée → scénario → beats → scènes → fiche épisode JSON | Lucas | prévu |
| **Production** | `prod-chef` | Fiche épisode → voix, Blender, rendu, montage, contrôle qualité | Guillaume | brouillon (v1) |
| **Communication** | `com-chef` | Légendes, visuels, calendrier de publication | à définir | prévu, plus tard |

Les définitions des agents sont dans [`.claude/agents/`](.claude/agents/), les contrats entre pôles dans [`contracts/`](contracts/).

## Organisation du dépôt

```
.claude/agents/    définitions des agents Claude (préfixes pilotage, story-, prod-, com-)
.claude/skills/    procédures réutilisables des agents
contracts/         contrats entre pôles (fiche épisode, vocabulaire d'actions)
docs/              architecture, carte des agents, décisions, conventions
engine/            production : pipeline, scripts Blender, packs de DA, assets (voir engine/README.md)
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
