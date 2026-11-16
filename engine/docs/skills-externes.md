# Skills externes (références Blender)

Statut : installées le 2026-11-16, **fait mais non testé en conditions réelles** (aucun épisode produit avec elles pour l'instant).

## Origine et licence

Onze skills du pack [arjun988/blender-skills](https://github.com/arjun988/blender-skills) (licence MIT, texte dans `.claude/skills/LICENSE-blender-skills.txt`) sont copiées dans `.claude/skills/` avec le préfixe `ref-`. Ce sont des fichiers Markdown uniquement : aucun script, aucun accès réseau.

Ne sont **pas** installés, parce qu'ils contredisent l'organisation du dépôt : le `CLAUDE.md` du pack (il impose ses propres conventions et l'exécution via le MCP), `blender-director` et `blender-modeler` (modélisation à la main via le MCP), ni les dossiers `references/` partagés.

## Règle de priorité

Chaque `SKILL.md` commence par un encadré « Cadre d'utilisation dans ce dépôt ». En cas de contradiction, font foi, dans l'ordre : `CLAUDE.md`, `contracts/`, les agents `prod-*` et `story-*`, `engine/docs/` (dont `conventions-blender.md`), puis les décisions notées dans le Drive. Concrètement :

1. La production passe par `engine/` et la fiche épisode, jamais par des modifications manuelles d'une scène via le MCP Blender.
2. Les préfixes `COL_*`, `LGT_*`, `FX_*` du pack sont remplacés par les conventions du dépôt.
3. Export vers moteur de jeu, LOD, collisions : hors sujet pour la série.
4. Un verdict « ship » d'une skill ne remplace jamais la validation humaine (plaquette Figma, animatique, publication).

Si une technique décrite dans une skill est utile mais absente du moteur, on ouvre une brique `maintenance` (voir `maintenance.md`) au lieu de la bricoler dans une scène.

## Qui lit quoi

| Skill | Agent | Usage |
|---|---|---|
| `ref-camera-cinematography` | prod-realisateur | grammaire des plans, focales, mouvements |
| `ref-lighting`, `ref-lookdev` | prod-directeur-artistique | lumière, matériaux, rendu des packs de DA |
| `ref-set-dressing`, `ref-scene-assembly` | prod-directeur-artistique | détails de décor, composition |
| `ref-lowpoly-style`, `ref-stylized-style`, `ref-cozy-wholesome-mood` | prod-directeur-artistique | directions artistiques |
| `ref-vfx-fx`, `ref-physics-sim` | prod-directeur-artistique, maintenance | pistes pour les futurs effets (poussière, débris, éclaboussures) |
| `ref-qa-review` | prod-controle-qualite | grille complémentaire, sans changer le budget d'images ni le format du verdict |

## Mise à jour

Pour reprendre une nouvelle version du pack : recopier le dossier de la skill, remettre l'encadré et le préfixe `ref-` (le script de l'installation initiale est décrit dans la PR correspondante), relancer les tests.
