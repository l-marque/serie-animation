# Le canard qui se multiplie — découpage technique

- Statut : essai, non validé par Lucas (essai demandé par Lucas le 2026-11-16) ; faisabilité à confirmer par Guillaume
- Beats source : `docs/storytelling/beats/2026-11-16-le-canard-qui-se-multiplie.md` (statut : essai, non validé par Lucas)
- Scénario source : note Drive `01_Claude_Lucas/2026-11-15_claude-lucas_pilote-canard-scenario-v3` (statut : validé par Lucas le 2026-11-15, faisabilité à confirmer par Guillaume ; lu dans une recopie locale hors dépôt)
- Durée : 40,0 s · Plans : 14 · Mouvements utilisés : plan_fixe × 4, plongee × 2, dolly_avant × 2, revelation × 2, orbite × 2, survol × 1, travelling_lateral × 1

Défauts du pilote traités ici (`engine/docs/pilotes/2026-11-15-canard.md`) : 19 `plan_fixe` → 4, jamais plus de 2 d'affilée ; chute trop loin → chute à 4,5 m sur le canard restant ; baignoire petite en bas de l'image → **repères de visée** (voir plus bas) qui placent le sujet au centre ; débordement sans eau → eau qui monte puis deux flaques qui grandissent ; canards qui traversent le bord → toutes les positions vérifiées avec les dimensions des primitives.

**Lecture importante pour `prod-realisateur`** :

