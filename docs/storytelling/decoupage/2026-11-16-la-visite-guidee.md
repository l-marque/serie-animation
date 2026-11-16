# La visite guidée — découpage technique

- Statut : proposé, à valider par Lucas ; faisabilité à confirmer par Guillaume
- Beats source : `docs/storytelling/beats/2026-11-16-la-visite-guidee.md` (statut : validé par Lucas le 2026-11-16 ; versions de secours seulement si la voix n° 12 déborde à l'animatique ; pas de mesure avant le découpage ; on garde les 0,7 s à la jonction de la boucle)
- Scénario source : `docs/storytelling/scenarios/2026-11-16-la-visite-guidee-v2.md` (statut : validé par Lucas le 2026-11-16, avec réserves)
- Épisode : `lancement-du-club` ; état de la série lu dans `episodes/serie/etat.json` (0 abonné, 0 €, 0 supporter, aucun choix en cours ; il n'a pas été transmis avec la demande, je l'ai lu dans le dépôt)
- Durée : 40,0 s · Plans : 16 · Mouvements utilisés : plan_fixe × 6, dolly_avant × 3, revelation × 2, survol × 2, travelling_lateral × 1, plongee × 1, orbite × 1 (`descente` non utilisée : ni le scénario ni un humain ne la demande)
- État réel : document écrit à partir des fichiers du dépôt ; **rien n'a été testé** (aucune validation par le pipeline, aucune animatique). Tous les cadrages sont calculés, pas vus.

**Lecture importante pour `prod-realisateur`** :

1. **Durées imposées.** Chaque beat reçoit `duree_s` égale à la durée du fichier de beats : 3,0 ; 2,6 ; 2,4 ; 2,5 ; 3,5 ; 2,0 ; 2,9 ; 1,6 ; 2,0 ; 2,5 ; 2,0 ; 3,0 ; 1,5 ; 4,0 ; 1,0 ; 3,5 (total 40,0 s). Sans cela, le moteur recalcule la durée depuis la voix (+ 0,45 s) et la boucle ne tombe plus à 40,0 s.
2. **La caméra est toujours du côté −y de sa cible** (`engine/blender/camera.py` : `plan_fixe`, `revelation`, `dolly_avant`, `plongee` et `travelling_lateral` partent de l'angle −90° ; `survol` va de −110° à −70°, `orbite` de −120° à −60°). Aucune vue de côté n'est possible : les « trois quarts » s'obtiennent en tournant Kevin (`rotation_z`), pas la caméra.
3. **La caméra vise 1,2 m au-dessus de sa cible** et sa position est lue à la première image du beat. Pour cadrer Kevin en pied au-dessus des sous-titres, je vise 0,6 m au-dessus du sol avec des **repères de visée** (`primitif:repere`, sans géométrie). Altitude de la caméra = z du repère + 1,2 + `hauteur`.
4. **`dolly_avant` va de 1,3 × `distance` à 0,8 × `distance`** ; **`revelation` va de 0,45 × `distance` à `distance`** (hauteur de départ : max(1,0 ; 0,25 × `hauteur`)) ; **`plongee` va de (0,25 × distance ; 1,7 × hauteur) à (0,15 × distance ; 1,2 × hauteur)**. Les plans ci-dessous donnent le paramètre et les distances réelles de départ et d'arrivée.
5. **Kevin change d'attitude et de place sur les coupes** : un élément par station et par attitude, échangé au début du beat (`disparaitre` l'ancien, `apparaitre` le nouveau, `debut` 0,0, durée 0,05 s), méthode décrite dans `.claude/agents/prod-realisateur.md`. Aucun `deplacer` de Kevin.
6. **Hypothèses de taille** (à confirmer, le modèle n'est pas sourcé) : Kevin mesure 1,75 m, bras ouverts ≈ 1,8 m d'envergure (± 0,9 m), il regarde vers −y à `rotation_z` 0 ; une rotation positive le tourne vers la droite de l'image (sens à vérifier sur la planche contact).

## Décor

Repère : x vers la droite de l'image d'ouverture, y vers le fond, z vers le haut, en mètres ; origine au centre du décor principal (centre du terrain, où pousse la touffe).

- Sol : oui, taille 120 m (asphalte gris, rôle `sol` du pack ; le plan p03 voit l'horizon, le bord du sol doit rester loin) · Pack de DA proposé : à choisir (aucun pack « stade » n'existe dans `engine/packs_da/` ; à créer)

### Lieu, ambiance et style (repris du scénario, § « Lieux »)

Un seul lieu : le stade du FC Miteux, petit terrain de quartier abandonné. Style low-poly coloré, couleurs vives. Début d'après-midi (vers 14 h), beau temps, ciel bleu vif, 3 nuages blancs, soleil haut à gauche de l'image d'ouverture, ombres courtes, teinte chaude. Sol : **terre sèche** ocre de 20 × 12 m, lignes blanches sommaires effacées sur la moitié de leur longueur, **une seule touffe verte** au centre (réponse 3 de Lucas, à confirmer par Guillaume) ; asphalte gris autour. Aucune autre végétation verte.

Kevin (bible, § 5 ; scénario) : la vingtaine, palier « Départ » : maillot de foot jaune vif deux tailles trop grand avec une tache de ketchup rouge, short bleu trop court, 1 chaussette rouge et 1 chaussette blanche, tongs bleues, coupe au bol ratée, casquette rouge à l'envers, sourire niais. Même tenue tout l'épisode (0 abonné, 0 €).

### Éléments

Dimensions utilisées : `primitif:panneau_entree` 2,4 × 0,9 m, panneau centré à z = 1,85 (haut à 2,3 m), deux poteaux, texte centré à (0 ; −0,07 ; 1,85) (docstring de `engine/blender/kits/village.py`) ; `primitif:caisse` cube de 0,8 m ; `bibliotheque:lampadaire_rue` 4,0 m ; `bibliotheque:barriere` 1,0 m de haut ; `bibliotheque:arbre_mort` 5,0 m ; `bibliotheque:rochers` 0,7 m ; `bibliotheque:tonneau` 0,9 m ; `bibliotheque:drapeau` 2,6 m ; `primitif:flaque` ≈ 1 m (registre et docstrings).

| id | Asset | Position x / y / z (m) | Rotation z (°) | Échelle | Rôle | Visible au début | Note (appui, contact) |
|---|---|---|---|---|---|---|---|
| terrain | à sourcer ou à construire : « dirt soccer field » / « football pitch lines » / « dry cracked ground texture » ; style low-poly coloré ; indispensable : rectangle de 20 × 12 m en terre sèche ocre, lignes blanches à moitié effacées (touche, ligne médiane, rond central), aucune herbe ; id proposé `bibliotheque:terrain_miteux` ; aucune primitive de repli | 0 / 0 / 0,01 | 0 | 1 | sol | oui | posé à plat sur le sol, 1 cm au-dessus pour éviter le scintillement ; état `terrain_ruine` |
| but_gauche | à sourcer : « soccer goal » / « football goal low poly » / « rusty goal post » ; low-poly ; indispensable : cage de foot à 7 de 5 × 2 × 1,5 m, rouille orange-brun, filet blanc grisé déchiré ; id proposé `bibliotheque:but_rouille` ; aucune primitive de repli | −10 / 0 / 0 | à régler : ouverture vers +x | 1 | accessoire | oui | posé au sol sur la ligne de but, ouverture vers le centre du terrain. **Visible dans aucun plan** (voir « Écarts ») |
| but_droit | même modèle ; indispensable en plus : filet absent | 10 / 0 / 0 | à régler : ouverture vers −x | 1 | accessoire | oui | posé au sol. Visible dans aucun plan ; son poteau avant (10 / 2,5) passe à 0,2 m du bord du cadre de p07 |
| barriere_1 | bibliotheque:barriere | −7,5 / −7 / 0 | 0 | 1 | accessoire | oui | debout, au sol |
| barriere_2 | bibliotheque:barriere | −4,5 / −7 / 0 | 30 | 1 | accessoire | oui | scénario : couchée au sol. Le contrat n'a que `rotation_z` : impossible de la coucher (brique manquante). Repli : debout, de travers |
| barriere_3 | bibliotheque:barriere | −1,5 / −7 / 0 | 0 | 1 | accessoire | oui | debout |
| barriere_4 | bibliotheque:barriere | 1,5 / −7 / 0 | 0 | 1 | accessoire | oui | debout ; la caméra de p09 passe 0,2 à 0,9 m devant elle |
| barriere_5 | bibliotheque:barriere | 4,5 / −7 / 0 | −30 | 1 | accessoire | oui | scénario : couchée ; même repli que barriere_2 |
| barriere_6 | bibliotheque:barriere | 7,5 / −7 / 0 | 0 | 1 | accessoire | oui | debout |
| tribune_supporters | à sourcer : « bleachers » / « concrete grandstand low poly » / « stadium stand » ; low-poly ; indispensable : gradins de quartier en béton gris, 3 rangs, 12 × 3 × 2,5 m, rebords en peinture bleue écaillée, **aucun personnage** ; id proposé `bibliotheque:tribune_beton` ; aucune primitive de repli | 0 / 9 / 0 | 0 | à régler pour 12 m de long | batiment | oui | posée au sol, x de −6 à 6, y de 7,5 à 10,5 ; face vers −y ; état `tribune_vide`, 0 supporter (`etat.json`) |
| caisse_vip | primitif:caisse (repli) ; mieux, à sourcer : « wooden crate » / « old wood box » / « broken crate low poly » ; indispensable : bois clair, une planche fendue ; id proposé `bibliotheque:caisse_bois` | −8 / 7 / 0 | 15 | 0,75 (côté 0,6 m) | accessoire | oui | posée au sol (la primitive est centrée à 0,4 m × 0,75 = 0,3 m) ; état `caisse_vip_bancale` |
| panneau_vip | primitif:panneau_entree | −8 / 7,8 / 0 | 0 | 1 | accent | non | 0,8 m derrière la caisse ; x de −9,2 à −6,8, hors de la tribune (qui finit à x = −6) et à 0,8 m du tas de planches |
| lampadaire_eclairage | bibliotheque:lampadaire_rue (intégré) | 7,5 / 7 / 0 | 0 | 1 | accessoire | oui | au sol, au coin droit de la tribune (1,5 m de son extrémité) ; `lampadaire_debout` → `lampadaire_retreci` (17,0 s) → absent (18,9 s) |
| panneau_eclairage | primitif:panneau_entree | 9,1 / 7,8 / 0 | 0 | 1 | accent | non | x de 7,9 à 10,3 : le lampadaire (x = 7,5) reste à 0,4 m à sa gauche, sans le cacher |
| touffe_herbe | à sourcer : « grass tuft » / « grass clump low poly » / « tall grass patch » ; low-poly ; indispensable : vert vif, 0,3 m de haut et de large, base plate ; id proposé `bibliotheque:touffe_herbe` ; aucune primitive de repli | 0 / 0 / 0 | 0 | à régler pour 0,3 m | vegetation | oui | posée sur le terrain, au centre ; `touffe_normale` → `touffe_fiere` (× 1,3 à 23,5 s) |
| panneau_pelouse | primitif:panneau_entree | −1,4 / 0,5 / 0 | 0 | 1 | accent | non | à gauche de la touffe, 0,5 m derrière elle ; x de −2,6 à −0,2 : il ne coupe l'axe x = 0 d'aucune caméra |
| panneau_question | primitif:panneau_entree | 3 / 6 / 0 | 0 | 1 | accent | non | à 3 m à droite de Kevin (K0), même profondeur ; x de 1,8 à 4,2 : hors du cadre de p01 et p16 (± 1,3 m) ; le gravat (3,5 / 7) est 1 m derrière |
| gravat_1 | bibliotheque:rochers | −3 / 7 / 0 | 0 | 1 | roche | oui | au pied de la tribune ; gris béton |
| gravat_2 | bibliotheque:rochers | 3,5 / 7 / 0 | 40 | 1 | roche | oui | au pied de la tribune (premier plan de p13) |
| gravat_3 | bibliotheque:rochers | 5 / −6,5 / 0 | 80 | 1 | roche | oui | visible dans aucun plan |
| gravat_4 | bibliotheque:rochers | −9 / −5 / 0 | 120 | 1 | roche | oui | visible dans aucun plan |
| flaque_1 | primitif:flaque | −4 / −2 / 0,02 | 0 | 1 | (celui de la pièce) | oui | à plat sur le terrain ; vue en p03 |
| flaque_2 | primitif:flaque | 6 / −3 / 0,02 | 0 | 1 | (celui de la pièce) | oui | visible dans aucun plan |
| tonneau_1 | bibliotheque:tonneau | 11 / −4 / 0 | 0 | 1 | accessoire | oui | visible dans aucun plan |
| tonneau_2 | bibliotheque:tonneau | 11 / −3 / 0 | 0 | 1 | accessoire | oui | visible dans aucun plan |
| drapeau_coin | bibliotheque:drapeau | −10 / −6 / 0 | 0 | 1 | accent | oui | scénario : penché à 20° ; impossible avec `rotation_z` seul (brique manquante), planté droit. Visible dans aucun plan |
| planches | bibliotheque:planches | −10 / 7 / 0 | 0 | 1 | accessoire | oui | au sol ; bord gauche de p05 au début du plan |
| arbre_mort | bibliotheque:arbre_mort | 4 / 12 / 0 | 0 | 1 | vegetation | oui | 1,5 m derrière la tribune ; sa cime (5 m) dépasse de 2,5 m ; brun, sans feuilles |
| visee_k0 | primitif:repere | 0 / 6 / −0,6 | 0 | 1 | accessoire | oui | repère de visée sans géométrie. Point visé : Kevin à K0, 0,6 m au-dessus du sol |
| visee_k1 | primitif:repere | −6 / 5 / −0,6 | 0 | 1 | accessoire | oui | point visé : Kevin à K1, z = 0,6 |
| visee_k2 | primitif:repere | 5,5 / 5 / −0,6 | 0 | 1 | accessoire | oui | point visé : Kevin à K2, z = 0,6 |
| visee_k3 | primitif:repere | 0,8 / −0,3 / −0,6 | 0 | 1 | accessoire | oui | point visé : milieu entre Kevin (K3) et la touffe, z = 0,6 |
| visee_vip | primitif:repere | −8 / 7,3 / −0,3 | 0 | 1 | accessoire | oui | point visé : entre la caisse et son panneau, z = 0,9 |
| visee_eclairage | primitif:repere | 8,9 / 7,4 / 0,8 | 0 | 1 | accessoire | oui | point visé : entre le lampadaire et son panneau, z = 2,0 |
| visee_pelouse | primitif:repere | −1,05 / 0,25 / −0,7 | 0 | 1 | accessoire | oui | point visé : entre la touffe et son panneau, z = 0,5 |
| visee_touffe | primitif:repere | 0 / 0 / −1,2 | 0 | 1 | accessoire | oui | point visé : la touffe, au sol (z = 0) |
| visee_tribune_d | primitif:repere | 3,5 / 9 / 0 | 0 | 1 | accessoire | oui | point visé : moitié droite de la tribune, z = 1,2 |
| visee_tribune | primitif:repere | 0 / 9 / 0 | 0 | 1 | accessoire | oui | point visé : centre de la tribune, z = 1,2 |

Personnages (à déclarer dans `personnages`). Kevin est **à sourcer** : « cartoon man animated » / « soccer fan low poly » / « casual man rigged » ; modèle animé CC0, low-poly coloré ; indispensable : la tenue décrite plus haut (maillot jaune taché, short bleu, chaussettes rouge et blanche, tongs bleues, casquette rouge à l'envers) et les attitudes ci-dessous, une entrée du registre par attitude. Aucune primitive de repli acceptable au premier plan (`primitif:personnage` est un cône et une sphère).

| id | Asset (entrée du registre proposée) | Position x / y / z (m) | Rotation z (°) | Échelle | Rôle | Visible au début | Note |
|---|---|---|---|---|---|---|---|
| kevin_k0_parle | bibliotheque:kevin_parle (« parle avec gestes », départ et fin bras grands ouverts) | 0 / 6 / 0 | 0 | 1 | personnage | oui | K0, face caméra ; b01-b03, b14, b16 |
| kevin_k1_montre | bibliotheque:kevin_montre_g (« montre du bras », bras tendu vers la gauche de l'image) | −6 / 5 / 0 | −25 | 1 | personnage | non | K1 ; bras vers la caisse (à 2,8 m, à gauche et derrière lui) ; b04 |
| kevin_k2_montre | bibliotheque:kevin_montre_d (même attitude en miroir, bras vers la droite de l'image) | 5,5 / 5 / 0 | 30 | 1 | personnage | non | K2 ; bras vers le lampadaire (à 2,8 m, à droite et derrière lui) ; b06 |
| kevin_k3_montre | bibliotheque:kevin_montre_g | 1,6 / −0,6 / 0 | −20 | 1 | personnage | non | K3 ; bras vers la touffe (à 1,7 m, à gauche) ; b09 |
| kevin_k3_parle | bibliotheque:kevin_parle | 1,6 / −0,6 / 0 | 0 | 1 | personnage | non | K3, face caméra ; b10-b11 (réserve b) |
| kevin_k0_montre | bibliotheque:kevin_montre_d | 0 / 6 / 0 | 35 | 1 | personnage | non | K0 ; bras vers l'arrière droit, vers la moitié de tribune que montre p13 ; b12-b13 |
| kevin_k0_immobile | bibliotheque:kevin_immobile (« immobile ») | 0 / 6 / 0 | 0 | 1 | personnage | non | K0 ; b15 (les 2 rotations) |

Réponse 1 de Lucas appliquée : les bras ouverts ne sont pas une attitude de plus, c'est la pose de départ et de fin de « parle avec gestes ».

### Foules (module `disperser`)

Aucune : la tribune a 0 supporter (`etat.json`, `supporters` : 0).

| id | Asset | Nombre | Motif | Centre x / y / z | Espacement | Rayon intérieur | Variation d'échelle | Seed | Visible au début | Ce qu'elle représente |
|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — |

## Plans

Instants des mots : pause avant + (rang du mot − 1) / 2,5 s. Demi-largeur visible = 0,29 × distance réelle ; demi-hauteur = 0,51 × distance réelle. Zone des sous-titres : de 67 à 80 % de la hauteur ; les pieds de Kevin et les objets importants restent au-dessus de 65 %.

### p01 → beat b01 (0,0 → 3,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Bienvenue au plus grand stade du monde. » |
| Caméra | plan_fixe · cible visee_k0 · distance 4,5 m · hauteur 0,6 m · focale 35 mm (caméra en 0 / 1,5 / 1,2) |
| Angle et cadrage | face, légère plongée (8°) ; plan moyen, Kevin en pied au centre (tête à 25 % de la hauteur, pieds à 63 %, mains à 15 % et 85 % de la largeur) ; demi-largeur visible ≈ 0,29 × 4,54 = 1,32 m pour des bras à ± 0,9 m (réserve a) |
| Ce qu'on voit | premier plan : kevin_k0_parle, bras grands ouverts dès la première image, maillot taché, tongs, casquette à l'envers ; fond : centre de tribune_supporters (`tribune_vide`), ciel au-dessus |
| Ce qu'on ne doit pas voir | les gravats, l'arbre mort, les buts ; aucun panneau (tous invisibles à ce moment) |
| Personnages | kevin_k0_parle : parle avec gestes, pose bras ouverts à 0,0 s ; face caméra |
| Transition vers le plan suivant | raccord dans l'axe : p02 démarre à la même distance (4,5 m), 0,4 m plus haut |
| Actions | aucune (Kevin bouge dès la première image par son animation) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | démarre à 0,0 s, très légère sous la voix (≈ −18 dB), même niveau qu'à 40,0 s |
| Lisible sans le son | oui — un type en tongs, bras ouverts, devant une tribune vide, deux compteurs à 0 et le sous-titre |

### p02 → beat b02 (3,0 → 5,6 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Je suis président du FC Miteux, » |
| Caméra | revelation · cible visee_k0 · distance 10 m · hauteur 2,5 m · focale 35 mm (de 4,5 m et 1,0 m de haut à 10 m et 2,5 m ; caméra de 0 / 1,5 / 1,6 à 0 / −4 / 3,1) |
| Angle et cadrage | face ; Kevin au centre, de plus en plus petit ; demi-largeur visible de 1,3 m à 0,29 × 10,3 = 3,0 m |
| Ce qu'on voit | premier plan : kevin_k0_parle ; fond : la tribune vide qui s'élargit, gravat_1, terre ocre et lignes blanches ; en fin de plan, l'arbre mort en haut à droite et la touffe tout en bas |
| Ce qu'on ne doit pas voir | les panneaux (invisibles) ; rien d'autre à exclure |
| Personnages | kevin_k0_parle : parle avec gestes ; face caméra |
| Transition vers le plan suivant | raccord dans l'axe : p03 démarre où p02 s'arrête (10 m, 2,5 m) |
| Actions | aucune |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — le recul montre que le « stade » est un terrain vague |

### p03 → beat b03 (5,6 → 8,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Entraîneur, et le seul joueur. » |
| Caméra | revelation · cible visee_k0 · distance 22 m · hauteur 10 m · focale 35 mm (de 9,9 m et 2,5 m de haut à 22 m et 10 m ; arrivée en 0 / −16 / 10,6, distance réelle 24,2 m) |
| Angle et cadrage | face, plongée de 24° à l'arrivée ; plan large, Kevin petit au centre (7 % de la hauteur) ; demi-largeur visible ≈ 0,29 × 24,2 = 7,0 m à la profondeur de Kevin |
| Ce qu'on voit | premier plan : barriere_3 et barriere_4, terre ocre, lignes, touffe_herbe, flaque_1 ; centre : kevin_k0_parle seul sur le terrain ; fond : toute la tribune vide (± 6 m), gravat_1, gravat_2, arbre_mort |
| Ce qu'on ne doit pas voir | pas le bord du sol ; les panneaux (invisibles). Hors cadre malgré le scénario : les 2 buts, la caisse, les tonneaux ; le lampadaire est à la limite droite du cadre |
| Personnages | kevin_k0_parle : parle avec gestes ; face caméra |
| Transition vers le plan suivant | coupe |
| Actions | aucune |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — un seul personnage, minuscule, au milieu d'un terrain vide |

### p04 → beat b04 (8,0 → 10,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « On commence par l'espace VIP. » |
| Caméra | survol · cible visee_k1 · distance 6 m · hauteur 0,8 m · focale 35 mm (arc de −110° à −70°, rayon de 6 à 5,7 m, caméra vers z = 1,4) |
| Angle et cadrage | de face à trois quarts en glissant (Kevin à 5° puis 45° de l'axe) ; plan moyen, Kevin en pied au centre ; demi-largeur visible ≈ 0,29 × 6,05 = 1,75 m |
| Ce qu'on voit | premier plan : kevin_k1_montre, bras tendu vers la gauche de l'image ; fond : caisse_vip, petite, au bord gauche ; extrémité gauche de la tribune |
| Ce qu'on ne doit pas voir | panneau_vip (invisible) ; le but gauche |
| Personnages | kevin_k1_montre : montre du bras ; trois quarts gauche |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre kevin_k0_parle, `debut` 0,0, durée 0,05 s → fin à 0,05 s. 2. apparaitre kevin_k1_montre, `debut` 0,0, durée 0,05 s → fin à 0,05 s (marge 2,45 s) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — Kevin désigne fièrement quelque chose hors champ |

### p05 → beat b05 (10,5 → 14,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Tribune VIP, places limitées, tout le confort moderne. » |
| Caméra | dolly_avant · cible visee_vip · distance 5,5 m · hauteur 0,5 m · focale 35 mm (de 7,15 m à 4,4 m ; caméra de −8 / 0,15 / 1,5 à −8 / 2,9 / 1,3) |
| Angle et cadrage | face ; la caisse au centre, à 63 % de la hauteur, le texte du panneau à 28 % ; demi-largeur visible à l'arrivée ≈ 0,29 × 4,9 = 1,42 m à la profondeur du panneau (large de ± 1,2 m) |
| Ce qu'on voit | premier plan : caisse_vip (`caisse_vip_bancale`) qui vacille ; juste derrière, panneau_vip et txt_vip « TRIBUNE VIP » ; fond : planches au bord gauche (début du plan), ciel |
| Ce qu'on ne doit pas voir | Kevin (à K1, hors cadre) ; la tribune des supporters ; le but gauche |
| Personnages | aucun à l'image (kevin_k1_montre reste à K1, hors cadre) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre panneau_vip, `debut` 0,0 (sur la coupe, juste avant « Tribune »), durée 0,6 s → fin à 0,6 s (marge 2,9 s). 2. cycle caisse_vip sur « places » (≈ 1,0 s), durée 2,5 s, params nom osciller, amplitude 0,5 → fin à 3,5 s (marge 0 s : mouvement continu jusqu'à la coupe, voulu par le scénario) |
| Texte à l'écran | rien (texte du décor : txt_vip) |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_vip |
| Effets sonores | pop automatique à 0,0 s (panneau) ; grincement sur « places » |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — un grand panneau « TRIBUNE VIP » au-dessus d'une caisse qui vacille |

### p06 → beat b06 (14,0 → 16,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Et ici, l'éclairage dernier cri. » |
| Caméra | travelling_lateral · cible visee_k2 · distance 6 m · hauteur 0,8 m · focale 35 mm (caméra de 3,1 / −1 / 1,4 à 7,9 / −1 / 1,4, soit 2,4 m/s) |
| Angle et cadrage | de profil trois quarts à face (Kevin à 52° puis 8° de l'axe) ; plan moyen, Kevin en pied au centre ; demi-largeur visible ≈ 0,29 × 6,0 à 6,5 = 1,75 à 1,9 m |
| Ce qu'on voit | premier plan : kevin_k2_montre, bras tendu vers la droite de l'image ; fond : lampadaire_eclairage (`lampadaire_debout`, 4 m) à droite, extrémité droite de la tribune |
| Ce qu'on ne doit pas voir | panneau_eclairage (invisible) ; le but droit |
| Personnages | kevin_k2_montre : montre du bras ; trois quarts droite |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre kevin_k1_montre, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k2_montre, `debut` 0,0, durée 0,05 s → fin à 0,05 s (marge 1,95 s) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — Kevin désigne un lampadaire, la caméra suit son bras |

### p07 → beat b07 (16,0 → 18,9 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | muet |
| Caméra | plan_fixe · cible visee_eclairage · distance 8 m · hauteur 0 m · focale 35 mm (caméra en 8,9 / −0,6 / 2,0) |
| Angle et cadrage | face, à hauteur du panneau ; lampadaire sur le tiers gauche (pied à 73 % de la hauteur, tête à 27 %), panneau au centre droit ; demi-largeur visible ≈ 0,29 × 8,0 = 2,3 m (lampadaire à −1,4 m, panneau de −1,0 à +1,4 m) |
| Ce qu'on voit | premier plan : lampadaire_eclairage, qui rétrécit puis disparaît ; panneau_eclairage et txt_eclairage « ÉCLAIRAGE » ; fond : bout droit des derniers rangs de la tribune, arbre_mort au bord gauche |
| Ce qu'on ne doit pas voir | Kevin (à K2, hors cadre à gauche) ; le poteau du but droit (à 0,2 m du bord droit : à vérifier à l'animatique) |
| Personnages | aucun à l'image |
| Transition vers le plan suivant | raccord dans l'axe : p08 démarre à la même distance (8,06 m) |
| Actions | 1. apparaitre panneau_eclairage, `debut` 0,0, durée 0,6 s → fin à 0,6 s. 2. grandir lampadaire_eclairage, `debut` 1,0, durée 0,8 s, params facteur 0,3 → fin à 1,8 s. 3. disparaitre lampadaire_eclairage, `debut` 2,5, durée 0,4 s → fin à 2,9 s (marge 0 s : instants fixés par le beat validé ; le résultat reste à l'image 1,6 s dans p08) |
| Texte à l'écran | rien (texte du décor : txt_eclairage) |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_eclairage |
| Effets sonores | pops automatiques à 0,0 s (panneau) et 1,0 s (rétrécissement) ; erreur à `debut` 2,5 (beat muet : calé sur un instant) |
| Musique | très légère, seule (pas de voix) |
| Lisible sans le son | oui — le panneau annonce « ÉCLAIRAGE », le lampadaire rétrécit et disparaît |

### p08 → beat b08 (18,9 → 20,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Ambiance tamisée, très tendance. » |
| Caméra | dolly_avant · cible visee_eclairage · distance 6,2 m · hauteur 0 m · focale 35 mm (de 8,06 m à 4,96 m ; caméra de 8,9 / −0,66 / 2,0 à 8,9 / 2,44 / 2,0) |
| Angle et cadrage | face ; le panneau seul au centre (texte à 52 % de la hauteur), la place vide du lampadaire à gauche ; demi-largeur visible à l'arrivée ≈ 0,29 × 5,36 = 1,55 m à la profondeur du panneau |
| Ce qu'on voit | premier plan : panneau_eclairage et txt_eclairage, la place vide du lampadaire (absent) ; fond : ciel, bout de tribune au début du plan |
| Ce qu'on ne doit pas voir | Kevin ; le lampadaire (disparu) ; le but droit |
| Personnages | aucun à l'image |
| Transition vers le plan suivant | coupe |
| Actions | aucune (la caméra avance dès la première image) |
| Texte à l'écran | rien (texte du décor : txt_eclairage) |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_eclairage |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — il ne reste que le panneau « ÉCLAIRAGE » et un emplacement vide |

### p09 → beat b09 (20,5 → 22,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Gazon entretenu brin par brin. » |
| Caméra | survol · cible visee_k3 · distance 6,5 m · hauteur 0,8 m · focale 35 mm (arc de −110° à −70°, rayon de 6,5 à 6,2 m, caméra vers z = 1,4, entre y = −6,8 et −6,1) |
| Angle et cadrage | de face à trois quarts en glissant (Kevin à 0° puis 40° de l'axe) ; plan moyen, Kevin en pied sur le tiers droit, la touffe sur le tiers gauche ; demi-largeur visible ≈ 0,29 × 6,55 = 1,9 m ; écart Kevin-touffe 1,6 m < 0,25 × 6,5 = 1,63 m |
| Ce qu'on voit | premier plan : kevin_k3_montre, bras tendu vers la touffe ; touffe_herbe (`touffe_normale`), seule tache verte ; terre ocre, ligne médiane ; fond : tribune vide au loin |
| Ce qu'on ne doit pas voir | panneau_pelouse (invisible) ; aucune autre végétation verte ; barriere_4 (derrière la caméra) |
| Personnages | kevin_k3_montre : montre du bras ; trois quarts gauche |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre kevin_k2_montre, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k3_montre, `debut` 0,0, durée 0,05 s → fin à 0,05 s (marge 1,95 s) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — Kevin montre le sol : il n'y a qu'une touffe |

### p10 → beat b10 (22,5 → 25,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | muet |
| Caméra | plan_fixe · cible visee_pelouse · distance 5,7 m · hauteur 0 m · focale 35 mm (caméra en −1,05 / −5,45 / 0,5, au ras du sol) |
| Angle et cadrage | face, caméra basse (0,5 m) ; la touffe en bas à droite (82 à 88 % de la largeur, 55 à 58 % de la hauteur), le panneau au centre gauche (texte à 28 % de la hauteur) ; demi-largeur visible ≈ 0,29 × 5,7 = 1,65 m (cadre de x = −2,7 à 0,6) |
| Ce qu'on voit | premier plan : touffe_herbe, qui gonfle (`touffe_fiere`) ; panneau_pelouse et txt_pelouse « PELOUSE » ; terre ocre ; fond : tribune vide au loin, gravat_1 |
| Ce qu'on ne doit pas voir | Kevin (à K3, hors cadre à droite, marge 0,3 m avec les bras ouverts) ; aucune autre végétation verte |
| Personnages | aucun à l'image ; kevin_k3_parle est en place hors cadre (réserve b : « parle avec gestes » dès 22,5 s) |
| Transition vers le plan suivant | coupe |
| Actions | 1. apparaitre panneau_pelouse, `debut` 0,0, durée 0,6 s → fin à 0,6 s. 2. grandir touffe_herbe, `debut` 1,0, durée 0,5 s, params facteur 1,3 → fin à 1,5 s (marge 1,0 s). 3 et 4, hors champ : disparaitre kevin_k3_montre et apparaitre kevin_k3_parle, `debut` 0,0, durée 0,05 s (4 actions : voir « Vérifications ») |
| Texte à l'écran | rien (texte du décor : txt_pelouse) |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_pelouse |
| Effets sonores | pops automatiques à 0,0 s (panneau) et 1,0 s (touffe) ; bonus à `debut` 1,0 (beat muet : calé sur un instant) |
| Musique | très légère, seule |
| Lisible sans le son | oui — un panneau « PELOUSE » pour une seule touffe, qui gonfle de fierté |

### p11 → beat b11 (25,0 → 27,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Pièce unique, rien que ça. » |
| Caméra | plongee · cible visee_touffe · distance 8 m · hauteur 8,5 m · focale 35 mm (caméra de 0 / −2 / 14,45 à 0 / −1,2 / 10,2) |
| Angle et cadrage | plongée presque verticale (à 8° de la verticale), le haut de l'image vers +y ; la touffe au centre (2,6 puis 3,7 % de la hauteur) ; demi-largeur visible de 0,29 × 14,6 = 4,2 m à 0,29 × 10,3 = 3,0 m ; hauteur visible de 14,8 m à 10,4 m |
| Ce qu'on voit | premier plan : touffe_herbe (`touffe_fiere`), seule tache verte sur la terre ocre, ligne médiane et rond central à moitié effacés ; kevin_k3_parle vu d'en haut à droite ; panneau_pelouse vu par la tranche à gauche ; au début du plan : flaque hors cadre, barrières tout en bas, premier rang de la tribune tout en haut |
| Ce qu'on ne doit pas voir | aucune autre végétation verte ; les buts |
| Personnages | kevin_k3_parle : parle avec gestes ; face caméra (tourné vers le bas de l'image) |
| Transition vers le plan suivant | coupe |
| Actions | aucune (la caméra descend dès la première image) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix |
| Lisible sans le son | oui — vue d'en haut, un point vert au milieu d'un rectangle de terre |

### p12 → beat b12 (27,0 → 30,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Et là, mes supporters déchaînés. » |
| Caméra | orbite · cible visee_k0 · distance 5 m · hauteur 0,8 m · focale 35 mm (arc de −120° à −60°, caméra de −2,5 / 1,7 / 1,4 à 2,5 / 1,7 / 1,4, soit 1,7 m/s) |
| Angle et cadrage | de profil trois quarts à face (Kevin à 65° puis 5° de l'axe : il finit face caméra sur « déchaînés ») ; plan moyen, Kevin en pied au centre ; demi-largeur visible ≈ 0,29 × 5,06 = 1,47 m |
| Ce qu'on voit | premier plan : kevin_k0_montre, bras tendu en arrière vers les gradins ; fond : tribune_supporters juste derrière lui (`tribune_vide`), ciel |
| Ce qu'on ne doit pas voir | panneau_question (invisible) ; panneau_pelouse et touffe (derrière la caméra) ; panneau_vip, panneau_eclairage |
| Personnages | kevin_k0_montre : montre du bras ; trois quarts droite |
| Transition vers le plan suivant | coupe ; la voix et la musique s'arrêtent à 30,0 s |
| Actions | 1. disparaitre kevin_k3_parle, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k0_montre, `debut` 0,0, durée 0,05 s → fin à 0,05 s (marge 2,95 s) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte |
| Effets sonores | aucun |
| Musique | très légère sous la voix, coupée net à 30,0 s |
| Lisible sans le son | oui — grand geste fier vers la tribune, puis le plan suivant la montre vide |

### p13 → beat b13 (30,0 → 31,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | muet (silence voulu) |
| Caméra | plan_fixe · cible visee_tribune_d · distance 8 m · hauteur 1,0 m · focale 35 mm (caméra en 3,5 / 1 / 2,2) |
| Angle et cadrage | face ; la moitié droite de la tribune occupe toute la largeur, au centre de la hauteur (30 % de la hauteur) ; demi-largeur visible ≈ 0,29 × 8,06 = 2,3 m ; cadre de x = 1,6 à 5,4 au premier rang, de 0,45 à 6,55 au dernier |
| Ce qu'on voit | premier plan : gravat_2 au sol ; centre : 3 rangs de tribune_supporters, 0 supporter ; fond : arbre_mort qui dépasse derrière, ciel |
| Ce qu'on ne doit pas voir | Kevin (à K0, hors cadre à gauche : le cadre commence à x = 2,05 à sa profondeur) ; panneau_eclairage (à droite, hors cadre) ; aucun personnage dans les gradins |
| Personnages | aucun à l'image (kevin_k0_montre reste à K0, hors cadre) |
| Transition vers le plan suivant | coupe ; la musique et la voix reprennent à 31,5 s |
| Actions | aucune (plan fixe sans mouvement : arrêt sur le vide, voulu par le scénario) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes (0), cpt_cagnotte (0) |
| Effets sonores | aucun ; le souffle automatique de coupe (vers 29,9 s) est à supprimer ici (brique manquante) |
| Musique | coupée de 30,0 à 31,5 s |
| Lisible sans le son | oui — des gradins vides, rien ne bouge |

### p14 → beat b14 (31,5 → 35,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « On répare quoi d'abord ? Dis-le en commentaire. » |
| Caméra | dolly_avant · cible panneau_question · distance 11 m · hauteur 1,0 m · focale 35 mm (de 14,3 m à 8,8 m ; caméra de 3 / −8,3 / 2,35 à 3 / −2,8 / 2,05) |
| Angle et cadrage | face ; au départ, Kevin sur le tiers gauche et le panneau au centre ; à l'arrivée, le panneau seul au centre (47 % de la largeur), Kevin sorti par la gauche ; demi-largeur visible de 0,29 × 14,35 = 4,2 m à 0,29 × 8,84 = 2,6 m |
| Ce qu'on voit | premier plan : kevin_k0_parle face caméra (au début), puis panneau_question et txt_question « ON RÉPARE QUOI ? » ; fond : moitié droite de la tribune vide, gravat_2 derrière le panneau |
| Ce qu'on ne doit pas voir | panneau_pelouse et touffe (hors cadre à gauche) ; panneau_eclairage (hors cadre à droite) ; à l'arrivée, Kevin (hors cadre : une main peut passer au bord gauche, à vérifier à l'animatique) |
| Personnages | kevin_k0_parle : parle avec gestes ; face caméra |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre kevin_k0_montre, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k0_parle, `debut` 0,0, durée 0,05 s. 3. apparaitre panneau_question sur « répare » (≈ 0,5 s), durée 0,6 s → fin à 1,1 s (marge 2,9 s) |
| Texte à l'écran | rien (texte du décor : txt_question) |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_question |
| Effets sonores | pop automatique sur « répare » (panneau) |
| Musique | reprend à 31,5 s, très légère sous la voix |
| Lisible sans le son | oui — un panneau « ON RÉPARE QUOI ? » surgit à côté de Kevin, la caméra s'en approche |

### p15 → beat b15 (35,5 → 36,5 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | muet |
| Caméra | plan_fixe · cible visee_tribune · distance 21 m · hauteur 4 m · focale 35 mm (caméra en 0 / −12 / 5,2, distance réelle 21,4 m) |
| Angle et cadrage | face, plongée de 11° ; plan large ; Kevin au centre (9 % de la hauteur), devant la tribune entière ; demi-largeur visible ≈ 0,29 × 21,4 = 6,2 m à la tribune, 5,3 m à Kevin |
| Ce qu'on voit | premier plan : terre ocre, touffe_herbe et panneau_pelouse à gauche ; centre : kevin_k0_immobile qui se tourne vers la tribune puis revient, panneau_question à sa droite ; fond : toute la tribune vide, gravats, arbre_mort |
| Ce qu'on ne doit pas voir | panneau_vip et panneau_eclairage (hors cadre) ; les barrières (sous le cadre) ; pas le bord du sol |
| Personnages | kevin_k0_immobile : immobile, tourne sur lui-même ; face caméra → dos (0,5 s environ, muet) → face caméra |
| Transition vers le plan suivant | coupe |
| Actions | 1. disparaitre kevin_k0_parle, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k0_immobile, `debut` 0,0, durée 0,05 s. 3. tourner kevin_k0_immobile, `debut` 0,0, durée 0,5 s, params degres 180 → fin à 0,5 s (marge 0,5 s). 4. tourner kevin_k0_immobile, `debut` 0,5, durée 0,5 s, params degres −180 → fin à 1,0 s (marge 0 s : beat de 1,0 s imposé) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte, txt_question, txt_pelouse |
| Effets sonores | aucun |
| Musique | très légère, seule |
| Lisible sans le son | oui — Kevin regarde la tribune vide, puis revient comme si de rien n'était |

### p16 → beat b16 (36,5 → 40,0 s)

| Champ | Valeur |
|---|---|
| Voix (rappel) | « Bienvenue au plus grand stade du monde. » |
| Caméra | plan_fixe · cible visee_k0 · distance 4,5 m · hauteur 0,6 m · focale 35 mm (caméra en 0 / 1,5 / 1,2 : **exactement la caméra de p01**) |
| Angle et cadrage | identique à p01 : face, plan moyen, Kevin en pied au centre, bras ouverts entièrement dans le cadre ; demi-largeur visible ≈ 1,32 m (réserve a) |
| Ce qu'on voit | premier plan : kevin_k0_parle, bras grands ouverts sur la dernière image ; fond : centre de la tribune vide, ciel |
| Ce qu'on ne doit pas voir | panneau_question (il commence à x = 1,8, le cadre s'arrête à 1,3 ; réponse 2 de Lucas) ; les 3 autres panneaux, la touffe gonflée (derrière la caméra), l'emplacement du lampadaire, les gravats |
| Personnages | kevin_k0_parle : parle avec gestes, pose bras ouverts à 40,0 s ; face caméra |
| Transition vers le plan suivant | boucle : coupe vers p01, image identique sauf le sous-titre |
| Actions | 1. disparaitre kevin_k0_immobile, `debut` 0,0, durée 0,05 s. 2. apparaitre kevin_k0_parle, `debut` 0,0, durée 0,05 s → fin à 0,05 s (marge 3,45 s) |
| Texte à l'écran | rien |
| Habillage | cpt_abonnes, cpt_cagnotte (identiques à 0,0 s) |
| Effets sonores | aucun |
| Musique | très légère sous la voix ; s'enchaîne de 40,0 s à 0,0 s |
| Lisible sans le son | oui — même image qu'au début : la visite recommence |

## Habillage (v1.1 ; exigences Production, § 6)

Valeurs tirées de `episodes/serie/etat.json` (0 abonné, 0 €, aucun choix en cours). Premier épisode : tout est à zéro et ne change pas.

### Compteurs (champ v1.1 `habillage.hud`, type `compteur`)

Les deux compteurs s'empilent sur l'ancre `haut_gauche`. Le beat b01 n'a pas de mot déclencheur : affichage à `debut` 0,0.

| id | Ressource (icône) | Valeur de départ (état de la série) | Valeur d'arrivée (s'il défile) | Permanent / ponctuel | Premier beat (mot déclencheur) | Dernier beat (`jusqu_au_beat`) | Position (`position`) |
|---|---|---|---|---|---|---|---|
| cpt_abonnes | abonnés (icône `habitant`, faute d'icône « abonné ») | 0 | rien (fixe) | permanent (décision n° 9) | b01 (`debut` 0,0) | b16 | haut_gauche |
| cpt_cagnotte | cagnotte en € (icône `piece`, faute de symbole €) | 0 | rien (fixe) | permanent (décision n° 9) | b01 (`debut` 0,0) | b16 | haut_gauche |

Aucun autre compteur. Le nombre de supporters (0) n'est pas affiché : la tribune vide le montre.

### Gains (champ v1.1 `habillage.hud`, type `gain`)

Aucun : aucun ajout dans cet épisode (0 like, 0 abonné).

| id | Texte | Icône | Plan et mot déclencheur | Endroit de l'image (au-dessus de quel objet) |
|---|---|---|---|---|
| — | — | — | — | — |

### Cartes de choix finales

Aucune : `choix_en_cours` est vide et le scénario validé remplace les cartes par le panneau « ON RÉPARE QUOI ? » (réponse 2 de Lucas à la v1 ; les 2 cartes arrivent à l'épisode 2).

| id | Objet montré (rendu 3D sur fond blanc) | Libellé | Coût (€) | Pictogramme | Phrase qui les fait apparaître (plan) |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

### Textes dans le décor (champ v1.1 `habillage.textes_3d`)

Chaque texte a son panneau pour parent : il surgit avec lui. Tailles calculées pour tenir dans le fond du panneau (2,22 m), avec une largeur de lettre estimée à 0,55 × la taille (ordre de grandeur tiré du test « Six Seven » ; à vérifier avec la police réelle).

| id | Texte (1 à 40 car.) | Support (`parent`) | Position x / y / z (m, repère du parent) | Rotation z (°) | Taille (m) | Épaisseur (m) | Rôle | Visible au début |
|---|---|---|---|---|---|---|---|---|
| txt_vip | TRIBUNE VIP | panneau_vip | 0 / −0,07 / 1,85 | 0 | 0,32 | 0,02 | tissu | non (suit le parent, 10,5 s) |
| txt_eclairage | ÉCLAIRAGE | panneau_eclairage | 0 / −0,07 / 1,85 | 0 | 0,38 | 0,02 | tissu | non (suit le parent, 16,0 s) |
| txt_pelouse | PELOUSE | panneau_pelouse | 0 / −0,07 / 1,85 | 0 | 0,44 | 0,02 | tissu | non (suit le parent, 22,5 s) |
| txt_question | ON RÉPARE QUOI ? | panneau_question | 0 / −0,07 / 1,85 | 0 | 0,22 | 0,02 | tissu | non (suit le parent, 32,0 s) |

Lettres noires demandées par le scénario : le rôle `tissu` (celui du test « Six Seven ») doit être noir dans le pack « stade ». Les 4 panneaux restent visibles jusqu'à 40,0 s.

### Bandeau titre

Aucun (réponse 2 de Lucas à la v1 : la question est un panneau 3D).

| Texte | Plan(s) |
|---|---|
| — | — |

## Sons (registre `engine/assets/sons/registre.json`)

### Ambiances (une par lieu)

| Lieu | Ambiance (id, catégorie `ambiance`) | Plans |
|---|---|---|
| Stade du FC Miteux | ambiance_vent (vent seul : stade désert) | p01 à p16, y compris pendant le silence de p13 (`habillage.ambiance` ne sait pas se couper sur un beat) |

### Effets (chacun calé sur un mot)

| Plan | Mot déclencheur | Son (id du registre) | Pourquoi |
|---|---|---|---|
| p05 | « places » | grincement | la caisse en bois se met à vaciller |
| p07 | beat muet : `debut` 2,5 | erreur | le lampadaire disparaît |
| p10 | beat muet : `debut` 1,0 | bonus | la touffe gonfle de fierté |

Sons automatiques du moteur (`engine/pipeline/effets_sonores.py`), sans rien écrire : un pop à chaque `apparaitre` et `grandir`, un souffle à chaque coupe. Ces trois effets sont des ajouts de ma part (le scénario n'en liste aucun) : à garder ou à retirer par Lucas.

## Vérifications chiffrées

| Règle | Valeur mesurée | Résultat |
|---|---|---|
| Un plan par beat, mêmes durées que les beats | 16 plans pour 16 beats ; 3,0 + 2,6 + 2,4 + 2,5 + 3,5 + 2,0 + 2,9 + 1,6 + 2,0 + 2,5 + 2,0 + 3,0 + 1,5 + 4,0 + 1,0 + 3,5 = 40,0 s | OK |
| Jamais plus de 2 mouvements identiques d'affilée | plus longue suite : 2 (`revelation` p02-p03 ; `plan_fixe` p15-p16). En lecture en boucle, p15-p16-p01 font 3 `plan_fixe` : imposé par la réserve (a) (même image fixe à 0,0 et 40,0 s) et par le plan de 1,0 s | OK |
| Plans serrés (≤ 12 m) majoritaires ; larges (≥ 20 m) présents et alternés | distance réelle à l'arrivée : 14 serrés (p11 et p14 partent de 14,6 et 14,3 m), 0 moyen, 2 larges (p03 : 24,2 m ; p15 : 21,4 m), jamais voisins | OK |
| Chaque action finit ≥ 1 s avant la fin de son beat | hors règle : b05 `cycle` de la caisse (marge 0 s, mouvement continu jusqu'à la coupe) ; b07 `disparaitre` du lampadaire (marge 0 s, instant fixé par le beat validé, résultat visible 1,6 s en p08) ; b15 les 2 `tourner` (marges 0,5 et 0 s, beat de 1,0 s) | ÉCART justifié |
| Chaque mot déclencheur figure dans la voix du beat | « places » (b05, 3e mot sur 8) ; « répare » (b14, 2e mot sur 7) ; toutes les autres actions sont calées par `debut` (beats muets ou échanges sur une coupe) | OK |
| Au plus 3 actions par beat (hors disparitions groupées justifiées) | b10 : 4, dont 2 hors champ (échange de Kevin, réserve b) ; b15 : 4, dont 2 pour l'échange sur la coupe ; tous les autres ≤ 3 | ÉCART justifié |
| Sujet dans le cadre (demi-largeur ≈ 0,29 × distance) | tenu dans les 16 plans (valeurs dans chaque tableau). Marges inférieures à 0,4 m, à vérifier à l'animatique : p07 (poteau du but droit, 0,2 m), p09 (barrière à 0,2 m derrière la caméra, écart Kevin-touffe 1,60 pour 1,63 m), p10 (bras de Kevin, 0,3 m), p14 (main gauche de Kevin à 0,25 m du bord au départ) | OK |
| Crédibilité physique (appuis, rien ne traverse, effets attendus) | tout repose au sol ; aucun objet n'en traverse un autre (positions vérifiées avec les dimensions des primitives et du registre). Non tenu : 2 barrières couchées et drapeau penché, impossibles avec `rotation_z` seul | ÉCART |
| Uniquement le vocabulaire v1.1 (dont `descente`) ; textes 3D au format du schéma | 6 types d'action sur 7 utilisés (`apparaitre`, `disparaitre`, `grandir`, `tourner`, `cycle` ; pas de `deplacer` ni de `transformer`), 7 mouvements sur 8 ; 4 textes 3D de 7 à 16 caractères | OK |
| Abonnés et cagnotte affichés du premier au dernier beat ; autres compteurs permanents ou ponctuels justifiés par l'histoire ; `position` écrite (jamais `bas_droite`) ; valeurs de l'état de la série | 2 compteurs permanents b01 → b16, `haut_gauche`, valeurs 0 et 0 de `etat.json` ; aucun autre compteur | OK |
| Un gain à chaque ajout ; cartes de choix finales avec leur coût | aucun ajout, donc aucun gain ; aucune carte (`choix_en_cours` vide, décision de Lucas) | OK (sans objet) |
| Sons : identifiants du registre seulement, une ambiance par lieu, chaque effet sur un mot de la voix | 4 identifiants, tous dans le registre (ambiance_vent, grincement, erreur, bonus) ; 1 ambiance pour 1 lieu ; 1 effet sur un mot, 2 effets calés sur un instant dans des beats muets | ÉCART justifié |

Correction d'une ligne ci-dessus : 5 types d'action sont utilisés, pas 6 (`apparaitre`, `disparaitre`, `grandir`, `tourner`, `cycle`).

## Écarts au scénario

1. **p01 et p16, cadrage** : le scénario demande un plan rapproché (3,5 m) ; le découpage fait un plan moyen en pied (4,5 m). Demandé par Lucas (réserve a).
2. **p01 à p03, recul** : le scénario fait reculer la caméra de 2,0 à 8,0 s en un seul mouvement. Ici p01 reste fixe jusqu'à 3,0 s (la boucle exige la même image fixe en p01 et p16), puis deux `revelation` s'enchaînent dans l'axe (4,5 → 10 → 22 m). Un léger ralentissement est possible à 5,6 s, à la jonction.
3. **p03, « tout le stade apparaît »** : impossible en 9:16 à 22 m (7 m visibles de chaque côté pour un terrain de 20 m). Les 2 buts, la caisse et les tonneaux sont hors cadre. **Les 2 buts ne sont visibles dans aucun plan**, comme le drapeau, les tonneaux, 2 gravats et 1 flaque.
4. **Panneaux** : le scénario décrit 1,2 × 0,6 m sur un poteau de 1,5 m ; la primitive `panneau_entree` fait 2,4 × 0,9 m sur deux poteaux (haut à 2,3 m). Gardée à l'échelle 1 : à 0,5, le texte « ON RÉPARE QUOI ? » serait illisible sur un téléphone.
5. **Positions déplacées** (la caméra reste toujours côté −y, et les panneaux sont deux fois plus larges) : lampadaire 8 / 7 → 7,5 / 7 ; panneau « ÉCLAIRAGE » 9 / 7,8 → 9,1 / 7,8 ; K2 6 / 5 → 5,5 / 5 (le but droit et le panneau sortent ainsi des cadres de p07, p13 et p14) ; panneau « PELOUSE » −1,5 / 0,5 → −1,4 / 0,5 ; **K3 −1,5 / −1 → 1,6 / −0,6** (Kevin passe à droite de la touffe, sinon il masque le panneau en p10) ; panneau « ON RÉPARE QUOI ? » 2 / 6 → 3 / 6 (hors du cadre de p16, plus large depuis la réserve a).
6. **Déplacements de Kevin** : le scénario prévoit 4 `deplacer` de 0,1 s sur les coupes ; le découpage utilise 7 éléments Kevin échangés sur les coupes (aucun glissement visible, méthode déjà décrite par la Production).
7. **« Montre du bras » en deux sens** : le scénario compte une attitude ; viser la gauche de l'image (p04, p09) puis la droite (p06, p12) sans tourner le dos demande l'attitude et son miroir. Le bras est le même partout : en p09 il ne vise pas précisément le sol.
8. **p07 et p08** : un seul plan de 16,0 à 20,5 s dans le scénario ; deux plans ici (un par beat), raccordés dans l'axe.
9. **p10** : « plan rapproché au ras du sol sur la touffe » ; ici caméra à 0,5 m du sol mais à 5,7 m, pour tenir le panneau de 2,4 m dans le cadre : la touffe fait 5 % de la hauteur de l'image (6,6 % une fois gonflée). Durée du `grandir` : 0,6 → 0,5 s, pour tenir la marge de 1 s.
10. **p11** : « tout le terrain » ; ici 8,4 × 14,8 m puis 6 × 10,4 m, pour que la touffe reste lisible (2,6 puis 3,7 % de la hauteur).
11. **p13** : le scénario place la caméra de trois quarts (7 / 4 / 2) ; impossible avec le vocabulaire. Plan de face sur la moitié droite de la tribune, Kevin hors champ.
12. **p14** : deux plans dans le scénario (plan moyen, puis plan rapproché sur le panneau à 33,5 s) ; un seul `dolly_avant` ici, qui part de Kevin et du panneau et finit sur le panneau seul.
13. **p15** : « plan large de trois quarts » ; plan large de face.
14. **p16** : le scénario montre le panneau à droite de Kevin de 36,5 à 39,0 s, puis resserre ; ici un seul plan identique à p01 pendant 3,5 s, panneau hors cadre du début à la fin.
15. **Réserve (b)** : Kevin passe en « parle avec gestes » à 22,5 s comme demandé, mais il est hors cadre en p10 ; on ne le voit dans cette attitude qu'en p11 (25,0 à 27,0 s).
16. **Sol et ciel** : terre sèche (réponse 3 de Lucas) au lieu de « terre battue » ; asphalte gris sur tout le sol autour du terrain, pas seulement sur 3 m ; les 3 nuages ne sont pas modélisables (voir « Briques manquantes »).
17. **Barrières couchées et drapeau penché** : non réalisables ; repli écrit dans le tableau des éléments.
18. **Caisse** : la primitive fait 0,8 m ; échelle 0,75 pour les 0,6 m du scénario.
19. **Sons** : ambiance de vent et 3 effets ajoutés ; le vent continue pendant le silence de 30,0 à 31,5 s.

## Briques manquantes

- **Vue de côté** : aucune caméra ne peut se placer ailleurs que du côté −y de sa cible (p13 et p15 du scénario).
- **Coucher ou pencher un objet** : le contrat n'a que `rotation_z` (2 barrières couchées, drapeau penché à 20°).
- **Terrain avec lignes peintes** : aucune primitive ; à construire ou à sourcer.
- **Nuages** : aucune primitive ni asset.
- **Silence** : le souffle automatique de chaque coupe et le pop automatique de chaque `apparaitre` ne se désactivent pas (souffle vers 29,9 s et 31,4 s, pops à chaque échange de Kevin) ; l'ambiance ne se coupe pas sur un beat ; `audio` ne sait ni couper la musique de 30,0 à 31,5 s ni la faire boucler.
- **Musique** : aucune piste rythmée dans le registre (seulement des jingles).
- **Icônes** : pas d'icône « abonné » ni de symbole « € » dans le schéma (seulement `piece` et `habitant`) ; le compteur affiche un entier, sans « € ».
- **Calage de l'animation** : rien ne garantit que « parle avec gestes » tombe sur la pose bras ouverts à 0,0 et 40,0 s ; aucun paramètre « boucle ».
- **Attitude en miroir** d'un personnage (« montre du bras » vers la droite).
- **Apparition sans rebond ni son** pour échanger un personnage sur une coupe.

## Non porté par le contrat v1.0 (v1.1)

- Angle et cadrage, place du sujet dans l'image : tous les plans.
- Transitions (coupe, raccord dans l'axe p01-p02, p02-p03, p07-p08 ; boucle p16-p01).
- « Ce qu'on voit » et « ce qu'on ne doit pas voir » : tous les plans.
- Attitudes de Kevin (portées par le choix de l'entrée du registre, pas par un champ) et états nommés des objets.
- Intonation, mots appuyés, découpage des sous-titres, créneaux sans sous-titres, « Bienvenue » affiché dès 0,0 s et « du monde » jusqu'à 40,0 s (fichier de beats).
- Sons et ambiance : clés `sons` et `ambiance` de `<fiche>.habillage.json`, hors contrat.
- Musique : niveau sous la voix, coupure de 30,0 à 31,5 s, enchaînement de 40,0 à 0,0 s.
- Boucle : p16 identique à p01 (consigne seulement).
- Mots-clés de sourcing, styles et éléments indispensables.
- Versions de secours de la voix (fichier de beats, réserve d) : si elles servent, les mots déclencheurs « places » et « répare » y figurent toujours.

## À confirmer par Guillaume

1. **Assets à sourcer** : Kevin (4 entrées : `kevin_parle`, `kevin_montre_g`, `kevin_montre_d`, `kevin_immobile`), terrain, but (× 2), tribune, touffe ; pack de DA « stade » à créer (asphalte gris, terre ocre, lettres noires pour le rôle `tissu`, ciel bleu, soleil haut à gauche).
2. **Primitives au premier plan** : `panneau_entree` (4 plans) et `caisse` (p05) sont faites en code. La caisse mérite un modèle sourcé (mots-clés dans le tableau).
3. **Hypothèses sur Kevin** : 1,75 m, envergure 1,8 m, face à −y à `rotation_z` 0, sens des rotations. Si le modèle est plus large, p01 et p16 passent à 5 m (et le panneau « ON RÉPARE QUOI ? » recule à x = 3,2).
4. **Échanges de Kevin sur les coupes** : `apparaitre` en 0,05 s déclenche un rebond et un pop ; un élément déjà disparu peut-il réapparaître (kevin_k0_parle en b14 et b16) ? Sinon, dupliquer l'élément.
5. **Jamais testé** : `tourner` sur un personnage animé (b15), `degres` négatif (sinon 180 puis 180, même orientation finale), `hauteur` 0 (p07, p08, p10), calage de la pose bras ouverts, attitude en miroir.
6. **Sol** : terre sèche, lignes sommaires, une seule touffe verte (réponse 3 de Lucas). Si le sol change, b09 et b11 sont à revoir (fichier de beats).
7. **Largeur des textes** des panneaux avec la police réelle (tailles 0,22 à 0,44 m).
8. **Marges de cadre faibles** : p07, p09, p10, p14 (voir « Vérifications »).
9. **Éléments jamais à l'image** : buts, drapeau, tonneaux, gravat_3, gravat_4, flaque_2. Le stade est récurrent : les garder ou les repousser à un épisode qui les montre.
10. **Avertissements attendus à la validation** : beat de 1,0 s (b15), actions qui finissent avec leur beat (b05, b07, b15).
11. **Musique** : piste à choisir ; coupure et boucle à faire au montage.
12. **Temps de rendu** : faible (aucune foule, une trentaine d'objets).

## Liste de contrôle de la Production (§ 9 de engine/docs/exigences-production-pour-storytelling.md)

- [x] Chaque lieu a sa description visuelle, son ambiance et son style (§ 1).
- [x] Chaque plan liste ce qu'on voit et ce qu'on ne voit pas (§ 2).
- [x] Au moins 5 détails d'ambiance par lieu (§ 3).
- [x] Chaque personnage a son apparence, son attitude et son orientation par plan ; jamais de dos quand il parle (§ 4).
- [x] Chaque élément « à sourcer » a ses mots-clés anglais (§ 5).
- [x] Compteurs, gains, cartes, textes du décor et bandeaux sont décrits selon le § 6 ; abonnés et cagnotte permanents (décision n° 9 du 2026-11-16), autres compteurs permanents ou ponctuels selon l'histoire ; chaque compteur a sa `position` (jamais en bas à droite).
- [x] Voix : nombres en lettres, phrases d'au moins 3 mots (§ 7).
- [x] Les briques manquantes sont listées.

Précisions sur les cases cochées :

- § 3 : 7 détails d'ambiance sont décrits (barrières, gravats, flaques, tonneaux, drapeau, planches, arbre mort), mais seuls 5 passent à l'image (barrières, gravats, 1 flaque, planches, arbre mort).
- § 4 : Kevin est de dos 0,5 s environ en p15, muet ; il ne parle jamais de dos.
- § 6 : aucun gain, aucune carte, aucun bandeau dans cet épisode, par décision de Lucas et d'après `etat.json`.
- § 7 : vérifié par le fichier de beats (aucun nombre dit ; phrase la plus courte : 3 mots).

---

Rôle de ce document : document de travail interne du pôle Storytelling, destiné à `prod-realisateur` pour écrire la fiche épisode. C'est une proposition tant que Lucas et Guillaume ne l'ont pas validée ; rien n'est publié. Il n'a aucune valeur juridique.
