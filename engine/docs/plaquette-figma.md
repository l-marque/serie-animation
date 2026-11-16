# Plaquette Figma : validation avant chaque vidéo

Règle fixée par Guillaume le 2026-11-16 : **pour chaque demande de vidéo, une plaquette Figma est créée et soumise à sa validation avant tout rendu.** Rien n'est rendu dans Blender (animatique comprise) sans un « validé » explicite de sa part.

## Qui fait quoi

| Étape | Responsable |
|---|---|
| Fiche épisode (plans, voix, actions) et habillage | prod-realisateur |
| Direction artistique, détails de décor | prod-directeur-artistique |
| Recherche des modèles (3 candidats par objet important) | prod-chef, via `sources_assets.py` |
| Création de la plaquette dans Figma | la session principale (seule à avoir le connecteur Figma) |
| Validation | Guillaume |

## Où

Fichier Figma « Série animation — Outils d'affichage (HUD) » (https://www.figma.com/design/4jgvjoxBzwQDQfoXgwW0Fs) : une **page par épisode**, nommée `<episode_id> — plaquette`. Les composants HUD de la page « Kit HUD » sont réutilisés (instances), jamais redessinés.

## Contenu (dans cet ordre, de gauche à droite)

1. **En-tête** : titre de l'épisode, durée visée, voix choisie, date, statut « À VALIDER ».
2. **Découpage** : une vignette 9:16 par plan (beat) avec le mouvement de caméra, la phrase de la voix et les actions. Vignette = rendu rapide si la scène existe déjà, sinon schéma simple (blocs nommés).
3. **Modèles 3D** : pour chaque objet important, les candidats avec aperçu, source, auteur, licence, triangles ; le choix recommandé est marqué.
4. **Direction artistique** : palette, ciel/HDRI, textures de sol, références d'ambiance.
5. **Habillage** : compteurs, gains « +10 », cartes de choix, bandeaux, placés sur une vignette 9:16 avec les zones masquées par Instagram.
6. **Points à trancher** : questions ouvertes pour Guillaume (une ligne chacune).

## Après la validation

- Les corrections demandées sont appliquées à la fiche et à l'habillage, puis l'animatique est lancée.
- Le lien de la page est noté dans le rapport à Guillaume et dans le Journal de bord du Drive.
- Une relance purement technique (même fiche, bug corrigé) ne demande pas de nouvelle plaquette.
