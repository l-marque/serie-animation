"""Kits de décor. Un kit fournit des prototypes d'assets ('primitif:<nom>').

Pour ajouter un kit : créer kits/<nom>.py exposant PRIMITIVES (dict nom -> fonction) et
ROLE_PRINCIPAL, puis l'ajouter à KITS ci-dessous et à engine/pipeline/chemins.py.
"""

from . import primitifs

KITS = {"primitifs": primitifs}
