# Contrat d'entrée du pôle Production : la fiche épisode (v1.0)

Le pôle Storytelling (agent `story-fiche`) ou un humain envoie au pôle Production une **fiche épisode** au format JSON. C'est la seule interface : tant qu'une fiche respecte ce contrat, la production sait la transformer en vidéo, sans connaître l'histoire.

- Schéma officiel (validé automatiquement) : [`contracts/fiche-episode.schema.json`](../../contracts/fiche-episode.schema.json)
- Exemple complet : [`episodes/exemples/demo_001.json`](../../episodes/exemples/demo_001.json)
- Vocabulaire : [`vocabulaire-actions.md`](../../contracts/vocabulaire-actions.md)

## Structure

| Champ | Obligatoire | Rôle |
|---|---|---|
| `version` | oui | `"1.0"` |
| `episode_id` | oui | minuscules, chiffres, `-`, `_` ; nom du dossier de rendu |
| `titre` | non | titre lisible |
| `format` | non | `resolution` (défaut `[1080, 1920]`), `fps` (24, 25, 30 ou 60 ; défaut 30) |
| `pack_da` | non | pack de direction artistique (`engine/packs_da/<nom>.json`, défaut `test_lowpoly`) |
| `serie` | non | `id` de la série et `continuite` (reprendre l'état de l'épisode précédent) |
| `decor` | non | `kit` (défaut `primitifs`), `sol`, `taille_sol` |
| `elements` | non | objets uniques du décor : `id`, `asset`, `position`, `rotation_z`, `echelle`, `role`, `visible_au_debut` |
| `personnages` | non | mêmes champs que les éléments |
| `modules` | non | modules procéduraux (`disperser`) |
| `audio` | non | `musique` (chemin) et `volume_musique` |
| `beats` | oui | le récit découpé (1 à 60 beats) |

Un **asset** s'écrit `primitif:<nom>` (généré par code) ou `bibliotheque:<id>` (modèle 3D du registre `engine/assets/registre.json`).

## Un beat

```json
{
  "id": "b2",
  "voix": "Puis quelqu'un a allumé une lumière.",
  "texte_ecran": "JOUR 2",
  "plan": { "camera": "revelation", "cible": "phare", "distance": 14, "hauteur": 6 },
  "actions": [ { "type": "apparaitre", "cible": "phare", "mot": "lumière", "duree_s": 0.7 } ]
}
```

- `voix` : la phrase de voix off. Elle donne la durée du beat et les sous-titres.
- `duree_s` : seulement pour imposer une durée (beat muet, silence voulu).
- `texte_ecran` : texte affiché en haut de l'image pendant tout le beat (1 à 4 mots).
- `voix_audio` : **rempli par le futur module Voix** (fichier WAV, durée, horodatage de chaque mot). Ne pas l'écrire à la main.

## Comment la durée et la synchronisation sont calculées

1. `duree_s` imposée, sinon
2. durée réelle de la voix (`voix_audio`) + 0,45 s de respiration, sinon
3. estimation : 14 caractères par seconde (débit d'une voix off posée), minimum 1,5 s, sinon
4. 2 s pour un beat muet.

Une action déclenchée sur un `mot` tombe à l'instant où ce mot est prononcé : estimé aujourd'hui, exact quand le module Voix existera. **Aucune fiche n'aura à changer** à ce moment-là.

## Ce que la production renvoie

- `renders/<episode>/<mode>/episode.mp4` : la vidéo (H.264 + AAC, sous-titres et textes intégrés) ;
- `planche_contact.png` : une image avec la vignette de chaque beat et sa phrase ;
- `rapport.json` : chaque étape, ses durées, les avertissements, et le champ `suite` (sous-agent à appeler ensuite) ;
- `timeline.json` et `scene.blend` : pour inspecter ou retoucher.

## Évolution du contrat

Toute modification passe par une PR qui met à jour **en même temps** le schéma, ce document, l'exemple et les tests. On ajoute des champs facultatifs plutôt que de changer le sens des champs existants ; un changement incompatible fait passer `version` à `2.0`.
