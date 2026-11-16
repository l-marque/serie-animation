# Gabarit de réalisation

- Source : note Drive `01_Claude_Lucas/2026-11-16_claude-lucas_gabarit-realisation` (Claude de Lucas, 2026-11-16), recopiée dans le dépôt.
- Statut : référence commune des agents `story-scenario`, `story-beats` et `story-decoupage`. **Liste en attente des commentaires de Guillaume** (ce qui manque, formats à corriger) ; toute modification passe par une PR.
- Décision de Lucas (2026-11-16, 8 h 54) : le pôle Storytelling livre un document où tout est décidé, pour que la production n'ait plus qu'à construire. Deux agents : `story-beats` (voix, phrase par phrase) et `story-decoupage` (plan par plan). Pas de `story-fiche` : la traduction en JSON et la validation restent à `prod-realisateur`.

## Pourquoi ce gabarit

`story-scenario` écrivait des intentions de voix off et des temps de 6 à 15 s ; `prod-realisateur` a besoin du texte exact et l'inventait sinon (pilote canard, `engine/docs/pilotes/2026-11-15-canard.md`). Ce gabarit liste environ 40 paramètres, rangés en 4 niveaux, avec pour chacun le champ du contrat fiche épisode v1.0 qui le porte, ou « absent → v1.1 ».

**Conséquence tant que la v1.1 n'existe pas** : les paramètres « absent → v1.1 » sont écrits par les agents, mais ne passent pas dans la fiche JSON. Ils servent de consigne lisible par un humain et par `prod-realisateur`, et sont listés dans la section « Non porté par le contrat v1.0 (v1.1) » du découpage.

Les exemples illustrent le format avec le scénario du canard ou les valeurs du pack de test : **ce ne sont pas des décisions**. « à fixer » = aucune valeur n'existe encore.

## A. Charte de série (fixée une fois, par Lucas et Guillaume)

Aucun agent ne remplit ce niveau : il est décidé par les humains. Un agent qui en a besoin et le trouve « à fixer » le signale dans ses questions.

| Paramètre | Format attendu | Exemple | Champ du contrat v1.0 |
|---|---|---|---|
| Police des sous-titres | nom de police + graisse | « Arial » (valeur du pack `test_lowpoly`) | `pack_da.sous_titres.police` |
| Taille et couleur des sous-titres | taille relative à la hauteur, couleur, contour | 0,042 ; blanc ; contour sombre | `pack_da.sous_titres` |
| Couleur du mot surligné | couleur | à fixer | absent → v1.1 |
| Police et style du texte à l'écran | police, taille, couleur, contour | Arial, 0,055, blanc | `pack_da.texte_ecran` |
| Style du compteur | police, position, animation au changement | à fixer | absent → v1.1 (module habillage) |
| Palette et matériaux | couleurs par rôle (sol, personnage, accent…) | pack de DA | `pack_da.materiaux` |
| Lumière et étalonnage par défaut | soleil, monde, exposition | pack de DA | `pack_da.soleil` / `monde` / `exposition` |
| Voix de la série | voix Kyutai, débit de base (mots/s) | fabieng-enhanced-v2 ; 2,5 mots/s | `audio` (à préciser) |
| Musique de la série | style, tempo, licence | à fixer | `audio` (à préciser) |
| Transitions | coupe sèche / fondu / autre, par défaut | coupe sèche | absent → v1.1 |
| Signature de fin | logo, texte, durée | à fixer | absent → v1.1 |
| Format | 9:16, 1080 × 1920, durée cible | 9:16, 30-45 s | `format` |

## B. Épisode (rempli par `story-scenario`)

