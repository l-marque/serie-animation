# Le canard qui se multiplie — beats et voix off

- Statut : essai, non validé par Lucas (essai demandé par Lucas le 2026-11-16)
- Scénario source : note Drive `01_Claude_Lucas/2026-11-15_claude-lucas_pilote-canard-scenario-v3` (statut : validé par Lucas le 2026-11-15, faisabilité à confirmer par Guillaume ; hors dépôt, lu dans une recopie locale)
- Durée du scénario : 40 s · Beats : 14 (dont 1 muet) · Voix : 82 mots, 32,8 s, soit 82 % de la durée

Retours du pilote pris en compte (`engine/docs/pilotes/2026-11-15-canard.md`) : aucun grand nombre dit à voix haute (le compteur les porte) ; aucune phrase de 1 ou 2 mots ; les pops ne suivent plus la longueur des phrases : leur calendrier est fixé d'abord, avec des intervalles strictement décroissants pendant l'escalade (2,8 → 2,4 → 2,0 → 1,6 → 1,2 → 0,8 → 0,6 → 0,4 s), puis la voix est calée dessus ; premier pop à 1,0 s.

## Calendrier du compteur (référence pour tous les beats)

| Valeur | Instant | Intervalle depuis le pop précédent | Beat, mot |
|---|---|---|---|
| 1 | 0,0 s | — | b01 |
| 2 | 1,0 s | — | b01, « deux » |
| 4 | 4,0 s | 3,0 s | b02, « pop » |
| 8 | 7,0 s | 3,0 s | b03, « huit » |
| 16 | 10,0 s | 3,0 s | b05, « Et » |
| 32 | 12,8 s | 2,8 s | b06, « Encore » |
| 64 | 15,2 s | 2,4 s | b06, « double » (2e) |
| 128 | 17,2 s | 2,0 s | b07 (muet) |
| 256 | 18,8 s | 1,6 s | b08, « Des » |
| 512 | 20,0 s | 1,2 s | b08, « maintenant » |
| 1 024 | 20,8 s | 0,8 s | b08, « milliers » |
| 2 048 | 21,4 s | 0,6 s | b08, pendant « de » |
| 4 096 | 21,8 s | 0,4 s | b08, pendant « canards » |
| 4 096 (figé) | 21,8 → 28,5 s | — | b08 à b11 |
| 1 | 28,5 s | — | b11, « Pouf » |

## Correspondance temps → beats

| Temps du scénario | Secondes | Beats |
|---|---|---|
| 1. Accroche | 0-3 | b01 |
| 2. Mise en situation | 3-10 | b02, b03, b04 |
| 3. Escalade | 10-25 | b05, b06, b07, b08, b09 |
| 3 bis. Arrêt sur l'image pleine | 25-28 | b10 |
| 4. Chute | 28-34 | b11, b12 |
| 5. Boucle et question | 34-40 | b13, b14 |

## Beats

### b01 — accroche faussement calme

| Champ | Valeur |
|---|---|
| Début → fin | 0,0 → 3,0 s (3,0 s) |
| Voix | « Un canard, deux canards, tu restes calme. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | faussement calme, amusé ; débit lent ; volume bas |
| Mots appuyés | « deux » |
| Pauses avant / après | 0,2 / 0,0 |
| Sous-titres | Un canard / **deux** canards / tu restes **calme** |
| Texte à l'écran | rien |
| Compteur | 1 → 2 à 1,0 s, sur « deux » |

### b02 — la règle du pop

| Champ | Valeur |
|---|---|
| Début → fin | 3,0 → 5,4 s (2,4 s) |
| Voix | « À chaque pop, ils doublent. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | explicatif, posé ; débit normal ; volume normal |
| Mots appuyés | « pop », « doublent » |
| Pauses avant / après | 0,2 / 0,2 |
| Sous-titres | À chaque / **pop** / ils **doublent** |
| Texte à l'écran | rien |
| Compteur | 2 → 4 à 1,0 s, sur « pop » |

