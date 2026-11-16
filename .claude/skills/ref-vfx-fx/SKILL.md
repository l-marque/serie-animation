---
name: ref-vfx-fx
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Cinematic and game VFX in Blender including smoke, fire, particles, trails, and Geometry Nodes FX setups.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: VFX, FX, smoke, fire, explosion, particles, sparks, trails, muzzle flash, magic effect, geometry nodes FX
  related-skills: geometry-nodes, physics-sim, materials, lighting, rendering, compositing
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


# VFX / FX

Readable effects. Controlled simulation domains. Game sprites vs cinematic volumes.

## When to Use

- Smoke, fire, dust, sparks, debris
- Magic / sci-fi energy FX
- Muzzle flashes, trails, impacts
- Geometry Nodes driven particle systems

## Path Decision

```
Game real-time → Meshes/cards/ribbons + emissive mats (+ GN)
Cinematic     → Mantaflow / particles / GN → render → comp
Hybrid        → Sim in Blender → bake flipbooks/meshes for engine
```

## Workflow

```
Brief (silhouette + timing) → Proxy emitter → Sim/GN prototype
  → Art-direct motion → Materials/lights → Cache → Render/comp or export
```

## Effect Types

| Type | Blender Approach |
|------|------------------|
| Smoke/fire | Mantaflow domain + flow; keep domain tight |
| Sparks | Particle Newtonian + collision + trail |
| Debris | Rigid body shards (`physics-sim`) |
| Magic ribbons | Curves / GN extrude + emissive |
| Dust hit | Short particle burst + soft sprites |

## Domain Rules (Volume)

- Domain only as large as needed
- Resolution from low → high after motion approved
- Open borders intentionally; avoid wasted empty voxels
- Collection: `COL_FX_[Shot]`

## Naming

- Emitters: `FX_Emit_[Name]`
- Domains: `FX_Domain_[Name]`
- Caches: document frame range in brief

## Game Export Notes

- Prefer mesh cards / GN instances over volume export
- Atlas flipbooks when baking fire/smoke for engines
- Keep pivot at logical spawn point

## Constraints

### MUST DO
- Approve motion at low res before high-res sim
- Light FX intentionally (emissive + key)
- Cache before final render

### MUST NOT DO
- Huge empty domains
- Unbounded particle counts
- Skip timing brief (start/peak/end frames)

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Fx Timing Brief | `references/fx-timing-brief.md` | When needed |
| Volume Domain Rules | `references/volume-domain-rules.md` | When needed |
| Game Fx Export | `references/game-fx-export.md` | When needed |
