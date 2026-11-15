# Initialise le suivi GitHub du projet : labels, issues et tableau Projects.
# Usage (depuis la racine du dépôt, une seule fois) :
#   gh auth refresh -s project
#   powershell -ExecutionPolicy Bypass -File scripts\setup-github.ps1

$repo  = "l-marque/serie-animation"
$owner = "l-marque"

Write-Host "== Labels ==" -ForegroundColor Cyan
$labels = @(
  @("agent-pilotage",   "1D76DB", "Agent de pilotage"),
  @("agent-com",        "D93F0B", "Agent de communication"),
  @("agent-production", "0E8A16", "Agent de production"),
  @("blender",          "5319E7", "Travail 3D dans Blender"),
  @("admin",            "BFDADC", "Outillage, GitHub, comptes"),
  @("recherche",        "FBCA04", "Vérification ou veille"),
  @("decision-humaine", "B60205", "Décision réservée à Lucas et Guillaume")
)
foreach ($l in $labels) {
  gh label create $l[0] --color $l[1] --description $l[2] --repo $repo --force | Out-Null
  Write-Host ("  label " + $l[0])
}

Write-Host "== Tableau Projects ==" -ForegroundColor Cyan
$projectJson = gh project create --owner $owner --title "Série animation" --format json
$project = $projectJson | ConvertFrom-Json
$num = $project.number
Write-Host ("  tableau n°" + $num + " : " + $project.url)

Write-Host "== Issues ==" -ForegroundColor Cyan
# Titre ; labels ; assigné (vide = personne, à attribuer à Guillaume après acceptation de l'invitation) ; description
$issues = @(
  @("Accepter l'invitation GitHub et cloner le dépôt", "admin", "", "Guillaume : accepter l'invitation, puis git clone https://github.com/l-marque/serie-animation.git"),
  @("Installer Blender et apprendre les bases", "blender", "", "Guillaume : interface, navigation, objets, matériaux, rendu simple."),
  @("Vérifier la machine de rendu disponible", "blender,admin", "", "Quelle carte graphique ? Temps de rendu d'une scène test ? Le PC de Lucas est en cours de remplacement."),
  @("Définir les conventions de nommage Blender", "blender,decision-humaine", "", "Créer docs/conventions-blender.md : nommage des objets et collections, un fichier .blend par quartier ou par élément, unités. Indispensable pour l'agent Production."),
  @("Installer et tester le Blender MCP sur une scène simple", "blender,agent-production", "", "Installer Blender MCP, demander à Claude de créer une scène basique (sol, 3 bâtiments, lumière, caméra), noter ce qui marche et ce qui casse."),
  @("Définir le concept de la ville et le nom de la série", "decision-humaine", "", "Style (low-poly recommandé pour débuter), ambiance, nom, format des vidéos (vertical court ou long), fréquence."),
  @("Vérifier ce que l'API Instagram permet de détecter", "recherche,agent-com", "l-marque", "Commentaires, mentions, messages, nouveaux abonnés : qu'est-ce qui est réellement accessible avec un compte professionnel ? Conditionne toute la mécanique d'interaction."),
  @("Créer les comptes Instagram professionnel et YouTube de la série", "admin,decision-humaine", "l-marque", "Après le choix du nom. Prévoir une adresse mail dédiée au projet."),
  @("Tester l'agent Pilotage : premier point hebdo", "agent-pilotage", "l-marque", "Dans Claude Code : demander à l'agent pilotage de produire le point hebdo à partir des issues et du Drive. Corriger sa définition selon le résultat."),
  @("Automatiser le point hebdo avec une tâche planifiée", "agent-pilotage", "l-marque", "Une fois le point hebdo satisfaisant : le transformer en skill puis le planifier chaque semaine."),
  @("Tester l'agent Communication sur un faux épisode", "agent-com", "l-marque", "Lui donner un pitch d'épisode fictif : légende Instagram, description YouTube, miniature Canva. Évaluer et ajuster."),
  @("Mettre en place Git LFS pour les fichiers .blend", "admin", "l-marque", "À faire avant le premier .blend versionné : git lfs install, git lfs track ""*.blend""."),
  @("Installer l'application GitHub de Claude sur le dépôt", "admin", "l-marque", "Permet à Claude de créer branches et PR directement, sans passer par le PC."),
  @("Pilote : une scène simple de bout en bout", "agent-production,agent-com", "", "Consigne → scène Blender → rendu 30-60 s → légende → publication validée. Objectif : valider toute la chaîne.")
)
foreach ($i in $issues) {
  $ghArgs = @("issue", "create", "--repo", $repo, "--title", $i[0], "--label", $i[1], "--body", $i[3])
  if ($i[2] -ne "") { $ghArgs += @("--assignee", $i[2]) }
  $url = (& gh @ghArgs) | Select-Object -Last 1
  gh project item-add $num --owner $owner --url $url | Out-Null
  Write-Host ("  " + $url + "  " + $i[0])
}

Write-Host "Terminé." -ForegroundColor Green
