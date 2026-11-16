---
name: ref-physics-sim
description: Référence externe à lire seulement (pack MIT arjun988/blender-skills), pour les agents de production. Rigid body, soft body, and destruction setups in Blender including constraints, cell fracture debris, and baked caches.
license: MIT
metadata:
  author: https://github.com/arjun988
  version: "1.0.0"
  domain: blender
  role: specialist
  triggers: physics, rigid body, soft body, destruction, fracture, debris, constraint, simulation bake, collapse
  related-skills: vfx-fx, cloth-sim, animation, export-pipeline, collision-proxy
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


# Physics Sim

Stable rigid/soft body setups. Motivated destruction. Baked caches.

## When to Use

- Rigid body interactions and collapses
- Soft body jiggle / rubber / simple soft props
- Destruction and debris (cell fracture / pre-cut shards)
- Pre-vis physics before VFX polish

## Workflow

```
Simplify collision meshes → Assign rigid/soft bodies
  → Constraints → Passive settings → Bake → Art-direct → Export cache
```

## Rigid Body Quick Rules

| Role | Settings notes |
|------|----------------|
| Active | Moving debris / props |
| Passive | Floors, walls, heavy anchors |
| Convex hull | Fast, approximate |
| Mesh | Accurate, heavier |

- Apply scale before sim
- Use margin appropriate to scale
- Collection: `COL_Physics_[Shot]`

## Constraints

- Hinge / fixed / motor for mechanical links
- Breakable constraints for destruction beats
- Name: `RBCON_[Object]_[Type]`

## Destruction Approach

```
1. Pre-cut shards (cell fracture or manual)
2. Island meshes as active rigid bodies
3. Passive shell until trigger frame
4. Animate trigger (force / keyframed activation)
5. Bake → cleanup interpenetrations
```

## Soft Body

- Prefer for simple soft props; use `cloth-sim` for garments
- Goal weights to retain shape
- Soft + collision object required

## Bake / Export

- Bake to cache before render
- Alembic/USD for cinematic debris
- For games: bake key poses or flipbook; rarely live Blender physics

## Constraints

### MUST DO
- Apply scale; use simplified colliders
- Bake before final delivery
- Trigger destruction intentionally (frame)

### MUST NOT DO
- High-res sculpt meshes as active colliders
- Unbounded shard counts
- Leave sims unbaked for final renders

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|----------|
| Rigid Body Presets | `references/rigid-body-presets.md` | When needed |
| Destruction Pipeline | `references/destruction-pipeline.md` | When needed |
| Sim Bake Checklist | `references/sim-bake-checklist.md` | When needed |
