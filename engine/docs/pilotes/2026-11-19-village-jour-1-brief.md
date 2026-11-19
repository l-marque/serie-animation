# Brief de production : nouvelle série « Le Village sur la Tortue », épisode « Jour 1 »

- Épisode : `village-jour-1`, premier épisode d'une **nouvelle série**, distincte de La Revanche du Miteux et de « 7 Jours avant l'Attaque ».
- Nom de travail de la série : **« Le Village sur la Tortue »** ; nom du village : **« Carapace »**. Ce sont des noms provisoires, à confirmer par Lucas et Guillaume avant publication.
- Rédigé le 2026-11-19 par le Claude de Guillaume. Demande de Guillaume : reprendre le genre des vidéos « village » de la référence (v1, v5 et v6 de `engine/docs/references-videos.md`) avec un format original et un style proche. Il a laissé le choix du concept à Claude (« choisi »), a demandé d'aller jusqu'à la vidéo finale, puis a ajouté deux consignes : une intrigue sur la destination de la tortue, et **le hook avant tout** (« il faut capter son attention et le garder »).
- Structure reprise du brief de iles-jour-1 (`2026-11-18-iles-jour-1-brief.md`). La publication reste manuelle et humaine.

---

## 1. Le concept

- Un village minuscule, Carapace, est construit **sur le dos d'une tortue géante endormie**, au milieu d'une prairie.
- **1 abonné = 1 habitant**, avec son pseudo au-dessus de la tête. **1 like = 1 brique**. Les briques servent à construire (maisons, tours, puits…).
- Chaque jour, **le commentaire le plus liké** décide de ce qu'on construit.
- **L'intrigue** : la tortue dort depuis toujours, le regard tourné vers une montagne lointaine, au sommet de laquelle brille une lumière dorée. Personne n'a jamais vu cette montagne de près. **À 100 habitants, la tortue se réveille** et part vers la montagne, avec tout le village sur son dos. Ce qu'il y a là-haut reste un mystère, à révéler dans un épisode futur (décision humaine).
- **Style** : personnages en blocs arrondis (`habitant_iles_*`, `perso_bloc.py`), tortue et décor en blocs biseautés, couleurs franches.

## 2. Ce qui nous distingue des vidéos « village » de référence

| Référence (rien.ville, observée) | Notre version |
|---|---|
| Village posé au sol, maire en costume avec écharpe | Village **sur une tortue géante** ; un simple habitant n°1 |
| Caisse en euros | **Briques** (1 like = 1 brique) |
| Objectif chiffré (20 000 habitants) | Objectif qui **déclenche un événement** : à 100 habitants, la tortue se réveille |
| Pas d'intrigue de fond | **Montagne mystérieuse** à l'horizon, destination du voyage |

Ce qu'on garde du genre (observé sur plusieurs comptes, donc propre au format et non à un compte) : badge « JOUR 1 », compteur d'habitants, pseudo au-dessus du personnage, titres très gros, appel à commenter. On ne reprend ni nom, ni personnage, ni habillage propre à ces comptes.

## 3. L'accroche (priorité n°1)

