# Direction artistique : du récit au pack de DA

## Principe

La direction artistique d'une série est un **fichier**, pas une suite de retouches : `blender/packs_da/<nom>.json`, conforme à `schemas/pack_da.schema.json`. Le module Look l'applique à chaque plan. Résultat : le style est cohérent d'un épisode à l'autre, reproductible, et ne coûte aucun crédit une fois écrit.

## Qui fait quoi

| Étape | Qui | Coût |
|---|---|---|
| Lire l'histoire, proposer 3 directions (palette, lumière, matière, références, risques) | `production-directeur-artistique` | 1 appel sonnet |
| Choisir une direction | **un humain** (décision de fond) | — |
| Écrire le pack, le valider | `production-directeur-artistique` + `python -m scripts.production.pack_da` | 1 appel + 0 crédit |
| HDRI si besoin | `production-bibliothecaire` (`sources_assets hdri`) | haiku, rare |
| Planche d'ambiance Figma (optionnelle) | session principale avec le connecteur Figma | sur demande |
| Juger l'animatique avec le nouveau pack | `production-controle-qualite` | 1 image |

## Pourquoi Blender fait foi et Figma reste optionnel

- Blender ne lit pas Figma : une maquette Figma devrait être retraduite à la main en réglages, avec des écarts (une couleur sRVB dans Figma n'est pas la même chose que la même couleur sous la lumière d'une scène 3D).
- Le pack JSON est versionné dans Git, validé automatiquement et appliqué identiquement partout.
- Figma est utile **avant** le choix, pour comparer les 3 directions côte à côte (palette, typographie, vignettes 9:16), et pour la communication (miniatures, posts). Son lien se range dans `planche_figma` du pack.

## Contrôles automatiques d'un pack

`python -m scripts.production.pack_da <pack.json>` vérifie :
1. la structure (champs, bornes des valeurs, couleurs RVB entre 0 et 1, couleurs ASS des textes) ;
2. que le nom du pack est celui du fichier ;
3. que les couleurs qui doivent se distinguer à l'image le font : personnage/sol, accent/sol, bâti/sol, toit/bâti, personnage/ciel. La mesure est une distance perceptuelle dans l'espace Oklab (seuil 0,10), qui tient compte de la teinte et pas seulement de la luminosité.

La fiche épisode refuse un pack invalide (code 2, `suite: production-directeur-artistique`).

## Couleurs : sRVB et linéaire

Les couleurs d'un pack sont en RVB **linéaire** (convention Blender). Un hex choisi dans Figma ou sur un site de palettes est en sRVB : il faut le convertir (commande dans l'agent directeur artistique), sinon tout paraît délavé.

## Versions

Un pack utilisé par un épisode publié ne se modifie plus : on crée `<nom>_v2`. Les anciens épisodes restent ainsi reproductibles à l'identique.
