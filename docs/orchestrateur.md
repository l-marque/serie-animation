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
        ─► story-chef p.5 (remise) ─► [Blender ?] ─► prod-chef : fiche (prod-realisateur), validation
        ─► ARRÊT PLAQUETTE (page Figma créée par la session principale, « validé » de Guillaume)
        ─► animatique, contrôle qualité, corrections (≤ 2 boucles) ─► « rendu final ? » (humain)
        ─► rendu final ─► ARRÊT 5 Lucas ET Guillaume voient la vidéo ─► PR episode/<id> → main (non fusionnée)
```

Sans réponse explicite d'un humain dans la conversation, aucun arrêt n'est franchi. Chaque réponse est consignée mot pour mot dans le suivi. Le rendu final demande en plus une demande explicite d'un humain après l'animatique : c'est une règle de `prod-chef`, que l'orchestrateur respecte (champ `demande_rendu_final` du suivi).

## Ce qui tourne sur quelle machine

| Étape | Machine | Pourquoi |
|---|---|---|
| Histoire (arrêts 1 à 4) | n'importe laquelle | agents de texte, aucun outil local |
| Production (fiche, animatique, contrôle, rendu final) | PC de Guillaume (Blender + GPU) | Blender 5.3, Kyutai, RTX 5070 |
| Plaquette Figma | session qui a le connecteur Figma ; validation par Guillaume | règle de Guillaume (`engine/docs/plaquette-figma.md`) : rien n'est rendu sans plaquette validée |
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

**Essai du 2026-11-16, PC de Lucas, sans Blender.** Fait dans un clone jetable du dépôt avec un faux `origin` local (scratchpad de la session) : aucune branche `episode/*` n'a été poussée sur GitHub. Dans ce clone, la branche d'épisode partait de `feature/orchestrateur-episode` (la commande n'est pas encore dans `main`).

| Essai | Résultat |
|---|---|
| `/episode premier épisode de la série : un environnement qui évolue avec l'audience` | id `premier-episode`, branche et suivi créés (suivi valide) ; `story-chef` passage 1 **arrêté à son étape 0** (5 sections « À DÉCIDER » de la bible) ; aucune idée lancée, rien écrit dans `docs/`, aucun arrêt validé ; `blocage` et historique consignés, commit et push vers le faux `origin`. **Fait et vérifié.** |
| `/episode reprendre premier-episode` depuis une autre copie | `git fetch`, `checkout`, lecture du suivi : étape `idee`, arrêts en attente, blocage rappelé, aucun agent relancé. Branche inexistante : refus de `git checkout`. **Fait et vérifié.** |
| Passage de machine, épisode factice `essai-orchestrateur` (étape `fiche`, arrêts 1 à 4 marqués valides « essai factice (aucune validation humaine) ») | arrêts 1 à 4 vérifiés, Blender absent (`BLENDER_PATH` vide, `blender` introuvable ; un Blender 4.2 installé hors du PATH n'est pas détecté, et le pipeline demande la 5.3), suivi mis à jour, commit et push vers le faux `origin`, message pour le PC de Guillaume. Suivi rangé dans `tests/fixtures/suivi/essai-orchestrateur.json`. **Fait et vérifié.** |
| ARRÊTS 1 à 5, production, PR d'épisode | **non testés** (aucun choix de Lucas demandé pendant l'essai, pas de Blender). |

Constat : la commande `/episode` a été chargée par Claude Code dans la version du **premier commit** du fichier, sans les sections ajoutées ensuite dans la même session. L'essai a suivi le fichier complet. **Après toute modification de `.claude/commands/episode.md`, redémarrer Claude Code** avant de lancer `/episode`.
