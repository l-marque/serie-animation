# Brief de référence : épisode « Jour 1 » (version blocs)

- Épisode : `jour-1`, vidéo finale `renders/jour-1/A_PUBLIER/jour-1_kevin_reel.mp4` (38,7 s, 1080 × 1920, 30 i/s).
- Rédigé le 2026-11-17 par le Claude de Guillaume, à la demande de Lucas et Guillaume, **à partir de la fiche et du minutage réellement utilisés** (`episodes/jour-1.json`, `episodes/jour-1.habillage.json`, `renders/jour-1/final/timeline.json`).
- Objet : montrer, sur un cas réel, ce que le pôle Storytelling (agents `story-*` de Lucas) doit transmettre à la Production pour obtenir cette vidéo sans aller-retour. Structure reprise de `docs/storytelling/gabarit-realisation.md` et de `engine/docs/exigences-production-pour-storytelling.md`.

---

## 1. Le prompt à transmettre à la Production

Bloc prêt à copier. C'est ce que le découpage de `story-decoupage` aurait dû contenir pour ce jour, en un seul message.

```text
ÉPISODE « JOUR 1 », série La Revanche du Miteux. Vidéo verticale 9:16, 1080 × 1920, 30 i/s, environ 38 s.

HISTOIRE EN UNE PHRASE
Kevin, un garçon de 12 ans qui fait un peu pitié, joue seul depuis un an et demi dans un stade de
quartier en ruine ; il rêve de devenir pro. Aujourd'hui commence l'aventure : avec 100 pièces et
l'aide des abonnés, il va réparer le stade. Fin : vote « pelouse ou filets ».

STYLE (charte de série, fixée par Guillaume)
- Personnages « en blocs » façon jeux à avatars (corps cubiques, plastique lisse, couleurs franches,
  visage simple : yeux, sourcils, bouche). Aucun élément repris d'un vrai jeu.
- Décor semi-réaliste épuré : le terrain boueux modélisé par Guillaume (pelouse rayée, plaques de boue,
  flaques), ruines et ville en blocs. Ciel bleu nuageux, soleil chaud de fin de matinée, rendu AgX.
- Pack de DA : stade_bloc.

PERSONNAGES
- Kevin : 1,45 m, t-shirt moutarde délavé trop grand avec une pièce cousue sur le ventre, short en jean,
  chaussette gauche tombée, vieilles baskets grises, cheveux bruns en bataille, mine triste
  (sourcils relevés au centre, bouche en accent circonflexe). Attitudes : court puis frappe (plan 1),
  parle face caméra, salue. Toujours face caméra ou de trois quarts quand il s'adresse au public.
- Abonnés : même bonhomme pour tous (1,75 m, jean, baskets blanches, cheveux courts, sourire) ;
  seul le t-shirt change de couleur (rouge, bleu, vert). Une étiquette « @ton_pseudo » au-dessus de
  chaque tête. Attitudes : immobile, saute (rouge), sautille (bleu, plan 8).

LIEU : STADE EN RUINE (terrain 105 × 68 m, cages en x = ±52,5)
- Tribune nord effondrée en partie : gradins en béton sombre, brèche avec éboulis, sièges rouges et
  bleus passés (certains arrachés ou renversés), toit en tôle troué, des tôles qui pendent.
- 4 pylônes d'éclairage rouillés, le nord-ouest penché ; projecteurs cassés.
- Tableau d'affichage décroché, penché, chiffres tombés (au nord-ouest, tourné vers le terrain).
- Abris de touche en béton, toit de travers.
- Cages rouillées SANS filet (restes de filet déchiré qui pendent) : c'est un des deux choix du vote.
- Lignes du terrain effacées par plaques ; barrières publicitaires délavées, certaines manquantes,
  penchées ou tombées.
- Débris : pneus, plots renversés, planches, herbes folles au pied des ruines.
- Autour : ville en blocs (boulevard, immeubles colorés à fenêtres, voitures, lampadaires, arbres).
- Ce qu'on ne voit pas : aucune personne en tribune, aucun objet neuf ou réparé.

VOIX (texte exact, une ligne = un plan ; nombres en lettres ; au moins 3 mots par phrase)
b01  Ça, c'est Kevin !
b02  Ça fait un an et demi...
b02b qu'il joue tout seul.
b03  Pourtant, depuis tout petit,
b03b il rêve de devenir pro !
b04  Et aujourd'hui, c'est le premier jour de l'aventure !
b05  Et Kevin n'a que cent pièces.
b06  Alors, on compte sur vous !
b07  Tu veux jouer avec Kevin ? Mets ton pseudo en commentaire !
b08  Les sélectionnés joueront dès la prochaine partie, avec leur pseudo affiché !
b09  Chaque like, c'est dix pièces en plus !
b10  Et mettez en commentaires vos suggestions d'amélioration !
b11  Avec nos cent pièces, on a deux choix.
b12  Entretenir la pelouse,
b13  ou réparer les cages avec des filets.
b14  La pelouse ou les filets ? Vote en commentaire !
b15  Rendez-vous au jour deux, pour voir la suite !
Voix : Zonos « conteur » (pack stade_bloc). Pauses : 0,3 s après b01, 0,2 s au milieu des phrases
coupées en deux plans (b02 → b02b, b03 → b03b), 0,5 s ailleurs.

PLANS (voir le tableau détaillé, section 5)
1 Kevin court et frappe, le ballon part sur la barre transversale · 2 la brèche de la tribune ·
3 Kevin minuscule seul sur le grand terrain · 4 le pylône penché en contre-plongée ·
5 le tableau d'affichage cassé · 6-7 Kevin parle, pièces qui apparaissent · 8 Kevin salue ·
9-10 les abonnés apparaissent avec leur pseudo, sautent · 11 Kevin, +10 pièces ·
12 vue d'ensemble stade + ville · 13 deux cartes de choix · 14 la boue · 15 la cage sans filet ·
16 cartes · 17 Kevin et l'équipe.

HABILLAGE
- Compteur pièces en haut à gauche : 0 au début, passe à 100 sur « que » (b05), reste jusqu'à la fin.
- Compteur abonnés en haut à gauche : 0, tout l'épisode.
- Gains : « +100 » sur « pièces » (b05) ; « +10 » sur « like » (b09).
- Titres (bandeau bleu nuit, mot jaune) : voir la colonne « texte à l'écran », section 4.
- Cartes de choix : « PELOUSE – 100 PIÈCES » (touffe d'herbe) et « FILETS – 100 PIÈCES » (cage).

SON
Musique piano doux très bas (0,07) ; ambiance de ville (0,18) ; métal sur la barre au début de b02 ;
bonus sur « suggestions » (b10) ; deux « cartes » à l'apparition des cartes (b11) ; jingle sur « jour »
(b15) ; souffle de transition entre plans très discret (0,025).

CRÉDIT À METTRE DANS LA LÉGENDE
Modèle « Soccer ball » par Poly by Google (CC-BY 3.0), poly.pizza/m/fnDmeCySRhV.
```

