# Ce que la Production attend d'un scénario et d'un découpage

> Statut : **proposition de Guillaume** (rédigée par son Claude le 2026-11-16), à intégrer par Lucas dans les agents `story-*`. Ce document est écrit par la Production et ne remplace pas le contrat (`contracts/`) : il dit ce dont la Production a besoin pour faire une vidéo de qualité **sans rien inventer** à la place du Storytelling.

Jusqu'ici, Guillaume donnait lui-même ces précisions à son Claude (test « Six Seven », 2026-11-16). Désormais, ce sont les agents de Lucas qui les fournissent, dans le scénario (`story-scenario`) puis le découpage (`story-decoupage`). La Production s'en sert pour la **plaquette Figma**, que Guillaume valide avant tout rendu (`engine/docs/plaquette-figma.md`).

## 1. Une description visuelle riche (pas seulement des positions)

Pour chaque lieu et chaque élément important, en plus de l'id, de l'asset et de la position :

- **Ce que c'est et à quoi ça ressemble** : type, époque, taille réelle, couleurs dominantes, matériaux (« mairie de village française, 2 étages, façade crème, toit de tuiles rouges »).
- **Son état** : neuf, abîmé, en ruine, en chantier, réparé à moitié… Un même objet qui change d'état dans l'épisode est écrit comme **deux états nommés** (ex. `mairie_ruine` puis `mairie_reparee_1`) : la Production sait faire une ruine puis la même ruine partiellement réparée.
- **L'ambiance** : moment de la journée, météo, ciel, sol (herbe, pavés, sable…), lumière (« fin de matinée, ciel bleu avec nuages, herbe verte »).
- **Le style attendu** : low-poly coloré (par défaut, cohérent avec les modèles Quaternius déjà intégrés) ou réaliste. Ne pas mélanger les deux sans le dire.

## 2. La liste des éléments présents à l'image, plan par plan

Dans le découpage, chaque plan liste **ce qu'on voit** (au premier plan, au fond) et **ce qu'on ne doit pas voir** (« rien d'autre de la ville n'est visible »). C'est ce qui permet à la Production de placer la caméra, de vérifier qu'aucun objet n'en cache un autre et de remplir la plaquette.

## 3. Des détails qui rendent la scène vivante

Au moins **5 détails d'ambiance** par lieu, chiffrés comme le reste : bancs, lampadaires, tonneaux, buissons, fleurs, gravats, oiseaux, flaques, panneaux… Ils viennent de la bible ou sont marqués « nouveau, à valider ». La Production peut en ajouter, mais seulement en le signalant dans la plaquette.

## 4. Les personnages

Pour chaque personnage : apparence (âge, tenue, couleurs, accessoires), **attitude par plan** (immobile, parle, travaille, salue, marche, saute) et **orientation**. Règle de Guillaume : un personnage qui s'adresse au public est **face caméra ou de trois quarts, jamais de dos**, même s'il travaille. Un personnage qui change d'attitude d'un plan à l'autre est permis : la Production l'échange sur une coupe.

## 5. Les modèles 3D à trouver

Pour chaque élément « à sourcer » : **2 ou 3 mots-clés en anglais** (« town hall », « old fountain », « businessman suit »), le style attendu (§ 1) et ce qui est indispensable (« le maire porte un costume et une chemise »). La Production cherche sur 7 sources (Poly Haven, Poly Pizza, 3DAssets.dev, Icosa, ambientCG, Sketchfab, 3DTexel) et présente 3 candidats dans la plaquette.

## 6. L'habillage (ce qui s'affiche par-dessus l'image 3D)

La Production sait désormais faire, au style du kit Figma « Outils d'affichage » (https://www.figma.com/design/4jgvjoxBzwQDQfoXgwW0Fs) :

