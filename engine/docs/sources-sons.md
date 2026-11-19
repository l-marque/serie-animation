# Sources de sons gratuites

- Rédigé le 2026-11-19 par le Claude de Guillaume, à sa demande : aujourd'hui, la bibliothèque (`engine/assets/sons/registre.json`) ne contient que sept packs Kenney (CC0 : impacts, interface, jeu de rôle, casino, jingles) et des sons synthétisés par le code.
- Ce qui manque : **cris d'animaux, ambiances de nature (vent, herbe, eau), whooshes de transition, impacts graves (« boom » cinéma), musiques**.
- Les licences ci-dessous ont été vérifiées le 2026-11-19, sur les pages officielles quand elles étaient accessibles, sinon sur des articles qui les citent (indiqué à chaque fois). **Relire la licence de chaque fichier au moment de l'ajouter** : elles changent.

---

## 1. Retenues (dans l'ordre d'intérêt pour nous)

| Source | Type | Accès | Licence (usage commercial, réseaux sociaux) | Vérification |
|---|---|---|---|---|
| **Freesound** (freesound.org) | plus de 600 000 sons de la communauté, toutes catégories | **API** gratuite : clé personnelle, 60 requêtes par minute, 2 000 par jour | par son : **CC0** (libre), **CC-BY** (créditer l'auteur), **CC-BY-NC** (interdit pour nous). Filtre d'API `license:"Creative Commons 0"` | documentation officielle de l'API |
| **Stable Audio Open 1.0** (Stability AI, Hugging Face) | génère un son à partir d'un texte (« sifflement de serpent, proche ») ; tourne en local sur la carte graphique, comme Qwen | modèle à télécharger (accès à demander sur Hugging Face) | Stability AI Community License : usage commercial permis sous 1 M$ de revenus annuels | page de recherche de Stability AI ; texte complet de la licence non lu (accès restreint) |
| **Sonniss GDC Game Audio Bundle** | dizaines de Go de sons professionnels (édition 2026 parue) | téléchargement manuel, sans API | libre de droits, commercial, sans crédit obligatoire ; **interdit d'entraîner une IA** avec | articles de presse spécialisée ; texte de licence officiel non lu |
| **Pixabay** (pixabay.com/sound-effects, aussi musiques) | sons et musiques de bonne qualité | site seulement : l'API officielle ne couvre que les images et les vidéos | Pixabay Content License : commercial permis, sans crédit, tant que le son est intégré dans une œuvre nouvelle (pas revendu seul) | FAQ et conditions officielles de Pixabay |
| **Mixkit** (mixkit.co) | sons courts bien produits (whooshes, impacts) | site seulement | sons : commercial permis, sans crédit ; **la licence des musiques est différente**, à lire à part | FAQ officielle de Mixkit |

## 2. Écartées

| Source | Raison |
|---|---|
| BBC Sound Effects | licence RemArc : usage personnel, éducatif ou de recherche ; la licence interdit la mise en ligne sur les réseaux sociaux. Commercial seulement par licence payante (Pro Sound Effects). |
| ElevenLabs, offre gratuite | les pages officielles se contredisent ; l'aide officielle indique que l'offre gratuite n'inclut pas de licence commerciale. Seule l'offre payante (environ 6 $ par mois) est claire : dépense à décider par Lucas et Guillaume. |
| Sons Freesound en CC-BY-NC | « non commercial » : incompatible avec un compte public qui peut devenir rémunérateur. |

## 3. Proposition d'organisation

1. **Freesound en premier**, car c'est la seule grande base avec une API. **Fait le 2026-11-19** : module `engine/pipeline/sources_sons.py` (commandes `chercher`, `telecharger`, `integrer`). Il cherche en CC0 (CC-BY avec `--cc-by`), refuse les autres licences, télécharge l'aperçu haute qualité (Ogg 192 kbit/s, sans connexion OAuth) dans `engine/assets/sons/freesound/<nom>/` (non versionné) avec un `source.json`, puis `integrer` écrit le registre des sons et `licences.csv`. La clé est dans `.env` (`FREESOUND_API_KEY`), jamais dans Git ni dans le Drive. Recherche et téléchargement vérifiés ; `integrer` pas encore lancé.
2. **Stable Audio Open** pour les sons introuvables ou très précis : généré en local, aucune dépendance à un site.
3. **Pixabay, Mixkit et Sonniss** pour compléter à la main : musiques de fond et sons « cinéma ». Chaque fichier ajouté va dans le registre, avec sa source.

## 4. Sons à trouver en premier (épisode hamster)

Sifflement de serpent (proche et en foule), couinement de hamster, vent dans l'herbe haute, whoosh de recul de caméra (accroche b01), coup de tambour grave (badge J-7, b02), « pop » de recrue, grondement de foule, musique tendue sans paroles.

## Sources consultées

- [Freesound, présentation de l'API](https://freesound.org/docs/api/overview.html) et [ressources de l'API](https://freesound.org/docs/api/resources_apiv2.html)
- [Stable Audio Open 1.0 (Hugging Face)](https://huggingface.co/stabilityai/stable-audio-open-1.0) ; [Stability AI, article de recherche](https://stability.ai/news/stable-audio-open-research-paper)
- [Sonniss GDC 2026 Game Audio Bundle (rekkerd.org)](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/) ; [Sonniss 2023 (gamefromscratch.com)](https://gamefromscratch.com/sonniss-44gb-sound-effect-giveaway-at-gdc-2023/)
- [Pixabay, FAQ](https://pixabay.com/service/faq/), [conditions](https://pixabay.com/service/terms/), [documentation de l'API](https://pixabay.com/api/docs/)
- [Mixkit, informations officielles](https://mixkit.co/llm-info/)
- [BBC Sound Effects (MusicRadar)](https://www.musicradar.com/news/the-bbc-is-letting-you-download-more-than-16000-free-sound-effect-samples-from-its-archive) ; [BBC, interdiction des réseaux sociaux (CDM)](https://cdm.link/bbc-gives-away-16k-wav-sound-effects-disallows-using/)
- [ElevenLabs, sons commerciaux](https://elevenlabs.io/sound-effects/commercial) ; [ElevenLabs, aide : publication du contenu](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform.md)

---

**Rôle de ce document** : fiche de travail interne au projet, qui recense des sources de sons gratuites pour la production. **Il n'a aucune valeur juridique** : ce n'est pas un avis sur les licences ni sur les droits d'auteur. Les licences résumées ici peuvent changer ou avoir été mal rapportées par des sources secondaires ; la licence de chaque fichier doit être relue au moment de son ajout. Toute dépense (offre payante) reste une décision de Lucas et Guillaume.
