"""Primitives « village » : mobilier et habillage simples, générés par code.

Les bâtiments, personnages et objets détaillés viennent de la bibliothèque (modèles sourcés,
engine/assets/registre.json) ; ce module ne fournit que ce qu'aucune banque ne propose dans
une forme utilisable : panneau d'entrée de ville à la française (texte ajouté par l'habillage),
carte de choix blanche, icône plate, point de visée invisible.

Convention : face avant tournée vers -y, posé au sol (z = 0), centré en (0, 0).
"""

from __future__ import annotations

from .formes import Piece, assembler, boite, cone, maillage, tourner


def panneau_entree(seed: int) -> list[Piece]:
    """Panneau d'entrée d'agglomération (2,4 × 0,9 m) : fond blanc, liseré rouge, deux poteaux.
    Le nom de la ville est un texte 3D de l'habillage, centré à (0, -0,07, 1,85)."""
    return [
        ("cadre", maillage("cadre", boite(2.4, 0.06, 0.9, biseau=0.03)), (0, 0, 1.85), 0.0, "accent", True),
        ("fond", maillage("fond", boite(2.22, 0.02, 0.74, biseau=0.01)), (0, -0.035, 1.85), 0.0, "blanc", False),
        ("poteaux", maillage("poteaux", assembler((cone(8, 0.04, 0.04, 2.3), (-0.85, 0.05, 0)),
                                                   (cone(8, 0.04, 0.04, 2.3), (0.85, 0.05, 0)))),
         (0, 0, 1.15), 0.0, "pierre", False),
    ]


def carte_choix(seed: int) -> list[Piece]:
    """Carte blanche debout (2,0 × 2,6 m) pour un écran de choix ; poser l'objet à montrer devant
    (y ≈ -0,25) et sa légende en texte 3D de l'habillage."""
    return [
        ("carte", maillage("carte", boite(2.0, 0.08, 2.6, biseau=0.06), lisse=True), (0, 0, 1.3), 0.0, "blanc", True),
        ("ombre", maillage("ombre", boite(2.06, 0.04, 2.66, biseau=0.06)), (0, 0.05, 1.3), 0.0, "accent", False),
    ]


def icone_fontaine(seed: int) -> list[Piece]:
    """Pictogramme plat de fontaine (≈ 0,5 m), face à -y : bassin, colonne, vasque, trois jets."""
    plat = 0.03

    def jet(angle_deg: float):
        return tourner(boite(0.035, plat, 0.16), angle_deg, "Y")

    return [
        ("bassin", maillage("bassin", assembler((boite(0.5, plat, 0.1), (0, 0, 0.05)),
                                                 (boite(0.07, plat, 0.16), (0, 0, 0.18)),
                                                 (boite(0.26, plat, 0.05), (0, 0, 0.28)))),
         (0, 0, 0), 0.0, "eau", True),
        ("jets", maillage("jets", assembler((jet(0), (0, 0, 0.4)), (jet(-35), (-0.1, 0, 0.37)),
                                             (jet(35), (0.1, 0, 0.37)))),
         (0, -0.005, 0), 0.0, "eau", False),
    ]


def repere(seed: int) -> list[Piece]:
    """Point invisible : cible de caméra ou centre d'une composition (aucune géométrie)."""
    return []


PRIMITIVES = {
    "panneau_entree": panneau_entree,
    "carte_choix": carte_choix,
    "icone_fontaine": icone_fontaine,
    "repere": repere,
}