| Élément | Ce qu'il faut écrire dans le découpage |
|---|---|
| **Compteur** (pièces, habitants…) | la ressource, la valeur de départ, la valeur d'arrivée s'il défile, le **mot de la voix** qui le fait apparaître et le plan après lequel il disparaît. **Permanent ou ponctuel selon ce que demande l'histoire** : un compteur permanent reste affiché tout l'épisode (écrire « permanent ») ; un compteur ponctuel apparaît quand on en parle et disparaît ensuite (écrire le plan après lequel il disparaît). Sans précision, la Production le traite comme ponctuel. **Position** : là où le découpage le demande (en haut à gauche, au centre, à droite, en bas…) ; par défaut en haut à gauche. |
| **Gain** (« +10 » qui monte, son de pièce) | le texte (« +10 »), l'icône, le mot déclencheur, l'endroit de l'image (au-dessus de quel objet). |
| **Cartes de choix** (vote de fin) | le nombre de cartes, pour chacune l'objet montré (rendu 3D sur fond blanc), le libellé (« LA FONTAINE »), un pictogramme éventuel, et la phrase qui les fait apparaître. |
| **Texte dans le décor** | le texte exact et son support (« panneau d'entrée de ville : SIX SEVEN »). |
| **Bandeau titre** | le texte (« À VOUS DE CHOISIR ! »). |

Texte à l'écran et compteurs peuvent être affichés ensemble : le texte se place automatiquement sous les compteurs du haut de l'image. Éviter le bas à droite (boutons d'Instagram). Les valeurs viennent de l'état de la série (`episodes/serie/etat.json`, chiffres fournis par un humain) ; à défaut, elles sont marquées fictives. Tout texte affiché ou lu (voix, textes 3D, HUD, pseudos) passe le filtre de modération de la Production (`engine/pipeline/textes_ecran.py`) : un texte refusé arrête la production (code 8), et chaque pseudo est relu par Guillaume dans la plaquette. Un élément d'habillage qui n'est pas dans ce tableau est écrit tel quel et listé comme **brique manquante**.

## 7. La voix

- Les nombres sont **écrits en lettres** dans la voix (« mille pièces ») et **montrés à l'écran** par un compteur ; jamais de chiffres dans le texte lu.
- Pas de phrase de moins de 3 mots (la synthèse vocale les rend mal).
- Le mot qui déclenche une action est dans la **première moitié** de la phrase quand c'est possible.
- La voix de la série est choisie par un humain ; pour le village, Guillaume a choisi la voix n° 12 de l'audition.

## 8. La caméra et le rythme

Plans de 1,5 à 3 s, surtout rapprochés ; une coupe dès que l'information change. Un mouvement qui n'existe pas dans le vocabulaire (ex. zoom continu depuis le ciel jusqu'au personnage) est écrit tel quel et listé comme brique manquante : la Production propose alors une solution dans la plaquette (aujourd'hui : plongée puis coupe).

## 9. Liste de contrôle avant de transmettre à la Production

- [ ] Chaque lieu a sa description visuelle, son ambiance et son style (§ 1).
- [ ] Chaque plan liste ce qu'on voit et ce qu'on ne voit pas (§ 2).
- [ ] Au moins 5 détails d'ambiance par lieu (§ 3).
- [ ] Chaque personnage a son apparence, son attitude et son orientation par plan ; jamais de dos quand il parle (§ 4).
- [ ] Chaque élément « à sourcer » a ses mots-clés anglais (§ 5).
- [ ] Compteurs, gains, cartes, textes du décor et bandeaux sont décrits selon le § 6.
- [ ] Voix : nombres en lettres, phrases d'au moins 3 mots (§ 7).
- [ ] Les briques manquantes sont listées.

## Exemple de référence

Le test « Six Seven » contient tout cela, côté Production : `episodes/tests/six_seven_001.json` (fiche) et `episodes/tests/six_seven_001.habillage.json` (panneau, cartes, compteurs, gain). La vidéo est dans le Drive de Guillaume.
