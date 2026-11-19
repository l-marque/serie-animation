"""Look : applique le pack de direction artistique (DA) à toute la scène.

Seul module autorisé à créer ou modifier des matériaux. Les assets (primitives ou
bibliothèque) ne portent qu'un RÔLE ; le pack décide de la couleur de chaque rôle.
C'est ce qui rend cohérents des assets venus de sources différentes.
"""

from __future__ import annotations

import math

import bpy

from commun import journal

ROLES = ("sol", "batiment", "toit", "vegetation", "roche", "personnage", "accessoire", "accent")

# Rôles facultatifs, utilisés par les pièces secondaires des primitives (visage d'un personnage,
# costume, panneau blanc, pièces d'or…). Un pack peut les redéfinir dans « materiaux » ; sinon ces
# valeurs neutres s'appliquent, ce qui évite d'imposer un rôle de plus à chaque pack existant.
ROLES_FACULTATIFS: dict[str, dict] = {
    "eau": {"couleur": [0.16, 0.5, 0.75], "rugosite": 0.08},
    "peau": {"couleur": [0.80, 0.56, 0.42], "rugosite": 0.55},
    "tissu": {"couleur": [0.07, 0.09, 0.17], "rugosite": 0.85},
    "blanc": {"couleur": [0.90, 0.90, 0.88], "rugosite": 0.5},
    "or": {"couleur": [1.0, 0.70, 0.12], "rugosite": 0.3, "metal": 1.0},
    "pierre": {"couleur": [0.62, 0.58, 0.52], "rugosite": 0.9},
}


def _principled(mat: bpy.types.Material) -> bpy.types.Node:
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _entree(noeud: bpy.types.Node, *noms: str):
    """Première entrée existante parmi plusieurs noms (ils ont changé entre versions)."""
    for nom in noms:
        if nom in noeud.inputs:
            return noeud.inputs[nom]
    return None


def materiau_role(pack: dict, role: str) -> bpy.types.Material:
    nom = f"MAT_{role}"
    mat = bpy.data.materials.get(nom)
    if mat is not None:
        return mat
    spec = pack["materiaux"].get(role) or ROLES_FACULTATIFS.get(role) or pack["materiaux"]["accessoire"]
    mat = bpy.data.materials.new(nom)
    mat.use_nodes = True
    bsdf = _principled(mat)
    couleur = (*spec["couleur"], 1.0)
    bsdf.inputs["Base Color"].default_value = couleur
    bsdf.inputs["Roughness"].default_value = spec.get("rugosite", 0.8)
    bsdf.inputs["Metallic"].default_value = spec.get("metal", 0.0)
    if spec.get("emission"):
        e = _entree(bsdf, "Emission Color", "Emission")
        s = _entree(bsdf, "Emission Strength")
        if e is not None:
            e.default_value = couleur
        if s is not None:
            s.default_value = spec["emission"]
    if spec.get("textures"):
        _brancher_textures(mat, bsdf, spec)
    mat.diffuse_color = couleur  # couleur utilisée par le moteur Workbench et le viewport
    return mat


def _brancher_textures(mat: bpy.types.Material, bsdf: bpy.types.Node, spec: dict) -> None:
    """Matériau PBR (Poly Haven, 3DTexel) : dossier avec cartes.json {couleur, normale, rugosite}.
    Projection « boîte » en coordonnées objet, une tuile tous les `echelle_texture` mètres ; la couleur
    du pack est multipliée par la texture (teinte), ce qui garde la palette de la DA."""
    import json as _json
    from pathlib import Path
    racine = Path(__file__).resolve().parents[2]
    dossier = racine / spec["textures"]
    fichier_cartes = dossier / "cartes.json"
    if not fichier_cartes.is_file():
        journal(f"textures absentes ({spec['textures']}) : couleur unie du pack utilisée")
        return
    cartes = _json.loads(fichier_cartes.read_text(encoding="utf-8"))
    nt = mat.node_tree
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    echelle = 1.0 / max(spec.get("echelle_texture", 1.0), 0.01)
    mapping.inputs["Scale"].default_value = (echelle, echelle, echelle)
    nt.links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    def image(nom_carte: str, non_couleur: bool):
        if nom_carte not in cartes:
            return None
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(str(dossier / cartes[nom_carte]), check_existing=True)
        tex.projection = "BOX"
        tex.projection_blend = 0.2
        if non_couleur:
            tex.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        return tex

    t_couleur = image("couleur", False)
    if t_couleur is not None:
        teinte = nt.nodes.new("ShaderNodeMix")
        teinte.data_type = "RGBA"
        teinte.blend_type = "MULTIPLY"
        teinte.inputs["Factor"].default_value = spec.get("force_teinte", 0.6)
        nt.links.new(t_couleur.outputs["Color"], teinte.inputs["A"])
        teinte.inputs["B"].default_value = (*spec["couleur"], 1.0)
        nt.links.new(teinte.outputs["Result"], bsdf.inputs["Base Color"])
    t_rug = image("rugosite", True)
    if t_rug is not None:
        nt.links.new(t_rug.outputs["Color"], bsdf.inputs["Roughness"])
    t_nor = image("normale", True)
    if t_nor is not None:
        carte_normale = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(t_nor.outputs["Color"], carte_normale.inputs["Color"])
        nt.links.new(carte_normale.outputs["Normal"], bsdf.inputs["Normal"])


