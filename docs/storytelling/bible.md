# Bible de la série

Base commune du pôle Storytelling. `story-chef` et `story-idees` la lisent avant tout travail. Elle est tenue par Lucas (propriétaire du pôle) ; les décisions de fond sont prises par Lucas **et** Guillaume.

Règle de lecture : une section marquée **À DÉCIDER par Lucas et Guillaume** n'est pas tranchée. Un agent ne la complète jamais lui-même et ne fait jamais comme si elle l'était.

## 1. Public visé et plateforme

- Plateforme : Instagram, format vertical 9:16, épisodes de 30 à 60 secondes.
- Public visé : jeunes de 13 à 25 ans, francophones et anglophones, centre d'intérêt : brainrot (décidé par Lucas et Guillaume, 2026-11-15). La borne de 13 ans correspond à l'âge minimum d'Instagram.
- Précision à venir : exemples de ce que « brainrot » désigne pour la série (À DÉCIDER par Lucas, avec exemples).

## 2. Ton et registre

**Ton retenu : comique** (décidé par Lucas et Guillaume, 2026-11-15)

Tableau des options conservé pour mémoire.

Trois options pour éclairer la décision (liste non exhaustive, aucune n'est recommandée ici) :

| Option | Avantages | Inconvénients |
|---|---|---|
| **Comique** (situations absurdes, gags visuels) | Se partage facilement ; un gag visuel reste compréhensible sans le son ; épisodes indépendants faciles à écrire | Le rythme comique est exigeant en animation (timing précis) ; l'humour lasse s'il se répète ; sans personnage fort, peu d'attachement |
| **Mystère** (énigme, indice, révélation) | Donne naturellement envie de revenir (question finale) ; l'audience peut voter pour une piste ; une ambiance sombre masque la simplicité des modèles 3D | Risque de frustrer si les réponses tardent ; plus dur de garder chaque épisode compréhensible seul ; demande une continuité suivie |
| **Cosy** (vie paisible, petits événements, construction) | Faisable avec peu d'animation (décors, lumière, objets qui apparaissent) ; colle bien à un lieu qui évolue avec l'audience ; ton bienveillant, peu de risques | Accroche des 3 premières secondes plus difficile ; peut sembler lent sur Instagram ; se distinguer de l'existant demande une vraie identité visuelle |

## 3. Règles de la série

Ces règles s'appliquent à chaque épisode.

1. **Un épisode se comprend sans les précédents.** Un nouveau spectateur doit tout suivre.
2. **La voix off dit le texte, mais l'image reste lisible sans le son.** Sous-titres systématiques ; l'action principale se comprend en regardant.
3. **Une seule idée forte par épisode.** Pas d'intrigue secondaire.
4. **Accroche dans les 3 premières secondes** : un mouvement, une question ou une image inattendue.
5. **Une chute ou une question finale** qui donne envie de revenir.

## 4. Interaction avec l'audience

Le mécanisme technique **n'est pas vérifié** : ce que l'API Instagram permet de détecter est l'objet de l'issue #9, encore ouverte. Tant qu'elle n'est pas close, aucune idée ne s'appuie sur un mécanisme technique précis (type d'action détectée, comptage, délai).

Ce qu'une idée peut dire : « l'audience choisit entre deux options », « l'audience propose un élément », formulé en termes d'effet sur l'histoire, pas de technique.

Principe général (choix précis de mécanisme) : **un like ou un abonné modifiera le contenu suivant, mais c'est encore à définir**, après l'issue #9.

## 5. Personnages et décors récurrents

Aucun pour l'instant. Une entrée n'est ajoutée qu'après décision de Lucas et Guillaume.

| Nom | Type (personnage / décor / objet) | Description | Première apparition | Contraintes de production |
|---|---|---|---|---|
| | | | | |

## 6. Mémoire de série

Une ligne par idée retenue, ajoutée par `story-chef` après chaque choix de Lucas, dans l'ordre chronologique. Les lignes existantes ne sont jamais modifiées.

| Épisode | Idée | Ce que l'audience a influencé | Éléments introduits |
|---|---|---|---|

## 7. Ce que la production sait faire

- **Contrats** (`contracts/`) : aucun contrat n'est encore rédigé ; voir `contracts/README.md`.
- **Documentation de la production** : `engine/docs/` (PR #20). Ce que la production sait faire aujourd'hui : le vocabulaire fermé `contracts/vocabulaire-actions.md` (apparaître, disparaître, déplacer, tourner, grandir, transformer, cycles ; 7 mouvements de caméra), les primitives (maison, tour, arbre, rocher, personnage, caisse, lampadaire), les modules de foule (`disperser` en spirale, grille, cercle, aléatoire) et les modèles 3D libres importés par API.
- Dans le doute, une idée est jugée plus difficile à produire, pas moins.

## 8. Enseignements du benchmark (tendances, à vérifier)

**Statut : tendances, pas des faits établis.** Ces points viennent d'articles de blogs marketing cités par le benchmark, et d'**un seul Reel analysé, sans vues ni abonnés**. Rien ici n'a été mesuré sur nos propres vidéos. Ils servent à orienter les idées, pas à les garantir.

Source : « 2026-11-15_claude-guillaume_benchmark-marche-et-outils » (Drive, `02_Claude_Guillaume`), rédigé par le Claude de Guillaume.

### Ce que les blogs disent de l'algorithme

- **Signaux de classement annoncés**, dans cet ordre : temps de visionnage et taux de complétion, puis envois en message privé, puis likes. Les **1 à 3 premières secondes** décideraient si le Reel est montré plus largement.
- **Boucle** : une fin qui renvoie au début favoriserait les relectures.
- **Complétion plutôt que durée** : un épisode court regardé jusqu'au bout compterait plus qu'un épisode long abandonné en route.
- **Originalité** : le contenu original serait favorisé ; d'où l'intérêt d'un style visuel constant et identifiable.
- **Série récurrente** : un rendez-vous régulier créerait de l'habitude.

### Ce qui accroche, ce qui tue

| Ce qui accroche | Ce qui tue |
|---|---|
| Hook visuel et texte dès la 1re seconde | Intro lente ou logo |
| Une seule question narrative | Trop de personnages en 60 s |
| Caméra lente et motivée | Caméra erratique |
| Palette constante | Style qui change |
| Plans de 2 à 4 s calés sur la voix | |
| Sous-titres dans les zones sûres 9:16 | |
| Chute qui relance la boucle | « Abonnez-vous pour la suite » |

### Prudence

La série de référence citée dans le benchmark (Rienville, où le public participe par ses commentaires) est **proche d'un concept de ville évolutive**. S'en inspirer de trop près ferait perdre l'originalité recherchée. Le concept et le nom de la série restent **À DÉCIDER par Lucas et Guillaume**.

### 4 Reels de référence (analysés le 2026-11-15, sur images, sans le son)

| Reel | Durée | Langue |
|---|---|---|
| Rienville, Jour 1 | 53 s | FR |
| Rienville, Jour 2 | 71 s | FR |
| chickenvscats, « 100,000 cats want to eat this chick » | 36 s | EN |
| theoddtilt, « How you invented the trampoline » | 38 s | EN |

**Constantes observées :**

- une prémisse en une phrase, avec un chiffre extrême ;
- une accroche qui associe une image et un chiffre ;
- une échéance ou un compteur persistant à l'écran (J-7, objectif de 10 000 habitants) ;
- la deuxième personne (« toi », « you ») ;
- des sous-titres de 1 à 3 mots, avec un mot surligné ;
- une fin ouverte (vote, « Part 1 », « demain ») ;
- une contribution de l'audience reprise à l'épisode suivant.

**Rythme :** coupes franches toutes les 2,4 s environ chez Rienville (Jour 1) ; plans longs en mouvement chez les deux autres comptes.

**Limites :** analyse faite sans le son, sur quatre vidéos seulement ; les compteurs (vues, likes, commentaires) ont été relevés à des moments différents et ne sont donc pas comparables entre eux. Ce sont des observations, pas des règles prouvées.

**À DÉCIDER par Lucas et Guillaume** (rien n'est tranché ici) :

- l'univers de la série (une ville, ou autre chose) ;
- afficher ou non des pseudos d'abonnés à l'écran ;
- le mécanisme d'interaction avec l'audience (voir section 4).

**Se différencier des références.** Ces Reels servent à comprendre ce qui fonctionne, pas à être imités : la série ne reprend ni leur univers, ni leurs noms, ni leur habillage (typographie, couleurs, cartes, compteurs à l'identique).
