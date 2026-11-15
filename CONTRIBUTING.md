# Règles de travail

## Le cycle Git (toujours le même)

1. Se mettre à jour : `git switch main` puis `git pull`
2. Créer une branche : `git switch -c type/sujet-court`
3. Travailler, puis `git add <fichiers>` et `git commit -m "Verbe à l'infinitif + quoi"`
4. Envoyer : `git push -u origin type/sujet-court`
5. Ouvrir la PR : `gh pr create --fill`
6. **L'autre relit et fusionne.** On ne fusionne jamais sa propre PR.
7. Après la fusion : `git switch main`, `git pull`, et on supprime la branche locale avec `git branch -d type/sujet-court`

**Personne ne pousse directement sur `main`.**

## Nommage des branches

| Préfixe | Usage | Exemple |
|---|---|---|
| `feature/` | nouvelle fonctionnalité | `feature/agent-pilotage` |
| `fix/` | correction | `fix/script-rendu` |
| `docs/` | documentation | `docs/conventions-blender` |
| `blender/` | travail sur une scène ou un modèle | `blender/quartier-centre` |

## Messages de commit

En français, à l'infinitif, courts : `Ajoute l'agent de pilotage`, `Corrige le chemin des rendus`.

## Fichiers Blender (`.blend`)

- Un `.blend` ne se fusionne pas : **une seule personne édite un fichier donné à la fois**. Prévenir dans l'issue correspondante avant de commencer.
- Les `.blend` passeront par Git LFS quand les premiers arriveront (à mettre en place).
- Les rendus et vidéos vont sur le Drive (`06_Rendus et assets lourds`), jamais dans Git.

## Secrets

Aucun mot de passe, clé d'API ou jeton dans le dépôt. Ils vont dans un fichier `.env` local, ignoré par Git. Une clé poussée par erreur doit être **révoquée**, pas seulement supprimée : elle reste dans l'historique.

## Tâches

Toutes les tâches sont des **issues GitHub**, suivies dans le tableau du projet. Une PR qui règle une issue contient `Closes #numéro` dans sa description.
