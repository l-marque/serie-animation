# Trouver et intégrer des modèles 3D (procédure du bibliothécaire)

## Ordre de préférence

1. **Primitive du kit** (`primitif:…`) : gratuite, instantanée, toujours cohérente avec le pack de DA.
2. **Asset déjà au registre** (`blender/assets/registre.json`).
3. **Nouvelle source libre**, dans cet ordre : Poly Pizza (low-poly, CC0/CC-BY, API), Kenney et Quaternius (packs CC0), Poly Haven (CC0, API), Sketchfab (CC0 ou CC-BY uniquement, API).
4. **Achat** (TurboSquid, CGTrader…) : décision humaine uniquement.

## Licences

| Licence | Utilisable | Obligation |
|---|---|---|
| CC0 | oui | aucune |
| CC-BY | oui | créditer l'auteur (texte dans `licences.csv`, repris dans la légende) |
| CC-BY-SA | à éviter | le partage à l'identique peut contaminer nos propres créations |
| NC (non commercial), ND (pas de modification) | **non** | — |
| « Editorial » (TurboSquid) | **non** | interdit en publicité |
| Hunyuan3D (modèles générés) | **non** | licence excluant l'Union européenne |

## Intégration

1. Fichier dans `blender/assets/modeles/<id>.glb` (glTF/GLB de préférence).
2. Entrée dans `blender/assets/registre.json` (fichier, échelle, rôles des pièces, pièce principale, source, date).
3. Ligne dans `blender/assets/licences.csv` (`id,source,auteur,licence,url,date_ajout,attribution_requise,texte_attribution`).
4. Vérification : `python -m scripts.production.run <fiche> --valider-seulement`.

Les matériaux d'origine sont **remplacés** par ceux du pack de DA selon le rôle de chaque pièce : c'est ce qui rend cohérents des modèles venus de sources différentes. Inutile de chercher des modèles texturés.

## Secrets

Les clés d'API (`POLY_PIZZA_KEY`, `SKETCHFAB_TOKEN`) vont dans un fichier `.env` local, ignoré par Git. Jamais dans le dépôt, le Drive, une issue ou une fiche.
