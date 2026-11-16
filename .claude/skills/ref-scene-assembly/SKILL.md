---
name: ref-scene-assembly
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Large scene layout in Blender with collections, linking, overrides, streaming-friendly organization, and set assembly.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: scene assembly, layout, linking, library override, collection instance, level layout, set assembly, outliner organization
  related-skills: environment-artist, set-dressing, blender-modeler, lighting, qa-review
---
> **Cadre d'utilisation dans ce dépôt (ajouté par le Claude de Guillaume, 2026-11-16).** Référence externe
> (MIT, https://github.com/arjun988/blender-skills, v1.3.0), **à lire, pas à exécuter**. En cas de contradiction,
> font foi, dans cet ordre : `CLAUDE.md`, les contrats (`contracts/`), les agents `prod-*` et `story-*`,
> `engine/docs/` (dont `conventions-blender.md` pour le nommage) et les décisions notées dans le Drive.
> En particulier : (1) la production passe par le code de `engine/` et la fiche épisode, **jamais par des
> modifications manuelles d'une scène via le MCP Blender** ; (2) les noms `COL_*`, `LGT_*`, `FX_*` de ce
> texte sont remplacés par les conventions du dépôt ; (3) les parties export vers un moteur de jeu, LOD et
> collisions ne concernent pas la série ; (4) un verdict « ship » ne remplace jamais la validation humaine.
> Les renvois à `../references/` et aux autres skills du pack ne sont pas installés : ignore-les.


# Scene Assembly

Layouts that scale. Clear collections. Linking/overrides for big sets.

## When to Use

- Levels, dioramas, cinematic sets
- Assembling modular kits into spaces
- Library linking / collection instances
- Outliner structure for team scenes

## Workflow

```
Block layout (greybox) → Modular assemble → Set dressing
  → Lighting volumes → Cameras → QA pass → Optimize visibility
```

## Collection Structure

```
COL_Layout
COL_Modular_Geo
COL_SetDressing
COL_Lights
COL_Cameras
COL_FX
COL_Collision
COL_Trash / COL_Ref
```

## Linking Strategy

| Approach | When |
|----------|------|
| Collection instance | Repeated modular pieces |
| Library link + override | Shared hero assets across scenes |
| Append | One-off ownership transfer |

Prefer non-destructive linking for repeated kits.

## Layout Rules

1. Greybox scale and navigation first
2. Snap to grid for modular kits
3. Hide heavy collections while dressing
4. Keep world origin meaningful (level zero)

## Performance Hygiene

- Instance repeated meshes
- Cull unseen interiors
- Separate streaming volumes if game-oriented
- Avoid unique high materials on every duplicate

## Handoff

- Dressing → `set-dressing`
- Mood → `lighting` + style skill
- Gate → `qa-review`

## Constraints

### MUST DO
- Establish collection hierarchy early
- Greybox before final dressing
- Name cameras and light groups

### MUST NOT DO
- Dump everything in Scene Collection
- Apply library overrides casually without need
- Duplicate hero meshes instead of instancing

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Collection Template | `references/collection-template.md` | When needed |
| Linking Overrides | `references/linking-overrides.md` | When needed |