def materiau_contour(pack: dict) -> bpy.types.Material | None:
    """Contour cartoon par « coque inversée » : visible seulement sur les faces tournées vers la caméra
    après inversion des normales. Fonctionne en EEVEE et en Cycles sans réglage de culling."""
    contours = pack.get("contours", {})
    if not contours.get("actif"):
        return None
    mat = bpy.data.materials.get("MAT_contour")
    if mat is not None:
        return mat
    mat = bpy.data.materials.new("MAT_contour")
    mat.use_nodes = True
    arbre = mat.node_tree
    arbre.nodes.clear()
    sortie = arbre.nodes.new("ShaderNodeOutputMaterial")
    melange = arbre.nodes.new("ShaderNodeMixShader")
    emission = arbre.nodes.new("ShaderNodeEmission")
    transparent = arbre.nodes.new("ShaderNodeBsdfTransparent")
    geometrie = arbre.nodes.new("ShaderNodeNewGeometry")
    emission.inputs["Color"].default_value = (*contours.get("couleur", [0, 0, 0]), 1.0)
    arbre.links.new(geometrie.outputs["Backfacing"], melange.inputs["Fac"])
    arbre.links.new(emission.outputs["Emission"], melange.inputs[1])
    arbre.links.new(transparent.outputs["BSDF"], melange.inputs[2])
    arbre.links.new(melange.outputs["Shader"], sortie.inputs["Surface"])
    mat.diffuse_color = (*contours.get("couleur", [0, 0, 0]), 1.0)
    return mat


def ajouter_contour(obj: bpy.types.Object, pack: dict) -> None:
    mat = materiau_contour(pack)
    if mat is None or obj.type != "MESH":
        return
    obj.data.materials.append(mat)
    mod = obj.modifiers.new("Contour", "SOLIDIFY")
    mod.thickness = pack["contours"].get("epaisseur", 0.03)
    mod.offset = 1.0
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.material_offset = len(obj.data.materials) - 1


def appliquer_role(obj: bpy.types.Object, role: str, pack: dict, garder_materiaux: bool = False) -> None:
    """Remplace les matériaux d'un maillage par celui du rôle (surcharge de style), puis ajoute le contour.

    garder_materiaux=True conserve les matériaux d'origine (asset texturé importé, registre :
    "materiaux": "origine") ; seul le contour du pack est ajouté.
    """
    if obj.type != "MESH":
        return
    garde = garder_materiaux and len(obj.data.materials)
    if not garde:
        obj.data.materials.clear()
        obj.data.materials.append(materiau_role(pack, role))
    # Le contour cartoon (coque inversée) abîme les modèles texturés et détaillés : seulement si le pack
    # le demande explicitement pour eux.
    if not garde or pack.get("contours", {}).get("sur_assets_textures", False):
        ajouter_contour(obj, pack)


def _brancher_hdri(monde: bpy.types.World, fond: bpy.types.Node, chemin_rel: str) -> None:
    """Éclairage par image HDRI (Poly Haven) ; chemin relatif à la racine du dépôt, ignoré s'il manque."""
    from pathlib import Path
    racine = Path(__file__).resolve().parents[2]  # engine/blender/look.py -> racine du dépôt
    chemin = racine / chemin_rel
    if not chemin.is_file():
        journal(f"HDRI absente ({chemin_rel}) : couleur unie du pack utilisée")
        return
    tex = monde.node_tree.nodes.new("ShaderNodeTexEnvironment")
    tex.image = bpy.data.images.load(str(chemin), check_existing=True)
    monde.node_tree.links.new(tex.outputs["Color"], fond.inputs["Color"])