---

## 2. Charte de série (niveau A du gabarit, décisions humaines)

| Paramètre | Valeur retenue | Décidé par | Où c'est porté |
|---|---|---|---|
| Style des personnages | blocs façon jeux à avatars, création du projet | Guillaume, 2026-11-17 | `engine/outils/atelier/modeles/perso_bloc.py` |
| Décor de référence | terrain boueux de Guillaume + ruines + ville | Guillaume | `stade_ruine.py` → `stade_ruine.blend` |
| Rendu | Eevee, AgX, 64 échantillons, ciel HDRI, soleil chaud | Guillaume | pack `stade_bloc` |
| Voix de la série | Zonos, réglage « conteur » | Guillaume (après essais Kyutai, Chatterbox, Kokoro) | `stade_bloc.voix_off` |
| Titres à l'écran | bandeau bleu nuit arrondi et penché, mot clé en jaune, appel à l'action avec flèche ↓ | Guillaume | `engine/pipeline/hud.py` |
| Sous-titres | Arial Black, blanc, contour sombre | Guillaume | pack |
| Format | 9:16, 1080 × 1920, 30 i/s, 35 à 45 s | Lucas et Guillaume | fiche `format` |

## 3. Épisode (niveau B)

| Paramètre | Valeur |
|---|---|
| Durée | 38,7 s (17 plans) |
| Accroche (1re seconde) | Kevin court vers le ballon ; titre « JOUR 1 · OBJECTIF : RÉPARER LE STADE » |
| États nommés | cages : `cage_rouillee` (sans filet) aujourd'hui → `cage_filet` si le vote l'emporte (modèle déjà prêt, non utilisé) |
| Question à l'audience | trois appels en commentaire : pseudo (b07), idées d'amélioration (b10), vote pelouse ou filets (b14) |
| Assets externes | ballon (Poly by Google, CC-BY 3.0, à créditer) ; tout le reste est une création du projet |

