"""Contrôle des textes qui seront affichés ou lus dans une vidéo.

Pourquoi : la série affiche des pseudos et des propositions d'abonnés. Tout texte qui finit à
l'écran (titre, voix off donc sous-titres, texte à l'écran, textes 3D, HUD) passe ici avant la
synthèse vocale et le rendu.

Deux niveaux :
- **refus** (bloquant, code 8) : mot de la liste `engine/assets/moderation/mots_interdits.txt`,
  lien web, caractères invisibles ou de contrôle (souvent utilisés pour contourner un filtre).
- **à valider par un humain** (non bloquant) : chaque pseudo « @… » est listé dans le rapport et
  dans la plaquette Figma ; c'est la validation de Guillaume qui l'autorise, pas ce module.

Ce filtre est une ceinture de sécurité, pas un modérateur : il ne remplace pas la relecture humaine.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from . import chemins

LISTE_MOTS = chemins.MOTEUR / "assets" / "moderation" / "mots_interdits.txt"
EXCEPTIONS = chemins.MOTEUR / "assets" / "moderation" / "exceptions.txt"

_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s", "€": "e"})
_LIEN = re.compile(r"(https?://|www\.|\b[\w-]+\.(com|fr|net|org|io|gg|ly|me|tv|xyz|be|co)\b)", re.IGNORECASE)
_PSEUDO = re.compile(r"(?<![\w@])@([A-Za-z0-9_.]{1,30})")
# Catégories Unicode refusées : contrôle (Cc) sauf saut de ligne, format (Cf : largeur nulle, sens
# d'écriture…), non attribué (Cn), usage privé (Co), substituts (Cs).
_CATEGORIES_REFUSEES = {"Cc", "Cf", "Cn", "Co", "Cs"}


@dataclass
class Resultat:
    refus: list[str] = field(default_factory=list)
    pseudos: list[dict[str, str]] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.refus


def _lignes(chemin: Path) -> list[str]:
    if not chemin.is_file():
        return []
    return [l for l in (x.split("#", 1)[0].strip() for x in chemin.read_text(encoding="utf-8").splitlines()) if l]


def charger_liste(chemin: Path = LISTE_MOTS, exceptions: Path = EXCEPTIONS):
    """(mots exacts, préfixes, exceptions) normalisés ; lignes vides et commentaires ignorés."""
    exacts, prefixes = set(), []
    for ligne in _lignes(chemin):
        if ligne.endswith("*"):
            prefixes.append(_normaliser(ligne[:-1]))
        else:
            exacts.add(_normaliser(ligne))
    autorises = frozenset(_normaliser(l.lstrip("@")) for l in _lignes(exceptions))
    return frozenset(exacts), tuple(p for p in prefixes if p), autorises


def _sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texte) if not unicodedata.combining(c))


def _normaliser(mot: str) -> str:
    """Minuscules, sans accents, leet traduit, seulement lettres et chiffres."""
    mot = _sans_accents(mot.lower()).translate(_LEET)
    return re.sub(r"[^a-z0-9]", "", mot)


def _sans_repetitions(mot: str) -> str:
    return re.sub(r"(.)\1+", r"\1", mot)


def _mots(texte: str) -> Iterable[str]:
    # Les séparateurs internes (« c.o.n.n.a.r.d », « f-u-c-k ») sont supprimés par la normalisation.
    for brut in texte.split():
        n = _normaliser(brut.lstrip("@#"))  # « @pseudo » : le @ n'est pas un « a »
        if n:
            yield n


def _interdit(mot: str, exacts: frozenset[str], prefixes: tuple[str, ...]) -> str | None:
    for forme in {mot, _sans_repetitions(mot)}:
        if forme in exacts:
            return forme
        for p in prefixes:
            if forme.startswith(p) or _sans_repetitions(forme).startswith(_sans_repetitions(p)):
                return p
    return None


def verifier_texte(origine: str, texte: str, liste=None) -> Resultat:
    exacts, prefixes, autorises = liste or charger_liste()
    r = Resultat()
    for c in texte:
        if c != "\n" and unicodedata.category(c) in _CATEGORIES_REFUSEES:
            r.refus.append(f"{origine} : caractère invisible ou de contrôle U+{ord(c):04X}")
            break
    if _LIEN.search(texte):
        r.refus.append(f"{origine} : lien web interdit à l'écran")
    for mot in _mots(texte):
        if mot in autorises:
            continue
        trouve = _interdit(mot, exacts, prefixes)
        if trouve:
            r.refus.append(f"{origine} : mot refusé (liste de modération : « {trouve} »)")
            break
    for m in _PSEUDO.finditer(texte):
        pseudo = "@" + m.group(1)
        # Dans un pseudo, les mots sont collés (« @kevin_nazi ») : on cherche aussi à l'intérieur,
        # pour les entrées d'au moins 4 lettres (en dessous, trop de faux positifs).
        colle = _normaliser(m.group(1))
        formes = {colle, _sans_repetitions(colle)}
        cachee = None if colle in autorises else next(
            (w for w in (*exacts, *prefixes) if len(w) >= 4 and any(w in f or _sans_repetitions(w) in f for f in formes)), None)
        if cachee and not r.refus:
            r.refus.append(f"{origine} : pseudo {pseudo} refusé (liste de modération : « {cachee} »)")
        r.pseudos.append({"origine": origine, "pseudo": pseudo})
    return r


def textes_episode(fiche: dict[str, Any], habillage: dict[str, Any] | None) -> list[tuple[str, str]]:
    """Tous les textes d'un épisode qui seront montrés ou dits, avec leur origine lisible."""
    textes: list[tuple[str, str]] = []
    if fiche.get("titre"):
        textes.append(("titre", fiche["titre"]))
    for b in fiche.get("beats", []):
        for cle in ("voix", "texte_ecran"):
            if (b.get(cle) or "").strip():
                textes.append((f"beat {b.get('id', '?')} / {cle}", b[cle]))
    hab = habillage or {}
    for t in hab.get("textes_3d", []):
        textes.append((f"texte 3D {t.get('id', '?')}", t.get("texte", "")))
    for i, e in enumerate(hab.get("hud", [])):
        for cle in ("texte", "etiquette", "libelle"):
            if isinstance(e.get(cle), str) and e[cle].strip():
                textes.append((f"hud {e.get('id', i)} / {cle}", e[cle]))
    return textes


def verifier_episode(fiche: dict[str, Any], habillage: dict[str, Any] | None) -> Resultat:
    liste = charger_liste()
    total = Resultat()
    for origine, texte in textes_episode(fiche, habillage):
        r = verifier_texte(origine, texte, liste)
        total.refus += r.refus
        total.pseudos += r.pseudos
    return total
