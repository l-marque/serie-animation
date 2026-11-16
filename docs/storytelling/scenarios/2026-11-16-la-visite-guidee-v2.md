# La visite guidée (v2)

- Statut : proposé par l'agent (à valider par Lucas)
- Idée source : [La visite guidée](../idees-retenues.md) — entrée du 2026-11-16
- Épisode : `lancement-du-club`, premier épisode de La Revanche du Miteux
- Version précédente : [v1](2026-11-16-la-visite-guidee.md), conservée telle quelle
- Durée visée : 40 s

## Changements depuis la v1 (consigne de Lucas, 2026-11-16)

| Point | Correction |
|---|---|
| (a) Chute | 15 mots au plus dans les 2 créneaux de parole (6 + 9) ; silence de 1,5 s sur la tribune vide conservé (30,0-31,5 s). |
| (b) Boucle | Temps « il la regarde, immobile » supprimé : la phrase finale a 3,5 s (36,5-40,0 s) pour 8 mots (3,2 s). Kevin a les bras grands ouverts dès 0,0 s et à 40,0 s : même position, même orientation, même cadrage. |
| (c) Gestes | 3 attitudes seulement : « immobile », « parle avec gestes », « montre du bras ». Le pouce par-dessus l'épaule, les deux bras vers le sol et les mains ouvertes de la v1 sont supprimés. |
| (d) Phrases | Chaque intention de voix vise des phrases d'au moins 3 mots ; aucune hésitation sonore ni interjection isolée (l'hésitation de la v1 devient un silence de 2,4 s). |
| (e) Arbre mort | Déplacé derrière la tribune (4 / 12 / 0). |
| (f) Gros plans | Aucun plan serré fixe sur Kevin de plus de 2,0 s ; plans moyens et plans larges en alternance. Même à la jonction de la boucle (39,0-40,0 s puis 0,0-2,0 s), le plan serré dure 3,0 s au total. |
| (1) Kevin | La vingtaine ; maillot jaune vif à tache rouge, short bleu, 1 chaussette rouge et 1 chaussette blanche, tongs bleues, casquette rouge. |
| (2) Question finale | Plus de bandeau : panneau 3D « ON RÉPARE QUOI ? » qui surgit à côté de Kevin à 32,0 s, comme les 3 autres panneaux. |
| (3) Nom du club | « FC Miteux », dit par Kevin dans la mise en situation (3,5-8,0 s). |

Autres ajustements : Kevin démarre à 0 / 6 / 0 (et non 0 / 5 / 0) pour que la tribune soit juste derrière lui ; le panneau « PELOUSE » passe à côté de la touffe (-1,5 / 0,5 / 0) pour ne pas masquer Kevin dans les plans de face ; un gravat passe de 2 / 7 à 3,5 / 7 pour libérer la place du panneau final. La contradiction sur les compteurs relevée en v1 est levée : le § 6 de `engine/docs/exigences-production-pour-storytelling.md` accepte maintenant les compteurs permanents et un texte affiché en même temps.

## Logline

En tongs et maillot taché, Kevin, président et seul joueur du FC Miteux, fait visiter son stade en ruine comme un agent immobilier de luxe : la « TRIBUNE VIP » est une caisse, l'« ÉCLAIRAGE » rétrécit puis disparaît, la « PELOUSE » est une touffe d'herbe, la tribune des supporters est vide, et un panneau demande aux abonnés « ON RÉPARE QUOI ? ».

## Décor et éléments nécessaires

Repère : x vers la droite de l'image d'ouverture, y vers le fond, z vers le haut, en mètres ; origine au centre du terrain. La caméra d'ouverture regarde vers +y : Kevin est face à elle, la tribune des supporters est derrière lui. Positions approximatives (à 0,5 m près), affinées par `story-decoupage`.

