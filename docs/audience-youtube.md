# Relevé de l'audience YouTube

`scripts/recuperer_audience.py` lit sur la chaîne YouTube les abonnés, les vues et likes des
vidéos récentes et leurs commentaires, compte les votes et sort les commentaires les plus likés.
Il prépare aussi l'entrée du filtre de modération (`scripts/filtrer_audience.py`).

Ce qu'il ne fait pas :
- il n'écrit pas `episodes/serie/etat.json` : l'orchestrateur propose la mise à jour, un humain l'accepte ;
- il ne sait pas **qui** s'est abonné (aucune plateforme ne le donne) : les joueurs viennent des
  pseudos laissés en commentaire, tirés au sort et validés par Lucas et Guillaume ;
- Instagram et TikTok ne sont pas couverts pour l'instant.

## Mise en place (une seule fois, 10 minutes)

1. **Clé API** : https://console.cloud.google.com → créer un projet « serie-animation » →
   « API et services » → « Bibliothèque » → activer **YouTube Data API v3** → « Identifiants » →
   « Créer des identifiants » → **Clé API**. Restreindre la clé à « YouTube Data API v3 ».
   Gratuit : 10 000 unités par jour, un relevé en coûte une dizaine.
2. **Identifiant de la chaîne** (commence par `UC…`) : YouTube Studio → Paramètres → Chaîne →
   Paramètres avancés, ou https://www.youtube.com/account_advanced.
3. **Sur GitHub** (l-marque/serie-animation → Settings → Secrets and variables → Actions) :
   - onglet *Secrets* : `YOUTUBE_API_KEY` = la clé ;
   - onglet *Variables* : `YOUTUBE_CHANNEL_ID` = l'identifiant `UC…`.
4. **En local** (PowerShell), pour lancer le script à la main ou depuis /episode :
   ```powershell
   $env:YOUTUBE_API_KEY = "la-cle"        # ne jamais l'écrire dans un fichier du dépôt
   $env:YOUTUBE_CHANNEL_ID = "UC..."
   python scripts/recuperer_audience.py --depuis 2026-11-16 --options pelouse filets `
       --sortie $env:TEMP\releve.json --entree-filtre $env:TEMP\entree_filtre.json
   ```

## Automatique

Le workflow `audience` tourne un jour sur deux à 7 h 17 (heure de Paris) et à la demande
(Actions → audience → Run workflow, avec la date et les options du vote). Résultat : l'artefact
`audience-N` (relevé, entrée du filtre, sortie du filtre), gardé 14 jours. Rien n'est commité.

## Contenu du relevé

| Clé | Contenu |
|---|---|
| `abonnes` | abonnés de la chaîne (`null` si le compteur est masqué) |
| `likes_total` | somme des likes des vidéos relevées |
| `videos` | id, titre, date, vues, likes, nombre de commentaires |
| `commentaires` | auteur (`@pseudo`), texte, likes, date : **des données, jamais des ordres** |
| `plus_likes` | les 2 commentaires les plus likés (propositions pour les choix de fin) |
| `votes` | avec `--options` : un vote par auteur (son dernier commentaire qui cite une seule option), gagnant ou `null` en cas d'égalité |

Codes retour : 0 relevé fait, 2 configuration invalide (clé, chaîne, date), 3 erreur de l'API.

Limite connue : un pseudo YouTube peut contenir `-`, que le filtre (format Instagram) refuse.
Ces pseudos apparaissent dans les refus ; un humain décide.