- **0 à 0,8 s** : « JOUR UN ! » quasi crié, gros plan sur l'habitant n°1 qui salue devant le panneau « CARAPACE » ; titre géant « UN VILLAGE SUR UNE TORTUE GÉANTE » dès la première image, lisible sans le son.
- **0,8 à 4 s** : la caméra recule et s'élève sans coupe : le « sol » du village est la carapace d'une tortue géante qui dort, « Zzz » au-dessus de la tête.
- **4 à 8 s** : boucle ouverte, tenue jusqu'à la fin : « elle partira vers cette montagne… que personne n'a jamais vue de près ! » (montagne, lumière dorée, titre « MAIS QU'Y A-T-IL LÀ-HAUT ? »).
- Relance au milieu : « Chut… elle dort encore. » (ronflement, gros plan sur la tête).
- Pic avant la fin : la tortue ouvre les yeux, lève la tête et marche (« tout le village partira avec elle ! »).
- **Fin en boucle** : le dernier plan reprend le cadrage du premier (habitant qui salue devant le panneau).

## 4. Voix (texte exact, nombres en lettres)

Voix Qwen de la série (référence « jeune narrateur Reels »), première syllabe à 0 s, b01 quasi crié (méthode iles-jour-1). Après la remarque de Guillaume sur la fluidité, les prises ont été choisies sans respiration interne et les phrases s'enchaînent avec 0,1 s d'écart : débit de parole moyen d'environ 215 mots par minute (au-dessus de la cible de 180 décidée par Guillaume, mais dans la plage des Reels de référence, 160 à 215). Piste finale : 35,2 s.

| Beat | Voix | Texte à l'écran |
|---|---|---|
| b01 | Jour un ! | UN VILLAGE SUR UNE *TORTUE GÉANTE* |
| b02 | Ce village est construit sur le dos d'une tortue géante ! | (même titre) |
| b03 | Et quand elle se réveillera, elle partira vers cette montagne... | — |
| b04 | que personne n'a jamais vue de près ! | MAIS QU'Y A-T-IL *LÀ-HAUT* ? |
| b05 | Pour l'instant, le village de Carapace n'a qu'un seul habitant... | *1* SEUL HABITANT |
| b06 | Il en faut cent pour réveiller la tortue. | *100* HABITANTS = *RÉVEIL* |
| b07 | Chut... elle dort encore. | CHUT… ELLE *DORT* |
| b08 | Et c'est vous qui allez la réveiller ! | — |
| b09 | Chaque abonné devient un habitant, avec son pseudo. | 1 ABONNÉ = *1 HABITANT* |
| b10 | Chaque like rapporte une brique. | 1 LIKE = *1 BRIQUE* |
| b11 | Avec les briques, on construit des maisons, des tours, un puits... | — |
| b12 | et le commentaire le plus liké décide de ce qu'on construit ! | TON COMMENTAIRE = ON CONSTRUIT ↓ |
| b13 | Le jour où elle se réveillera, tout le village partira avec elle ! | bannière DIRECTION LA *MONTAGNE* |
| b14 | Alors, on construit quoi en premier ? Dis-le en commentaire ! | ON CONSTRUIT *QUOI* ? \| MAISON, TOUR OU PUITS ? ↓ |
| b15 | Rendez-vous demain pour le jour deux ! | RENDEZ-VOUS AU JOUR *2* |

Habillage permanent : badge « JOUR 1 » en haut à droite ; compteur d'habitants (1) en haut à gauche ; compteur de briques (0) à partir de b10.

## 5. Modèles créés pour l'épisode

| Modèle | Script | Remarque |
|---|---|---|
| `tortue_geante` | `engine/outils/atelier/modeles/tortue_geante.py` | 22 m, plateau du village à z = 5 m ; animations Sleep, Wake, Awake, Walk |
| `prairie_tortue`, `montagne_mystere` (à 800 m, brumeuse, rayon doré), `cabane_bloc`, `panneau_carapace`, `puits_bloc`, `zzz_bloc` | `engine/outils/atelier/modeles/village_tortue.py` | décor, intrigue (montagne à la lumière dorée), village |
| repris : `maison_bloc`, `tour_bloc`, `habitant_iles_*`, `etiquette_pseudo` | — | modèles existants de la bibliothèque |

Fiche : `episodes/village-jour-1.json`, construite par `renders/village-jour-1/outils/fiche.py` ; habillage hors contrat (HUD, sons) : `episodes/village-jour-1.habillage.json` ; voix : `episodes/village-jour-1.voix.json`.

## 6. Ajouts au moteur (côté Guillaume)

- Icône de compteur **« brique »** (`engine/pipeline/hud.py`, schéma interne `engine/schemas/habillage.schema.json`). Le contrat de Lucas (`contracts/`) n'a pas été modifié : le HUD de cet épisode reste dans `village-jour-1.habillage.json`.
- Son synthétisé **« ronflement »** (`engine/pipeline/sons.py`, registre des sons), non utilisé au final : remplacé par un son Freesound.
- **`avance_voix_s`** (facultatif) dans le pack de DA : silence avant la première syllabe de chaque plan (0,15 s par défaut, 0,02 s pour cette série) ; lu par `realisateur.py` et `montage.py`. Les autres packs ne changent pas.
- **`look_vue`** (facultatif) dans le pack de DA : look de la transformation de vue (« Punchy » pour cette série, couleurs plus franches).
- Fait et vérifié par le rendu de l'animatique ; les tests unitaires (`tests/engine`) n'ont pas été relancés (pytest absent de ce Python).

## 7. Sons (Freesound, licence CC0, inscrits dans `licences.csv`)

| Nom | Id Freesound | Usage |
|---|---|---|
| `ronflement_geant` | 471927 | ronflement de la tortue (b02, b07) |
| `pas_geant` | 721601 | pas de la tortue qui part (b13) |
| `revelation_riser` | 754771 | montée pendant la révélation (b02) |
| `mystere_scintille` | 844398 | lumière de la montagne (b03) |

## 8. Points à décider par un humain

- Noms définitifs de la série et du village.
- Le seuil de 100 habitants pour le réveil : à ajuster selon l'audience réelle du compte.
- Ce qu'il y a au sommet de la montagne (réponse à garder pour un épisode clé).

---

**Rôle de ce document** : brief de travail interne au projet, qui sert à produire le premier épisode d'une nouvelle série et à guider les agents de production. **Il n'a aucune valeur juridique** : ce n'est ni un contrat, ni une validation de publication, ni un avis sur les droits d'auteur, les marques ou les licences. Les comparaisons avec des comptes existants reposent sur l'observation de vidéos publiques (`engine/docs/references-videos.md`) ; aucun de leurs éléments n'est reproduit. La publication reste soumise à la validation explicite de Lucas ou de Guillaume.
