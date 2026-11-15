"""Pipeline de l'agent Production (partie hors Blender).

Modules :
    chemins        chemins du dépôt et constantes
    contrat        chargement et validation de la fiche épisode
    realisateur    timeline maître (durées, horodatages, déclenchement des actions)
    continuite     état persistant d'une série d'épisodes
    bibliothecaire vérification des assets demandés
    cache          empreintes par beat pour ne re-rendre que ce qui a changé
    montage        sous-titres, textes à l'écran, audio, encodage MP4 (ffmpeg)
    qa_auto        contrôles automatiques et planche contact
    run            chef d'orchestre (point d'entrée en ligne de commande)
"""

__version__ = "1.0.0"
