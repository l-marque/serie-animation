"""Filtre d'entrée des textes de l'audience (étape 0 de /episode).

Pourquoi : les commentaires et pseudos donnés par Lucas viennent d'abonnés. Ils passent par le
filtre de la Production (`engine/pipeline/textes_ecran.py`, utilisé tel quel) **dès leur entrée**,
avant d'être transmis à story-chef : un texte refusé ne va jamais plus loin dans la chaîne.

Entrée : un fichier JSON `{"commentaires": ["…"], "pseudos": ["kevin_75", "@marie"]}`.
Passer les textes par un fichier, jamais dans la ligne de commande : un commentaire peut contenir
des guillemets ou des caractères que le shell interpréterait.

Sortie (stdout, JSON) : textes transmis, motifs des textes refusés (sans les recopier), pseudos à
valider. Mêmes clés que `audience.filtre` du suivi (`episodes/suivi/suivi.schema.json`).
Code retour : 0 si tout est accepté, 8 si au moins un texte est refusé (même code que le pipeline),
2 si le fichier d'entrée est invalide.

Le filtre est une ceinture de sécurité : un pseudo accepté reste « à valider par Lucas et Guillaume ».
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from engine.pipeline import textes_ecran  # noqa: E402

# Format d'un nom d'utilisateur Instagram : lettres, chiffres, « _ » et « . », 30 caractères au plus.
_FORMAT_PSEUDO = re.compile(r"[A-Za-z0-9_.]{1,30}")


def filtrer(commentaires: list[str], pseudos: list[str], liste=None) -> dict:
    """Passe chaque texte au filtre ; renvoie transmis, refusés et pseudos à valider."""
    liste = liste or textes_ecran.charger_liste()
    sortie = {"commentaires_transmis": [], "pseudos_transmis": [], "refuses": [], "pseudos_a_valider": []}

    for i, texte in enumerate(commentaires, 1):
        r = textes_ecran.verifier_texte(f"commentaire {i}", texte, liste)
        if r.ok:
            sortie["commentaires_transmis"].append(texte)
            # Un pseudo cité dans un commentaire accepté doit aussi être validé par un humain.
            sortie["pseudos_a_valider"] += [p["pseudo"] for p in r.pseudos]
        else:
            sortie["refuses"] += r.refus

    for i, brut in enumerate(pseudos, 1):
        origine = f"pseudo {i}"
        nom = brut.strip().removeprefix("@")
        if not _FORMAT_PSEUDO.fullmatch(nom):
            sortie["refuses"].append(f"{origine} : format de pseudo Instagram invalide")
            continue
        # Le @ active, dans le filtre, la recherche de mots collés à l'intérieur du pseudo.
        r = textes_ecran.verifier_texte(origine, "@" + nom, liste)
        if r.ok:
            sortie["pseudos_transmis"].append("@" + nom)
            sortie["pseudos_a_valider"].append("@" + nom)
        else:
            sortie["refuses"] += r.refus

    # Sans doublon, ordre conservé.
    sortie["pseudos_a_valider"] = list(dict.fromkeys(sortie["pseudos_a_valider"]))
    return sortie


def _liste_de_textes(donnees: dict, cle: str) -> list[str]:
    valeur = donnees.get(cle, [])
    if not isinstance(valeur, list) or not all(isinstance(t, str) for t in valeur):
        raise ValueError(f"« {cle} » doit être une liste de textes")
    return valeur


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("entree", type=Path, help="fichier JSON {commentaires, pseudos}")
    args = parser.parse_args(argv)
    # Windows : console en cp1252 par défaut ; les textes de l'audience peuvent contenir des accents.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    try:
        donnees = json.loads(args.entree.read_text(encoding="utf-8"))
        if not isinstance(donnees, dict):
            raise ValueError("l'entrée doit être un objet JSON")
        resultat = filtrer(_liste_de_textes(donnees, "commentaires"), _liste_de_textes(donnees, "pseudos"))
    except (OSError, ValueError) as e:  # json.JSONDecodeError hérite de ValueError
        print(f"Entrée invalide : {e}", file=sys.stderr)
        return 2
    print(json.dumps(resultat, ensure_ascii=False, indent=2))
    return 8 if resultat["refuses"] else 0


if __name__ == "__main__":
    sys.exit(main())