### b03 — calcul tranquille

| Champ | Valeur |
|---|---|
| Début → fin | 5,4 → 7,8 s (2,4 s) |
| Voix | « Donc quatre, et puis huit, logique. » |
| Mots | 6 |
| Durée de voix (2,5 mots/s) | 2,4 s |
| Intonation | sûr de lui, un peu professoral ; débit normal ; volume normal |
| Mots appuyés | « quatre », « huit » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Donc **quatre** / et puis **huit** / logique |
| Texte à l'écran | rien |
| Compteur | 4 → 8 à 1,6 s, sur « huit » |

### b04 — fausse assurance

| Champ | Valeur |
|---|---|
| Début → fin | 7,8 → 10,0 s (2,2 s) |
| Voix | « Facile, tu sais compter, non ? » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | complice, légèrement taquin ; débit normal ; volume normal |
| Mots appuyés | « Facile » |
| Pauses avant / après | 0,0 / 0,2 |
| Sous-titres | **Facile** / tu sais compter / non |
| Texte à l'écran | rien |
| Compteur | 8 |

### b05 — ça s'emballe

| Champ | Valeur |
|---|---|
| Début → fin | 10,0 → 12,8 s (2,8 s) |
| Voix | « Et là, ça s'accélère, tu sens ? » |
| Mots | 6 |
| Durée de voix (2,5 mots/s) | 2,4 s |
| Intonation | premier doute, tension qui monte ; débit normal ; volume normal |
| Mots appuyés | « s'accélère » |
| Pauses avant / après | 0,0 / 0,4 |
| Sous-titres | Et là / ça **s'accélère** / tu sens |
| Texte à l'écran | rien |
| Compteur | 8 → 16 à 0,0 s, sur « Et » |

### b06 — doublements en série

| Champ | Valeur |
|---|---|
| Début → fin | 12,8 → 15,8 s (3,0 s) |
| Voix | « Encore le double, et encore le double. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | agacé, s'emballe ; débit rapide ; volume normal puis fort |
| Mots appuyés | « double » (les deux fois) |
| Pauses avant / après | 0,0 / 0,2 |
| Sous-titres | Encore le **double** / et encore / le **double** |
| Texte à l'écran | rien |
| Compteur | 16 → 32 à 0,0 s, sur « Encore » ; 32 → 64 à 2,4 s, sur « double » (le second) |

### b07 — pops sans voix

| Champ | Valeur |
|---|---|
| Début → fin | 15,8 → 18,8 s (3,0 s) |
| Voix | muet : les pops et le compteur qui passe à 128 portent le beat |
| Mots | 0 |
| Durée de voix (2,5 mots/s) | 0,0 s |
| Intonation | — |
| Mots appuyés | aucun |
| Pauses avant / après | 3,0 (beat muet) |
| Sous-titres | — |
| Texte à l'écran | rien |
| Compteur | 64 → 128 à 1,4 s |

### b08 — énumération débordée

| Champ | Valeur |
|---|---|
| Début → fin | 18,8 → 22,0 s (3,2 s) |
| Voix | « Des centaines, et maintenant, des milliers de canards. » |
| Mots | 8 |
| Durée de voix (2,5 mots/s) | 3,2 s |
| Intonation | paniqué, dépassé ; débit rapide ; volume fort |
| Mots appuyés | « centaines », « milliers » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Des **centaines** / et maintenant / des **milliers** / de canards |
| Texte à l'écran | rien (le compteur porte les nombres) |
| Compteur | 128 → 256 à 0,0 s, sur « Des » ; 256 → 512 à 1,2 s, sur « maintenant » ; 512 → 1 024 à 2,0 s, sur « milliers » ; 1 024 → 2 048 à 2,6 s, pendant « de » ; 2 048 → 4 096 à 3,0 s, pendant « canards » |

### b09 — abandon

