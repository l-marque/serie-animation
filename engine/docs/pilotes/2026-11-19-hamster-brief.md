# Brief de production : « 10 000 serpents contre 1 hamster », épisode de lancement

- Épisode : `hamster-jour-0`, premier épisode d'une **nouvelle série**, distincte de La Revanche du Miteux et de « 7 Jours avant l'Attaque ».
- Nom de travail : **« 10 000 serpents contre 1 hamster »** (provisoire, à confirmer par Lucas et Guillaume avant publication).
- Rédigé le 2026-11-19 par le Claude de Guillaume, à la demande de Guillaume : reprendre la mécanique du Reel de référence v3 avec un hamster à protéger et 10 000 méchants, choisis par Claude.
- Structure reprise du brief `2026-11-18-iles-jour-1-brief.md`.
- Statut : **brief validé par Guillaume le 2026-11-19** (serpents, paliers, texte, « sept jours » au lieu de « dimanche ») ; il a validé d'avance tout l'enchaînement jusqu'à la vidéo finale (« va jusqu'à la fin »). Non relu par Lucas. La publication reste manuelle et humaine.

---

## 1. Le concept

- Un **hamster seul** au milieu d'un désert (décor changé du pré au désert à la demande de Guillaume, 2026-11-19). En face, **10 000 serpents** qui veulent le manger. Ils attaquent **dans sept jours** : compte à rebours « J-7 ».
- L'audience construit l'armée du hamster : **chaque commentaire ajoute un soldat avec le pseudo de son auteur**.
- **Paliers** selon le nombre d'amis tagués dans le commentaire :

