# Conventions Blender

Proposées par le Claude de Guillaume pour le pipeline de production (2026-11-15). À valider par Guillaume.

## Version

- **Blender 5.3** (version installée chez Guillaume). Le pipeline utilise des API compatibles 4.4+ (actions « en couches ») via `commun.cle()` / `commun.fcurves()`.
- Connecteur officiel Blender Lab (MCP) pour le débogage et la vérification visuelle ; la production passe par les scripts.

## Unités et repères

- 1 unité = 1 mètre. Z vers le haut. Les assets sont posés au sol (z = 0) et centrés en (0, 0).
- Format vertical 9:16 (1080 × 1920) par défaut, 30 images/s.

## Nommage des objets créés par le pipeline

| Préfixe | Objet |
|---|---|
| `PROTO_<asset>_<role>` | collection prototype (instanciée, jamais liée à la scène) |
| `EP_<id>` | élément ou personnage de la fiche (empty qui instancie un prototype) |
| `MOD_<id>` / `MOD_<id>_<0000>` | racine d'un module procédural / ses instances |
| `CAM_<beat>` / `VISEE_<beat>` | caméra d'un beat / point visé |
| `MAT_<role>` / `MAT_contour` | matériau d'un rôle du pack de DA / contour cartoon |
| `SOL`, `SOLEIL`, `MONDE` | sol, lumière principale, monde |

Collections de scène : `DECOR`, `PERSONNAGES`, `MODULES`, `CAMERAS`.

## Rôles visuels

`sol`, `batiment`, `toit`, `vegetation`, `roche`, `personnage`, `accessoire`, `accent`. Un asset ne porte jamais de couleur « en dur » : il porte des rôles, le pack de DA choisit les couleurs.

## Fichiers

- Les scènes générées (`renders/<id>/<mode>/scene.blend`) sont jetables : elles sont reconstruites à chaque rendu. On ne les retouche que pour inspecter.
- Un `.blend` édité à la main : une seule personne à la fois (voir CONTRIBUTING.md), Git LFS à mettre en place avant le premier.
- Modèles importés : `engine/assets/modeles/`, toujours déclarés au registre avec leur licence.