def monde_et_lumiere(scene: bpy.types.Scene, pack: dict) -> None:
    monde = bpy.data.worlds.new("MONDE")
    monde.use_nodes = True
    fond = next(n for n in monde.node_tree.nodes if n.type == "BACKGROUND")
    fond.inputs["Color"].default_value = (*pack["monde"]["couleur"], 1.0)
    fond.inputs["Strength"].default_value = pack["monde"].get("intensite", 1.0)
    hdri = pack["monde"].get("hdri")
    if hdri:
        _brancher_hdri(monde, fond, hdri)
    monde.color = pack["monde"]["couleur"]  # couleur lue par Workbench et le viewport
    scene.world = monde
    s = pack["soleil"]
    donnees = bpy.data.lights.new("SOLEIL", "SUN")
    donnees.energy = s.get("energie", 3.0)
    donnees.color = s.get("couleur", [1, 1, 1])
    soleil = bpy.data.objects.new("SOLEIL", donnees)
    soleil.rotation_euler = [math.radians(a) for a in s.get("rotation_deg", [50, 0, 35])]
    scene.collection.objects.link(soleil)
    scene.view_settings.view_transform = pack.get("transformation_vue", "Standard")
    scene.view_settings.exposure = pack.get("exposition", 0.0)
    if pack.get("look_vue"):   # facultatif : look de la transformation (ex. AgX « Punchy », plus saturé)
        nom = pack["look_vue"]
        try:
            scene.view_settings.look = nom
        except TypeError:
            scene.view_settings.look = f"{scene.view_settings.view_transform} - {nom}"


def moteur(scene: bpy.types.Scene, pack: dict, mode: str, forcer: str | None = None) -> str:
    """Règle le moteur de rendu. Renvoie le moteur effectivement retenu."""
    voulu = forcer or pack["moteur"].get(mode, "BLENDER_EEVEE")
    candidats = [voulu, "BLENDER_EEVEE_NEXT"] if voulu == "BLENDER_EEVEE" else [voulu]
    candidats.append(pack["moteur"].get("secours", "CYCLES"))
    for c in candidats:
        try:
            scene.render.engine = c
            break
        except TypeError:
            continue
    retenu = scene.render.engine
    adapter_contours(retenu)
    if retenu == "BLENDER_WORKBENCH":
        # Aperçu rapide : couleurs des matériaux du pack, contours natifs du moteur.
        ombrage = scene.display.shading
        ombrage.light = "STUDIO"
        ombrage.color_type = "MATERIAL"
        ombrage.show_object_outline = bool(pack.get("contours", {}).get("actif"))
        ombrage.object_outline_color = pack.get("contours", {}).get("couleur", [0, 0, 0])
        ombrage.show_shadows = True
        ombrage.background_type = "WORLD"
        scene.display.render_aa = "8"
    elif retenu == "CYCLES":
        scene.cycles.samples = pack.get("cycles", {}).get(f"echantillons_{mode}", 16)
        scene.cycles.use_denoising = True
        _activer_gpu_cycles(scene)
    elif retenu.startswith("BLENDER_EEVEE"):
        reglages = pack.get("eevee", {})
        scene.eevee.taa_render_samples = reglages.get(f"echantillons_{mode}", 16)
        # Lumière indirecte, reflets et ombres de contact : grosse différence de qualité perçue,
        # activée par défaut au rendu final (coût modéré sur une RTX), désactivable dans le pack.
        rt = reglages.get("lancer_de_rayons", mode == "final")
        if hasattr(scene.eevee, "use_raytracing"):
            scene.eevee.use_raytracing = bool(rt)
        if hasattr(scene.eevee, "use_shadows"):
            scene.eevee.use_shadows = True
    journal(f"moteur de rendu : {retenu}")
    return retenu


def adapter_contours(moteur_retenu: str) -> None:
    """La coque inversée ne fonctionne pas en Workbench (pas de nœuds de shader) : on la masque au rendu.
    Appelée aussi après la construction du décor, et en cas de bascule de moteur."""
    visible = moteur_retenu != "BLENDER_WORKBENCH"
    for obj in bpy.data.objects:
        mod = obj.modifiers.get("Contour") if obj.type == "MESH" else None
        if mod is not None:
            mod.show_render = visible
            mod.show_viewport = visible


def _activer_gpu_cycles(scene: bpy.types.Scene) -> None:
    """Active le GPU pour Cycles s'il y en a un (OptiX, puis CUDA, puis HIP/Metal/oneAPI). Sinon CPU."""
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
    except KeyError:
        return
    for type_calcul in ("OPTIX", "CUDA", "HIP", "METAL", "ONEAPI"):
        try:
            prefs.compute_device_type = type_calcul
            prefs.get_devices()
        except (TypeError, AttributeError):
            continue
        gpus = [d for d in prefs.devices if d.type == type_calcul]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == type_calcul
            scene.cycles.device = "GPU"
            journal(f"Cycles sur GPU ({type_calcul}, {len(gpus)} périphérique(s))")
            return
    scene.cycles.device = "CPU"
    journal("Cycles sur CPU (aucun GPU détecté)")
