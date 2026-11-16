---
name: ref-lowpoly-style
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Low-poly art direction for Blender inspired by PS1/PS2, Lethal Company, Mouthwashing, and Fear to Fathom. Use for readable silhouettes, minimal polygons, simple materials, and strong atmosphere.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: lowpoly, low poly, PS1, PS2, retro, Lethal Company, Mouthwashing, minimal polygon, flat shading
  related-skills: environment-artist, materials, export-pipeline, horror-style
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


# Low Poly Style Specialist

Readable silhouettes. Large shapes. Minimal polygons. Atmosphere over detail.

## When to Use

- Retro aesthetic games (PS1/PS2 era)
- Lethal Company / Mouthwashing style projects
- Mobile/low-spec targets
- Horror with efficient geometry
- Stylized simplicity

## Core Rules

1. **Readable silhouettes** — Shape reads at distance without detail
2. **Minimal polygons** — Every face must earn its place
3. **Large shapes** — Primary forms dominate; micro-detail forbidden
4. **Simple materials** — Flat or lightly textured; 512px default
5. **Limited texture sizes** — 256–512px most assets; 1024 hero only
6. **Strong atmosphere** — Lighting and fog carry visual weight

## Polygon Guidelines

| Asset | Triangle Target |
|-------|-----------------|
| Character | 500–3,000 |
| Prop | 50–500 |
| Environment module | 100–800 |
| Tree | 200–800 |
| Vehicle | 2,000–8,000 |

See `../references/polycount-budgets.md` — apply 50–90% reduction.

## Modeling Approach

- No subdivision surface
- No micro-bevels (0 bevel or single segment max)
- Flat shading OR auto smooth at 60°+
- Merge coplanar faces where possible
- Texture carries detail, not geometry

## PS1 Authenticity (Optional)

| Effect | Technique |
|--------|-----------|
| Affine texture warp | Engine-side; note in export docs |
| Vertex jitter | Slight snap to low grid |
| Low resolution | 320×240 render target reference |
| No filtering | Nearest neighbor textures |
| Z-fighting aesthetic | Intentional minimal offset (use carefully) |

## PS2 Era

- Slightly higher poly budgets
- Basic normal maps allowed
- Single directional light + ambient
- 512–1024 textures

## Material Approach

- Vertex colors for variation (preferred)
- Single texture atlas per scene/kit
- Minimal roughness variation
- Emissive for screens/lights
- No PBR micro-detail

## Silhouette Test

Before approving any asset:
1. Solid flat color material
2. View at gameplay distance
3. Silhouette must communicate identity
4. If unreadable → simplify geometry, not add detail

## Lethal Company Influence

- Industrial sci-fi interiors
- High contrast lighting
- Chunky readable props
- Fog-heavy environments
- Multiplayer-readable shapes (clear at distance)

## Mouthwashing Influence

- Soft pastel palette option
- Surreal but simple geometry
- Strong color blocking
- Uncanny but low-detail characters

## MCP Integration

1. Create low-poly blockouts via MCP
2. Enforce face count limits via MCP queries
3. Assign flat materials via MCP
4. Validate triangle budgets continuously
5. Skip subdiv/bevel modifiers entirely

## Constraints

### MUST DO
- Enforce strict poly budgets
- Prioritize silhouette over surface detail
- Use vertex colors and atlases
- Test at gameplay camera distance
- Coordinate atmosphere with lighting skill

### MUST NOT DO
- Subdivision surfaces
- High-resolution textures on background assets
- Micro-bevels or weighted normal stacks
- Sculpting detail (bake workflow unnecessary)
- Exceed triangle budgets "just a little"

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|-----------|
| PS1 techniques | `references/ps1-aesthetic.md` | Retro authentic look |
| Asset budgets | `../references/polycount-budgets.md` | Budget setting |
