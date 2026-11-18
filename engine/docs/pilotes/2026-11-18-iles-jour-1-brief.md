# Brief de production : nouvelle série « 7 Jours avant l'Attaque », épisode « Jour 1 »

- Épisode : `iles-jour-1`, premier épisode d'une **nouvelle série**, distincte de La Revanche du Miteux.
- Nom de travail de la série : **« 7 Jours avant l'Attaque »**. Guillaume a laissé le choix ouvert (« on s'en fout ») : c'est un nom provisoire, à confirmer par Lucas et Guillaume avant publication.
- Rédigé le 2026-11-18 par le Claude de Guillaume, à partir du concept donné par Guillaume. Guillaume a validé d'avance tout l'enchaînement jusqu'à la vidéo finale (« je valide tout », 2026-11-18), plaquette comprise. La publication reste manuelle et humaine.
- Structure reprise du brief du jour 2 de La Revanche du Miteux (`2026-11-18-jour-2-brief.md`).

---

## 1. Le concept (donné par Guillaume)

- **Deux îles** : une pour Instagram, une pour YouTube.
- **Sept jours** pour construire la meilleure base et la meilleure défense. Au septième jour, les deux îles s'attaquent ; la meilleure gagne. Le compte à rebours est au cœur de chaque épisode.
- **Économie** : 1 abonné = 100 pièces, et l'île de sa plateforme s'agrandit ; 1 like = 10 pièces. Chaque île a sa cagnotte, alimentée par sa plateforme.
- **Construction** : chaque jour, le commentaire le plus liké de chaque plateforme décide de ce qui est ajouté sur son île. Il n'y a pas de choix imposé.
- **Habitants** : chaque abonné vit sur l'île de sa plateforme, avec son pseudo, et se battra le jour de l'attaque.
- **Style** : personnages en blocs, comme La Revanche du Miteux (`perso_bloc.py`).

## 2. Ressemblance avec une vidéo existante (à garder en tête)

Le Reel de référence v7 (« comentopia », `engine/docs/references-videos.md`) a la même mécanique de base : une île par plateforme, le commentaire le plus liké construit, les abonnés deviennent habitants. Pour s'en distinguer, cet épisode met en avant ce qui est propre à notre concept : le **duel à deux îles**, le **compte à rebours de 7 jours** et la **bataille finale**, les **pièces**, le **style en blocs**. On ne reprend ni leur habillage (« SEASON 1 · DAY 0 », un mot géant à la fois), ni leur cadrage des îles côte à côte en plongée.

## 3. Le prompt à transmettre à la Production

```text
ÉPISODE « JOUR 1 », série « 7 Jours avant l'Attaque » (nom provisoire). Vidéo verticale 9:16,
1080 × 1920, 30 i/s, environ 42 à 46 s.

HISTOIRE EN UNE PHRASE
Une alarme retentit : dans sept jours, l'une de ces deux îles sera rayée de la carte. L'île
d'Instagram et l'île de YouTube sont vides ; les abonnés ont sept jours pour construire la
meilleure base, avant que les deux îles s'attaquent.

STYLE
- Personnages en blocs façon jeux à avatars (perso_bloc.py), comme La Revanche du Miteux.
- Mer turquoise, ciel bleu de fin de matinée, couleurs vives.
- Deux petites îles de sable et d'herbe, vides, face à face, séparées par un bras de mer
  d'environ 40 m. Un drapeau sur chaque île : couleurs dégradées rose-violet pour Instagram,
  rouge pour YouTube (couleurs seulement, aucun logo).

PERSONNAGES
- Habitants en blocs (abonne_bloc_<couleur>) : n'apparaissent qu'en b10, deux sur chaque île,
  avec une étiquette « @ton_pseudo » au-dessus de la tête.

VOIX (texte exact, nombres en lettres ; voix Qwen du jour 2 de La Revanche du Miteux, même
référence ; première syllabe dès 0 s ; 0,1 à 0,2 s entre les phrases)
b01  Alerte ! Dans sept jours, une de ces deux îles sera rayée de la carte !
b02  À gauche, l'île d'Instagram. À droite, l'île de YouTube.
b03  Pour l'instant, elles sont vides, et c'est vous qui allez les construire.
b04  Il ne reste que sept jours pour bâtir la meilleure base et la meilleure défense.
b05  Car au septième jour, les deux îles s'attaquent, et une seule gagnera !
b06  Chaque abonné rapporte cent pièces, et agrandit son île !
b07  Chaque like en rapporte dix.
b08  Avec ces pièces, on peut construire des maisons, des remparts, des tours...
b09  et même des crocodiles autour de l'île !
b10  Chaque abonné vivra sur son île, avec son pseudo, prêt à se battre.
b11  Chaque jour, le commentaire le plus liké de chaque plateforme décide de ce qu'on construit.
b12  Instagram contre YouTube : qui aura la meilleure île ?
b13  Rendez-vous au jour deux pour savoir laquelle des deux îles sera la meilleure !

HABILLAGE
- Badge « J-7 » permanent en haut au centre.
- Compteurs de l'île Instagram en haut à gauche (pièces 0, abonnés 0) ; de l'île YouTube en
  haut à droite (pièces 0, abonnés 0). Permanents, valeurs à zéro.
- b01 : ruban de chantier « ALERTE ! » et son d'alarme dès la première image.
- Titres : voir la section 5.

SON
Alarme (sirène synthétisée) sur b01 ; vagues et vent légers en fond ; musique très basse ;
« pop » sur chaque apparition ; jingle sur « jour » (b13).
```

