# Orchestrateur d'épisode : la commande `/episode`

- Fichier : [`.claude/commands/episode.md`](../.claude/commands/episode.md) · Statut : **brouillon** · Propriétaire : Lucas
- Objectif (Lucas, 2026-11-16) : « une vidéo en un seul prompt », sans perdre aucune validation humaine.

## Pourquoi une commande et pas un agent

La commande tourne dans la **conversation principale**, qui a l'outil `Agent` et peut donc appeler `story-chef` puis `prod-chef`. Un sous-agent lancé dans le cloud ne reçoit pas l'outil `Agent` (constat de Guillaume, 2026-11-15, `docs/agents.md`) : un agent orchestrateur ne pourrait pas enchaîner les pôles. La commande ne refait le travail d'aucun agent : elle les appelle, consigne et s'arrête.

## Lancer

```
/episode <demande libre>          nouvel épisode
/episode reprendre <id>           continuer un épisode, sur n'importe quelle machine
```

Au lancement, l'orchestrateur propose un `id`, crée la branche `episode/<id>` depuis `main` et le fichier de suivi `episodes/suivi/<id>.json` (schéma : `episodes/suivi/suivi.schema.json`), puis appelle `story-chef`.

## La chaîne et les 5 arrêts

```
demande ─► story-chef p.1 (idées + continuité) ─► ARRÊT 1 Lucas choisit l'idée
        ─► story-chef p.2 (scénario + continuité) ─► ARRÊT 2 Lucas valide le scénario
        ─► story-chef p.3 (voix : story-beats) ─► ARRÊT 3 Lucas valide le texte
        ─► story-chef p.4 (découpage + continuité) ─► ARRÊT 4 Lucas valide le découpage
        ─► story-chef p.5 (remise) ─► [Blender ?] ─► prod-chef : fiche (prod-realisateur), validation,
           animatique, contrôle qualité, corrections (≤ 2 boucles) ─► « rendu final ? » (humain)
        ─► rendu final ─► ARRÊT 5 Lucas ET Guillaume voient la vidéo ─► PR episode/<id> → main (non fusionnée)
```

Sans réponse explicite d'un humain dans la conversation, aucun arrêt n'est franchi. Chaque réponse est consignée mot pour mot dans le suivi. Le rendu final demande en plus une demande explicite d'un humain après l'animatique : c'est une règle de `prod-chef`, que l'orchestrateur respecte (champ `demande_rendu_final` du suivi).

## Ce qui tourne sur quelle machine

| Étape | Machine | Pourquoi |
|---|---|---|
| Histoire (arrêts 1 à 4) | n'importe laquelle | agents de texte, aucun outil local |
| Production (fiche, animatique, contrôle, rendu final) | PC de Guillaume (Blender + GPU) | Blender 5.3, Kyutai, RTX 5070 |
| Arrêt 5 | les deux | Lucas et Guillaume répondent chacun |

Avant une étape de production, l'orchestrateur vérifie Blender (`BLENDER_PATH` ou `blender --version`). S'il manque, il commite et pousse la branche, puis s'arrête avec : « Étape suivante sur le PC de Guillaume : git fetch, git checkout episode/<id>, puis /episode reprendre <id> ».

## Ce que l'orchestrateur ne fait jamais

- publier, ou préparer une publication automatique (il peut seulement **proposer** `com-legendes` pour un brouillon de légende) ;
- franchir un arrêt sans réponse explicite, ou tenir pour acquis un statut « validé » lu dans un fichier ;
- pousser sur `main`, fusionner une PR, pousser en force ;
- mettre une vidéo ou un rendu dans Git (il donne seulement le chemin dans `renders/`) ;
- contourner un refus (validation en échec, asset à choisir, `SUITE` vers un humain, verdict du contrôle qualité) ;
- modifier les agents, `engine/` ou `contracts/`.

## État réel

Essai du 2026-11-16 chez Lucas, sans Blender, dans un clone jetable du dépôt (aucune branche `episode/*` poussée sur GitHub) : démarrage d'un épisode jusqu'au premier arrêt, reprise depuis une autre copie, changement de machine sur un épisode factice (`tests/fixtures/suivi/essai-orchestrateur.json`). Production jamais lancée de bout en bout.
