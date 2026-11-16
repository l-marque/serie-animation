# La visite guidée — beats et voix off

- Statut : proposé, voix à valider par Lucas
- Scénario source : `docs/storytelling/scenarios/2026-11-16-la-visite-guidee-v2.md` (statut : validé par Lucas le 2026-11-16, avec réserves ; la v1 n'est pas retenue)
- Épisode : `lancement-du-club` ; état de la série : `episodes/serie/etat.json` (0 abonné, 0 €, 0 supporter)
- Durée du scénario : 40 s · Beats : 16 (dont 4 muets) · Voix : 69 mots, 27,6 s, soit 69 % de la durée
- Voix : Kevin, voix n° 12 de Kyutai, sans synchronisation des lèvres. **Débit retenu : 2,5 mots/s** (débit de référence du gabarit, § A). Aucune mesure du débit réel de la voix n° 12 n'existe dans le dépôt : la Production le mesurera. Les trois passages critiques de la réserve (d) sont aussi vérifiés avec l'estimation de repli du moteur (`engine/pipeline/realisateur.py` : 14 caractères/s, plus 0,15 s avant et 0,45 s après la voix).

## Réserves et réponses de Lucas (ARRÊT 2, 2026-11-16) : application

| Point | Ce qu'il dit | Où et comment |
|---|---|---|
| (1) | La pose bras ouverts est la pose de départ et de fin de « parle avec gestes », pas une 4e attitude | Pour `story-decoupage`. b01 commence et b16 finit sur cette pose ; aucune voix ne la décrit. |
| (2) | Le panneau « ON RÉPARE QUOI ? » reste jusqu'à 40,0 s, hors du cadre du plan final | Pour `story-decoupage`. La voix ne le cite pas après b14 ; aucun « texte à l'écran » ne le double (c'est un texte du décor). |
| (3) | Sol : terre sèche, lignes blanches sommaires, une seule touffe verte (version ratée de la « pelouse aux lignes sommaires » de la bible), à confirmer par Guillaume | Pour `story-decoupage` et Guillaume. La voix de b09 (« Gazon entretenu brin par brin ») et de b11 (« Pièce unique ») suppose une seule touffe verte : si Guillaume change le sol, ces deux beats sont à revoir. |
| (a) | Plan d'ouverture et de fin : Kevin en pied, bras ouverts entièrement dans le cadre 9:16 (plan moyen), même cadrage à 0,0 s et à 40,0 s | **Pour `story-decoupage`** : remplace le plan rapproché du scénario (0,0-2,0 s et 39,0-40,0 s). Aucun effet sur la voix : b01 et b16 gardent le même texte et la même durée. |
| (b) | Kevin a l'attitude « parle avec gestes » de 22,5 à 27,0 s | **Pour `story-decoupage`** (le scénario ne donnait pas d'attitude sur ce créneau). Cohérent avec la voix : b10 (22,5-25,0 s) est muet, b11 (25,0-27,0 s) est dit par Kevin. |
| (c) | `story-beats` corrige la liste des moments sans sous-titres | Fait : voir « Moments sans sous-titres (liste corrigée) ». Le scénario oubliait 22,5-25,0 s (aucune voix entre la phrase sur la pelouse et la vue d'en haut) et ses trois autres créneaux ne suivaient pas les vraies fins de phrase. |
| (d) | Aucune marge de voix à l'accroche, à la chute et à la phrase finale ; raccourcir si la voix n° 12 est plus lente que 2,5 mots/s | Fait : les trois passages sont raccourcis dès maintenant (accroche et phrase finale 8 → 7 mots, phrase de la tribune 6 → 5 mots, question finale 9 → 7 mots) et tiennent aussi avec l'estimation de repli du moteur ; une version encore plus courte est prête si le débit mesuré passe sous le seuil indiqué. Voir « Marges de la réserve (d) ». |

## Correspondance temps → beats

| Temps du scénario | Secondes | Beats |
|---|---|---|
| 1. Accroche | 0,0-3,0 | b01 |
| 2. Mise en situation | 3,0-8,0 | b02, b03 |
| 3 a. Escalade : « TRIBUNE VIP » | 8,0-14,0 | b04, b05 |
| 3 b. Escalade : « ÉCLAIRAGE » | 14,0-20,5 | b06, b07, b08 |
| 3 c. Escalade : « PELOUSE » | 20,5-27,0 | b09, b10, b11 |
| 4. Chute | 27,0-35,5 | b12, b13, b14 |
| 5. Boucle | 35,5-40,0 | b15, b16 |

Mots par temps (écrits / visés par le scénario) : 1. 7/8 · 2. 11/11 · 3 a. 13/13 · 3 b. 9/10 · 3 c. 10/10 · 4. 12/15 · 5. 7/8 · total 69/75.

## Beats

### b01 — bienvenue, accroche

| Champ | Valeur |
|---|---|
| Début → fin | 0,0 → 3,0 s (3,0 s) |
| Voix | « Bienvenue au plus grand stade du monde. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | fier, très sûr de lui, ton d'agent immobilier de luxe ; débit normal ; volume fort |
| Mots appuyés | « Bienvenue », « monde » |
| Pauses avant / après | 0,2 / 0,0 |
| Sous-titres | Bienvenue / au plus / grand stade / du monde (sans mot surligné, bible § 9 ; « Bienvenue » affiché dès 0,0 s) |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € (permanents dès 0,0 s, fixes) ; aucun changement |

Note pour `story-decoupage` : Kevin à K0, « parle avec gestes », pose bras ouverts dès 0,0 s (réponse 1), plan moyen en pied (réserve a). Le recul de caméra du scénario commence à 2,0 s, sur « stade » ; ce n'est pas une action déclenchée par un mot. Le scénario autorise la voix jusqu'à 3,4 s (0,4 s sur le début du temps 2).

### b02 — le président

| Champ | Valeur |
|---|---|
| Début → fin | 3,0 → 5,6 s (2,6 s) |
| Voix | « Je suis président du FC Miteux, » |
| Mots | 6 |
| Durée de voix (2,5 mots/s) | 2,4 s |
| Intonation | aplomb, solennel ; débit normal ; volume normal |
| Mots appuyés | « président », « Miteux » |
| Pauses avant / après | 0,2 / 0,0 |
| Sous-titres | Je suis / président / du FC Miteux |
| Texte à l'écran | rien (le nom du club n'est écrit nulle part, scénario) |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b03 — et seul joueur

| Champ | Valeur |
|---|---|
| Début → fin | 5,6 → 8,0 s (2,4 s) |
| Voix | « Entraîneur, et le seul joueur. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | même aplomb, fierté sur « seul » comme si c'était un exploit ; débit normal ; volume normal |
| Mots appuyés | « seul » |
| Pauses avant / après | 0,1 / 0,3 |
| Sous-titres | Entraîneur / et le seul / joueur |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

b02 et b03 forment une seule phrase de 11 mots, coupée en deux beats (règle : plus de 10 mots).

### b04 — début de la visite

| Champ | Valeur |
|---|---|
| Début → fin | 8,0 → 10,5 s (2,5 s) |
| Voix | « On commence par l'espace VIP. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | agent immobilier de luxe, mielleux ; débit normal ; volume normal |
| Mots appuyés | « VIP » |
| Pauses avant / après | 0,2 / 0,3 |
| Sous-titres | On commence / par l'espace / VIP |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b05 — la caisse VIP

| Champ | Valeur |
|---|---|
| Début → fin | 10,5 → 14,0 s (3,5 s) |
| Voix | « Tribune VIP, places limitées, tout le confort moderne. » |
| Mots | 8 |
| Durée de voix (2,5 mots/s) | 3,2 s |
| Intonation | vendeur enthousiaste, très sérieux ; débit normal ; volume normal |
| Mots appuyés | « limitées », « confort » |
| Pauses avant / après | 0,2 / 0,1 |
| Sous-titres | Tribune VIP / places limitées / tout le confort / moderne |
| Texte à l'écran | rien (texte du décor : panneau « TRIBUNE VIP ») |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

Actions du scénario dans ce beat : panneau « TRIBUNE VIP » qui surgit à 0,0 s (10,5 s, sur la coupe, juste avant « Tribune ») ; la caisse oscille à partir de 1,0 s (11,5 s), sur « places », jusqu'à la fin du beat.

### b06 — l'éclairage

| Champ | Valeur |
|---|---|
| Début → fin | 14,0 → 16,0 s (2,0 s) |
| Voix | « Et ici, l'éclairage dernier cri. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | fier, présentateur ; débit normal ; volume normal |
| Mots appuyés | « dernier cri » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Et ici / l'éclairage / dernier cri |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

La voix peut déborder jusqu'à 16,5 s sur le beat muet suivant (créneau du scénario : 14,1-16,5 s) sans gêner aucune action.

### b07 — le lampadaire disparaît

| Champ | Valeur |
|---|---|
| Début → fin | 16,0 → 18,9 s (2,9 s) |
| Voix | muet : le panneau « ÉCLAIRAGE » surgit (pop) à 0,0 s, le lampadaire rétrécit à 1,0 s puis disparaît à 2,5 s |
| Mots | 0 |
| Durée de voix (2,5 mots/s) | 0,0 s |
| Intonation | — |
| Mots appuyés | aucun |
| Pauses avant / après | 2,9 (beat muet) |
| Sous-titres | — |
| Texte à l'écran | rien (texte du décor : panneau « ÉCLAIRAGE ») |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b08 — comme si de rien n'était

| Champ | Valeur |
|---|---|
| Début → fin | 18,9 → 20,5 s (1,6 s) |
| Voix | « Ambiance tamisée, très tendance. » |
| Mots | 4 |
| Durée de voix (2,5 mots/s) | 1,6 s |
| Intonation | imperturbable, comme si rien ne s'était passé ; débit normal ; volume normal |
| Mots appuyés | « tamisée » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Ambiance / tamisée / très tendance |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b09 — la pelouse annoncée

| Champ | Valeur |
|---|---|
| Début → fin | 20,5 → 22,5 s (2,0 s) |
| Voix | « Gazon entretenu brin par brin. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | précieux, presque ému ; débit lent ; volume normal |
| Mots appuyés | « brin par brin » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Gazon entretenu / brin / par brin |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b10 — la touffe

| Champ | Valeur |
|---|---|
| Début → fin | 22,5 → 25,0 s (2,5 s) |
| Voix | muet : le panneau « PELOUSE » surgit (pop) à 0,0 s, la touffe gonfle de fierté à 1,0 s |
| Mots | 0 |
| Durée de voix (2,5 mots/s) | 0,0 s |
| Intonation | — |
| Mots appuyés | aucun |
| Pauses avant / après | 2,5 (beat muet) |
| Sous-titres | — |
| Texte à l'écran | rien (texte du décor : panneau « PELOUSE ») |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

Réserve (b) : Kevin est en « parle avec gestes » de 22,5 à 27,0 s, même pendant ce beat muet.

### b11 — pièce unique

| Champ | Valeur |
|---|---|
| Début → fin | 25,0 → 27,0 s (2,0 s) |
| Voix | « Pièce unique, rien que ça. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | assume tout, satisfait ; débit normal ; volume normal |
| Mots appuyés | « unique » |
| Pauses avant / après | 0,0 / 0,0 |
| Sous-titres | Pièce unique / rien que ça |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b12 — la tribune des supporters

| Champ | Valeur |
|---|---|
| Début → fin | 27,0 → 30,0 s (3,0 s) |
| Voix | « Et là, mes supporters déchaînés. » |
| Mots | 5 |
| Durée de voix (2,5 mots/s) | 2,0 s |
| Intonation | fierté maximale, grand geste ; débit normal ; volume fort |
| Mots appuyés | « déchaînés » |
| Pauses avant / après | 0,2 / 0,8 |
| Sous-titres | Et là / mes supporters / déchaînés |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

La voix finit à 29,2 s, avant la coupure de la voix et de la musique à 30,0 s.

### b13 — tribune vide, silence

| Champ | Valeur |
|---|---|
| Début → fin | 30,0 → 31,5 s (1,5 s) |
| Voix | muet : silence voulu, voix et musique coupées, plan fixe sur la tribune vide (0 supporter) |
| Mots | 0 |
| Durée de voix (2,5 mots/s) | 0,0 s |
| Intonation | — |
| Mots appuyés | aucun |
| Pauses avant / après | 1,5 (beat muet) |
| Sous-titres | — |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b14 — la question aux abonnés

| Champ | Valeur |
|---|---|
| Début → fin | 31,5 → 35,5 s (4,0 s) |
| Voix | « On répare quoi d'abord ? Dis-le en commentaire. » |
| Mots | 7 (4 + 3) |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | toujours enjoué, comme si tout était normal, question franche puis appel complice ; débit normal ; volume normal |
| Mots appuyés | « répare », « commentaire » |
| Pauses avant / après | 0,1 / 1,1 |
| Sous-titres | On répare / quoi d'abord / Dis-le / en commentaire |
| Texte à l'écran | rien (texte du décor : panneau « ON RÉPARE QUOI ? ») |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

Action du scénario : le panneau « ON RÉPARE QUOI ? » surgit à 0,5 s (32,0 s), sur « répare » (2e mot de 7), et finit à 1,1 s (32,6 s), 2,9 s avant la fin du beat. La voix continue sur la coupe de 33,5 s (plan sur le panneau) et finit à 34,4 s.

### b15 — aller-retour vers la tribune

| Champ | Valeur |
|---|---|
| Début → fin | 35,5 → 36,5 s (1,0 s) |
| Voix | muet : Kevin se tourne vers la tribune vide, puis revient face caméra |
| Mots | 0 |
| Durée de voix (2,5 mots/s) | 0,0 s |
| Intonation | — |
| Mots appuyés | aucun |
| Pauses avant / après | 1,0 (beat muet) |
| Sous-titres | — |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement |

### b16 — bienvenue, boucle

| Champ | Valeur |
|---|---|
| Début → fin | 36,5 → 40,0 s (3,5 s) |
| Voix | « Bienvenue au plus grand stade du monde. » |
| Mots | 7 |
| Durée de voix (2,5 mots/s) | 2,8 s |
| Intonation | même aplomb qu'en b01, comme si rien ne s'était passé ; débit normal ; volume fort |
| Mots appuyés | « Bienvenue », « monde » |
| Pauses avant / après | 0,2 / 0,5 |
| Sous-titres | Bienvenue / au plus / grand stade / du monde (« du monde » reste affiché jusqu'à 40,0 s, seul écart toléré avec la première image) |
| Texte à l'écran | rien |
| Compteur | abonnés 0 ; cagnotte 0 € ; aucun changement (identique à 0,0 s) |

Note pour `story-decoupage` : texte strictement identique à b01, pour la boucle. Kevin en « parle avec gestes », bras ouverts sur la dernière image (réponse 1), plan moyen en pied, même cadrage qu'à 0,0 s (réserve a) ; le panneau « ON RÉPARE QUOI ? » reste hors du cadre final (réponse 2). À la jonction, 0,5 s de silence à la fin et 0,2 s au début : 0,7 s sans voix entre « du monde » et « Bienvenue ».

## Moments sans sous-titres (liste corrigée, réserve c)

Un sous-titre s'affiche de la première à la dernière syllabe de sa phrase. Fenêtres de voix estimées à 2,5 mots/s : 0,2-3,0 · 3,2-5,6 · 5,7-7,7 · 8,2-10,2 · 10,7-13,9 · 14,0-16,0 · 18,9-20,5 · 20,5-22,5 · 25,0-27,0 · 27,2-29,2 · 31,6-34,4 · 36,7-39,5 s.

| Créneau sans sous-titre | Beat | Ce qui le porte | Dans la liste du scénario ? |
|---|---|---|---|
| 16,0-18,9 s | b07 | panneau « ÉCLAIRAGE », lampadaire qui rétrécit puis disparaît | oui, mais à partir de 16,5 s ; corrigé en 16,0 s |
| 22,5-25,0 s | b10 | panneau « PELOUSE », touffe qui gonfle | **non, oublié** ; ajouté |
| 29,2-31,6 s | fin de b12, b13 | tribune vide, silence de 30,0 à 31,5 s | oui, mais 30,0-31,5 s ; corrigé en 29,2-31,6 s |
| 34,4-36,7 s | fin de b14, b15, début de b16 | panneau « ON RÉPARE QUOI ? », aller-retour de Kevin | oui, mais 35,5-36,5 s ; corrigé en 34,4-36,7 s |

Trous de moins de 0,6 s entre deux phrases (3,0-3,2 ; 5,6-5,7 ; 7,7-8,2 ; 10,2-10,7 ; 13,9-14,0 s) : proposition, le groupe précédent reste affiché, pour éviter un clignotement. Boucle : « Bienvenue » s'affiche dès 0,0 s et « du monde » reste jusqu'à 40,0 s (seul écart toléré entre la première et la dernière image). Ces bornes bougeront avec la voix réelle : le montage les recale sur les vraies fins de phrase.

## Marges de la réserve (d)

| Passage | Créneau disponible pour la voix | Texte | Estimation à 2,5 mots/s | Estimation de repli du moteur (14 car./s + 0,6 s) | Débit minimal qui tient | Si le débit mesuré est plus lent |
|---|---|---|---|---|---|---|
| Accroche (b01) | 0,2-3,4 s (le scénario autorise 0,4 s sur le temps 2) | 7 mots, 39 caractères | 2,8 s, finit à 3,0 s | 3,4 s, finit à 3,4 s | 2,2 mots/s | « Bienvenue au plus grand stade. » (5 mots, 2,0 s ; le sous-titre de boucle devient « grand stade ») |
| Chute, tribune (b12) | 27,2-30,0 s (coupure à 30,0 s) | 5 mots, 32 caractères | 2,0 s, finit à 29,2 s | 2,9 s, finit à 29,9 s | 1,8 mot/s | « Et là, mes supporters. » (4 mots) |
| Chute, question (b14) | 31,6-35,5 s | 7 mots, 47 caractères | 2,8 s, finit à 34,4 s | 4,0 s, finit à 35,5 s | 1,8 mot/s | « On répare quoi d'abord, dis-moi ? » (5 mots, une seule phrase) |
| Phrase finale (b16) | 36,7-40,0 s | 7 mots, 39 caractères | 2,8 s, finit à 39,5 s | 3,4 s, finit à 39,9 s | 2,1 mots/s | même version courte qu'en b01 (le texte doit rester identique pour la boucle) |

Règle pour la Production : si la voix réelle d'un de ces passages déborde de son créneau, on passe à la version courte (b01 et b16 ensemble) au lieu d'allonger le beat.

## Vérifications chiffrées

| Règle | Valeur mesurée | Résultat |
|---|---|---|
| Somme des durées = durée du scénario (± 1 s) | 3,0 + 2,6 + 2,4 + 2,5 + 3,5 + 2,0 + 2,9 + 1,6 + 2,0 + 2,5 + 2,0 + 3,0 + 1,5 + 4,0 + 1,0 + 3,5 = 40,0 s pour 40 s ; bornes des temps respectées (3,0 ; 8,0 ; 14,0 ; 20,5 ; 27,0 ; 35,5) | OK |
| Voix totale ≤ 85 % de la durée | 69 mots → 27,6 s / 40 s = 69 % | OK |
| Chaque temps du scénario couvert | 1 (b01), 2 (b02-b03), 3 a (b04-b05), 3 b (b06-b08), 3 c (b09-b11), 4 (b12-b14), 5 (b15-b16) | OK |
| Phrases de 5 à 12 mots | toutes sauf b08 (4 mots) et les deux phrases de b14 (4 et 3 mots) ; b02 + b03 = une phrase de 11 mots avec virgules | ÉCART justifié |
| Aucune phrase de moins de 3 mots | aucune (la plus courte : « Dis-le en commentaire », 3 mots) | OK |
| Nombres en lettres, aucun nombre composé dit, chaque nombre dit montré par un compteur | aucun nombre dit ; compteurs 0 abonné et 0 € permanents et fixes (`etat.json`) | OK |
| Mot déclencheur dans la première moitié de sa phrase | b05 : panneau sur la coupe, juste avant « Tribune » (1er mot), oscillation sur « places » (3e mot sur 8) ; b14 : panneau sur « répare » (2e mot sur 7) ; les autres actions tombent dans des beats muets ou sur des coupes | OK |
| Beats de 1,5 à 3 s (4 s maximum) | hors règle : b05 (3,5 s), b14 (4,0 s), b16 (3,5 s), b15 (1,0 s) | ÉCART justifié |
| Au plus 2 beats muets d'affilée | 4 beats muets (b07, b10, b13, b15), jamais deux d'affilée | OK |
| Deuxième personne | b14 (« Dis-le ») seulement ; le reste est Kevin qui fait visiter, en « je », « on », « mes » | ÉCART justifié |

## Écarts justifiés

- **b05, 3,5 s** : le plan sur la caisse dure 3,5 s dans le scénario (10,5-14,0 s), avec une intention de 8 mots. Deux phrases d'au moins 5 mots feraient 4,0 s : impossible dans le créneau. Reste sous 4 s.
- **b14, 4,0 s, phrases de 4 et 3 mots** : le scénario demande 2 phrases d'au moins 3 mots sur 31,6-35,2 s. Un seul beat évite de payer deux fois la respiration ajoutée par le moteur (0,6 s par beat), ce qui laisse 1,1 s de marge à la chute (réserve d). Reste à 4 s, le maximum.
- **b16, 3,5 s** : la phrase finale doit être identique à celle de l'accroche (boucle) et le créneau du scénario fait 3,5 s (36,5-40,0 s). La couper casserait la boucle.
- **b15, 1,0 s** : plan d'1,0 s imposé par le scénario (aller-retour muet de Kevin, 35,5-36,5 s), déjà signalé comme plus court que la règle. `story-decoupage` peut l'allonger en le commençant plus tôt, sur le plan du panneau : la voix de b14 finit à 34,4 s, rien ne gêne.
- **b08, 4 mots en 1,6 s** : le scénario fixe 4 mots entre la disparition du lampadaire (18,9 s) et la coupe (20,5 s). 4 mots est au-dessus du minimum Kyutai (3 mots).
- **Deuxième personne rare** : le scénario fait parler Kevin en guide, en « je » et « on ». La deuxième personne arrive avec l'appel aux abonnés (b14). En ajouter ailleurs ferait dépasser les créneaux.
- **Sous-titres sans mot en gras** : la bible (§ 9, décision de Lucas et Guillaume) et le scénario veulent des sous-titres sans mot surligné. Cette décision passe avant le format par défaut de `story-beats`.
- **Beats sans pause (b06, b08, b09, b11)** : la voix remplit exactement leur créneau à 2,5 mots/s. b06 et b09 peuvent déborder sur le beat muet suivant sans gêne. b08 et b11 n'ont pas de marge (voir question 3).
- **Pour `story-decoupage`, actions du scénario proches de la règle « fini 1 s avant la fin du beat »** : la touffe finit de gonfler à 24,1 s pour une coupe à 25,0 s (0,9 s) ; le lampadaire disparaît à 18,9 s, à la fin de b07, mais le plan continue jusqu'à 20,5 s, donc le résultat reste visible 1,6 s ; la caisse oscille jusqu'à la coupe de 14,0 s (mouvement continu, pas un résultat à lire).

## Questions pour Lucas

1. **Mots en moins qu'au scénario (réserve d)** : accroche et phrase finale 8 → 7 mots (« Bienvenue au plus grand stade du monde » au lieu de « dans le plus grand stade du monde ») ; tribune 6 → 5 mots ; question finale 9 → 7 mots ; « ÉCLAIRAGE » 10 → 9 ; total 75 → 69. Tu valides ces coupes ?
2. **Choix de texte à confirmer** : « places limitées » (b05, une seule caisse), « Ambiance tamisée, très tendance » (b08, après la disparition du lampadaire), « Pièce unique, rien que ça » (b11, la touffe) et « mes supporters déchaînés » (b12, sur la tribune vide). La version la plus proche de l'intention du scénario serait « Voici la tribune de mes supporters » (6 mots), mais elle déborde de 0,1 s avec l'estimation de repli du moteur. Ça te va ?
3. **b08 et b11 sans marge** : ils remplissent exactement leur créneau (1,6 et 2,0 s) et sont suivis d'une phrase. Avec l'estimation de repli du moteur, ils dépasseraient d'environ 1,3 s et 0,5 s. Si la voix mesurée déborde, je propose « Ambiance tamisée, magnifique » (3 mots) et « Une pièce unique » (3 mots). Ou tu préfères faire mesurer d'abord la voix n° 12 ?
4. **Débit de la voix n° 12** : aucune mesure dans le dépôt, j'ai gardé 2,5 mots/s. Faut-il demander à Guillaume une mesure (une phrase test de 7 mots) avant `story-decoupage`, pour savoir tout de suite s'il faut les versions courtes ?
5. **Jonction de la boucle** : 0,7 s sans voix entre « du monde » (39,5 s) et « Bienvenue » (0,2 s). Tu gardes ce petit souffle, ou on resserre (pause après b16 ramenée à 0,2 s, la voix commençant alors à 37,0 s) ?