| Paramètre | Format attendu | Exemple | Champ du contrat v1.0 |
|---|---|---|---|
| Durée totale | secondes | 40 s | calculée depuis les beats |
| Pack de DA | nom du pack | à choisir | `pack_da` |
| Décor | lieu, primitives, sol, fond | baignoire, sol simple, mur neutre | `decor` |
| Éléments et quantités | id, asset, nombre, position x/y/z, échelle, visible au début | canard × 1 → × 4 096 | `elements` / `modules` |
| Assets externes | id, source, licence, vérifié par | baignoire, canard, donut, ballon | asset `bibliotheque:…` |
| Ambiance lumière | moment de la journée, intention | salle de bain, lumière douce | pack de DA (pas par épisode) |
| Musique de l'épisode | début, montées, coupure, volume sous la voix | silence à 28 s | `audio` (à préciser) |
| Hook | ce qui bouge dans la 1re seconde | pop à 1 s, compteur 1 → 2 | beat 1 |
| Boucle | dernière image = première ? écarts tolérés | oui, cadrage identique | absent → v1.1 |
| Question à l'audience | texte, moment, éléments à l'écran | « Et après ? » 34-38 s | `texte_ecran` (limité) |

## C. Chaque phrase de voix, ou beat (rempli par `story-beats`)

| Paramètre | Format attendu | Exemple | Champ du contrat v1.0 |
|---|---|---|---|
| Texte exact de la voix | phrase de 4 à 10 mots dans la note Drive ; **les agents appliquent 5 à 12 mots** (règle Kyutai de `prod-realisateur`, plus récente), ou « muet » | « Toi aussi, tu vois deux canards ? » | `beat.voix` |
| Nombre de mots et durée | mots, secondes (2,5 mots/s) | 7 mots, 2,8 s | `beat.duree_s` (calculée) |
| Intonation | émotion, débit (lent / normal / rapide), volume | faussement calme, lent, bas | absent → v1.1 |
| Mots appuyés | liste de mots | « deux » | absent → v1.1 |
| Pauses et silences | avant / après, en secondes | 0,5 s de silence avant | `beat.duree_s` (beat muet) |
| Sous-titre | découpage en groupes de 1 à 3 mots, mot surligné | TOI AUSSI / tu vois / DEUX canards | absent → v1.1 (montage mot à mot aujourd'hui) |
| Texte à l'écran | 1 à 4 mots, majuscules, ou rien | « 2 » | `beat.texte_ecran` |
| Compteur | valeur affichée à chaque instant | 1 → 2 à 1,0 s | absent → v1.1 |

## D. Chaque plan (rempli par `story-decoupage`)

| Paramètre | Format attendu | Exemple | Champ du contrat v1.0 |
|---|---|---|---|
| Mouvement de caméra | un des 7 mouvements du vocabulaire | `plan_fixe` | `beat.plan.camera` |
| Cible | id de l'élément visé | `canard_1` | `beat.plan.cible` |
| Distance, hauteur, focale | mètres, mètres, mm | 6 ; 1,5 ; 35 | `beat.plan.distance` / `hauteur` / `focale` |
| Angle et cadrage | face, trois quarts, plongée ; place du sujet dans l'image | trois quarts, sujet au centre | absent → v1.1 |
| Coupe ou transition vers le plan suivant | coupe / fondu / raccord | coupe | absent → v1.1 |
| Actions | type, cible, mot déclencheur, durée, paramètres | `apparaitre` `canards_2` sur « deux », 0,4 s | `beat.actions` |
| Position dans l'image (zone sûre) | haut / centre / bas, marges | compteur en haut | absent → v1.1 |
| Effets sonores | son, instant (mot ou seconde), volume | pop sur « deux » | `audio` / effets (à préciser) |
| Volume de la musique sous la voix | dB ou niveau | −18 dB | `audio` (à préciser) |
| Lisible sans le son ? | oui / non + ce qui porte le sens à l'image | oui : le compteur | contrôle (pas un champ) |

## Questions ouvertes (reprises de la note Drive)

- Guillaume : qu'est-ce qui manque dans cette liste pour que tu n'aies plus rien à décider ? Quels formats sont mauvais pour toi ?
- Guillaume : d'accord pour que `prod-realisateur` suive le découpage de `story-decoupage` au lieu de rechoisir les plans ?
- Lucas et Guillaume : contrat v1.1 avec les champs « absent → v1.1 » ? Quand fixez-vous la charte de série (section A) ?