## 4. Plans (proposition)

Repère : x de l'île Instagram (à gauche, x = −20) vers l'île YouTube (à droite, x = +20) ; y vers le large ; z vers le haut. Chaque île fait environ 18 m de diamètre.

| Plan | Ce qu'on voit | Actions |
|---|---|---|
| b01 | plan large des deux îles, la caméra tremble légèrement | ruban « ALERTE ! », alarme |
| b02 | survol de l'île Instagram puis de l'île YouTube | drapeaux qui flottent |
| b03 | plan sur une île vide | — |
| b04 | plan large, les deux îles | titre « IL RESTE 7 JOURS » |
| b05 | les deux îles face à face, caméra basse au ras de l'eau | titre « JOUR 7 : L'ATTAQUE » |
| b06 | plan sur l'île Instagram | gain « +100 » sur « cent » ; l'île grandit sur « agrandit » |
| b07 | idem | gain « +10 » sur « dix » |
| b08 | plan sur une île | une maison, puis un rempart, puis une tour apparaissent et disparaissent l'une après l'autre, sur « maisons », « remparts », « tours » |
| b09 | plan au ras de l'eau | trois crocodiles sortent de l'eau autour de l'île, puis disparaissent |
| b10 | plan sur les deux îles | deux habitants en blocs apparaissent sur chaque île, pseudo au-dessus de la tête |
| b11 | plan large | titre « TOP COMMENTAIRE = ON CONSTRUIT ↓ » |
| b12 | les deux îles face à face | bannière « INSTAGRAM VS YOUTUBE » |
| b13 | recul sur les deux îles | titre « RENDEZ-VOUS AU JOUR 2 », jingle |

## 5. Textes à l'écran

| Plan | Texte |
|---|---|
| b01 | ruban « ALERTE ! » |
| b04 | IL RESTE *7* JOURS |
| b05 | JOUR *7* : L'ATTAQUE |
| b06 | 1 ABONNÉ = *100* PIÈCES \| + L'ÎLE S'AGRANDIT |
| b07 | 1 LIKE = *10* PIÈCES |
| b11 | TOP COMMENTAIRE = ON CONSTRUIT ↓ |
| b12 | bannière INSTAGRAM *VS* YOUTUBE |
| b13 | RENDEZ-VOUS AU JOUR *2* |

## 6. À produire

| Élément | Qui |
|---|---|
| Deux îles vides, mer, drapeaux | `prod-modeleur` |
| Maison, rempart, tour, crocodile (style blocs, lisibles de loin) | `prod-modeleur` |
| Pack de DA « iles » (mer, ciel, lumière) | `prod-directeur-artistique` ou `prod-modeleur` |
| Fiche épisode | `prod-realisateur` |
| Voix Qwen | `prod-directeur-voix` |
| Son d'alarme | fait (`alarme`, synthétisé, registre des sons) |

---

**Rôle de ce document** : brief de travail interne au projet, qui sert à produire le premier épisode d'une nouvelle série et à guider les agents de production. **Il n'a aucune valeur juridique** : ce n'est ni un contrat, ni une validation de publication, ni un avis sur les droits d'auteur, les marques ou les licences. Les noms Instagram et YouTube désignent les plateformes de l'audience ; aucun logo n'est reproduit. La publication reste soumise à la validation explicite de Lucas ou de Guillaume.
