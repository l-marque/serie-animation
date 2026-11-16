---
name: ref-lookdev
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Look development loop for Blender assets combining materials, lighting, camera, and screenshot comparison until shading reads correctly.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: lookdev, look development, shading review, material lighting loop, turntable, asset presentation
  related-skills: materials, lighting, rendering, camera-cinematography, compositing, qa-review
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


# Lookdev

Material + light + camera loop. Screenshot compare. Stop when it reads.

## When to Use

- Finalizing asset shading before export/portfolio
- Turntable / grey shader checks
- Matching material references
- Bridging `materials` and `lighting` intentionally

## Workflow

```
Clay/grey pass → Base materials → Neutral light rig
  → Beauty light → Screenshot → Gap list → Iterate (≤3–5)
  → Optional grade → QA
```

## Standard Rigs

| Rig | Use |
|-----|-----|
| Neutral 3-point | Evaluate materials fairly |
| HDRI studio | Product / character |
| In-situ scene lights | Final context |

Keep a reusable `COL_Lookdev_Lights` + `CAM_Lookdev_*`.

## Checklist

- [ ] Values read in grayscale
- [ ] Specular roughness believable
- [ ] Edges catch light (bevels/normals)
- [ ] Emissive under control
- [ ] No pure black / pure white traps unless stylized
- [ ] Matches reference palette if provided

## Iteration Rule

Each pass: change one major variable (material OR light OR camera), then screenshot.

## Constraints

### MUST DO
- Grey pass before fancy textures when forms unsure
- Capture screenshots each iteration
- Hand off to `qa-review` before ship

### MUST NOT DO
- Fix modeling problems only with roughness maps
- Infinite tweak loops without gap list

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Lookdev Rig | `references/lookdev-rig.md` | When needed |
| Lookdev Checklist | `references/lookdev-checklist.md` | When needed |