## 4. Voix phrase par phrase (niveau C)

Instants mesurés dans la vidéo finale.

| Plan | De → à (s) | Voix | Texte à l'écran | Intonation et remarque |
|---|---|---|---|---|
| b01 | 0,00 → 1,24 | Ça, c'est Kevin ! | JOUR **1** \| OBJECTIF : RÉPARER LE STADE | présentation, appui sur « Kevin » ; le pied touche le ballon juste après ce mot |
| b02 | 1,24 → 2,50 | Ça fait un an et demi... | TOUT SEUL \| DEPUIS 1 AN ET DEMI (ruban) | suspendu, triste |
| b02b | 2,50 → 3,77 | qu'il joue tout seul. | (même titre) | suite directe, sans pause |
| b03 | 3,77 → 5,49 | Pourtant, depuis tout petit, | SON **RÊVE** : DEVENIR PRO | relance |
| b03b | 5,49 → 7,21 | il rêve de devenir pro ! | (même titre) | élan, appui sur « pro » |
| b04 | 7,21 → 10,23 | Et aujourd'hui, c'est le premier jour de l'aventure ! | LE DÉBUT DE **L'AVENTURE** | enthousiaste |
| b05 | 10,23 → 12,09 | Et Kevin n'a que cent pièces. | (aucun ; compteur 0 → 100) | constat, un peu dépité |
| b06 | 12,09 → 13,87 | Alors, on compte sur vous ! | ON COMPTE SUR VOUS ! (appel) | adresse directe |
| b07 | 13,87 → 16,85 | Tu veux jouer avec Kevin ? Mets ton pseudo en commentaire ! | COMMENTE TON PSEUDO ↓ | question puis consigne |
| b08 | 16,85 → 21,15 | Les sélectionnés joueront dès la prochaine partie, avec leur pseudo affiché ! | (aucun) | promesse |
| b09 | 21,15 → 23,79 | Chaque like, c'est dix pièces en plus ! | 1 LIKE = **+10** PIÈCES | règle du jeu, appui sur « dix » |
| b10 | 23,79 → 27,09 | Et mettez en commentaires vos suggestions d'amélioration ! | VOS IDÉES D'AMÉLIORATION ↓ | appel |
| b11 | 27,09 → 29,27 | Avec nos cent pièces, on a deux choix. | **2** CHOIX \| 100 PIÈCES CHACUN | annonce |
| b12 | 29,27 → 30,85 | Entretenir la pelouse, | **PELOUSE** \| 100 PIÈCES | énumération |
| b13 | 30,85 → 33,11 | ou réparer les cages avec des filets. | **FILETS** \| 100 PIÈCES | suite |
| b14 | 33,11 → 35,87 | La pelouse ou les filets ? Vote en commentaire ! | PELOUSE **OU** FILETS ? \| VOTE EN COMMENTAIRE ↓ | question, appel |
| b15 | 35,87 → 38,73 | Rendez-vous au jour deux, pour voir la suite ! | RENDEZ-VOUS AU JOUR **2** | conclusion, laisser la fin entière |

## 5. Plan par plan (niveau D)

Coordonnées en mètres dans le stade (x vers la cage droite, y vers la tribune nord, z vers le haut). Toutes les caméras du moteur filment depuis le côté sud (−y) de leur cible.