| Élément | id proposé | Asset (vocabulaire) | Quantité | Position approx. x / y / z (m) | Visible au début | Origine |
|---|---|---|---|---|---|---|
| Kevin | `kevin` | à sourcer (modèle animé CC0, 3 attitudes : « immobile », « parle avec gestes », « montre du bras ») | 1 | départ K0 : 0 / 6 / 0, face caméra ; stations K1 -6 / 5 / 0, K2 6 / 5 / 0, K3 -1,5 / -1 / 0 | oui | bible, section 5 |
| Terrain (sol du stade) | `terrain` | sol du décor (terre battue, lignes peintes) ; à construire par la Production | 1 | centre 0 / 0 / 0, 20 × 12 m | oui | bible, section 5 (le stade) |
| But gauche | `but_gauche` | à sourcer | 1 | -10 / 0 / 0 | oui | bible, section 5 (poteaux rouillés) |
| But droit | `but_droit` | à sourcer | 1 | 10 / 0 / 0 | oui | bible, section 5 (poteaux rouillés) |
| Barrières cassées (bord avant du terrain) | `barrieres` | bibliotheque:barriere | 6 (dont 2 renversées) | ligne y = -7, x = -7,5 / -4,5 / -1,5 / 1,5 / 4,5 / 7,5 ; renversées : x = -4,5 et 4,5 | oui | bible, section 5 (barrières cassées) |
| Tribune des supporters (vide) | `tribune_supporters` | à sourcer | 1 | centre 0 / 9 / 0 ; 12 m de long (x = -6 à 6), 3 m de profondeur (y = 7,5 à 10,5) | oui | nouveau (introduit par l'idée source) ; élément récurrent sur décision de Lucas (2026-11-16), ajout à la bible section 5 en attente |
| Caisse « tribune VIP » | `caisse_vip` | primitif:caisse | 1 | -8 / 7 / 0 | oui | nouveau, propre à cet épisode (décision de Lucas, 2026-11-16 : non récurrent) |
| Panneau « TRIBUNE VIP » | `panneau_vip` | primitif:panneau_entree + texte 3D « TRIBUNE VIP » (parent `panneau_vip`) | 1 | -8 / 7,8 / 0 | non | nouveau, à valider (introduit par l'idée source) |
| Lampadaire « éclairage » | `lampadaire_eclairage` | bibliotheque:lampadaire_rue | 1 | 8 / 7 / 0 | oui | nouveau, propre à cet épisode (décision de Lucas, 2026-11-16 : non récurrent) |
| Panneau « ÉCLAIRAGE » | `panneau_eclairage` | primitif:panneau_entree + texte 3D « ÉCLAIRAGE » (parent `panneau_eclairage`) | 1 | 9 / 7,8 / 0 | non | nouveau, à valider (introduit par l'idée source) |
| Touffe d'herbe « pelouse » | `touffe_herbe` | à sourcer | 1 | 0 / 0 / 0 | oui | nouveau, à valider (introduit par l'idée source) |
| Panneau « PELOUSE » | `panneau_pelouse` | primitif:panneau_entree + texte 3D « PELOUSE » (parent `panneau_pelouse`) | 1 | -1,5 / 0,5 / 0, à gauche de la touffe | non | nouveau, à valider (introduit par l'idée source) |
| Panneau « ON RÉPARE QUOI ? » | `panneau_question` | primitif:panneau_entree + texte 3D « ON RÉPARE QUOI ? » (parent `panneau_question`) | 1 | 2 / 6 / 0, à 2 m à droite de Kevin dans l'image | non | nouveau, demandé par Lucas (2026-11-16, réponse 2), à valider |

Aucune foule : la tribune a 0 supporter, conformément à `episodes/serie/etat.json` (`supporters` : 0).

### Lieux : ambiance et style

Un seul lieu.

| Paramètre | Valeur |
|---|---|
| Lieu | Le stade du FC Miteux (`terrain`, décor principal) |
| Style | low-poly coloré, couleurs vives (bible, section 2) ; un seul style |
| Moment de la journée | début d'après-midi, vers 14 h (nouveau, à valider) |
| Météo et ciel | beau temps, ciel bleu vif, 3 nuages blancs (nouveau, à valider) |
| Sol | terre battue ocre sur 20 × 12 m ; lignes blanches sommaires, effacées sur environ la moitié de leur longueur ; asphalte gris autour du terrain, sur 3 m de large ; 1 seule touffe verte, au centre (nouveau, à valider) |
| Lumière | soleil haut à gauche de l'image d'ouverture, ombres courtes, teinte chaude (nouveau, à valider) |

Détails d'ambiance :

| Détail | Quantité | Position approx. x / y / z (m) | Origine |
|---|---|---|---|
| Barrières cassées (voir tableau des éléments), 2 sur 6 couchées au sol | 6 | ligne y = -7, x de -7,5 à 7,5 | bible, section 5 |
| Gravats (bibliotheque:rochers, gris béton) | 4 | -3 / 7 / 0 ; 3,5 / 7 / 0 ; 5 / -6,5 / 0 ; -9 / -5 / 0 | nouveau, à valider |
| Flaques d'eau (primitif:flaque) | 2 | -4 / -2 / 0 ; 6 / -3 / 0 | nouveau, à valider |
| Tonneaux rouillés (bibliotheque:tonneau) | 2 | 11 / -4 / 0 ; 11 / -3 / 0 | nouveau, à valider |
| Drapeau de coin penché à 20° (bibliotheque:drapeau) | 1 | -10 / -6 / 0 | nouveau, à valider |
| Tas de planches (bibliotheque:planches) | 1 | -10 / 7 / 0 | nouveau, à valider |
| Arbre mort derrière la tribune, sa cime dépasse d'environ 2,5 m au-dessus du 3e rang (bibliotheque:arbre_mort) | 1 | 4 / 12 / 0 | nouveau, à valider |

Aucune autre végétation verte : la touffe d'herbe doit rester la seule tache verte du décor, sinon le gag de la « PELOUSE » ne se lit plus (l'arbre mort est brun, sans feuilles).

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
| `panneau_vip`, `panneau_eclairage`, `panneau_pelouse`, `panneau_question` | panneaux sur poteau, façon panneau d'entrée de ville, tous identiques | panneau 1,2 × 0,6 m sur poteau de 1,5 m (haut du panneau à 2,1 m) | fond blanc, bord rouge, lettres noires en majuscules | métal peint | `panneau_cache` → `panneau_visible` (VIP à 10,5 s, ÉCLAIRAGE à 16,0 s, PELOUSE à 22,5 s, ON RÉPARE QUOI ? à 32,0 s) ; visibles ensuite jusqu'à 40,0 s |

### Personnages

| id | Âge | Tenue | Couleurs | Accessoires | Origine |
|---|---|---|---|---|---|
| `kevin` | la vingtaine | palier « Départ » (0 abonné) : maillot de foot deux tailles trop grand avec une tache de ketchup, short trop court, chaussettes dépareillées, tongs, coupe au bol ratée, casquette à l'envers, sourire niais | maillot jaune vif, tache rouge ; short bleu ; 1 chaussette rouge et 1 chaussette blanche ; tongs bleues ; casquette rouge | casquette à l'envers | tenue et palier : bible, section 5 ; âge et couleurs : décidés par Lucas pour toute la série (2026-11-16, réponse 1), ajout à la bible section 5 en attente |

Kevin est président, entraîneur et seul joueur du **FC Miteux** (nom décidé par Lucas, 2026-11-16, réponse 3 ; ajout à la bible section 5 en attente). Le nom est dit par Kevin, il n'est écrit sur aucun élément du décor dans cet épisode.

Kevin parle lui-même, voix n° 12 (bible, section 9), **sans synchronisation des lèvres**. Il a **3 attitudes**, échangées uniquement sur une coupe :

| Attitude | Quand | Orientation |
|---|---|---|
| « parle avec gestes » (bras et tête) ; sa pose de départ et de fin est **bras grands ouverts** | 0,0-8,0 s ; 31,5-33,5 s ; 36,5-40,0 s | face caméra |
| « montre du bras » (un bras tendu vers ce qu'il présente) | 8,0-10,5 s (vers la caisse, à gauche de l'image) ; 14,0-16,0 s (vers le lampadaire, à droite) ; 20,5-22,5 s (vers la touffe, au sol) ; 27,0-30,0 s (vers la tribune, derrière lui) | trois quarts face caméra |
| « immobile » | 35,5-36,5 s (les 2 rotations) ; quand il est hors champ | de trois quarts, de dos pendant 0,5 s environ, muet |

Il n'est jamais de dos quand il parle. Palier : 0 abonné et 0 € (`etat.json`), donc tenue de départ sur tout l'épisode, aucun changement de palier.

## Déroulé en 5 temps

Cadrages : plan rapproché = Kevin de la taille à la tête, bras ouverts compris, caméra à environ 3,5 m, à 1,6 m de haut ; plan moyen = Kevin en pied, caméra à environ 8 m ; plan large = Kevin, panneau et tribune, caméra à environ 12 m.

| Temps | Secondes (début-fin) | Ce qu'on voit | Ce qui change (élément, quantité, action du vocabulaire) |
|---|---|---|---|
| 1. Accroche | 0,0-3,0 | 0,0-2,0 : plan rapproché fixe de Kevin face caméra à K0, bras grands ouverts dès la première image, sourire niais ; maillot taché, coupe au bol, casquette à l'envers ; derrière lui, le centre de la tribune vide. Compteurs « 0 » abonné et « 0 € » en haut de l'image dès 0,0 s. 2,0-3,0 : la caméra commence à reculer et à monter. | `kevin` à K0, attitude « parle avec gestes » (pose bras ouverts à 0,0 s). Caméra `revelation` sur `kevin`, de 2,0 à 8,0 s. |
| 2. Mise en situation | 3,0-8,0 | Suite du recul (de 3,5 m à environ 20 m de distance, 10 m de haut) : tout le stade apparaît, terre battue, 2 buts rouillés, 6 barrières dont 2 couchées, tribune vide, arbre mort derrière elle. Kevin, petit au centre, continue de parler avec gestes. | Caméra `revelation` (suite). Aucun objet ne bouge. |
| 3 a. Escalade : « TRIBUNE VIP » | 8,0-14,0 | 8,0-10,5 : plan moyen, Kevin de trois quarts à K1, bras tendu vers la gauche de l'image, air fier. 10,5-14,0 : coupe sur la caisse seule ; le panneau « TRIBUNE VIP » surgit derrière elle ; la caisse vacille. | `deplacer` `kevin` K0 → K1 sur la coupe à 8,0 s (0,1 s, masqué par la coupe), attitude « montre du bras ». `apparaitre` `panneau_vip` à 10,5 s (0,6 s). `cycle` `osciller` sur `caisse_vip`, amplitude 0,5, de 11,5 à 14,0 s. |
| 3 b. Escalade : « ÉCLAIRAGE » | 14,0-20,5 | 14,0-16,0 : plan moyen, Kevin de trois quarts à K2, bras tendu vers la droite. 16,0-20,5 : coupe sur le lampadaire ; le panneau « ÉCLAIRAGE » surgit ; le lampadaire rétrécit à 30 % puis disparaît ; il ne reste que le panneau. | `deplacer` `kevin` K1 → K2 sur la coupe à 14,0 s (0,1 s), attitude « montre du bras ». `apparaitre` `panneau_eclairage` à 16,0 s (0,6 s). `grandir` `lampadaire_eclairage`, facteur 0,3, à 17,0 s (0,8 s). `disparaitre` `lampadaire_eclairage` à 18,5 s (0,4 s). Panneau seul à l'image de 18,9 à 20,5 s. |
| 3 c. Escalade : « PELOUSE » | 20,5-27,0 | 20,5-22,5 : plan moyen, Kevin de trois quarts à K3, un bras tendu vers le sol, vers la touffe. 22,5-25,0 : plan rapproché au ras du sol sur la touffe ; le panneau « PELOUSE » surgit à sa gauche ; la touffe gonfle de fierté. 25,0-27,0 : vue presque verticale de tout le terrain : une seule tache verte au centre de 240 m² de terre ocre. | `deplacer` `kevin` K2 → K3 sur la coupe à 20,5 s (0,1 s), attitude « montre du bras ». `apparaitre` `panneau_pelouse` à 22,5 s (0,6 s). `grandir` `touffe_herbe`, facteur 1,3, à 23,5 s (0,6 s). Caméra `plongee` sur `terrain`, 25,0-27,0 s. |
| 4. Chute | 27,0-35,5 | 27,0-30,0 : plan moyen, Kevin de trois quarts à K0, la tribune juste derrière lui, un bras tendu en arrière vers les gradins. 30,0-31,5 : plan fixe sur la tribune, caméra à environ 7 / 4 / 2 visant 0 / 9 / 1 : 3 rangs, 0 supporter, Kevin hors champ ; voix et musique coupées. 31,5-33,5 : plan moyen de face, Kevin à K0 parle avec gestes ; à 32,0 s, le panneau « ON RÉPARE QUOI ? » surgit à sa droite (dans l'image). 33,5-35,5 : plan rapproché sur le panneau « ON RÉPARE QUOI ? », Kevin hors champ, sa voix continue. | `deplacer` `kevin` K3 → K0 sur la coupe à 27,0 s (0,1 s), attitude « montre du bras », de trois quarts. 30,0-31,5 : aucune action (silence) ; `kevin` passe à « parle avec gestes », face caméra, sur la coupe à 31,5 s. `apparaitre` `panneau_question` à 32,0 s (0,6 s). |
| 5. Boucle | 35,5-40,0 | 35,5-36,5 : plan large de trois quarts : Kevin, le panneau « ON RÉPARE QUOI ? » et la tribune vide ; Kevin se tourne vers la tribune, puis revient face caméra, muet. 36,5-39,0 : plan moyen de face, Kevin bras ouverts, panneau à sa droite ; il répète la phrase d'ouverture. 39,0-40,0 : plan rapproché, cadrage identique à celui de 0,0 s ; Kevin termine la phrase, bras grands ouverts sur la dernière image. Hors champ : les 4 panneaux, l'emplacement du lampadaire et la touffe. | `kevin` passe à « immobile » sur la coupe à 35,5 s. `tourner` `kevin`, 180°, à 35,5 s (0,5 s). `tourner` `kevin`, 180°, à 36,0 s (0,5 s) : orientation finale = orientation de 0,0 s. Attitude « parle avec gestes » sur la coupe à 36,5 s, jusqu'à 40,0 s, pose bras ouverts à 40,0 s. |

Somme : 3,0 + 5,0 + 6,0 + 6,5 + 6,5 + 8,5 + 4,5 = 40,0 s.

Boucle, écarts tolérés entre 40,0 s et 0,0 s : le sous-titre seulement (« DU MONDE » à la fin, « BIENVENUE » au début). Tout le reste est identique : cadrage, position K0, orientation, pose bras ouverts, fond (centre de la tribune vide), compteurs 0 et 0 €. Le panneau « ON RÉPARE QUOI ? » (2 / 6 / 0), la touffe gonflée et l'emplacement vide du lampadaire sont hors du cadre du plan rapproché, qui couvre environ 1 m de part et d'autre de Kevin.

Plans serrés sur Kevin quand il parle : 0,0-2,0 s (2,0 s) et 39,0-40,0 s (1,0 s) ; en relecture en boucle, ils s'enchaînent sur 3,0 s au total. Aucun autre plan serré fixe sur son visage.

## Intentions de voix off

Voix : Kevin lui-même, voix n° 12. Les nombres sont dits en lettres. Chaque phrase compte au moins 3 mots ; aucune interjection isolée, aucune hésitation sonore.

| Temps | Intention (pas de phrase finale) | Mots estimés |
|---|---|---|
| 1. Accroche | Kevin, très sûr de lui, souhaite la bienvenue « dans le plus grand stade du monde » (formule donnée par l'idée retenue) ; créneau 0,2-3,4 s, la fin déborde de 0,4 s sur le début du recul | 8 |
| 2. Mise en situation | Il se présente comme le président, l'entraîneur et le seul joueur du FC Miteux, avec le même aplomb ; créneau 3,5-8,0 s | 11 |
| 3 a. « TRIBUNE VIP » | 8,1-10,1 s : ton d'agent immobilier de luxe, il ouvre la visite par l'espace VIP (5 mots) ; 10,7-13,9 s : sur la caisse, il en vante fièrement le standing (8 mots) | 13 |
| 3 b. « ÉCLAIRAGE » | 14,1-16,5 s : il vante un éclairage de niveau professionnel (6 mots) ; 16,5-18,9 s : silence pendant que le lampadaire rétrécit et disparaît ; 18,9-20,5 s : une phrase complète, comme si de rien n'était (4 mots) | 10 |
| 3 c. « PELOUSE » | 20,6-22,6 s : il vante une pelouse entretenue à la main, brin par brin (5 mots) ; 25,0-27,0 s : sur la vue d'en haut, il assume la touffe unique (5 mots) | 10 |
| 4. Chute | 27,2-29,6 s : il présente fièrement la tribune de ses supporters (6 mots) ; 30,0-31,5 s : silence ; 31,6-35,2 s : il demande ce qu'on répare en premier, puis invite les abonnés à répondre en commentaire, en 2 phrases d'au moins 3 mots (9 mots) | 15 |
| 5. Boucle | 35,5-36,5 s muet ; 36,6-39,8 s : il répète la formule d'ouverture avec le même aplomb | 8 |
| **Total** | | **75 mots, soit environ 30,0 s de voix** (10,0 s sans voix : silences, gags et coupes) |

## Habillage

| Élément | Où et quand | Contenu |
|---|---|---|
| Sous-titres | tout l'épisode, tiers bas de l'image, zone sûre 9:16, hors du coin bas droit | 1 à 3 mots à la fois, police grasse libre, **sans mot surligné** (bible, section 9) ; aucun sous-titre de 16,5 à 18,9 s, de 30,0 à 31,5 s ni de 35,5 à 36,5 s (pas de voix) |
| Éléments d'interface | aucun | pas de bandeau ni de carte de choix dans cet épisode (réponse 2 de Lucas : la question est un panneau 3D ; les 2 cartes viendront à l'épisode 2) |
| Textes dans le décor | sur les 4 panneaux, dès leur apparition | « TRIBUNE VIP » (10,5 s), « ÉCLAIRAGE » (16,0 s), « PELOUSE » (22,5 s), « ON RÉPARE QUOI ? » (32,0 s) ; fond blanc, bord rouge, lettres noires |
| Compteurs | permanents de 0,0 à 40,0 s, en haut de l'image (bible, section 9) | abonnés : 0 ; cagnotte : 0 € ; valeurs de `episodes/serie/etat.json`, fixes sur tout l'épisode ; aucune animation de gain (aucun ajout) |
| Musique | 0,0-30,0 s, puis 31,5-40,0 s | rythmée, libre de droits, très légère sous la voix (bible, section 9) ; coupée de 30,0 à 31,5 s sur la tribune vide ; doit pouvoir s'enchaîner de 40,0 s à 0,0 s pour la relecture en boucle |

Aucun pseudo d'abonné n'est affiché dans cet épisode.

## Ce que l'audience peut influencer

Les abonnés répondent en commentaire à la question du panneau et de Kevin : qu'est-ce qu'on répare en premier dans le stade ? Les 2 propositions les plus aimées deviendront les 2 choix de l'épisode 2, chacun avec son coût, payé avec la cagnotte du club. Comme dans la règle de la série, chaque abonné devient un supporter de plus dans la tribune et chaque like ajoute 1 € à la cagnotte : la tribune vide et les compteurs à zéro de cet épisode sont le point de départ que l'audience fera évoluer.

### Boucle d'audience

| Temps | Ce qu'on voit |
|---|---|
| 1. Résultat de la contribution précédente | aucun : premier épisode, aucune contribution antérieure |
| 2. Conséquence visible | l'état de départ : tribune à 0 supporter, compteurs à 0 abonné et 0 € |
| 3. Nouvelle question | panneau « ON RÉPARE QUOI ? », réponses en commentaire ; les auteurs des 2 commentaires retenus pourront être affichés à l'épisode 2 (pseudos : à valider par Lucas et Guillaume) |

## Contraintes de production

- **Premier stade jamais construit** : terrain, 2 buts et tribune n'existent dans aucun pack ni dans le registre. À sourcer (mots-clés proposés : « soccer goal », « football goal low poly » ; « bleachers », « concrete grandstand low poly » ; « grass tuft », « grass clump low poly »). Aucun pack de DA « stade » n'existe dans `engine/packs_da/` : à créer. Le stade et la tribune deviennent récurrents (décision de Lucas) : leur modèle servira à tous les épisodes.
- **Kevin n'est pas sourcé** : modèle animé CC0 avec exactement 3 attitudes (« immobile », « parle avec gestes » de bras et de tête, « montre du bras »), échangées sur une coupe. La tenue de départ (tongs, coupe au bol, tache de ketchup, casquette à l'envers, chaussettes rouge et blanche) demande des textures et de petits objets ajoutés au modèle. Mots-clés proposés : « cartoon man animated », « soccer fan low poly », « casual man rigged ».
- **Pose bras ouverts** : l'animation « parle avec gestes » doit commencer et finir sur la pose bras grands ouverts, et l'animation doit être calée pour que 0,0 s et 40,0 s tombent sur cette pose. Ce calage n'a jamais été fait.
- **Kevin parle sans synchronisation des lèvres** : la crédibilité repose sur les gestes ; les plans serrés sont limités à 2,0 s et 1,0 s (voir le déroulé), le reste est en plan moyen, en plan large ou sur un objet.
- **Déplacements de Kevin masqués par les coupes** : 4 `deplacer` de 0,1 s sur des coupes (8,0 ; 14,0 ; 20,5 ; 27,0 s). Un déplacement aussi court n'a jamais été testé ; sinon, il faut une animation de marche, absente aujourd'hui.
- **`tourner` sur un personnage animé** (35,5 et 36,0 s) : jamais testé sur un modèle qui joue une animation.
- **Plan de 1,0 s** (35,5-36,5 s) : plus court que les 1,5 à 3 s recommandés (`engine/docs/exigences-production-pour-storytelling.md`, § 8). Il porte une seule action (l'aller-retour vers la tribune) ; `story-decoupage` peut le rallonger en l'avançant à 35,0 s, sur le plan du panneau.
- **Boucle** : la dernière image (40,0 s) doit être identique à la première (0,0 s), sauf le sous-titre. Les éléments qui ont changé (4 panneaux, lampadaire, touffe) doivent rester hors du cadre du plan rapproché final. Paramètre « boucle » absent du contrat (v1.1, consigne seulement).
- **Compteurs permanents** : demandés par la bible (section 9) ; le § 6 des exigences de la Production les accepte désormais (« écrire permanent »), avec un texte affiché en même temps. Valeurs réelles de `etat.json` (0 et 0 €), sur décision de Lucas (2026-11-16).
- **Textes 3D des panneaux** (4) : champ `habillage.textes_3d` de la v1.1 ; tant que le moteur n'accepte pas la v1.1, la Production les lit dans `<fiche>.habillage.json` (déjà fait pour le test « Six Seven »). Les 4 textes passent le filtre de modération de la Production.
- **Lisibilité de la touffe** dans la vue verticale (25,0-27,0 s) : 0,3 m sur 20 m de terrain ; elle doit rester visible sur un téléphone, sans autre élément vert.

Difficulté globale : moyenne (l'idée retenue disait « simple » ; le décor entier et le personnage restent à sourcer, et 4 gestes n'ont jamais été testés : téléportation sur coupe, `tourner` sur un personnage animé, calage de la pose bras ouverts, boucle image par image).

## Vérification (grille de story-idees)

| Critère | Coché | Justification |
|---|---|---|
| 1. Accroche en 3 s | oui | Dès 0,0 s : Kevin bras ouverts en tongs et maillot taché, la promesse du « plus grand stade du monde » en sous-titres, les compteurs à zéro, puis le recul à 2,0 s. |
| 2. Lisible sans le son | oui | Chaque gag se lit à l'image : un grand panneau au-dessus d'un objet minable, un lampadaire qui disparaît, une seule tache verte vue d'en haut, une tribune vide, puis un panneau « ON RÉPARE QUOI ? ». |
| 3. Une seule idée forte | oui | Une visite de luxe d'un stade minable, sans intrigue secondaire ; le nom du club est dit dans la présentation, sans histoire autour. |
| 4. Chute | oui | La tribune vide, en silence, puis la question aux abonnés sur un panneau, qui donne une raison de revenir à l'épisode 2. |
| 5. Faisabilité | non | À confirmer par Guillaume : stade, tribune, buts, touffe et Kevin à sourcer ; téléportation sur coupe, `tourner` sur un personnage animé, calage de pose et compteurs permanents jamais réalisés. |
| 6. Boucle | oui | La dernière image reprend exactement la première (même cadrage, même pose bras ouverts), avec la même phrase. |
| 7. Partageable | oui | Le contraste entre le ton d'agent immobilier et le stade minable est un gag à envoyer à un ami qui joue dans un club nul ; la question invite à débattre en commentaire. |

Score : 6/7

## Questions pour Lucas

1. **Pose bras ouverts** : je l'ai traitée comme la pose de départ et de fin de l'attitude « parle avec gestes », et non comme une 4e attitude. Tu valides cette lecture ? Sinon, il faut une attitude « bras ouverts » de plus.
2. **Panneau « ON RÉPARE QUOI ? »** : il surgit à 32,0 s et reste dans le décor jusqu'à 40,0 s ; il est visible dans les plans moyen et large de la boucle, mais hors du cadre du plan rapproché final, pour que la dernière image reste identique à la première. Ça te va, ou préfères-tu qu'il disparaisse avant la phrase finale ?
3. **Sol du stade** : la bible (section 5) décrit une « pelouse aux lignes sommaires », alors que le scénario (v1 et v2) met de la terre battue avec une seule touffe, pour le gag de la « PELOUSE ». Comme le stade devient récurrent, je garde la terre battue pour toute la série, ou la description de la bible doit primer ?