| Champ | Valeur |
|---|---|
| Début → fin | 22,0 → 25,0 s (3,0 s) |
| Voix | « Bon, laisse tomber, tu ne comptes plus. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | résigné, soupir ; débit lent ; volume normal |
| Mots appuyés | « tomber », « plus » |
| Pauses avant / après | 0,2 / 0,0 |
| Sous-titres | Bon / laisse **tomber** / tu ne comptes / **plus** |
| Texte à l'écran | rien |
| Compteur | 4 096 (figé) |

### b10 — défi du canard à l'envers

| Champ | Valeur |
|---|---|
| Début → fin | 25,0 → 28,0 s (3,0 s) |
| Voix | « Un seul regarde de l'autre côté, trouve-le. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | complice, défi à voix basse ; débit normal ; volume bas |
| Mots appuyés | « seul », « trouve-le » |
| Pauses avant / après | 0,1 / 0,1 |
| Sous-titres | Un **seul** / regarde de / l'autre côté / **trouve-le** |
| Texte à l'écran | rien |
| Compteur | 4 096 (figé) |

### b11 — chute, il en reste un

| Champ | Valeur |
|---|---|
| Début → fin | 28,0 → 31,0 s (3,0 s) |
| Voix | « Pouf, il n'en reste qu'un. » (après 0,5 s de silence) |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | surpris puis soulagé ; débit lent ; volume normal |
| Mots appuyés | « Pouf », « qu'un » |
| Pauses avant / après | 0,5 (silence voulu, compteur figé) / 0,5 |
| Sous-titres | **Pouf** / il n'en reste / **qu'un** |
| Texte à l'écran | rien |
| Compteur | 4 096 figé de 0,0 à 0,5 s ; 4 096 → 1 à 0,5 s, sur « Pouf » |

### b12 — faux répit

| Champ | Valeur |
|---|---|
| Début → fin | 31,0 → 34,0 s (3,0 s) |
| Voix | « Tout est calme, tu peux respirer. » |
| Mots | 6 |
| Durée de voix (2,5 mots/s) | 2,4 s |
| Intonation | apaisé, faussement rassurant ; débit lent ; volume bas |
| Mots appuyés | « calme » |
| Pauses avant / après | 0,3 / 0,3 |
| Sous-titres | Tout est **calme** / tu peux / **respirer** |
| Texte à l'écran | rien |
| Compteur | 1 |

### b13 — question à l'audience

| Champ | Valeur |
|---|---|
| Début → fin | 34,0 → 37,0 s (3,0 s) |
| Voix | « Donut ou ballon, toi, tu choisis lequel ? » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | curieux, interpelle le spectateur ; débit normal ; volume normal |
| Mots appuyés | « Donut », « ballon », « toi » |
| Pauses avant / après | 0,2 / 0,0 |
| Sous-titres | **Donut** / ou **ballon** / toi, tu choisis / **lequel** |
| Texte à l'écran | « ET APRÈS ? » de 0,0 à 3,0 s (plus les étiquettes « DONUT » et « BALLON » sous les objets, prévues par le scénario, module d'habillage) |
| Compteur | 1 |

### b14 — inquiétude, boucle

| Champ | Valeur |
|---|---|
| Début → fin | 37,0 → 40,0 s (3,0 s) |
| Voix | « Attends, tu le vois trembler, celui-là ? » |
| Mots | 6 |
| Durée de voix (2,5 mots/s) | 2,4 s |
| Intonation | inquiet, chuchoté ; débit lent ; volume bas |
| Mots appuyés | « trembler » |
| Pauses avant / après | 0,2 / 0,4 |
| Sous-titres | **Attends** / tu le vois / **trembler** / celui-là |
| Texte à l'écran | « ET APRÈS ? » de 0,0 à 1,0 s (disparaît à 38,0 s avec le donut et le ballon), puis rien |
| Compteur | 1 (dernière image identique à la première) |

## Vérifications chiffrées

