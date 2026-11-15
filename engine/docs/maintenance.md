# Maintenance du pipeline de production

Ce guide s'adresse à la session de développement (Guillaume et son Claude Code) qui corrige le pipeline ou lui ajoute une brique. Ce n'est pas un agent : conformément à l'organigramme (seuls `prod-chef`, `prod-realisateur` et `prod-controle-qualite` ont un fichier d'agent, plus `prod-directeur-artistique` ajouté à la demande de Guillaume), la maintenance se fait dans une session normale, avec le modèle le plus capable disponible. Chaque brique ajoutée sera réutilisée gratuitement dans tous les épisodes suivants. À lire d'abord : `CLAUDE.md`, `CONTRIBUTING.md`, `engine/docs/architecture.md` et `engine/docs/conventions-blender.md`.

## Quand intervenir

1. **Échec du pipeline** : `rapport.json` indique l'étape bloquante ; `renders/<id>/<mode>/blender.log` contient la trace Blender.
2. **Brique manquante** : une fiche a besoin d'une action, d'un mouvement de caméra, d'une primitive, d'un module procédural ou d'un pack de DA qui n'existe pas.
3. **Amélioration** demandée par un humain (performance, qualité visuelle, nouvelle option).

## Carte du code

| Où | Quoi |
|---|---|
| `contracts/fiche-episode.schema.json` | contrat d'entrée (toute nouvelle option commence ici) |
| `engine/pipeline/contrat.py` | validation de structure et de cohérence |
| `engine/pipeline/realisateur.py` | timeline maître (durées, mots, frames) |
| `engine/pipeline/run.py` | chef d'orchestre, codes de sortie, champ `suite` |
| `engine/pipeline/cache.py`, `montage.py`, `qa_auto.py`, `bibliothecaire.py`, `continuite.py` | modules hors Blender |
| `engine/blender/construire_scene.py` | point d'entrée Blender |
| `engine/blender/decorateur.py` | décor, prototypes, modules procéduraux |
| `engine/blender/animateur.py` | une méthode par action (`apparaitre`, `deplacer`…) |
| `engine/blender/camera.py` | mouvements de caméra (`trajectoire`) |
| `engine/blender/look.py` | matériaux par rôle, monde, moteur, contours |
| `engine/blender/kits/primitifs.py` | primitives low-poly |
| `engine/packs_da/*.json` | packs de direction artistique |
| `tests/engine/` | tests (pytest) |

## Recettes

**Nouvelle action** (ex. `sauter`) :
1. Ajouter le nom dans l'`enum` du schéma (`$defs.action.properties.type`).
2. Règles de cohérence dans `contrat.py` (paramètres requis, cible objet ou module ?).
3. Méthode `sauter(self, a)` dans `Animateur` (l'appel est automatique par son nom).
4. Si l'action modifie l'état persistant, la gérer dans `continuite.etat_final`.
5. Documenter dans `contracts/vocabulaire-actions.md`.
6. Test dans `tests/engine/`.

**Nouveau mouvement de caméra** : `enum` du schéma (`$defs.plan.properties.camera`) + branche dans `camera.trajectoire` + doc + test de trajectoire.

**Nouvelle primitive** : fonction dans `kits/primitifs.py` + entrée dans `PRIMITIVES` **et** dans `engine/pipeline/chemins.py` (un test vérifie la concordance). Une seule pièce `principale`, chaque pièce avec un rôle.

**Nouveau pack de DA** : copier `engine/packs_da/test_lowpoly.json`, garder toutes les clés (les 8 rôles de matériaux sont obligatoires), puis rendre `episodes/exemples/demo_001.json` avec ce pack pour comparer.

## Méthode de travail

1. **Reproduire** avant de corriger : relance la commande exacte du rapport, lis le journal en entier autour de l'erreur.
2. **Corriger à la racine**, pas en contournant dans une fiche. Un défaut qui touche un épisode touchera les suivants.
3. **Tester** :
   ```bash
   python -m pytest tests/engine -q
   python -m engine.pipeline.run episodes/exemples/demo_001.json --mode animatique --pourcent 25 --moteur BLENDER_WORKBENCH
   ```
   Si Blender n'est pas installé dans l'environnement, `pip install bpy` (même version majeure que celle de Guillaume, actuellement 5.3) permet de tester avec `--blender python`.
4. **Vérifier visuellement** la planche contact produite (lis l'image).
5. **Branche + PR** (`fix/…` ou `feature/…`), message de commit en français à l'infinitif, PR relue par l'autre humain. Jamais de push sur `main`, jamais de fusion de sa propre PR.

## Exigences de qualité (non négociables)

- Pas de chemin en dur : tout passe par `engine/pipeline/chemins.py` ou par la timeline.
- Déterminisme : toute part d'aléatoire passe par une `seed` de la fiche.
- Compatibilité Blender : l'API des actions a changé en 4.4/5.0 ; utiliser `commun.cle()` et `commun.fcurves()` plutôt que `action.fcurves`.
- Performance : instancier (empties + collections prototypes), ne jamais dupliquer des maillages ; au-delà de ~5 000 instances, passer aux Geometry Nodes.
- Messages d'erreur actionnables (en français, avec la valeur fautive et la correction attendue).
- Toute modification de `engine/blender/` invalide le cache de rendu (empreinte du code) : c'est voulu.

## Compte rendu attendu en fin d'intervention

```
DIAGNOSTIC : <cause racine en une ou deux phrases>
CORRECTION : <fichiers modifiés et pourquoi>
TESTS : pytest <n passés / n> · rendu de contrôle <OK | KO> (planche vérifiée : oui/non)
BRANCHE / PR : <nom> / <lien ou « à ouvrir »>
SUITE : prod-chef (relancer l'épisode) | humain (relire la PR)
ÉTAT RÉEL : fait et vérifié / fait non vérifié / non fait
```
