# Vocabulaire d'actions et mouvements de caméra (v1.1)

> Statut : **proposition de Guillaume**, à valider par Lucas et Guillaume (règle des contrats, `contracts/README.md`). Implémenté et testé dans `engine/`, sauf ce qui est marqué « prévu ».
>
> v1.1 (2026-11-16, décidée par Lucas) : mouvement de caméra `descente` et section « Textes 3D et cartes de choix ». Ces ajouts exigent `"version": "1.1"` dans la fiche.

La production ne connaît pas les histoires : elle connaît ce vocabulaire. Toute fiche épisode s'écrit avec ces mots. Un besoin qui n'y figure pas = une nouvelle brique à ajouter au pipeline (`engine/docs/maintenance.md`), puis une nouvelle version de ce contrat.

## Déclencher une action

Chaque action d'un beat a une `cible` (id d'un élément, d'un personnage ou d'un module) et se déclenche :
- **sur un mot de la voix off** : `"mot": "lumière"` (recommandé : l'action reste synchronisée quand la durée de la voix change) ;
- **ou à un instant** : `"debut": 1.2` (secondes depuis le début du beat).

`duree_s` (défaut 0,6 s) fixe la durée du mouvement. Une action peut déborder sur le beat suivant.

## Actions

| Action | Effet | Cible | `params` |
|---|---|---|---|
| `apparaitre` | Surgit avec un léger rebond (« pop »). Sur un module : vague d'apparitions du centre vers l'extérieur. L'objet est invisible avant. | objet ou module | — |
| `disparaitre` | Se réduit jusqu'à disparaître. | objet ou module | — |
| `deplacer` | Se déplace avec départ et arrivée en douceur. | objet | `vers: [x, y, z]` **ou** `vers_cible: "<id>"` |
| `tourner` | Tourne sur lui-même autour de l'axe vertical. | objet | `degres` (défaut 360) |
| `grandir` | Change de taille avec rebond. | objet ou module | `facteur` (défaut 1,5 ; < 1 pour rétrécir) |
| `transformer` | Se réduit pendant qu'un autre asset apparaît au même endroit (tente → maison). | objet | `vers_asset: "primitif:…"`, `role` (facultatif) |
| `cycle` | Mouvement répété, additionné aux déplacements. | objet | `nom` : `flotter`, `sautiller`, `tourner_sur_soi`, `osciller` ; `amplitude` (défaut 1) |

Visibilité : un objet ou module déclaré avec `"visible_au_debut": false` reste invisible tant qu'une action `apparaitre` ne le fait pas surgir.

## Mouvements de caméra (`plan.camera`)

| Mouvement | Effet | Usage conseillé |
|---|---|---|
| `plan_fixe` | Immobile | pause, chute, réplique |
| `survol` | Glisse en arc autour de la cible | présenter un lieu |
| `revelation` | Part bas et près, recule et s'élève | dévoiler un élément important |
| `dolly_avant` | Avance vers la cible | tension, rapprochement |
| `orbite` | Tourne d'un tiers de tour autour de la cible | mettre en valeur, transformation |
| `plongee` | Vue presque verticale qui descend | vue d'ensemble, effet carte |
| `travelling_lateral` | Translation latérale face à la cible | suivre un déplacement |
| `descente` (v1.1) | Part haut au-dessus de la cible et descend en continu jusqu'à elle (zoom continu du ciel jusqu'au personnage) | ouverture, situer un personnage dans son monde. Implémenté dans `engine/blender/camera.py` : départ à au moins 40 m (ou 8 × distance), arrivée à `distance` et `hauteur` du plan, sans coupe ; prévoir un beat d'au moins 2,5 s |

Paramètres facultatifs : `cible` (id visé ; sinon le centre du décor), `distance` (défaut 20 m), `hauteur` (défaut 10 m), `focale` (défaut 35 mm). La caméra vise un point situé 1,2 m au-dessus de la cible.

## Textes 3D et cartes de choix (v1.1)

Un texte posé dans le décor (nom de lieu sur un panneau, légende d'une carte de choix) s'écrit dans le champ facultatif `habillage.textes_3d` de la fiche, avec `"version": "1.1"`. Format, contraintes et rôles : voir [`fiche-episode.schema.json`](fiche-episode.schema.json) (`properties.habillage`), repris tel quel de `engine/schemas/habillage.schema.json`.

En bref : `id`, `texte` (1 à 40 caractères), `parent` (élément ou personnage que le texte suit, apparitions comprises), `position` dans le repère du parent, `rotation_z`, `taille`, `epaisseur`, `role`, `visible_au_debut`. Une carte de choix = un élément (primitive `carte_choix`) + un texte 3D qui l'a pour parent.

Tant que le moteur n'accepte pas la v1.1 (`engine/pipeline/contrat.py`), la production continue de lire l'habillage dans `<fiche>.habillage.json`.

## Modules procéduraux

| Module | Effet | Paramètres |
|---|---|---|
| `disperser` | Répète un asset (village, foule, forêt, armée) | `nombre`, `motif` (`spirale`, `grille`, `cercle`, `aleatoire`), `centre`, `espacement` (pour `aleatoire` : rayon de la zone), `rayon_interieur` (`aleatoire` : centre laissé libre), `variation_echelle`, `seed` |

Même `seed` = même disposition, à chaque rendu et d'un épisode à l'autre.

## Primitives du kit « primitifs »

`maison`, `tour`, `arbre`, `rocher`, `personnage`, `caisse`, `lampadaire`. Chaque pièce porte un rôle (`sol`, `batiment`, `toit`, `vegetation`, `roche`, `personnage`, `accessoire`, `accent`) ; le pack de DA décide de sa couleur.
