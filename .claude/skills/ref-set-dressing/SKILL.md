---
name: ref-set-dressing
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Set dressing and environmental storytelling placement for interiors and exteriors using prop density, narrative clusters, and readability rules.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: set dressing, dressing, storytelling props, interior dressing, clutter, narrative placement, set decals
  related-skills: prop-artist, scene-assembly, environment-artist, horror-style, qa-review
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


# Set Dressing

Story through placement. Controlled clutter. Readable clusters.

## When to Use

- Interior/exterior dressing passes
- Narrative prop clusters
- Avoiding empty or overstuffed spaces
- After modular layout is locked

## Workflow

```
Layout locked → Hero narrative props → Secondary clusters
  → Background filler → Decals/wear → Lighting check → QA
```

## Density Rules

| Zone | Density |
|------|---------|
| Hero interact zone | High intent, low noise |
| Midground | Supporting story clusters |
| Background | Sparse; silhouette only |
| Traversal path | Clearance for player/camera |

## Cluster Method

1. Pick a story beat (meal abandoned, workbench used, escape rushed)
2. Place 3–7 props that sell the beat
3. Add 1–2 wear/decal cues
4. Stop — do not fill every surface

## Prop Sources

- `prop-artist` for unique pieces
- Kitbash / modular libraries for filler
- Instance repeats; vary rotation/scale slightly

## Horror / Sparse Styles

- Fewer props, more meaning
- Negative space intentional
- Coordinate with `horror-style` / `psx-horror-style`

## Constraints

### MUST DO
- Dress after greybox navigation works
- Keep player/camera paths clear
- Instance repeated meshes

### MUST NOT DO
- Uniform clutter wallpaper
- Block doors/windows without story reason

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Story Clusters | `references/story-clusters.md` | When needed |
| Density Map | `references/density-map.md` | When needed |