| Plan | Caméra (mouvement, cible, distance / hauteur, focale) | On voit | Actions |
|---|---|---|---|
| b01 | plan fixe sur Kevin (40,6 ; −0,6), 4,2 / 0,35 m, 35 mm | Kevin de profil sur la boue, ballon, tribune et ville au fond | Kevin court de (39,5 ; −0,6) à (41 ; −0,6) dès 0,27 s ; frappe, contact à 1,07 s ; le ballon part sur la barre (52,4 ; −0,8 ; 2,3) |
| b02 | survol de la brèche de la tribune (9 ; 42 ; 2), 16 / 3 m | éboulis, sièges cassés, toit troué | ballon qui retombe (son métal) |
| b02b | révélation (la caméra recule et monte) sur Kevin, 42 / 20 m | Kevin minuscule, seul sur l'immense terrain | — |
| b03 | plan fixe contre-plongée sur le pylône nord-ouest (−60 ; 44 ; 12), 19 / −9,5 m, 24 mm | pylône rouillé penché, ciel | — |
| b03b | travelling avant sur le tableau d'affichage (−40 ; 47 ; 4,5), 13 / 0,5 m | tableau penché, chiffres tombés | — |
| b04 | travelling avant sur Kevin (44 ; −2), 4,6 / 0,7 m | Kevin face caméra, parle | Kevin passe de « frappe » à « parle » sur la coupe |
| b05 | plan fixe sur Kevin, 4,2 / 0,7 m | Kevin, tas de pièces à ses pieds | tas de pièces apparaît sur « pièces » ; +100 |
| b06 | orbite autour de Kevin, 5 / 1 m | Kevin salue | Kevin passe à « salue » |
| b07 | travelling avant sur l'équipe (44,6 ; 0,6), 11 / 3 m | Kevin et trois abonnés | abonné rouge sur « jouer », bleu sur « pseudo », vert sur « commentaire », chacun avec son étiquette |
| b08 | survol de l'équipe, 8 / 2,2 m | équipe, étiquettes lisibles | le bleu sautille 2,5 s ; le rouge saute en boucle |
| b09 | plan fixe sur Kevin, 4,2 / 0,7 m | Kevin, abonnés derrière | +10 sur « like » |
| b10 | révélation sur le centre du terrain (0 ; 0), 80 / 32 m | tout le stade en ruine et la ville | son bonus sur « suggestions » |
| b11 | plan fixe sur les cartes (en l'air, z = 45), 8,4 / 2,2 m | deux cartes blanches, ville au fond | cartes et miniatures apparaissent l'une après l'autre (0,05 à 0,5 s) |
| b12 | travelling latéral sur la boue (18 ; 3), 6 / 1,3 m | plaques de boue, flaques | — |
| b13 | travelling avant sur la cage droite (51,3 ; 0 ; 1,2), 6,5 / 0,2 m | poteaux rouillés, restes de filet déchiré | — |
| b14 | plan fixe sur les cartes, 8,4 / 2,2 m | deux cartes | — |
| b15 | révélation sur Kevin, 15 / 5 m | Kevin salue, équipe derrière | Kevin passe à « salue » ; jingle sur « jour » |

## 6. Ce qui manquait dans les briefs et a coûté du temps

À intégrer aux agents `story-*` pour les prochains épisodes.

1. **Le style des personnages et du décor n'était pas fixé** : trois styles successifs (Quaternius, bonhomme blanc, puis blocs). Le brief doit renvoyer à la charte de série (section 2) au lieu de laisser la Production choisir.
2. **La position de Kevin sur le terrain** était implicite. Un brief doit dire où se trouve chaque personnage (« sur la pelouse, à 12 m de la cage droite »), pas seulement « sur le terrain ».
3. **Les pauses entre les phrases** n'étaient pas écrites. Sans consigne, le moteur met 0,6 s partout, ce qui donne un rythme haché, surtout quand une phrase est coupée en deux plans. Le brief doit donner le blanc voulu après chaque phrase.
4. **Les phrases courtes et les fins de phrase** sont fragiles avec la synthèse vocale (charabia sur « Ça, c'est Kevin », fin avalée sur « la suite »). Éviter les phrases de moins de 4 mots, et ne pas terminer sur un mot faible. Si c'est voulu, le signaler pour que la Production vérifie à l'oreille.
5. **Les sons de transition** n'étaient pas réglés (« bruit de balai »). Le brief doit donner le volume du souffle entre les plans, ou demander une coupe sèche.
6. **Les plans de décor** (ruines) étaient demandés après coup. Prévoir dès le découpage au moins un plan de décor pour trois plans de personnages.

---

**Rôle de ce document** : référence de travail interne au projet. Il décrit la vidéo telle qu'elle a été produite et sert de modèle pour les briefs du pôle Storytelling. **Il n'a aucune valeur juridique** : ce n'est ni un contrat, ni une validation de publication, ni un avis sur les licences. La publication reste soumise à la validation explicite de Lucas ou Guillaume, et les licences se vérifient dans `engine/assets/licences.csv`.