| Règle | Valeur mesurée | Résultat |
|---|---|---|
| Somme des durées = durée du scénario (± 1 s) | 3,0 + 2,4 + 2,4 + 2,2 + 2,8 + 3,0 + 3,0 + 3,2 + 3,0 + 3,0 + 3,0 + 3,0 + 3,0 + 3,0 = 40,0 s pour 40 s ; bornes des temps respectées (10,0 ; 25,0 ; 28,0 ; 34,0) | OK |
| Voix totale ≤ 85 % de la durée | 82 mots → 32,8 s / 40 s = 82 % | OK |
| Chaque temps du scénario couvert | 1 (b01), 2 (b02-b04), 3 (b05-b09), 3 bis (b10), 4 (b11-b12), 5 (b13-b14) | OK |
| Phrases de 5 à 12 mots | toutes (5 à 8 mots ; virgule dans la phrase de 8 mots, b08) | OK |
| Aucune phrase de 1 ou 2 mots | aucune (« Pouf » et « Facile » sont dans une phrase de 5 mots) | OK |
| Aucun grand nombre dit à voix haute | nombres dits : deux, quatre, huit ; ensuite « centaines », « milliers » ; 16 à 4 096 seulement au compteur | OK |
| Beats de 1,5 à 3 s (4 s maximum) | tous entre 2,2 et 3,0 s sauf b08 (3,2 s) | ÉCART justifié |
| Au plus 2 beats muets d'affilée | 1 seul beat muet (b07) | OK |
| Deuxième personne | b01, b04, b05, b09, b10 (impératif), b12, b13, b14 | OK |
| Pops qui accélèrent (retour du pilote) | intervalles 3,0 / 3,0 / 3,0 puis 2,8 / 2,4 / 2,0 / 1,6 / 1,2 / 0,8 / 0,6 / 0,4 s : jamais croissants | OK |

Mots par temps (écrits / visés) : 1. 7/6 · 2. 16/16 · 3. 28/28 · 3 bis. 7/7 · 4. 11/10 · 5. 13/14 · total 82/81.

## Écarts justifiés

- **b08, 3,2 s** : sommet de l'escalade, cinq pops en 3 s sur une seule phrase de 8 mots (« centaines » → « milliers » doit rester d'un seul souffle) ; la couper donnerait une phrase de moins de 5 mots. Reste sous les 4 s.
- **b07 muet, 3,0 s, au milieu de l'escalade** : le faire parler pousserait la voix au-delà de 85 % (au moins 5 mots, soit 87 mots, 87 %). Un seul pop (128) y tombe, avec un intervalle de 2,0 s : ce n'est pas un enchaînement rapide découpé en beats muets.

## Questions pour Lucas

1. **Intervalle des premiers pops** : le scénario dit « environ 2,5 s » au temps 2 ; j'ai mis 3,0 s (pops à 1, 4, 7 et 10 s). Avec 2,5 s, le pop 16 (fixé au début de l'escalade, 10 s) arriverait après 3,5 à 4 s d'attente : les pops ralentiraient juste avant l'escalade, le défaut relevé au pilote. Tu confirmes 3,0 s ?
2. **Nombre de mots** : temps 1 : 6 → 7 ; temps 4 : 10 → 11 ; temps 5 : 14 → 13 ; total 81 → 82. À valider ou à ajuster.
3. **b07 muet** dans l'escalade (15,8-18,8 s) : tu le gardes ainsi, ou tu préfères une phrase de plus, en retirant autant de mots ailleurs (par exemple au temps 5) pour rester sous 85 % ?
4. **Ton de la chute** : « Pouf » (onomatopée) et « Tout est calme, tu peux respirer » (faux répit avant le frémissement) sont des choix de texte à confirmer. Le scénario ne dit pas quel canard survit : la voix reste neutre (« il n'en reste qu'un »).
5. **Arrêt sur image (b10)** : la voix occupe 2,8 s sur 3 s, il reste peu de silence pour chercher le canard à l'envers. Accepter, ou raccourcir la phrase (par exemple « Un seul regarde ailleurs, trouve-le vite. », 6 mots) ?
