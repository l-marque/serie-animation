"""Instances en nœuds de géométrie (Geometry Nodes) pour l'atelier : touffes d'herbe, foules.

Principe compatible avec le moteur (vérifié le 2026-11-19 avec engine/blender/bibliotheque.py) : l'asset est
un .blend dont la collection principale contient UN objet « nuage » (un maillage fait seulement de sommets,
un sommet = une instance, avec ses attributs : variante, rotation, échelle, phase…) porteur d'un modificateur
Geometry Nodes. Les modèles instanciés vivent dans une AUTRE collection (« <Asset>_sources ») qui n'est pas
enfant de la collection principale : le moteur ne l'ajoute donc pas au prototype (sinon les modèles sources
apparaîtraient à l'origine), mais elle est importée avec l'arbre de nœuds qui la référence.

    import instances as ins
    nuage = ins.nuage("Touffes", points, {"variante": ("INT", [...]), "rotz": ("FLOAT", [...])})
    a = ins.Arbre("GN_touffes")
    pts = a.entree_geo()
    ...
    a.sortie_geo(geo)
    a.poser(nuage)
"""
from __future__ import annotations

import bpy


def nuage(nom: str, points, attributs: dict, materiau=None) -> bpy.types.Object:
    """Objet maillage fait de sommets seuls. attributs : {nom: ("FLOAT"|"INT"|"FLOAT_VECTOR", valeurs)}.

    `materiau` : un matériau posé sur le nuage (le moteur garde alors les matériaux d'origine des instances
    avec « materiaux »: « origine » ; sans matériau, il remplacerait par celui du rôle)."""
    me = bpy.data.meshes.new(nom)
    me.from_pydata([tuple(p) for p in points], [], [])
    for cle, (type_, valeurs) in attributs.items():
        at = me.attributes.new(cle, type_, "POINT")
        champ = "vector" if type_ == "FLOAT_VECTOR" else "value"
        plat = [c for v in valeurs for c in v] if type_ == "FLOAT_VECTOR" else list(valeurs)
        at.data.foreach_set(champ, plat)
    if materiau is not None:
        me.materials.append(materiau)
    o = bpy.data.objects.new(nom, me)
    return o


class Arbre:
    """Petit outil pour écrire un arbre de nœuds de géométrie en Python sans se perdre dans les liens."""

    def __init__(self, nom: str):
        self.ng = bpy.data.node_groups.new(nom, "GeometryNodeTree")
        self.ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
        self.ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        self.n_in = self.ng.nodes.new("NodeGroupInput")
        self.n_out = self.ng.nodes.new("NodeGroupOutput")
        self.x = 0

    def entree_geo(self):
        return self.n_in.outputs[0]

    def sortie_geo(self, geo) -> None:
        self.ng.links.new(geo, self.n_out.inputs[0])

    def noeud(self, type_: str, entrees: dict | None = None, **proprietes):
        n = self.ng.nodes.new(type_)
        self.x += 180
        n.location = (self.x, 0)
        for k, v in proprietes.items():
            setattr(n, k, v)
        for k, v in (entrees or {}).items():
            prise = n.inputs[k]
            if isinstance(v, bpy.types.NodeSocket):
                self.ng.links.new(v, prise)
            else:
                prise.default_value = v
        return n

    def attr(self, nom: str, type_: str = "FLOAT"):
        return self.noeud("GeometryNodeInputNamedAttribute", {"Name": nom}, data_type=type_).outputs["Attribute"]

    def math(self, op: str, a, b=None, c=None):
        n = self.noeud("ShaderNodeMath", operation=op)
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, bpy.types.NodeSocket):
                self.ng.links.new(v, n.inputs[i])
            else:
                n.inputs[i].default_value = v
        return n.outputs[0]

    def xyz(self, x=0.0, y=0.0, z=0.0):
        return self.noeud("ShaderNodeCombineXYZ", {"X": x, "Y": y, "Z": z}).outputs[0]

    def temps(self):
        return self.noeud("GeometryNodeInputSceneTime").outputs["Frame"]

    def poser(self, objet: bpy.types.Object, nom_modificateur: str = "Instances") -> None:
        mod = objet.modifiers.new(nom_modificateur, "NODES")
        mod.node_group = self.ng


def instancier_variantes(a: Arbre, points, collection: bpy.types.Collection, selection=None):
    """Instance on Points : une variante par sommet (attribut entier « variante », ordre alphabétique des
    objets de `collection`), rotation z « rotz » (radians), échelle « echelle »."""
    info = a.noeud("GeometryNodeCollectionInfo", {"Collection": collection, "Separate Children": True,
                                                  "Reset Children": True})
    rot = a.noeud("FunctionNodeEulerToRotation", {"Euler": a.xyz(0, 0, a.attr("rotz"))}).outputs[0]
    entrees = {"Points": points, "Instance": info.outputs[0], "Pick Instance": True,
               "Instance Index": a.attr("variante", "INT"), "Rotation": rot, "Scale": a.attr("echelle")}
    if selection is not None:
        entrees["Selection"] = selection
    return a.noeud("GeometryNodeInstanceOnPoints", entrees).outputs[0]


def brume(mat, couleur, debut=70.0, fin=950.0, force=1.0):
    """Ajoute au matériau un fondu vers la couleur du ciel selon la distance à la caméra (perspective aérienne)."""
    nt = mat.node_tree
    sortie = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    bsdf = sortie.inputs["Surface"].links[0].from_node
    cam = nt.nodes.new("ShaderNodeCameraData")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = debut
    mr.inputs["From Max"].default_value = fin
    mr.inputs["To Max"].default_value = force
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 0.7
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*couleur[:3], 1.0)
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(cam.outputs["View Distance"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], pw.inputs[0])
    nt.links.new(pw.outputs[0], mix.inputs["Fac"])
    nt.links.new(bsdf.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], sortie.inputs["Surface"])
    return mat