1. **Durées imposées** : chaque beat reçoit `duree_s` égale à la durée du fichier de beats (3,0 ; 2,4 ; 2,4 ; 2,2 ; 2,8 ; 3,0 ; 3,0 ; 3,2 ; 3,0 ; 3,0 ; 3,0 ; 3,0 ; 3,0 ; 3,0). Sans cela le moteur calcule la durée depuis la voix (+ 0,45 s) et tout le calendrier des pops dérive.
2. **La caméra vise 1,2 m au-dessus de sa cible** (`HAUTEUR_VISEE` dans `engine/blender/camera.py`) et se place toujours côté −y pour `plan_fixe`, `revelation`, `dolly_avant`, `plongee` et `travelling_lateral`. Pour un sujet bas (canard à z ≈ 0,6 à 0,9 m), viser la baignoire met le sujet en bas de l'image : c'est le défaut du pilote. Je compense avec trois **repères de visée** : des éléments invisibles (jamais apparus, donc à l'échelle 0) placés 1,2 m sous le point à viser. La caméra vise alors exactement le sujet. Les hauteurs `hauteur` ci-dessous s'ajoutent à ce point visé : altitude de la caméra = point visé + hauteur.
3. **`dolly_avant` s'arrête à 0,8 × distance** (`camera.py` : départ 1,3 × distance, arrivée 0,8 × distance), contrairement à ce que dit la consigne « distance = distance d'arrivée ». Les valeurs ci-dessous donnent le paramètre `distance` **et** la distance d'arrivée réelle.
4. **Mots répétés** : le moteur déclenche une action sur le **premier** mot qui commence par le mot déclencheur (`_instant_mot`). Le second « double » (b06) et « de » (b08, qui attraperait « Des ») sont donc déclenchés par `debut`, pas par `mot`.

## Décor

Repère : x vers la droite de l'image d'ouverture, y vers le fond, z vers le haut, en mètres ; origine au centre du décor principal (centre de la baignoire, au sol).

- Sol : oui, taille 120 m (la foule finale atteint un rayon de 32,9 m ; le plan p09 voit l'horizon, le bord du sol doit rester loin) · Pack de DA proposé : `pilote_canard` (existe déjà dans `engine/packs_da/`)

Dimensions utilisées (docstrings de `engine/blender/kits/primitifs.py` et géométrie de la cuve) : baignoire 2,4 × 1,2 m, rebord à z ≈ 0,77, paroi de 0,09 m (ouverture intérieure en haut ≈ 2,22 × 1,02 m), fond intérieur à z ≈ 0,22, parois inclinées (ouverture intérieure à z = 0,60 ≈ 2,15 × 0,97 m) ; demi-diagonale extérieure 1,34 m ; eau 2,2 × 1,0 m ; flaque ≈ 1 m ; donut ≈ 0,5 m ; ballon ≈ 0,5 m, enveloppe centrée à 0,95 m au-dessus du pied de la ficelle. **Canard : j'ai supposé une emprise ≤ 0,45 m de diamètre et un dos à ≈ 0,27 m au-dessus de sa base** (dimensions de la primitive `canard`) ; la taille réelle du modèle Poly Haven à l'échelle 1,3 du registre n'est pas écrite dans le registre (à confirmer par Guillaume). Un canard plus petit ne crée aucune collision, il laisse seulement plus d'espace entre les canards ; seule la hauteur de la pile (z = 0,88) dépend de la hauteur du dos.

### Éléments

| id | Asset | Position x / y / z (m) | Rotation z (°) | Échelle | Rôle | Visible au début | Note (appui, contact) |
|---|---|---|---|---|---|---|---|
| baignoire | à sourcer : « bathtub » / « freestanding bathtub » / « clawfoot bathtub » / « bath tub » ; id proposé `bibliotheque:baignoire` ; **repli `primitif:baignoire`** | 0 / 0 / 0 | 0 | 1 | batiment | oui | posée au sol sur ses 4 pieds, rebord à z ≈ 0,77. Un modèle sourcé doit être mis aux dimensions de la primitive (2,4 × 1,2 m, rebord 0,77, ouverture ≈ 2,2 × 1,0 m) : toutes les positions en dépendent |
| eau | primitif:eau | 0 / 0 / 0,60 | 0 | 1 | (celui de la pièce) | oui | plan d'eau dans la cuve, 0,17 m sous le rebord ; dépasse de 1 à 4 cm dans les parois (caché dans leur épaisseur de 9 cm). Monte à 0,74 en b05, redescend à 0,60 en b11 |
| canard_0 | bibliotheque:canard_caoutchouc (intégré, registre) | −0,25 / −0,25 / 0,60 | −45 | 1 | personnage | oui | le héros, posé sur l'eau, premier rang à gauche ; regard de trois quarts vers la caméra (si le modèle regarde vers +x comme la primitive). Survit à la chute. Emprise jusqu'à x −0,45 et y −0,45 : dans l'ouverture (±1,07 × ±0,48 à z 0,60) |
| canard_envers | bibliotheque:canard_caoutchouc | 0,75 / −0,25 / 0,88 | 180 | 1 | personnage | non | le canard « à l'envers », posé sur le dos du canard de `pop08` situé en (0,75 ; −0,25 ; 0,60), à une place que la pile `pop16` laisse libre. Même échelle que les autres (pas de triche par la taille). Apparaît avec `pop128` (il compte dans les 128) |
| flaque_a | primitif:flaque | 0,3 / −1,15 / 0 | 0 | 1 | (celui de la pièce) | non | au sol devant la baignoire (y de −1,7 à −0,6 environ) ; après `grandir` × 2,2 (rayon ≈ 1,2 m), elle passe sous la cuve, qui repose sur des pieds : crédible |
| flaque_b | primitif:flaque | −1,75 / −0,6 / 0 | 0 | 1 | (celui de la pièce) | non | au sol à l'avant gauche (x de −2,3 à −1,2) ; grandit × 2,5 en b09 |
| donut | à sourcer : « donut » / « glazed doughnut » / « doughnut food » / « donut lowpoly » ; id proposé `bibliotheque:donut` ; **repli `primitif:donut`** | −0,95 / −0,555 / 0,77 | 0 | 0,6 | accessoire | non | posé à plat sur le rebord avant (milieu du rebord y = −0,555), diamètre ≈ 0,32 m : déborde de chaque côté du rebord de 9 cm mais son centre est au-dessus du rebord |
| ballon | à sourcer : « balloon » / « party balloon » / « helium balloon string » / « toy balloon » ; id proposé `bibliotheque:ballon` ; **repli `primitif:ballon`** | −0,05 / −0,555 / 0,77 | 0 | 0,8 | accent | non | pied de la ficelle sur le rebord avant, enveloppe vers z ≈ 1,53 (sommet ≈ 1,76) : un ballon gonflé à l'hélium tenu par sa ficelle, rien ne flotte sans raison. Écart donut-ballon 0,9 m, milieu x = −0,5 (sous le repère `visee_duo`) |
| visee_duo | primitif:caisse | −0,5 / −0,25 / −0,45 | 0 | 1 | accessoire | non | **repère de visée, jamais visible** (aucune action `apparaitre`). Point visé : (−0,5 ; −0,25 ; 0,75), milieu du premier rang gauche (canard_0 et son double) |
| visee_heros | primitif:caisse | −0,25 / −0,25 / −0,45 | 0 | 1 | accessoire | non | repère de visée, jamais visible. Point visé : canard_0 (z 0,75) |
| visee_baignoire | primitif:caisse | 0 / 0 / −0,6 | 0 | 1 | accessoire | non | repère de visée, jamais visible. Point visé : centre de la baignoire à z 0,60 (niveau de l'eau) |

### Foules (module `disperser`)

Tous les canards : `bibliotheque:canard_caoutchouc`, rôle personnage, variation d'échelle 0,9 – 1,1, invisibles au début. Chaque module est l'**ajout** d'un pop : la somme suit le compteur. 1 (canard_0) + 1 + 2 + 4 + 8 + 16 + 32 + 63 (+ canard_envers) + 128 + 256 + 512 + 1 024 + 2 048 = **4 096**.

Dans la baignoire, les modules forment une grille 4 × 2 dont la géométrie **double** à chaque pop : un canard → une paire (rang avant gauche) → un carré 2 × 2 (moitié gauche) → deux carrés (toute l'eau). Places : x ∈ {−0,75 ; −0,25 ; 0,25 ; 0,75}, y ∈ {−0,25 ; 0,25}, z 0,60 ; emprise extrême x ±0,95, y ±0,45, dans l'ouverture (±1,07 × ±0,48). Au sol, des anneaux `aleatoire` concentriques dont le rayon intérieur dépasse le bord de la baignoire (1,34 m + 0,2 m de demi-canard → 1,6 m) ; la surface de chaque anneau vaut 0,83 m² par canard, la densité maximale que permet la distance minimale du moteur entre deux instances (0,5 m, `decorateur.py`).

| id | Asset | Nombre | Motif | Centre x / y / z | Espacement | Rayon intérieur | Variation d'échelle | Seed | Visible au début | Ce qu'elle représente |
|---|---|---|---|---|---|---|---|---|---|---|
| pop02 | bibliotheque:canard_caoutchouc | 1 | grille | −0,75 / −0,25 / 0,60 | 0,5 | 0 | 0,9 – 1,1 | 202 | non | le double du héros, à sa gauche (compteur 2) |
| pop04 | bibliotheque:canard_caoutchouc | 2 | grille | −0,5 / 0,5 / 0,60 | 0,5 | 0 | 0,9 – 1,1 | 204 | non | rang arrière gauche, places (−0,75 ; 0,25) et (−0,25 ; 0,25) (compteur 4) |
| pop08 | bibliotheque:canard_caoutchouc | 4 | grille | 0,5 / 0 / 0,60 | 0,5 | 0 | 0,9 – 1,1 | 208 | non | moitié droite de l'eau, x 0,25 et 0,75, y ±0,25 (compteur 8 : l'eau est couverte) |
| pop16 | bibliotheque:canard_caoutchouc | 8 | grille | 0 / 0 / 0,88 | 0,36 | 0 | 0,9 – 1,1 | 216 | non | deuxième couche **posée sur le dos** de la première (grille 3 × 3 moins un coin, x et y ∈ {−0,36 ; 0 ; 0,36}) ; emprise y ±0,56, sous le bord extérieur (±0,6) (compteur 16 : ils s'empilent) |
| pop32 | bibliotheque:canard_caoutchouc | 16 | aleatoire | 0 / 0 / 0 | 2,6 | 1,6 | 0,9 – 1,1 | 232 | non | premiers canards tombés au sol, autour de la baignoire (compteur 32 : ça déborde) |
| pop64 | bibliotheque:canard_caoutchouc | 32 | aleatoire | 0 / 0 / 0 | 3,9 | 2,6 | 0,9 – 1,1 | 264 | non | anneau au sol 2,6 – 3,9 m |
| pop128 | bibliotheque:canard_caoutchouc | 63 | aleatoire | 0 / 0 / 0 | 5,7 | 3,9 | 0,9 – 1,1 | 328 | non | anneau 3,9 – 5,7 m ; avec `canard_envers` : 64 canards ajoutés |
| pop256 | bibliotheque:canard_caoutchouc | 128 | aleatoire | 0 / 0 / 0 | 8,1 | 5,7 | 0,9 – 1,1 | 456 | non | anneau 5,7 – 8,1 m (« des centaines ») |
| pop512 | bibliotheque:canard_caoutchouc | 256 | aleatoire | 0 / 0 / 0 | 11,5 | 8,1 | 0,9 – 1,1 | 712 | non | anneau 8,1 – 11,5 m |
| pop1024 | bibliotheque:canard_caoutchouc | 512 | aleatoire | 0 / 0 / 0 | 16,4 | 11,5 | 0,9 – 1,1 | 1224 | non | anneau 11,5 – 16,4 m (« des milliers ») |
| pop2048 | bibliotheque:canard_caoutchouc | 1 024 | aleatoire | 0 / 0 / 0 | 23,2 | 16,4 | 0,9 – 1,1 | 2248 | non | anneau 16,4 – 23,2 m |
| pop4096 | bibliotheque:canard_caoutchouc | 2 048 | aleatoire | 0 / 0 / 0 | 32,9 | 23,2 | 0,9 – 1,1 | 4296 | non | anneau 23,2 – 32,9 m : la mer de canards |

Contrôle des anneaux (surface / nombre, distance minimale `max(√(S/n) × 0,55 ; 0,5)`) : pop32 13,2 m² / 16 ; pop64 26,5 / 32 ; pop128 54,3 / 63 ; pop256 104,0 / 128 ; pop512 209,4 / 256 ; pop1024 429,5 / 512 ; pop2048 846 / 1 024 ; pop4096 1 710 / 2 048 → 0,82 à 0,86 m² par canard, distance minimale 0,50 m partout, capacité de placement ≈ 2,3 fois le nombre demandé : tous les canards se placent.

## Plans

Instants des mots : pause avant + (rang du mot − 1) / 2,5 s, comme dans le fichier de beats. Durées des pops : 0,4 s pendant la mise en place, 0,3 s pendant l'escalade.

### p01 → beat b01 (0,0 → 3,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Un canard, deux canards, tu restes calme. » |
| Caméra | plan_fixe · cible visee_duo · distance 2,6 m · hauteur 0,8 m · focale 35 mm (caméra en (−0,5 ; −2,85 ; 1,55)) |
| Angle et cadrage | face, légère plongée (17°) ; canard_0 sur le tiers droit, la place de son double libre sur le tiers gauche ; les canards au centre vertical de l'image, le rebord avant cache seulement leur base ; demi-largeur visible ≈ 0,29 × 2,72 = 0,79 m (sujets à ±0,45 m du centre) |
| Transition vers le plan suivant | coupe |
| Actions | 1. cycle canard_0, `debut` 0,0, durée 2,0 s, params nom flotter, amplitude 0,5 → fin à 2,0 s (marge 1,0 s). 2. apparaitre pop02 sur « deux » (≈ 1,0 s), durée 0,4 s → fin à 1,4 s (marge 1,6 s) |
| Texte à l'écran | rien |
| Compteur | 1, puis 2 à 1,0 s ; en haut à gauche, dans la zone sûre (≈ 8 à 30 % de la largeur, 7 à 12 % de la hauteur) |
| Effets sonores | pop sur « deux » (automatique) ; clapotis léger à 0,0 s (proposé, pas de son disponible) |
| Musique | légère, basse sous la voix (≈ −18 dB) dès 0,0 s ; même niveau qu'à 40,0 s pour la boucle |
| Lisible sans le son | oui — le canard bouge dès l'image 1, son double surgit à 1 s, le compteur passe de 1 à 2 |

### p02 → beat b02 (3,0 → 5,4 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « À chaque pop, ils doublent. » |
| Caméra | survol · cible visee_duo · distance 3,5 m · hauteur 1,4 m · focale 35 mm (arc de −110° à −70°, caméra vers z 2,15) |
| Angle et cadrage | trois quarts gauche → trois quarts droit en glissant ; plus haut que p01 pour voir le rang arrière par-dessus le rang avant ; sujet au centre ; demi-largeur visible ≈ 0,29 × 3,77 = 1,09 m (les 4 canards à ±0,45 m) |
| Transition vers le plan suivant | coupe |
| Actions | apparaitre pop04 sur « pop » (≈ 1,0 s), durée 0,4 s → fin à 1,4 s (marge 1,0 s) |
| Texte à l'écran | rien |
| Compteur | 2, puis 4 à 1,0 s ; en haut à gauche |
| Effets sonores | pop sur « pop » |
| Musique | même niveau, sous la voix |
| Lisible sans le son | oui — la paire devient un carré de quatre ; le compteur 4 |

### p03 → beat b03 (5,4 → 7,8 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Donc quatre, et puis huit, logique. » |
| Caméra | plongee · cible visee_baignoire · distance 4 m · hauteur 4 m · focale 35 mm (de (0 ; −1,0 ; 7,4) à (0 ; −0,6 ; 5,4) : distance réelle 7,0 → 4,84 m) |
| Angle et cadrage | vue presque verticale, « on compte » ; baignoire au centre, sur toute la largeur ; demi-largeur visible à l'arrivée ≈ 0,29 × 4,84 = 1,40 m (baignoire ±1,2 m) |
| Transition vers le plan suivant | coupe |
| Actions | apparaitre pop08 sur « huit » (≈ 1,6 s), durée 0,3 s → fin à 1,9 s (**marge 0,5 s : ÉCART**, l'instant du pop est fixé par le calendrier du compteur ; le résultat reste visible dans p04) |
| Texte à l'écran | rien |
| Compteur | 4, puis 8 à 1,6 s ; en haut à gauche |
| Effets sonores | pop sur « huit » |
| Musique | même niveau |
| Lisible sans le son | oui — vue du dessus : 4 canards sur la moitié gauche, puis la moitié droite se remplit ; le compteur 8 |

### p04 → beat b04 (7,8 → 10,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Facile, tu sais compter, non ? » |
| Caméra | dolly_avant · cible visee_heros · distance 2,5 m · hauteur 0,6 m · focale 35 mm (départ 3,25 m / 0,69 m, **arrivée réelle 2,0 m / 0,51 m**) |
| Angle et cadrage | face, caméra basse (altitude 1,26 à 1,44 m) pour donner de la présence au héros ; canard_0 au centre ; demi-largeur visible à l'arrivée ≈ 0,29 × 2,06 = 0,60 m (ses voisins à 0,5 m entrent à moitié dans le cadre) |
| Transition vers le plan suivant | coupe |
| Actions | cycle canard_0 sur « Facile » (≈ 0,0 s), durée 1,2 s, params nom flotter, amplitude 0,5 → fin à 1,2 s (marge 1,0 s) |
| Texte à l'écran | rien |
| Compteur | 8 ; en haut à gauche |
| Effets sonores | aucun |
| Musique | même niveau ; première montée légère vers 9,5 s, avant l'escalade |
| Lisible sans le son | oui — le héros se dandine, sûr de lui, entouré de ses copies |

### p05 → beat b05 (10,0 → 12,8 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Et là, ça s'accélère, tu sens ? » |
| Caméra | revelation · cible visee_baignoire · distance 7 m · hauteur 3 m · focale 35 mm (départ 3,15 m / 1,0 m, arrivée 7 m / 3 m) |
| Angle et cadrage | face, la caméra recule et s'élève (consigne du scénario pour l'escalade) ; baignoire au centre ; demi-largeur visible à l'arrivée ≈ 0,29 × 7,62 = 2,21 m (baignoire ±1,2 m) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre pop16 sur « Et » (≈ 0,0 s), durée 0,4 s → fin à 0,4 s (marge 2,4 s). 2. deplacer eau sur « là » (≈ 0,4 s), durée 0,8 s, params vers [0 ; 0 ; 0,74] → fin à 1,2 s (marge 1,6 s) |
| Texte à l'écran | rien |
| Compteur | 8, puis 16 à 0,0 s ; en haut à gauche |
| Effets sonores | pop sur « Et » ; montée d'eau (glouglou) sur « là » (proposé, pas de son disponible) |
| Musique | monte d'un cran, tempo plus serré |
| Lisible sans le son | oui — une couche de canards s'empile sur la première, l'eau monte presque au rebord (0,74 pour 0,77) |

Note physique : les canards de la première couche ne montent pas avec l'eau (un module ne se déplace pas) ; ils s'enfoncent de 0,14 m sous le poids de la pile, ce qui explique que l'eau monte. Le héros reste aussi à 0,60, sous la pile.

### p06 → beat b06 (12,8 → 15,8 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Encore le double, et encore le double. » |
| Caméra | orbite · cible visee_baignoire · distance 9 m · hauteur 4 m · focale 35 mm (tiers de tour de −120° à −60°) |
| Angle et cadrage | trois quarts gauche → trois quarts droit ; baignoire au centre ; demi-largeur visible ≈ 0,29 × 9,85 = 2,86 m : l'anneau de 32 (2,6 m) tient dans le cadre, celui de 64 (3,9 m) sort sur les côtés, volontairement (ça déborde du cadre) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre pop32 sur « Encore » (≈ 0,0 s), durée 0,3 s → fin à 0,3 s (marge 2,7 s). 2. apparaitre flaque_a sur « double » (1er, ≈ 0,8 s), durée 0,5 s → fin à 1,3 s (marge 1,7 s). 3. apparaitre pop64 à `debut` 2,4 s (second « double » ; pas de `mot`, le moteur prendrait le premier), durée 0,3 s → fin à 2,7 s (**marge 0,3 s : ÉCART**, instant fixé par le calendrier du compteur ; résultat visible dans p07) |
| Texte à l'écran | rien |
| Compteur | 16, puis 32 à 0,0 s, puis 64 à 2,4 s ; en haut à gauche |
| Effets sonores | pop sur « Encore » ; éclaboussure sur « double » (1er) (proposé, pas de son ni d'effet visuel disponibles) ; pop à 2,4 s |
| Musique | continue de monter |
| Lisible sans le son | oui — des canards tombent au sol autour de la baignoire, une flaque apparaît, un deuxième anneau suit |

### p07 → beat b07, muet (15,8 → 18,8 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | muet |
| Caméra | plongee · cible baignoire · distance 16 m · hauteur 10 m · focale 35 mm (point visé 1,2 m au-dessus de la baignoire ; de (0 ; −4,0 ; 18,2) à (0 ; −2,4 ; 13,2) : distance réelle 17,5 → 12,2 m) |
| Angle et cadrage | vue presque verticale qui descend ; baignoire au centre ; demi-largeur visible à l'arrivée ≈ 0,29 × 12,2 = 3,5 m, demi-hauteur ≈ 6,2 m : l'anneau de 128 (5,7 m) remplit le haut et le bas, déborde sur les côtés |
| Transition vers le plan suivant | coupe |
| Actions | 1. grandir flaque_a, `debut` 0,0 s, durée 1,0 s, params facteur 2,2 → fin à 1,0 s (marge 2,0 s). 2. apparaitre pop128, `debut` 1,4 s, durée 0,3 s → fin à 1,7 s (marge 1,3 s). 3. apparaitre canard_envers, `debut` 1,4 s, durée 0,3 s → fin à 1,7 s (marge 1,3 s ; il fait partie du même pop, pas d'une action séparée à l'image) |
| Texte à l'écran | rien |
| Compteur | 64, puis 128 à 1,4 s ; en haut à gauche |
| Effets sonores | pop à 1,4 s ; nappe d'eau qui s'étale (proposé) |
| Musique | seule à porter le beat avec le pop : monte franchement |
| Lisible sans le son | oui — la flaque s'étend, un nouvel anneau de canards surgit autour |

### p08 → beat b08 (18,8 → 22,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Des centaines, et maintenant, des milliers de canards. » |
| Caméra | revelation · cible baignoire · distance 30 m · hauteur 14 m · focale 35 mm (départ 13,5 m / 3,5 m, arrivée 30 m / 14 m ; point visé à z 1,2) |
| Angle et cadrage | face, grand recul en s'élevant : la foule s'étend plus vite que la caméra ne recule ; baignoire au centre (≈ 12 % de la largeur à l'arrivée) ; demi-largeur visible à l'arrivée ≈ 0,29 × 33,1 = 9,6 m : la foule (rayon 32,9 m) remplit tout le cadre et passe sous la caméra, volontairement (mer de canards) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre pop256 sur « Des » (≈ 0,0 s), durée 0,3 s → fin à 0,3 s (marge 2,9 s). 2. apparaitre pop512 sur « maintenant » (≈ 1,2 s), durée 0,3 s → fin à 1,5 s (marge 1,7 s). 3. apparaitre pop1024 sur « milliers » (≈ 2,0 s), durée 0,3 s → fin à 2,3 s (**marge 0,9 s : ÉCART**). 4. apparaitre pop2048 à `debut` 2,6 s (pendant « de » ; pas de `mot` : « de » attraperait « Des »), durée 0,3 s → fin à 2,9 s (**marge 0,3 s : ÉCART**). 5. apparaitre pop4096 à `debut` 3,0 s (pendant « canards »), durée 0,3 s → fin à 3,3 s (**déborde de 0,1 s sur b09 : ÉCART** ; le vocabulaire autorise le débordement) |
| Texte à l'écran | rien (le compteur porte les nombres) |
| Compteur | 128 → 256 à 0,0 s ; 512 à 1,2 s ; 1 024 à 2,0 s ; 2 048 à 2,6 s ; 4 096 à 3,0 s ; en haut à gauche |
| Effets sonores | cinq pops, de plus en plus rapprochés (1,2 / 0,8 / 0,6 / 0,4 s) |
| Musique | sommet, fort sous une voix forte |
| Lisible sans le son | oui pour la masse (les anneaux s'élargissent à chaque pop) ; les nombres exacts dépendent du compteur (absent du contrat v1.0) |

Choix assumé : **5 actions dans ce beat** (règle : 3 au plus). Le fichier de beats fixe 5 pops pour que les intervalles raccourcissent jusqu'au bout (retour du pilote) ; les fusionner en un seul module (« vague » de 3 584 canards sur « milliers », durée 1,0 s) tiendrait la règle des 3 actions, mais ferait perdre les pops à 2,6 et 3,0 s. Je garde les 5 pops et je signale l'écart ; l'autre option est décrite dans « Questions pour Lucas ».

### p09 → beat b09 (22,0 → 25,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Bon, laisse tomber, tu ne comptes plus. » |
| Caméra | travelling_lateral · cible visee_baignoire · distance 6 m · hauteur 2,5 m · focale 35 mm (caméra de (−2,4 ; −6 ; 3,1) à (2,4 ; −6 ; 3,1), elle pivote pour garder la baignoire) |
| Angle et cadrage | face, légère plongée (23°), l'horizon de canards visible derrière la baignoire ; baignoire au centre ; demi-largeur visible ≈ 0,29 × 6,5 = 1,9 m (baignoire ±1,2 m) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre flaque_b sur « Bon » (≈ 0,2 s), durée 0,5 s → fin à 0,7 s (marge 2,3 s). 2. grandir flaque_b sur « tomber » (≈ 1,0 s), durée 0,8 s, params facteur 2,5 → fin à 1,8 s (marge 1,2 s) |
| Texte à l'écran | rien |
| Compteur | 4 096 (figé) ; en haut à gauche |
| Effets sonores | soupir d'eau (proposé) |
| Musique | redescend d'un cran, reste soutenue |
| Lisible sans le son | oui — la baignoire noyée, la pile, une flaque qui s'étale, des canards jusqu'à l'horizon |

### p10 → beat b10 (25,0 → 28,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Un seul regarde de l'autre côté, trouve-le. » |
| Caméra | plan_fixe · cible visee_baignoire · distance 8 m · hauteur 3,5 m · focale 35 mm (caméra en (0 ; −8 ; 4,1)) |
| Angle et cadrage | face, plongée de 24° ; arrêt sur l'image pleine : baignoire au centre, canards partout autour ; demi-largeur visible ≈ 0,29 × 8,73 = 2,53 m ; canard_envers (0,75 ; −0,25 ; 0,88) au tiers droit, sur la pile, ≈ 9 % de la largeur de l'image : trouvable |
| Transition vers le plan suivant | coupe |
| Actions | aucune (arrêt sur image voulu) |
| Texte à l'écran | rien |
| Compteur | 4 096 (figé) ; en haut à gauche |
| Effets sonores | aucun |
| Musique | tenue basse, suspendue |
| Lisible sans le son | **non en v1.0** — sans orientation fixe des canards de foule, aucun ne « regarde de l'autre côté » de façon visible (voir « Briques manquantes ») |

### p11 → beat b11 (28,0 → 31,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Pouf, il n'en reste qu'un. » (après 0,5 s de silence) |
| Caméra | plan_fixe · cible visee_heros · distance 4,5 m · hauteur 1,5 m · focale 35 mm (caméra en (−0,25 ; −4,75 ; 2,25)) |
| Angle et cadrage | face, plongée de 18° ; canard_0 au centre ; demi-largeur visible ≈ 0,29 × 4,74 = 1,37 m (la baignoire presque entière, le bord droit coupé de 8 cm) ; caméra au-dessus des canards du sol (z 2,25), rien ne la traverse |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre, sur « Pouf » (≈ 0,5 s), durée 0,3 s → fin à 0,8 s (marge 2,2 s), groupées : pop02, pop04, pop08, pop16, pop32, pop64, pop128, pop256, pop512, pop1024, pop2048, pop4096, canard_envers, flaque_a, flaque_b (15 actions). 2. deplacer eau sur « il » (≈ 0,9 s), durée 0,8 s, params vers [0 ; 0 ; 0,60] → fin à 1,7 s (marge 1,3 s) |
| Texte à l'écran | rien |
| Compteur | 4 096 figé de 0,0 à 0,5 s, puis 1 à 0,5 s ; en haut à gauche |
| Effets sonores | silence total de 0,0 à 0,5 s ; « pouf » sur « Pouf » |
| Musique | **coupée net à 28,0 s** |
| Lisible sans le son | oui — tout disparaît d'un coup sauf le héros, l'eau redescend ; le compteur 1 |

Justification des 16 actions : 15 disparitions groupées sur un même mot (« Pouf »), un seul événement à l'image ; la seule autre action (eau) est sur un autre mot.

### p12 → beat b12 (31,0 → 34,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Tout est calme, tu peux respirer. » |
| Caméra | dolly_avant · cible visee_heros · distance 3 m · hauteur 0,3 m · focale 35 mm (départ 3,9 m / 0,35 m, **arrivée réelle 2,4 m / 0,26 m**) |
| Angle et cadrage | face, caméra très basse, presque au ras de l'eau (altitude ≈ 1,0 à 1,1 m) ; canard_0 au centre ; demi-largeur visible à l'arrivée ≈ 0,29 × 2,41 = 0,70 m |
| Transition vers le plan suivant | coupe |
| Actions | cycle canard_0 sur « calme » (≈ 1,1 s), durée 0,9 s, params nom flotter, amplitude 0,5 → fin à 2,0 s (marge 1,0 s) |
| Texte à l'écran | rien |
| Compteur | 1 ; en haut à gauche |
| Effets sonores | clapotis léger (proposé) |
| Musique | reprise douce à 31,0 s, très basse (≈ −22 dB) |
| Lisible sans le son | oui — un seul canard, qui flotte tranquillement |

### p13 → beat b13 (34,0 → 37,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Donut ou ballon, toi, tu choisis lequel ? » |
| Caméra | orbite · cible visee_duo · distance 4,5 m · hauteur 1,2 m · focale 35 mm (tiers de tour de −120° à −60°) |
| Angle et cadrage | trois quarts → trois quarts ; donut à gauche, ballon à droite, héros entre les deux un peu en retrait ; demi-largeur visible ≈ 0,29 × 4,66 = 1,35 m ; écart donut-ballon 0,9 m < 0,25 × 4,5 = 1,13 m ; sommet du ballon à ≈ 29 % du haut de l'image, sous la bande du texte (≈ 15 %) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre donut sur « Donut » (≈ 0,2 s), durée 0,5 s → fin à 0,7 s (marge 2,3 s). 2. apparaitre ballon sur « ballon » (≈ 1,0 s), durée 0,5 s → fin à 1,5 s (marge 1,5 s) |
| Texte à l'écran | « ET APRÈS ? » en haut, centré, dans la zone sûre, de 0,0 à 3,0 s ; étiquettes « DONUT » et « BALLON » sous les objets (prévues par le scénario ; module d'habillage absent, voir v1.1) |
| Compteur | 1 ; en haut à gauche, au-dessus et à gauche du texte |
| Effets sonores | pop sur « Donut », pop sur « ballon » |
| Musique | basse, légère remontée interrogative |
| Lisible sans le son | oui en partie — deux objets surgissent et « ET APRÈS ? » ; sans les étiquettes, le choix entre les deux reste implicite |

### p14 → beat b14 (37,0 → 40,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Attends, tu le vois trembler, celui-là ? » |
| Caméra | plan_fixe · cible visee_duo · distance 2,6 m · hauteur 0,8 m · focale 35 mm (**identique à p01** : boucle) |
| Angle et cadrage | identique à p01 ; donut et ballon visibles sur le rebord avant (bords à ±0,6 m du centre pour une demi-largeur de 0,70 m à leur profondeur) jusqu'à leur disparition |
| Transition vers le plan suivant | boucle sur p01 : raccord exact (même caméra ; canard_0 au même endroit, eau à 0,60, ni flaque, ni objet, ni texte) |
| Actions | 1. disparaitre donut sur « le » (≈ 1,0 s), durée 0,3 s → fin à 1,3 s (marge 1,7 s). 2. disparaitre ballon sur « le » (≈ 1,0 s), durée 0,3 s → fin à 1,3 s (marge 1,7 s) ; disparitions groupées sur un même mot. 3. cycle canard_0 sur « tu » (≈ 0,6 s), durée 1,4 s, params nom osciller, amplitude 0,3 → fin à 2,0 s (marge 1,0 s) : le frémissement commence avant « trembler » (≈ 1,8 s) et le couvre |
| Texte à l'écran | « ET APRÈS ? » de 0,0 à 1,0 s (disparaît avec le donut et le ballon), puis rien |
| Compteur | 1 ; en haut à gauche (dernière image identique à la première) |
| Effets sonores | « pouf » léger sur « le » ; petit cliquetis de frémissement (proposé) |
| Musique | même niveau qu'à 0,0 s pour la boucle |
| Lisible sans le son | oui — les objets disparaissent, le canard frémit : ça va recommencer |

## Vérifications chiffrées

| Règle | Valeur mesurée | Résultat |
|---|---|---|
| Un plan par beat, mêmes durées que les beats | 14 plans p01-p14 pour b01-b14 ; durées reprises telles quelles, total 40,0 s ; à imposer par `duree_s` sur les 14 beats | OK |
| Jamais plus de 2 mouvements identiques d'affilée | suite : fixe, survol, plongee, dolly, revelation, orbite, plongee, revelation, travelling, fixe, fixe, dolly, orbite, fixe ; plus longue suite : 2 (p10-p11, distance et cible différentes : 8 m sur la baignoire, 4,5 m sur le héros) | OK |
| Plans serrés (≤ 12 m) majoritaires ; larges (≥ 20 m) présents et alternés | 12 serrés (p01-p06, p09-p14), 1 moyen (p07, 16 m), 1 large (p08, 30 m) ; le recul de l'escalade 7 → 9 → 16 → 30 m est suivi d'une coupe à 6 m | OK (un seul plan large, réservé au bilan « des milliers ») |
| Chaque action finit ≥ 1 s avant la fin de son beat | hors règle : b03 pop08 (marge 0,5 s), b06 pop64 (0,3 s), b08 pop1024 (0,9 s), b08 pop2048 (0,3 s), b08 pop4096 (−0,1 s, déborde sur b09). Tous sont des pops du compteur dont l'instant est fixé par le fichier de beats ; leur résultat reste à l'image dans le plan suivant | ÉCART (5 actions) |
| Chaque mot déclencheur figure dans la voix du beat | deux, pop, huit, Facile, Et, là, Encore, double (1er), Des, maintenant, milliers, Bon, tomber, Pouf, il, calme, Donut, ballon, le, tu : tous présents ; 3 déclenchements par `debut` pour éviter un mot répété ou un préfixe ambigu (b06 2,4 s ; b08 2,6 s et 3,0 s) | OK |
| Au plus 3 actions par beat (hors disparitions groupées justifiées) | b08 : 5 apparitions ; b11 : 15 disparitions groupées sur « Pouf » + 1 (justifié) ; b14 : 3 ; autres : 0 à 3 | ÉCART (b08) |
| Sujet dans le cadre (demi-largeur ≈ 0,29 × distance) | demi-largeur ≥ demi-emprise du sujet à chaque plan (p01 0,79/0,45 ; p02 1,09/0,45 ; p03 1,40/1,2 ; p04 0,60/0,2 ; p05 2,21/1,2 ; p06 2,86/1,2 ; p07 3,5/1,2 ; p08 9,6/1,2 ; p09 1,9/1,2 ; p10 2,53/1,2 ; p11 1,37/0,2 ; p12 0,70/0,2 ; p13 1,35/0,6 ; p14 0,79/0,6) ; sujet centré verticalement grâce aux repères de visée | OK |
| Crédibilité physique (appuis, rien ne traverse, effets attendus) | canards posés sur l'eau (0,60) ou sur le dos d'un autre canard (0,88), anneaux au sol à partir de 1,6 m (bord de la baignoire à 1,34 m + demi-canard) ; donut et ballon sur le rebord (0,77) ; caméras toujours au-dessus des canards du sol ; eau qui monte (b05) puis deux flaques qui apparaissent et grandissent (b06, b07, b09). Restent : canards de la première couche qui ne montent pas avec l'eau (enfoncés de 0,14 m), pas d'éclaboussure, empilement limité à deux couches dans la baignoire | OK (limites listées en briques manquantes) |
| Uniquement le vocabulaire v1.0 | actions : apparaitre, disparaitre, deplacer, grandir, cycle ; mouvements : les 7 ; module : disperser ; assets : primitives de `PRIMITIVES` et `bibliotheque:canard_caoutchouc` (registre), 3 assets à sourcer avec repli en primitive | OK |

## Briques manquantes

- **Orientation fixe des instances de `disperser`** : le moteur donne une rotation aléatoire à chaque canard d'une foule (`decorateur.py`). Le défi de b10 (« un seul regarde de l'autre côté ») est donc **illisible** en v1.0 : tous les canards regardent dans des directions différentes. Il faut un paramètre du type « rotation fixe » (tous vers +x), avec `canard_envers` à 180°.
- **Compteur animé** à l'écran (13 valeurs, dont 5 en 3,2 s en b08) : pas de champ ; c'est lui qui porte les nombres de 16 à 4 096.
- **Étiquettes sous les objets** (« DONUT », « BALLON », b13) : module d'habillage absent.
- **Déplacer un module** : la foule posée sur l'eau ne peut pas monter avec l'eau (`deplacer` refusé sur un module) ; contourné par une eau qui ne monte que de 0,14 m.
- **Éclaboussure et vague** quand les canards débordent (b06) : aucun effet.
- **Empilement réel, tas** : deux couches dans la baignoire, puis un tapis au sol ; pas de tas qui monte au-dessus du rebord comme le décrit le scénario (« s'empilent »).
- **Foule dense au sol** : la distance minimale de 0,5 m entre deux instances d'un module `aleatoire` impose 0,83 m² par canard ; 4 096 canards occupent un disque de 33 m de rayon. Un paramètre de distance minimale permettrait une mer plus serrée, plus proche de la baignoire.
- **Azimut de la caméra** et **hauteur de visée** : la caméra est toujours côté −y et vise 1,2 m au-dessus de sa cible ; contourné par trois repères invisibles. Un vrai « trois quarts » fixe n'existe qu'avec `survol` ou `orbite`.
- **Silence avant la voix** (« pause avant », 0,5 s en b11) : sans champ, la voix démarre à 0,15 s du début du beat.

## Non porté par le contrat v1.0 (v1.1)

- **Angle et cadrage** (face, trois quarts, place du sujet) : tous les plans. Seule la combinaison mouvement + cible + distance + hauteur passe dans la fiche.
- **Transitions** (coupe, raccord de boucle p14 → p01) : tous les plans ; coupe sèche par défaut du moteur.
- **Compteur** (valeurs, instants, position en haut à gauche) : tous les plans. Il ne doit pas être détourné dans `texte_ecran`.
- **Position dans l'image** du compteur et du texte (zone sûre) : tous les plans ; le moteur place le texte à ≈ 15 % du haut et les sous-titres à ≈ 70 % de la hauteur, ce qui respecte la zone sûre.
- **Texte à l'écran limité à une partie du beat** : b14, « ET APRÈS ? » de 0,0 à 1,0 s. `texte_ecran` couvre tout le beat ; dans la fiche v1.0, b14 n'a donc **pas** de `texte_ecran` (le texte s'arrête à 37,0 s au lieu de 38,0 s). b13 porte « ET APRÈS ? » sur tout le beat, conforme.
- **Étiquettes** « DONUT » et « BALLON » : p13.
- **Sous-titres** (découpage en groupes et mots surlignés du fichier de beats) : tous les plans ; le moteur fait son propre découpage karaoké.
- **Intonation, mots appuyés, pauses avant et après** : tous les beats ; en particulier le silence de 0,5 s de b11.
- **Effets sonores** autres que le pop automatique d'`apparaitre` : « pouf » (p11, p14), clapotis (p01, p12), glouglou (p05), éclaboussure (p06), nappe d'eau (p07), soupir d'eau (p09), frémissement (p14).
- **Musique par moment** (montées, coupure à 28,0 s, reprise à 31,0 s, niveau identique au début et à la fin) : le contrat n'a qu'un fichier et un volume global (`audio.musique`, `audio.volume_musique`) ; musique de série encore « à fixer » (charte, niveau A).
- **Instants des mots** : la fiche se cale sur des mots dont l'instant est estimé par le moteur (voix à 0,15 s, débit pondéré par la longueur des mots), pas sur le calcul à 2,5 mots/s du fichier de beats ; les instants réels différeront de quelques dixièmes de seconde, et les marges tenues de justesse (1,0 s en p01, p02, p04, p12, p14) peuvent basculer. À vérifier dans `timeline.json`.

## À confirmer par Guillaume

1. **Repères de visée invisibles** (`visee_duo`, `visee_heros`, `visee_baignoire`, des `primitif:caisse` sous le sol et jamais apparus) : usage acceptable des champs v1.0 ? Ils corrigent la baignoire « petite en bas de l'image » du pilote. Sinon, il faut un paramètre de hauteur de visée.
2. **`dolly_avant`** : la caméra arrive à 0,8 × `distance`, pas à `distance` comme le disent `prod-realisateur` et la consigne de découpage. Lequel fait foi ? Mes valeurs suivent le code.
3. **Taille réelle du canard** `canard_caoutchouc` à l'échelle 1,3 (longueur, hauteur du dos) : les places en grille supposent une emprise ≤ 0,45 m, la pile suppose un dos à 0,27 m (z 0,88). Si le dos est plus bas, abaisser `pop16` et `canard_envers` d'autant.
4. **Baignoire, donut, ballon** : seulement des primitives faites en code, au premier plan (baignoire dans tous les plans, donut et ballon en p13-p14). Leçon du pilote : image pauvre. Assets à sourcer (mots-clés dans le tableau des éléments) ; pour la baignoire, Poly Haven et 3DTexel n'en ont pas, Sketchfab et Poly Pizza demandent des comptes (tâche 14 du Backlog). Un modèle sourcé doit être mis aux dimensions de la primitive.
5. **Défi du canard à l'envers (b10)** : illisible tant que les instances ont une rotation aléatoire. Ajouter une option de rotation fixe au module, ou accepter un b10 non lisible pour l'animatique ?
6. **Durées imposées** : avec la vraie voix Kyutai, une phrase plus longue que son `duree_s` fait échouer la timeline (« duree_s plus courte que la voix »). b03 (6 mots en 2,4 s, voix de 2,4 s) et b08 (8 mots en 3,2 s) n'ont aucune marge.
7. **Son de `disparaitre`** : y a-t-il un « pouf » automatique comme le pop d'`apparaitre` ? La chute en dépend.
8. **Temps de rendu** : 4 096 canards Poly Haven (≈ 4 300 polygones chacun) visibles de 21,8 à 28,5 s ; la v2 du pilote a pris ≈ 13 min en animatique. Le sol passe à 120 m (horizon visible en p09).
9. **Flaques sous la foule** : leur matériau reste-t-il visible entre les canards (densité ≈ 1,2 canard par m², 15 % du sol couvert) ?

## Questions pour Lucas

1. **Pops tardifs** : 5 pops du compteur finissent moins d'1 s avant la fin de leur beat (b03 « huit », b06 second « double », b08 « milliers », « de », « canards »). Je n'ai changé ni le texte ni les durées. Tu acceptes ces écarts (le résultat reste visible au plan suivant), ou tu demandes à `story-beats` de placer ces mots plus tôt dans les phrases ?
2. **b08, 5 actions** : je garde les 5 pops (intervalles qui raccourcissent jusqu'au bout). L'autre option fusionne 1 024, 2 048 et 4 096 en une seule vague de 3 584 canards sur « milliers » (fin à 3,0 s, pile au moment du 4 096) : 3 actions, mais deux pops audibles de moins. Laquelle ?
3. **Canard survivant** : j'ai choisi le héros du début (`canard_0`), ce qui rend la boucle exacte. D'accord ?
