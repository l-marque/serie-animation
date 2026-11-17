# Modéliser soi-même : l'atelier (`engine/outils/atelier/`)

Quand aucune banque libre n'a le bon modèle, Claude le construit lui-même en Python dans Blender, au lieu de se contenter de primitives empilées. Le modèle reste un script versionné : on peut le relire, le modifier et le régénérer.

## Contenu

| Fichier | Rôle |
|---|---|
| `formes.py` | briques de modélisation : `boite` (bords biseautés), `tube` (raccords arrondis), `tube_courbe` (Bézier : tuyaux, rambardes, montants cintrés), `revolution` (profil tourné : poteaux, vases, têtes), `organique` (modificateur Skin + subdivision : corps, membres, branches), `filet` (grille de cordes avec affaissement), `miroir_x`, `usure`, `fusionner`, `exporter` |
| `blender_direct.py` | pilote **le Blender ouvert** en direct par le pont de l'extension « MCP » de Blender Lab (port 9876) : exécute du Python (`-c` ou un fichier) et capture la vue 3D (`--capture vue.png`) pour voir le résultat |
| `apercu.py` | planche 2 × 2 (face, trois-quarts, profil, plongée) avec une silhouette de 1,75 m pour l'échelle |
| `modeles/<id>.py` | un script par modèle ; il écrit `engine/assets/modeles/<id>/<id>.glb` |

## Travail en direct dans Blender

Dans Blender : extension MCP activée, « Start MCP Bridge Server ». Claude envoie son code avec `blender_direct.py`, regarde la capture de la vue 3D, corrige, puis exporte le modèle en GLB dans `engine/assets/modeles/` (même enregistrement qu'à l'étape 5 ci-dessous). Règle : Claude travaille dans une scène à lui (« ATELIER_CLAUDE ») et ne modifie jamais une scène ouverte par Guillaume sans son accord.

## Méthode (boucle d'autocontrôle, d'après ref-lookdev)

1. Écrire `modeles/<id>.py` : dimensions réelles en mètres, base à z = 0, face vers -y (ou orientation de l'asset qu'il remplace).
2. Générer : `blender --background --factory-startup --python engine/outils/atelier/modeles/<id>.py`
3. Aperçu : `blender --background --factory-startup --python engine/outils/atelier/apercu.py -- <glb> <planche.png>`
4. Regarder la planche et noter les écarts (silhouette, proportions, contraste, épaisseurs). Corriger, recommencer. Trois tours au plus avant de demander l'avis d'un humain.
5. Enregistrer : entrée dans `registre.json` (`"materiaux": "origine"`, source = le script) et ligne « création du projet » dans `licences.csv`.

Règles de style (ref-stylized-style, ref-lowpoly-style) : silhouette lisible de loin, bords biseautés plutôt qu'arêtes vives, palette courte, contraste entre pièces voisines (ex. cadre blanc, filet gris), pas de micro-détail invisible en 9:16.

## Modèles produits

| Modèle | Script | Remarques |
|---|---|---|
| `cage_filet` | `modeles/cage_filet.py` | cage 4 × 2 m réparée avec filet, mêmes dimensions et orientation que `cage_rouillee` (choix « FILETS » du vote de jour-1) ; 17 600 triangles |

## Limites actuelles

- Personnages : `organique` donne le volume, mais le squelette, les poids et les animations restent à construire (prochaine étape : réutiliser les animations Quaternius avec les mêmes noms d'os).
- Pas de textures peintes : couleurs unies par matériau, cohérentes avec les packs de DA actuels.
