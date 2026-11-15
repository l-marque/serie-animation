# engine/ : le moteur de production (propriétaire : Guillaume)

Transforme une fiche épisode (`contracts/fiche-episode.schema.json`) en vidéo verticale 9:16, sans appel à Claude. Les agents `prod-*` (`.claude/agents/`) le pilotent.

| Dossier | Contenu |
|---|---|
| `pipeline/` | chef d'orchestre déterministe (`run.py`) et modules hors Blender : contrat, continuité, bibliothèque, sources d'assets par API, timeline, cache, montage, contrôles |
| `voix/` | synthèse vocale Kyutai, exécutée dans l'environnement Python qui a PyTorch (`docs/voix-et-son.md`) |
| `blender/` | modules exécutés dans Blender : décorateur, look, animateur, caméra, rendu, kits de décor |
| `packs_da/` | packs de direction artistique (JSON) |
| `schemas/` | schémas internes au moteur (`pack-da.schema.json`) ; les contrats entre pôles sont dans `contracts/` |
| `assets/` | registre des modèles 3D, `licences.csv`, modèles et HDRI téléchargés |
| `docs/` | démarrage, architecture, contrat détaillé, sourcing, direction artistique, maintenance, conventions Blender |

Démarrage : [`docs/README.md`](docs/README.md). Tests : `python -m pytest tests/engine -q` depuis la racine du dépôt.

```bash
pip install -r engine/requirements.txt
python -m engine.pipeline.run episodes/exemples/demo_001.json --valider-seulement
python -m engine.pipeline.run episodes/exemples/demo_001.json            # animatique
```
