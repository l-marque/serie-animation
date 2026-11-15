# Vocabulaire d'actions et mouvements de caméra (v1.0)

La production ne connaît pas les histoires : elle connaît ce vocabulaire. Toute fiche épisode s'écrit avec ces mots. Un besoin qui n'y figure pas = une nouvelle brique à demander à `production-technicien`.

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

Paramètres facultatifs : `cible` (id visé ; sinon le centre du décor), `distance` (défaut 20 m), `hauteur` (défaut 10 m), `focale` (défaut 35 mm). La caméra vise un point situé 1,2 m au-dessus de la cible.

## Modules procéduraux

| Module | Effet | Paramètres |
|---|---|---|
| `disperser` | Répète un asset (village, foule, forêt, armée) | `nombre`, `motif` (`spirale`, `grille`, `cercle`, `aleatoire`), `centre`, `espacement` (pour `aleatoire` : rayon de la zone), `rayon_interieur` (`aleatoire` : centre laissé libre), `variation_echelle`, `seed` |

Même `seed` = même disposition, à chaque rendu et d'un épisode à l'autre.

## Primitives du kit « primitifs »

`maison`, `tour`, `arbre`, `rocher`, `personnage`, `caisse`, `lampadaire`. Chaque pièce porte un rôle (`sol`, `batiment`, `toit`, `vegetation`, `roche`, `personnage`, `accessoire`, `accent`) ; le pack de DA décide de sa couleur.
