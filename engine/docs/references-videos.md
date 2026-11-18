# Données des vidéos de référence (Reels du même genre)

- Source : 8 Reels envoyés par Guillaume le 2026-11-17 (dossier `exemple de vidéo/`, vidéos hors Git ; copie sur le Drive, `06_Rendus et assets lourds/videos_reference`).
- Mesures faites par le Claude de Guillaume le 2026-11-17 : `ffprobe` (format), `ffmpeg` (coupes détectées, volume EBU R128), Whisper small (instant de chaque mot), lecture d'une planche de 12 images par vidéo.
- Ce sont des **données d'observation** pour orienter nos choix, pas des modèles à copier : on ne reprend ni nom, ni personnage, ni habillage propre à ces comptes.

## Les vidéos

| Id | Compte (observé) | Concept | Durée | Langue | Personnages |
|---|---|---|---|---|---|
| v1 | rien.ville | ville construite jour après jour par les abonnés (« Jour 8 ») | 58 s | fr | semi-réalistes |
| v2 | leclubdesabonnes | « Jour 1 : on crée un club de foot » avec les abonnés | 42 s | fr | en blocs |
| v3 | chickenvscats | poussins contre 100 000 chats, pseudos des abonnés | 36 s | en | 3D stylisée |
| v4 | theoddtilt | « comment on a inventé le trampoline » | 38 s | en | réalistes |
| v5 | rien.ville | « Jour 1 » de la ville | 53 s | fr | semi-réalistes |
| v6 | rien.ville | « Jour 2 » de la ville | 71 s | fr | semi-réalistes |
| v7 | comentopia | « le meilleur commentaire construit l'île » | 65 s | en | low-poly |
| v8 | ile_sans_nom | île : 1 abonné = 1 habitant, 1 like = 1 € | 55 s | fr | avatars ronds |

Format reçu : 384 × 832, 60 i/s (recompression WhatsApp : la définition d'origine n'est pas connue).

## Voix : débit et pauses (mesuré)

| Id | Mots | Mots par minute | Pauses > 0,35 s | Pause max | Premier mot | Mots dans les 3 premières s |
|---|---|---|---|---|---|---|
| v1 | 195 | 201 | 1 | 0,46 s | 0,0 s | 7 |
| v2 | 119 | 171 | 0 | 0,12 s | 0,0 s | 7 |
| v3 | 96 | 160 | 0 | 0,14 s | 0,0 s | 7 |
| v4 | 133 | 213 | 1 | 0,40 s | 0,0 s | 9 |
| v5 | 157 | 180 | 0 | 0,20 s | 0,0 s | 10 |
| v6 | 252 | 214 | 1 | 0,54 s | 0,0 s | 9 |
| v7 | 142 (corrigé le 2026-11-18) | 132 | 1 | 0,66 s | 0,0 s | 5 |
| v8 | 113 | 123 | 2 | 2,48 s | 0,0 s | 7 |
| **jour-1 (nous)** | 110 | 212 | 16 | 0,5 s | 0,15 s | ~6 |

Correction du 2026-11-18 (v7) : la première mesure (274 mots, 255 mots par minute) était faussée par une erreur de Whisper, qui avait répété un passage et inventé une phrase à la jonction de deux tranches de 30 s. Recompté sur la transcription nettoyée : 142 mots en 64,6 s, soit environ 132 mots par minute. La médiane ci-dessous n'en est pas changée.

À retenir :
1. **Débit** : médiane d'environ 190 mots par minute ; 6 vidéos sur 8 entre 160 et 215. La cible de 180 décidée par Guillaume est dans la norme.
2. **Pas de silences** : la voix enchaîne les phrases sans s'arrêter (0 ou 1 pause de plus de 0,35 s par vidéo). Nos 16 pauses de 0,2 à 0,5 s (une par changement de plan) sont l'écart le plus net. **Cible : 0,1 à 0,2 s entre deux phrases**, une seule vraie pause (0,4 à 0,6 s) avant l'appel final, si l'histoire le demande.
3. **Accroche immédiate** : la voix démarre à 0 s, avec 7 à 10 mots dans les 3 premières secondes.
4. **La voix couvre toute la vidéo** : elle s'arrête moins d'une demi-seconde avant la dernière image.

## Rythme des images (indicatif)

Coupes détectées automatiquement (seuil de changement de scène 0,30) : v1 11, v2 23, v3 1, v4 4, v5 22, v6 14, v7 0, v8 4. Les vidéos à mouvement de caméra continu (v3, v7) ne sont pas comptées correctement par cette méthode. Sur les vidéos à coupes franches : **un plan toutes les 1,8 à 2,4 s** (v2, v5), jusqu'à 5 s pour les vidéos « ville » (v1, v6). Les **sous-titres changent beaucoup plus souvent** (2 ou 3 mots par carton) et donnent l'impression de rythme même quand le plan dure.

## Son

Volume intégré : **−14,1 à −14,7 LUFS** pour toutes les références ; jour-1 : −14,1 LUFS. Rien à corriger.

## Habillage observé (récurrent)

- **Badge « JOUR N » fixe en haut** pendant tout l'épisode, souvent avec un compte à rebours (« J-7 ») ou un minuteur de vote (« VOTE DANS 48 s »).
- **Compteurs en haut à gauche** (habitants, cagnotte, budget) qui changent en direct quand la voix en parle, avec « +319 » ou « +834 € » à côté.
- **Sous-titres mot par mot**, très gros, au centre de l'image, mot clé en jaune.
- **Commentaires d'abonnés affichés comme des bulles Instagram** (pseudo, texte, nombre de likes, mention « en tête ») ; **pseudo au-dessus du personnage** de l'abonné.
- **Vote final en 2 ou 3 choix** (« A – … / B – … », « ou autre chose ? »), puis appel à commenter.
- **Chiffres concrets à l'écran** (« 1 000 € », « 13 334 habitants », « 5 039 € − 2 500 € travaux »).
- **Bannière d'événement** (« FLASH SPÉCIAL », « CHANTIER », « NOUVEL HABITANT ») au moment d'un événement.

## Ce que ça change pour nos agents

- `prod-directeur-voix` : débit 180 mots par minute (réglage de Guillaume, dans la norme des références) ; expressivité visée ≥ 4,8 demi-tons par phrase ; pauses par défaut 0,1 à 0,2 s ; voix qui démarre à 0 s ; voix jusqu'à la fin.
- `prod-realisateur` : `duree_s` = 0,15 + voix + 0,1 à 0,2 s (au lieu de 0,5) ; premier mot dès la première image (avance de la voix à réduire : brique moteur `AVANCE_VOIX_S`, aujourd'hui 0,15 s) ; plans d'environ 2 s ; badge « JOUR N » et compteurs dès la première seconde.
- `prod-directeur-artistique` : idées d'habillage à étudier (badge de jour permanent, bulles de commentaires, minuteur de vote) ; à décider par Lucas et Guillaume, sans copier un compte existant.
- **Point d'attention (décision humaine)** : v2 « leclubdesabonnes » a un concept très proche du nôtre (club de foot créé avec les abonnés, personnages en blocs, terrain abandonné). À prendre en compte pour se différencier.

---

**Rôle de ce document** : fiche de données internes au projet, tirée de vidéos publiques reçues par Guillaume, pour orienter la production. **Il n'a aucune valeur juridique** : ce n'est ni une étude de marché, ni un avis sur des droits d'auteur. Les comptes cités sont des observations ; aucun de leurs éléments ne doit être reproduit.