| Commentaire | Unité |
|---|---|
| sans tag | hamster soldat (casque, épée cure-dent) |
| 1 ami tagué | hamster archer |
| 2 amis tagués | hamster en boule blindée (sa boule d'exercice transformée en char) |
| 3 amis tagués | cochon d'Inde géant, trois fois plus gros |

- **Style** : personnages en blocs, comme les autres séries (`perso_bloc.py`).

### Pourquoi des serpents (choix de Claude, à valider)

1. Le serpent est un prédateur réel des petits rongeurs : la menace est comprise sans explication.
2. Silhouette très lisible en blocs (une suite de segments, une tête, une langue rouge) et simple à multiplier par 10 000.
3. Visuellement très éloigné des chats de la référence : pas de confusion avec le compte d'origine.

## 2. Ressemblance avec une vidéo existante (à garder en tête)

Le Reel v3 (« chickenvscats », `engine/docs/references-videos.md`) a exactement cette mécanique : une petite bête seule, une foule de 100 000 prédateurs, un soldat par commentaire avec le pseudo, des paliers selon les amis tagués, une bataille à date fixe (chez nous, un compte à rebours de sept jours). **Le concept de base est donc emprunté** ; c'est un point à trancher par Lucas et Guillaume avant publication.

Ce qui nous distingue : le hamster et les serpents, les paliers propres au hamster (boule blindée, cochon d'Inde géant), le style en blocs, une voix en français. On ne reprend ni leur texte, ni leur habillage (liste à cocher « JOIN THE … ARMY », titre « PART 1 »), ni leur rayon de lumière sur chaque recrue.

## 3. Le prompt à transmettre à la Production

```text
ÉPISODE DE LANCEMENT, série « 10 000 serpents contre 1 hamster » (nom provisoire). Vidéo
verticale 9:16, 1080 × 1920, 30 i/s, environ 36 à 40 s.

HISTOIRE EN UNE PHRASE
Dix mille serpents veulent manger un petit hamster tout seul ; ils attaquent dans sept jours, et
chaque commentaire ajoute un soldat à son armée, avec le pseudo de son auteur.

STYLE
- Personnages en blocs (perso_bloc.py), couleurs vives.
- DÉSERT (décor changé à la demande de Guillaume le 2026-11-19 : l'herbe haute se confondait avec la foule de serpents) : sable ocre clair en blocs, longues dunes basses, rochers, un ou deux os blanchis au premier plan, terrier du hamster = trou dans le sable au pied d'un rocher. Tempête de sable qui approche : ciel rouge sang et violet foncé, soleil rouge bas derrière la foule (contre-jour), voile de sable rougeâtre à l'horizon, couleurs sombres, vignettage marqué. Le hamster garde une petite lumière chaude pour rester mignon et lisible.
- Le hamster : petit, rond, beige et blanc, grands yeux, très attachant.
- Les serpents : en blocs segmentés, vert très foncé et violet noir, YEUX ROUGES LUMINEUX (émissifs, avec halo, pupille fendue, sourcils en blocs méchants), langue rouge ;
  un « chef » plus gros avec une cicatrice pour le gros plan de b03.
- La foule de 10 000 serpents : instances (pas 10 000 objets), ondulation décalée, qui
  remplit tout l'horizon.

VOIX (texte exact, nombres en lettres ; voix Qwen habituelle, accroche avec entrain ;
première syllabe dès 0 s ; 0,1 à 0,2 s entre les phrases ; environ 180 mots par minute)
b01  Dix mille serpents veulent manger ce hamster !
b02  Dans sept jours, ils attaquent.
b03  Ils ont faim, et ils ne laissent rien derrière eux.
b04  Pour l'instant, le hamster est tout seul... mais tu peux changer ça.
b05  Chaque commentaire sous cette vidéo ajoute un soldat à son armée, avec ton pseudo dessus.
b06  Tu commentes : tu es soldat.
b07  Tu tagues un ami : tu es archer.
b08  Deux amis : tu pilotes une boule blindée.
b09  Trois amis : tu deviens un cochon d'Inde géant, trois fois plus gros !
b10  Soldats, archers, boules blindées, cochons d'Inde...
b11  Est-ce que ça suffira contre dix mille serpents ?
b12  La bataille commence dans sept jours. Abonne-toi pour ne pas la rater !

HABILLAGE
- Badge « J-7 » permanent en haut au centre.
- Compteur permanent en haut : « 10 000 🐍 » contre « 1 🐹 » (le chiffre du hamster monte
  en b05-b10 à chaque recrue).
- Pseudos « @ton_pseudo » au-dessus de chaque recrue.
- Sous-titres mot par mot, mot clé en jaune.

SON
Sifflements de serpents en fond dès b01 ; « pop » à chaque recrue ; tambour sourd en b11 ;
musique basse et tendue.
```

## 4. Plans (proposition)

| Plan | Ce qu'on voit | Actions |
|---|---|---|
| b01 | plan large en plongée : la foule de serpents jusqu'à l'horizon, le hamster minuscule au premier plan | compteur « 10 000 » |
| b02 | gros plan sur le hamster, qui tremble | titre « DANS 7 JOURS » |
| b03 | gros plan sur le serpent chef, qui sort la langue | sifflement |
| b04 | plan large, le hamster seul dans l'herbe | — |
| b05 | un soldat hamster apparaît à côté de lui, puis trois autres | « @ton_pseudo » au-dessus de chacun, compteur hamster qui monte |
| b06 | plan sur un soldat | étiquette « SOLDAT » |
| b07 | plan sur un archer | étiquette « ARCHER » + « 1 AMI TAGUÉ » |
| b08 | une boule blindée roule dans le cadre | étiquette « BOULE BLINDÉE » + « 2 AMIS » |
| b09 | le cochon d'Inde géant arrive, contre-plongée | étiquette « COCHON D'INDE GÉANT » + « 3 AMIS » |
| b10 | toute la petite armée réunie | — |
| b11 | recul : la petite armée face à la foule immense | tambour |
| b12 | plan très large sur la foule | titre « ABONNE-TOI POUR LA BATAILLE » |

## 4 bis. L'accroche (priorité donnée par Guillaume le 2026-11-19)

Guillaume : « le plus important c'est le hook, il faut capter son attention et le garder ». Les règles ci-dessous s'appuient sur les mesures des Reels de référence (`engine/docs/references-videos.md` : voix dès 0 s, 7 à 10 mots dans les 3 premières secondes, un plan toutes les 2 s environ, sous-titres de 2 ou 3 mots).

1. **Les 2 premières secondes (b01)** : plan très serré sur le hamster, mignon, qui grignote une graine (0 à 0,7 s) ; un sifflement monte ; la caméra recule vite et en hauteur et révèle le mur de 10 000 serpents jusqu'à l'horizon, avant 2 s. Contraste immédiat entre le mignon et la menace.
2. **Titre géant dès la première image**, en deux lignes : « 10 000 SERPENTS » / « VS 1 HAMSTER » (« 1 HAMSTER » en jaune). Badge J-7 et compteur visibles dès la première image. On doit comprendre l'enjeu sans le son.
3. **b02** : le badge « J-7 » arrive avec un coup de tambour et un léger tremblement de caméra.
4. **Garder l'attention** : un changement de plan ou de cadrage toutes les 2 s au plus ; le compteur du hamster monte avec un « +1 » à chaque recrue ; les unités grossissent de palier en palier, jusqu'au cochon d'Inde géant qui remplit l'écran en b09 (le pic de la vidéo).
5. **Fin en boucle** : le dernier plan revient sur le hamster en gros plan, cadré comme la première image, pour que la relecture s'enchaîne sans coupure visible.
## 5. À produire

| Élément | Qui |
|---|---|
| Hamster, soldat, archer, boule blindée, cochon d'Inde géant (blocs) | `prod-modeleur` |
| Serpent en blocs (version foule légère + version chef) | `prod-modeleur` |
| Désert de sable (changé du pré à la demande de Guillaume le 2026-11-19), foule de 10 000 serpents en instances | `prod-modeleur` |
| Pack de DA « pre_hamster » (lumière de fin d'après-midi) | `prod-directeur-artistique` |
| Fiche épisode | `prod-realisateur` |
| Voix Qwen | `prod-directeur-voix` |

## 6. Décisions humaines à prendre

1. Serpents et paliers : validés par Guillaume le 2026-11-19.
2. Accepter ou non une mécanique empruntée au Reel v3 (voir section 2).
3. Le nom de la série. (Jour de la bataille : tranché par Guillaume, « dans sept jours ».)
4. Publication : manuelle, par Lucas ou Guillaume.

---

**Rôle de ce document** : brief de travail interne au projet, qui sert à lancer un nouvel épisode et à guider les agents de production. **Il n'a aucune valeur juridique** : ce n'est ni un contrat, ni une validation de publication, ni un avis sur les droits d'auteur ou sur la reprise d'un concept existant. La publication reste soumise à la validation explicite de Lucas ou de Guillaume.
