"""Chef d'orchestre de l'agent Production : une commande, tout le pipeline.

Usage (depuis la racine du dépôt) :
    python -m scripts.production.run episodes/exemples/demo_001.json
    python -m scripts.production.run FICHE --mode final --blender "C:/Program Files/Blender Foundation/Blender 5.3/blender.exe"
    python -m scripts.production.run FICHE --valider-seulement

Étapes :
  1. contrat        valider la fiche (structure + cohérence)
  2. continuite     reprendre l'état de la série si demandé
  3. bibliothecaire vérifier les assets (sinon : code 3 et liste des manquants)
  4. realisateur    construire la timeline maître
  5. cache          déterminer les beats à (re)rendre
  6. blender        construire la scène et rendre (sous-processus Blender)
  7. montage        sous-titres, textes, audio, MP4
  8. qa_auto        contrôles + planche contact
  9. continuite     enregistrer l'état de fin (mode final uniquement)

Codes de sortie : 0 succès · 2 fiche invalide · 3 assets manquants · 4 échec Blender
                  5 échec montage · 6 contrôles qualité en échec · 1 erreur inattendue.
Le rapport complet est écrit dans renders/<episode>/<mode>/rapport.json et une ligne
de synthèse JSON est imprimée en dernier sur la sortie standard (lisible par un agent).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from . import bibliothecaire, cache, chemins, continuite, contrat, montage, qa_auto, realisateur


# Sous-agent à appeler ensuite selon le code de sortie (lu par l'agent production ou la session principale).
# Dans Claude Code, un sous-agent ne peut pas en lancer un autre : c'est l'appelant qui enchaîne.
SUITE = {
    0: "production-controle-qualite",   # succès : vérification visuelle de la planche contact
    2: "production-realisateur",        # fiche invalide : corriger ou compléter la fiche
    3: "production-bibliothecaire",     # assets manquants : les trouver et les intégrer
    4: "production-technicien",         # échec Blender : diagnostiquer le code ou la scène
    5: "production-technicien",         # échec du montage (ffmpeg)
    6: "production-controle-qualite",   # contrôles automatiques en échec : diagnostic visuel
}


class Rapport:
    def __init__(self, dossier: Path | None):
        self.dossier = dossier
        self.donnees: dict = {"debut": datetime.now().isoformat(timespec="seconds"), "etapes": [],
                              "avertissements": [], "appels_claude_scripts": 0}

    def etape(self, nom: str, statut: str, **details) -> None:
        self.donnees["etapes"].append({"etape": nom, "statut": statut, **details})
        print(f"[{statut:>7}] {nom}" + (f" — {details.get('resume')}" if details.get("resume") else ""), flush=True)

    def terminer(self, code: int, **synthese) -> int:
        self.donnees.update({"fin": datetime.now().isoformat(timespec="seconds"), "code_sortie": code, **synthese})
        if self.dossier:
            self.dossier.mkdir(parents=True, exist_ok=True)
            (self.dossier / "rapport.json").write_text(json.dumps(self.donnees, ensure_ascii=False, indent=2),
                                                       encoding="utf-8")
        synthese.setdefault("suite", SUITE.get(code))
        self.donnees["suite"] = synthese["suite"]
        print("SYNTHESE " + json.dumps({"code": code, **synthese}, ensure_ascii=False), flush=True)
        return code


def _commande_blender(blender: str, timeline_json: Path, beats: list[str], dossier: Path,
                      moteur: str | None = None) -> list[str]:
    script = str(chemins.SCRIPT_CONSTRUCTION)
    args = ["--", "--timeline", str(timeline_json), "--sortie", str(dossier), "--beats", ",".join(beats)]
    if moteur:
        args += ["--moteur", moteur]
    if Path(blender).name.lower().startswith("python"):
        # Mode « module bpy » (pip install bpy) : utile pour les tests sans interface.
        return [blender, script, *args]
    return [blender, "--background", "--factory-startup", "-noaudio", "--python-exit-code", "1",
            "--python", script, *args]


def executer(args: argparse.Namespace) -> int:
    rapport = Rapport(None)

    # 1. Contrat
    try:
        fiche = contrat.charger(args.fiche)
    except contrat.FicheInvalide as e:
        rapport.etape("contrat", "ECHEC", erreurs=e.erreurs, resume=f"{len(e.erreurs)} erreur(s)")
        for err in e.erreurs:
            print(f"   - {err}")
        # Seul le pack de DA pose problème : c'est le travail du directeur artistique, pas du réalisateur.
        que_le_pack = all(err.startswith("pack de DA") for err in e.erreurs)
        return rapport.terminer(2, etape_bloquante="contrat", erreurs=e.erreurs,
                                **({"suite": "production-directeur-artistique"} if que_le_pack else {}))
    dossier = chemins.dossier_sortie(fiche.episode_id, args.mode) if not args.sortie else Path(args.sortie)
    rapport.dossier = dossier
    rapport.etape("contrat", "OK", resume=fiche.episode_id)

    # 2. Continuité
    donnees, notes = continuite.fusionner(fiche.donnees)
    if notes:
        fiche = contrat.valider_donnees(donnees, source=fiche.source)
    rapport.etape("continuite", "OK", notes=notes, resume="; ".join(notes) or "sans objet")

    # 3. Bibliothécaire
    verif = bibliothecaire.verifier(fiche.donnees)
    if not verif.ok:
        rapport.etape("bibliothecaire", "ECHEC", manquants=verif.manquants,
                      resume=f"{len(verif.manquants)} asset(s) manquant(s)")
        return rapport.terminer(3, etape_bloquante="bibliothecaire", assets_manquants=verif.manquants)
    rapport.etape("bibliothecaire", "OK", attributions=verif.attributions)

    # 4. Réalisateur
    try:
        timeline = realisateur.construire_timeline(fiche, mode=args.mode)
    except realisateur.TimelineInvalide as e:
        rapport.etape("realisateur", "ECHEC", erreurs=[str(e)], resume=str(e))
        return rapport.terminer(2, etape_bloquante="realisateur", erreurs=[str(e)])
    if args.pourcent:
        timeline["pourcentage_resolution"] = args.pourcent
    dossier.mkdir(parents=True, exist_ok=True)
    timeline_json = dossier / "timeline.json"
    timeline_json.write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    rapport.donnees["avertissements"] += fiche.avertissements
    rapport.etape("realisateur", "OK", duree_s=timeline["duree_totale_s"], nb_frames=timeline["nb_frames"],
                  resume=f"{len(timeline['beats'])} beats, {timeline['duree_totale_s']:.1f} s, {timeline['nb_frames']} frames")
    if args.valider_seulement:
        return rapport.terminer(0, episode=fiche.episode_id, timeline=str(timeline_json), valider_seulement=True, suite=None)

    # 5. Cache
    a_rendre, empreintes = cache.beats_a_rendre(timeline, dossier, forcer=args.forcer)
    rapport.etape("cache", "OK", a_rendre=a_rendre,
                  resume=f"{len(a_rendre)}/{len(timeline['beats'])} beat(s) à rendre")

    # 6. Blender
    if a_rendre:
        cmd = _commande_blender(args.blender, timeline_json, a_rendre, dossier, args.moteur)
        t0 = time.time()
        journal = dossier / "blender.log"
        with journal.open("w", encoding="utf-8") as log:
            res = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, text=True)
        duree = round(time.time() - t0, 1)
        if res.returncode != 0:
            fin_log = journal.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-25:]
            rapport.etape("blender", "ECHEC", duree_s=duree, journal=str(journal), fin_journal=fin_log,
                          resume=f"code {res.returncode}, voir {journal}")
            return rapport.terminer(4, etape_bloquante="blender", journal=str(journal))
        cache.enregistrer(dossier, empreintes)
        rapport.etape("blender", "OK", duree_s=duree, resume=f"{len(a_rendre)} beat(s) rendus en {duree} s")
    else:
        rapport.etape("blender", "IGNORE", resume="tout est déjà en cache")

    # 7. Montage
    try:
        video = montage.monter(timeline, dossier)
    except montage.MontageErreur as e:
        rapport.etape("montage", "ECHEC", erreurs=[str(e)], resume=str(e))
        return rapport.terminer(5, etape_bloquante="montage", erreurs=[str(e)])
    rapport.etape("montage", "OK", video=str(video))

    # 8. Contrôle qualité automatique + planche contact
    qa = qa_auto.controler(timeline, dossier)
    planche = qa_auto.planche_contact(timeline, dossier)
    rapport.etape("qa_auto", "OK" if qa["ok"] else "ECHEC", **qa, planche=str(planche),
                  resume="aucun problème" if qa["ok"] else f"{len(qa['problemes'])} problème(s)")

    # 9. Continuité : état de fin (seulement en final, quand tout est bon)
    serie = fiche.donnees.get("serie")
    if serie and serie.get("continuite") and args.mode == "final" and qa["ok"]:
        continuite.enregistrer(serie["id"], continuite.etat_final(timeline))
        rapport.etape("continuite_fin", "OK", resume=f"état de la série '{serie['id']}' mis à jour")

    synthese = {"episode": fiche.episode_id, "mode": args.mode, "video": str(video), "planche_contact": str(planche),
                "duree_s": timeline["duree_totale_s"], "beats_rendus": a_rendre, "qa_ok": qa["ok"],
                "problemes": qa["problemes"], "attributions": verif.attributions}
    return rapport.terminer(0 if qa["ok"] else 6, **synthese)


def analyser_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="production", description="Pipeline de l'agent Production : fiche épisode -> vidéo 9:16.")
    p.add_argument("fiche", help="chemin de la fiche épisode JSON")
    p.add_argument("--mode", choices=["animatique", "final"], default="animatique",
                   help="animatique : rapide, basse définition, pour valider le rythme ; final : qualité de publication")
    p.add_argument("--blender", default=os.environ.get("BLENDER_PATH", "blender"),
                   help="exécutable Blender (ou variable d'environnement BLENDER_PATH)")
    p.add_argument("--sortie", help="dossier de sortie (défaut : renders/<episode>/<mode>)")
    p.add_argument("--forcer", action="store_true", help="ignorer le cache et tout re-rendre")
    p.add_argument("--pourcent", type=int, choices=range(5, 101), metavar="5-100",
                   help="pourcentage de résolution (défaut : 50 en animatique, 100 en final)")
    p.add_argument("--moteur", choices=["BLENDER_EEVEE", "CYCLES", "BLENDER_WORKBENCH"],
                   help="forcer un moteur de rendu (défaut : celui du pack de DA)")
    p.add_argument("--valider-seulement", action="store_true", help="contrat + timeline, sans rendu")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return executer(analyser_arguments(argv))
    except KeyboardInterrupt:
        print("Interrompu.")
        return 130
    except Exception as e:  # dernier filet : un agent doit toujours recevoir une synthèse lisible
        print(f"SYNTHESE {json.dumps({'code': 1, 'erreur_inattendue': repr(e)}, ensure_ascii=False)}")
        raise


if __name__ == "__main__":
    sys.exit(main())
