# La visite guidée

- Statut : proposé par l'agent (à valider par Lucas)
- Idée source : [La visite guidée](../idees-retenues.md) — entrée du 2026-11-16
- Épisode : `lancement-du-club`, premier épisode de La Revanche du Miteux
- Durée visée : 40 s

## Logline

En tongs et maillot taché, Kevin fait visiter son stade en ruine comme un agent immobilier de luxe : la « TRIBUNE VIP » est une caisse, l'« ÉCLAIRAGE » rétrécit puis disparaît, la « PELOUSE » est une touffe d'herbe, la tribune des supporters est vide, et il demande aux abonnés ce qu'on répare en premier.

## Décor et éléments nécessaires

Repère : x vers la droite de l'image d'ouverture, y vers le fond, z vers le haut, en mètres ; origine au centre du terrain. La caméra d'ouverture regarde vers +y : Kevin est face à elle, la tribune des supporters est derrière lui. Positions approximatives (à 0,5 m près), affinées par `story-decoupage`.

| Élément | id proposé | Asset (vocabulaire) | Quantité | Position approx. x / y / z (m) | Visible au début | Origine |
|---|---|---|---|---|---|---|
| Kevin | `kevin` | à sourcer (modèle animé CC0 : attitudes « immobile » et « parle avec gestes ») | 1 | départ K0 : 0 / 5 / 0, face caméra ; stations K1 -6 / 5 / 0, K2 6 / 5 / 0, K3 -1,5 / -1 / 0 | oui | bible, section 5 |
| Terrain (sol du stade) | `terrain` | sol du décor (terre battue, lignes peintes) ; à construire par la Production | 1 | centre 0 / 0 / 0, 20 × 12 m | oui | bible, section 5 (le stade) |
| But gauche | `but_gauche` | à sourcer | 1 | -10 / 0 / 0 | oui | bible, section 5 (poteaux rouillés) |
| But droit | `but_droit` | à sourcer | 1 | 10 / 0 / 0 | oui | bible, section 5 (poteaux rouillés) |
| Barrières cassées (bord avant du terrain) | `barrieres` | bibliotheque:barriere | 6 (dont 2 renversées) | ligne y = -7, x = -7,5 / -4,5 / -1,5 / 1,5 / 4,5 / 7,5 ; renversées : x = -4,5 et 4,5 | oui | bible, section 5 (barrières cassées) |
| Tribune des supporters (vide) | `tribune_supporters` | à sourcer | 1 | 0 / 9 / 0 (12 m de long, de x = -6 à 6) | oui | nouveau, à valider (introduit par l'idée source) |
| Caisse « tribune VIP » | `caisse_vip` | primitif:caisse | 1 | -8 / 7 / 0 | oui | nouveau, à valider (introduit par l'idée source) |
| Panneau « TRIBUNE VIP » | `panneau_vip` | primitif:panneau_entree + texte 3D « TRIBUNE VIP » (parent `panneau_vip`) | 1 | -8 / 7,8 / 0 | non | nouveau, à valider (introduit par l'idée source) |
| Lampadaire « éclairage » | `lampadaire_eclairage` | bibliotheque:lampadaire_rue | 1 | 8 / 7 / 0 | oui | nouveau, à valider (introduit par l'idée source) |
| Panneau « ÉCLAIRAGE » | `panneau_eclairage` | primitif:panneau_entree + texte 3D « ÉCLAIRAGE » (parent `panneau_eclairage`) | 1 | 9 / 7,8 / 0 | non | nouveau, à valider (introduit par l'idée source) |
| Touffe d'herbe « pelouse » | `touffe_herbe` | à sourcer | 1 | 0 / 0 / 0 | oui | nouveau, à valider (introduit par l'idée source) |
| Panneau « PELOUSE » | `panneau_pelouse` | primitif:panneau_entree + texte 3D « PELOUSE » (parent `panneau_pelouse`) | 1 | 0 / 1 / 0 | non | nouveau, à valider (introduit par l'idée source) |

Aucune foule : la tribune a 0 supporter, conformément à `episodes/serie/etat.json` (`supporters` : 0).

### Lieux : ambiance et style

Un seul lieu.

| Paramètre | Valeur |
|---|---|
| Lieu | Le stade de Kevin (`terrain`, décor principal) |
| Style | low-poly coloré, couleurs vives (bible, section 2) ; un seul style |
| Moment de la journée | début d'après-midi, vers 14 h (nouveau, à valider) |
| Météo et ciel | beau temps, ciel bleu vif, 3 nuages blancs (nouveau, à valider) |
| Sol | terre battue ocre sur 20 × 12 m ; lignes blanches sommaires, effacées sur environ la moitié de leur longueur ; asphalte gris autour du terrain, sur 3 m de large ; 1 seule touffe verte, au centre (nouveau, à valider) |
| Lumière | soleil haut à gauche de l'image d'ouverture, ombres courtes, teinte chaude (nouveau, à valider) |

Détails d'ambiance :

| Détail | Quantité | Position approx. x / y / z (m) | Origine |
|---|---|---|---|
| Barrières cassées (voir tableau des éléments), 2 sur 6 couchées au sol | 6 | ligne y = -7, x de -7,5 à 7,5 | bible, section 5 |
| Gravats (bibliotheque:rochers, gris béton) | 4 | -3 / 7 / 0 ; 2 / 7 / 0 ; 5 / -6,5 / 0 ; -9 / -5 / 0 | nouveau, à valider |
| Flaques d'eau (primitif:flaque) | 2 | -4 / -2 / 0 ; 6 / -3 / 0 | nouveau, à valider |
| Tonneaux rouillés (bibliotheque:tonneau) | 2 | 11 / -4 / 0 ; 11 / -3 / 0 | nouveau, à valider |
| Drapeau de coin penché à 20° (bibliotheque:drapeau) | 1 | -10 / -6 / 0 | nouveau, à valider |
| Tas de planches (bibliotheque:planches) | 1 | -10 / 7 / 0 | nouveau, à valider |
| Arbre mort derrière la tribune (bibliotheque:arbre_mort) | 1 | -12 / 11 / 0 | nouveau, à valider |

Aucune autre végétation verte : la touffe d'herbe doit rester la seule tache verte du décor, sinon le gag de la « PELOUSE » ne se lit plus.

### Description visuelle des éléments importants

| id | Ce que c'est (type, époque) | Taille réelle | Couleurs dominantes | Matériaux | État(s) nommé(s) |
|---|---|---|---|---|---|
| `terrain` | petit terrain de foot de quartier, années 1970, abandonné | 20 × 12 m | ocre, blanc cassé (lignes) | terre battue, peinture | `terrain_ruine` (0,0-40,0 s) |
| `but_gauche`, `but_droit` | cages de foot à 7 | 5 × 2 × 1,5 m | orange-brun (rouille), filet blanc grisé | métal rouillé, filet déchiré (filet du but droit absent) | `but_rouille` (0,0-40,0 s) |
| `barrieres` | barrières de bord de terrain | 2 × 1 m chacune | gris, taches de rouille | métal (à confirmer selon le modèle du registre) | `barriere_cassee` (0,0-40,0 s) |
| `tribune_supporters` | gradins de quartier en béton, 3 rangs | 12 × 3 × 2,5 m | gris béton, peinture bleue écaillée sur les rebords | béton, peinture | `tribune_vide` (0,0-40,0 s), 0 supporter |
| `caisse_vip` | caisse en bois ordinaire | 0,6 × 0,6 × 0,6 m | bois clair | planches, 1 planche fendue | `caisse_vip_bancale` (0,0-40,0 s) |
| `lampadaire_eclairage` | lampadaire de rue, ampoule éteinte | 4 m de haut | gris métal | métal | `lampadaire_debout` (0,0-17,0 s) → `lampadaire_retreci` (17,0-18,5 s, 30 % de sa taille) → absent (18,5-40,0 s) |
| `touffe_herbe` | touffe d'herbe isolée | 0,3 m de haut, 0,3 m de large | vert vif | herbe | `touffe_normale` (0,0-23,5 s) → `touffe_fiere` (23,5-40,0 s, × 1,3) |
| `panneau_vip`, `panneau_eclairage`, `panneau_pelouse` | panneaux sur poteau, façon panneau d'entrée de ville | panneau 1,2 × 0,6 m sur poteau de 1,5 m | fond blanc, bord rouge, lettres noires en majuscules | métal peint | `panneau_cache` → `panneau_visible` (VIP à 10,5 s, ÉCLAIRAGE à 16,0 s, PELOUSE à 22,5 s) |

### Personnages

| id | Âge | Tenue | Couleurs | Accessoires | Origine |
|---|---|---|---|---|---|
| `kevin` | la vingtaine (nouveau, à valider) | palier « Départ » (0 abonné) : maillot de foot deux tailles trop grand avec une tache de ketchup, short trop court, chaussettes dépareillées, tongs, coupe au bol ratée, casquette à l'envers, sourire niais | maillot jaune vif, tache rouge ; short bleu ; 1 chaussette rouge et 1 verte ; tongs bleues ; casquette rouge (couleurs : nouveau, à valider) | casquette à l'envers | bible, section 5 (tenue et palier) ; couleurs et âge : nouveau, à valider |

Kevin parle lui-même, voix n° 12 (bible, section 9), **sans synchronisation des lèvres**, avec des gestes de bras et de tête (précision de Lucas, 2026-11-16). Attitudes : « parle avec gestes » quand il parle, « immobile » dans les silences. Il est face caméra ou de trois quarts chaque fois qu'il parle ; il n'est de dos que pendant 1,0 s, muet (temps 5). Palier : 0 abonné et 0 € (`etat.json`), donc tenue de départ sur tout l'épisode, aucun changement de palier.

## Déroulé en 5 temps

| Temps | Secondes (début-fin) | Ce qu'on voit | Ce qui change (élément, quantité, action du vocabulaire) |
|---|---|---|---|
| 1. Accroche | 0,0-3,0 | Gros plan de Kevin face caméra (environ 2 m, à hauteur de visage), sourire niais, bras grands ouverts à 0,3 s ; on voit le maillot taché, la coupe au bol et la casquette à l'envers. Compteurs « 0 » abonné et « 0 € » en haut de l'image dès 0,0 s. | `kevin` à K0, attitude « parle avec gestes ». Aucune autre action : l'accroche est le contraste entre la tenue, la phrase en sous-titres et les compteurs à zéro. |
| 2. Mise en situation | 3,0-8,0 | La caméra recule et s'élève depuis Kevin (mouvement `revelation`, de 2 m à environ 20 m de distance, 10 m de haut) et dévoile tout le stade : terre battue, 2 buts rouillés, 6 barrières dont 2 couchées, tribune vide. Kevin, petit au centre, garde les bras ouverts. | Caméra `revelation` sur `kevin`, 3,0-8,0 s. Aucun objet ne bouge. |
| 3 a. Escalade : « TRIBUNE VIP » | 8,0-14,0 | 8,0-10,5 : Kevin de trois quarts à K1, bras tendu vers la gauche de l'image, air fier. 10,5-14,0 : coupe sur la caisse seule ; le panneau « TRIBUNE VIP » surgit derrière elle ; la caisse vacille. | `deplacer` `kevin` K0 → K1 sur la coupe à 8,0 s (0,1 s, masqué par la coupe). `apparaitre` `panneau_vip` à 10,5 s (0,6 s). `cycle` `osciller` sur `caisse_vip`, amplitude 0,5, de 11,5 à 14,0 s. |
| 3 b. Escalade : « ÉCLAIRAGE » | 14,0-20,5 | 14,0-16,0 : Kevin de trois quarts à K2, bras tendu vers la droite. 16,0-20,5 : coupe sur le lampadaire ; le panneau « ÉCLAIRAGE » surgit ; le lampadaire rétrécit à 30 % puis disparaît ; il ne reste que le panneau. | `deplacer` `kevin` K1 → K2 sur la coupe à 14,0 s (0,1 s). `apparaitre` `panneau_eclairage` à 16,0 s (0,6 s). `grandir` `lampadaire_eclairage`, facteur 0,3, à 17,0 s (0,8 s). `disparaitre` `lampadaire_eclairage` à 18,5 s (0,4 s). Panneau seul à l'image de 18,9 à 20,5 s. |
| 3 c. Escalade : « PELOUSE » | 20,5-27,0 | 20,5-22,5 : Kevin de trois quarts à K3, les deux bras vers le sol devant lui. 22,5-25,0 : plan rapproché au ras du sol sur la touffe ; le panneau « PELOUSE » surgit derrière elle ; la touffe gonfle de fierté. 25,0-27,0 : vue presque verticale de tout le terrain : une seule tache verte au centre de 240 m² de terre ocre. | `deplacer` `kevin` K2 → K3 sur la coupe à 20,5 s (0,1 s). `apparaitre` `panneau_pelouse` à 22,5 s (0,6 s). `grandir` `touffe_herbe`, facteur 1,3, à 23,5 s (0,6 s). Caméra `plongee` sur `terrain`, 25,0-27,0 s. |
| 4. Chute | 27,0-35,5 | 27,0-30,0 : Kevin de trois quarts à K0, la tribune derrière lui, pouce tendu par-dessus l'épaule vers les gradins. 30,0-31,5 : plan fixe de face sur la tribune : 3 rangs, 0 supporter ; voix et musique coupées. 31,5-35,5 : gros plan de Kevin face caméra, même cadrage qu'à 0,0 s ; il pose la question, mains ouvertes vers la caméra. Bandeau « ON RÉPARE QUOI EN 1ER ? » au centre de l'image de 32,0 à 35,5 s. | `deplacer` `kevin` K3 → K0 sur la coupe à 27,0 s (0,1 s). 30,0-31,5 : aucune action (silence). Bandeau : 32,0-35,5 s. |
| 5. Boucle | 35,5-40,0 | Même plan que 31,5 s. 35,5-36,0 : Kevin se tourne vers la tribune (de dos, muet). 36,0-36,5 : il la regarde, immobile. 36,5-37,0 : il se retourne vers la caméra. 37,0-40,0 : bras grands ouverts, il répète la phrase d'ouverture. La dernière image est la première : même cadrage, même position, même tenue. | `tourner` `kevin`, 180°, à 35,5 s (0,5 s). `tourner` `kevin`, 180°, à 36,5 s (0,5 s). Attitude « parle avec gestes » de 37,0 à 40,0 s. |

Somme : 3,0 + 5,0 + 6,0 + 6,5 + 6,5 + 8,5 + 4,5 = 40,0 s.

## Intentions de voix off

Voix : Kevin lui-même, voix n° 12. Les nombres sont dits en lettres.

| Temps | Intention (pas de phrase finale) | Mots estimés |
|---|---|---|
| 1. Accroche | Kevin, très sûr de lui, souhaite la bienvenue « dans le plus grand stade du monde » (formule donnée par l'idée retenue) ; la phrase commence à 0,2 s et peut finir vers 3,4 s, pendant le début du recul | 8 |
| 2. Mise en situation | Il se présente comme le président, l'entraîneur et le seul joueur du club, et annonce la visite du propriétaire | 9 |
| 3 a. « TRIBUNE VIP » | Ton d'agent immobilier de luxe : il vante un espace VIP exclusif ; à la coupe, constat fier que c'est une caisse | 11 |
| 3 b. « ÉCLAIRAGE » | Il vante un éclairage de niveau professionnel ; pendant que le lampadaire disparaît, il hésite puis enchaîne comme si de rien n'était | 11 |
| 3 c. « PELOUSE » | Il vante une pelouse entretenue à la main, « brin par brin » ; sur la vue d'en haut, il assume la touffe unique | 11 |
| 4. Chute | 27,0-30,0 : il présente la tribune de ses supporters ; 30,0-31,5 : silence ; 31,5-35,5 : il avoue qu'il manque un peu de tout, demande aux abonnés ce qu'on répare en premier et les invite à répondre en commentaire | 18 |
| 5. Boucle | Après 1,5 s muette, il répète la formule d'ouverture avec le même aplomb | 8 |
| **Total** | | **76 mots, soit environ 30,4 s de voix** (9,6 s sans voix : silences, gags et coupes) |

## Habillage

| Élément | Où et quand | Contenu |
|---|---|---|
| Sous-titres | tout l'épisode, tiers bas de l'image, zone sûre 9:16 | 1 à 3 mots à la fois, police grasse libre, **sans mot surligné** (bible, section 9) ; aucun sous-titre de 30,0 à 31,5 s ni de 35,5 à 37,0 s (pas de voix) |
| Éléments d'interface | 32,0-35,5 s, centre de l'image (le haut est pris par les compteurs) | bandeau « ON RÉPARE QUOI EN 1ER ? » ; aucune carte de choix dans cet épisode (précision de Lucas : les 2 cartes viendront à l'épisode 2) |
| Textes dans le décor | sur les 3 panneaux, dès leur apparition | « TRIBUNE VIP » (10,5 s), « ÉCLAIRAGE » (16,0 s), « PELOUSE » (22,5 s) ; fond blanc, bord rouge, lettres noires |
| Compteurs | permanents de 0,0 à 40,0 s, en haut de l'image (bible, section 9) | abonnés : 0 ; cagnotte : 0 € ; valeurs de `episodes/serie/etat.json`, fixes sur tout l'épisode ; aucune animation de gain (aucun ajout) |
| Musique | 0,0-30,0 s, puis 31,5-40,0 s | rythmée, libre de droits, très légère sous la voix (bible, section 9) ; coupée de 30,0 à 31,5 s sur la tribune vide ; doit pouvoir s'enchaîner de 40,0 s à 0,0 s pour la relecture en boucle |

Aucun pseudo d'abonné n'est affiché dans cet épisode.

## Ce que l'audience peut influencer

Les abonnés répondent en commentaire à la question de Kevin : qu'est-ce qu'on répare en premier dans le stade ? Les 2 propositions les plus aimées deviendront les 2 choix de l'épisode 2, chacun avec son coût, payé avec la cagnotte du club. Comme dans la règle de la série, chaque abonné devient un supporter de plus dans la tribune et chaque like ajoute 1 € à la cagnotte : la tribune vide et les compteurs à zéro de cet épisode sont le point de départ que l'audience fera évoluer.

### Boucle d'audience

| Temps | Ce qu'on voit |
|---|---|
| 1. Résultat de la contribution précédente | aucun : premier épisode, aucune contribution antérieure |
| 2. Conséquence visible | l'état de départ : tribune à 0 supporter, compteurs à 0 abonné et 0 € |
| 3. Nouvelle question | « On répare quoi en premier ? », réponses en commentaire ; les auteurs des 2 commentaires retenus pourront être affichés à l'épisode 2 (pseudos : à valider par Lucas et Guillaume) |

## Contraintes de production

- **Premier stade jamais construit** : terrain, 2 buts et tribune n'existent dans aucun pack ni dans le registre. À sourcer (mots-clés proposés : « soccer goal », « football goal low poly » ; « bleachers », « concrete grandstand low poly » ; « grass tuft », « grass clump low poly »). Aucun pack de DA « stade » n'existe dans `engine/packs_da/` : à créer.
- **Kevin n'est pas sourcé** : modèle animé CC0 avec au moins 2 attitudes (« immobile », « parle avec gestes » de bras et de tête), échangées sur une coupe. La tenue de départ (tongs, coupe au bol, tache de ketchup, casquette à l'envers) demande des textures et de petits objets ajoutés au modèle. Mots-clés proposés : « cartoon man animated », « soccer fan low poly », « casual man rigged ».
- **Kevin parle sans synchronisation des lèvres** : la crédibilité repose sur les gestes ; un cadrage serré sur le visage pendant 8,5 s (31,5-40,0 s) rendra l'absence de mouvement des lèvres visible. `story-decoupage` peut couper ce plan, à condition de garder le cadrage d'ouverture pour la dernière seconde.
- **Déplacements de Kevin masqués par les coupes** : 4 `deplacer` de 0,1 s sur des coupes (8,0 ; 14,0 ; 20,5 ; 27,0 s). Un déplacement aussi court n'a jamais été testé ; sinon, il faut une animation de marche, absente aujourd'hui.
- **`tourner` sur un personnage animé** (35,5 et 36,5 s) : jamais testé sur un modèle qui joue une animation.
- **Boucle** : la dernière image (40,0 s) doit être identique à la première (0,0 s) : cadrage, position, rotation de Kevin, attitude. Paramètre « boucle » absent du contrat (v1.1, consigne seulement).
- **Compteurs permanents** : la bible (section 9, décision de Lucas et Guillaume) les veut affichés en permanence ; `engine/docs/exigences-production-pour-storytelling.md` § 6 dit l'inverse (« apparaît quand on en parle et disparaît ensuite ») et interdit un texte à l'écran en même temps qu'un compteur. Lucas a indiqué que la bible fait foi et que ce document sera mis à jour. Conséquence : le bandeau final est placé au centre de l'image, pas en haut ; la position dans l'image et le bandeau titre sont absents du contrat et de `habillage.json` (brique manquante, à confirmer par Guillaume).
- **Valeurs des compteurs** : ce sont les vraies valeurs de `etat.json` (0 et 0 €), et non des valeurs inventées, sur décision de Lucas (2026-11-16).
- **Textes 3D des panneaux** : champ `habillage.textes_3d` de la v1.1 ; tant que le moteur n'accepte pas la v1.1, la Production les lit dans `<fiche>.habillage.json` (déjà fait pour le test « Six Seven »).
- **Lisibilité de la touffe** dans la vue verticale (25,0-27,0 s) : 0,3 m sur 20 m de terrain ; elle doit rester visible sur un téléphone, sans autre élément vert.

Difficulté globale : moyenne (l'idée retenue disait « simple » ; le décor entier et le personnage restent à sourcer, et 3 gestes n'ont jamais été testés : téléportation sur coupe, `tourner` sur un personnage animé, boucle image par image).

## Vérification (grille de story-idees)

| Critère | Coché | Justification |
|---|---|---|
| 1. Accroche en 3 s | oui | Dès 0,0 s : Kevin en tongs et maillot taché, la promesse du « plus grand stade du monde » en sous-titres et les compteurs à zéro. |
| 2. Lisible sans le son | oui | Chaque gag se lit à l'image : un grand panneau au-dessus d'un objet minable, un lampadaire qui disparaît, une seule tache verte vue d'en haut, une tribune vide, puis un bandeau pour la question. |
| 3. Une seule idée forte | oui | Une visite de luxe d'un stade minable, sans intrigue secondaire. |
| 4. Chute | oui | La tribune vide, en silence, puis la question aux abonnés, qui donne une raison de revenir à l'épisode 2. |
| 5. Faisabilité | non | À confirmer par Guillaume : stade, tribune, buts, touffe et Kevin à sourcer ; téléportation sur coupe, `tourner` sur un personnage animé et compteurs permanents jamais réalisés. |
| 6. Boucle | oui | La dernière image reprend exactement la première, avec la même phrase. |
| 7. Partageable | oui | Le contraste entre le ton d'agent immobilier et le stade minable est un gag à envoyer à un ami qui joue dans un club nul ; la question invite à débattre en commentaire. |

Score : 6/7

## Questions pour Lucas

1. **Apparence de Kevin** : la bible donne sa tenue de départ mais ni son âge ni ses couleurs. J'ai proposé la vingtaine, maillot jaune vif à tache rouge, short bleu, chaussettes rouge et verte, casquette rouge (marqué « nouveau, à valider »). Tu valides, ou tu fixes d'autres couleurs ? Elles serviront à tous les épisodes.
2. **Bandeau de la question finale** : les compteurs permanents occupent le haut de l'image ; j'ai placé « ON RÉPARE QUOI EN 1ER ? » au centre, de 32,0 à 35,5 s. Tu le gardes ainsi, ou la question reste seulement dans les sous-titres (en attendant que Guillaume mette à jour son § 6) ?
3. **Nom du club** : Kevin dit « mon club » sans le nommer, car aucun nom n'est décidé dans la bible. Un nom est-il prévu avant le premier épisode, ou on le laisse sans nom ?
