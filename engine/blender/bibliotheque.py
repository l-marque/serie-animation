"""Chargement des assets de bibliothèque ('bibliotheque:<id>') dans des collections prototypes.

Le registre engine/assets/registre.json décrit chaque asset :
    {
      "fichier": "engine/assets/modeles/phare_01.glb",   # .blend, .glb, .gltf ou .fbx
      "collection": "Phare",                              # pour les .blend uniquement
      "echelle": 1.0,                                     # facteur appliqué à l'import (ignoré si "hauteur")
      "hauteur": 1.8,                                     # facultatif : hauteur voulue en mètres (mise à l'échelle auto)
      "poser_au_sol": true,                               # facultatif : recentre en (0, 0) et pose le bas à z = 0
      "rotation_z": 180,                                  # facultatif : correction d'orientation (degrés)
      "animation": "Idle",                                # facultatif : animation de l'asset jouée en boucle
      "degats": {"seed": 3, "nombre": 5, "taille": 0.22, "reparation": 0.0, "gravats": 14},
                                                          # facultatif : version abîmée (voir abimer())
      "role_defaut": "batiment",                          # rôle des pièces non listées
      "roles": {"Lanterne": "accent"},                    # rôle par nom d'objet (facultatif)
      "principal": "Corps",                               # pièce qui prend le rôle de la fiche
      "materiaux": "pack"                                 # "pack" (style unifié, défaut) ou "origine" (textures de l'asset)
    }

Convention : un asset posé au sol regarde vers -y (vers la caméra des plans par défaut). Utiliser
"rotation_z" pour corriger un modèle tourné autrement.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

from commun import journal


def charger_registre(racine: Path) -> dict:
    chemin = racine / "engine" / "assets" / "registre.json"
    return json.loads(chemin.read_text(encoding="utf-8")).get("assets", {}) if chemin.is_file() else {}


def _importer(fichier: Path, entree: dict) -> list[bpy.types.Object]:
    ext = fichier.suffix.lower()
    if ext == ".blend":
        with bpy.data.libraries.load(str(fichier), link=False) as (source, cible):
            cible.collections = [entree["collection"]]
        col = cible.collections[0]
        if col is None:
            raise RuntimeError(f"collection '{entree['collection']}' absente de {fichier}")
        return list(col.all_objects)
    avant = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(fichier))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(fichier))
    else:
        raise RuntimeError(f"format non pris en charge : {ext}")
    return [o for o in bpy.data.objects if o not in avant]


def _hierarchie(o: bpy.types.Object) -> list[bpy.types.Object]:
    chaine = []
    while o is not None:
        chaine.append(o)
        o = o.parent
    return chaine


def _retirer_parasites(objets: list[bpy.types.Object], entree: dict, asset_id: str) -> list[bpy.types.Object]:
    """Retire les objets indésirables livrés dans certains fichiers (sphère de collision, gizmo…).

    - "exclure" (registre) : noms ou débuts de noms à retirer ;
    - personnage animé : tout maillage hors de la hiérarchie de l'armature est retiré, sinon il
      fausserait la mise à l'échelle et apparaîtrait à l'image."""
    exclure = tuple(entree.get("exclure", []))
    armatures = [o for o in objets if o.type == "ARMATURE"]
    gardes, retires = [], []
    for o in objets:
        hors_armature = armatures and o.type == "MESH" and not any(a in _hierarchie(o) for a in armatures) \
            and not any(m.type == "ARMATURE" for m in o.modifiers)
        if (exclure and o.name.startswith(exclure)) or hors_armature:
            retires.append(o.name)
            bpy.data.objects.remove(o, do_unlink=True)
        else:
            gardes.append(o)
    if retires:
        journal(f"asset {asset_id} : objet(s) parasite(s) retiré(s) : {', '.join(retires)}")
    return gardes


# ----- animation -------------------------------------------------------------------------------
def _jouer_animation(objets: list[bpy.types.Object], nom: str) -> None:
    """Joue en boucle l'animation `nom` (ex. 'Idle', 'Wave') sur les armatures de l'asset.

    Les fichiers glTF nomment souvent leurs actions 'Armature|Idle' : on accepte le nom exact ou
    le suffixe après '|'. Une piste NLA répétée couvre n'importe quelle durée d'épisode."""
    armatures = [o for o in objets if o.type == "ARMATURE"]
    if not armatures:
        journal(f"animation '{nom}' demandée mais l'asset n'a pas d'armature : ignorée")
        return
    action = next((a for a in bpy.data.actions if a.name == nom or a.name.split("|")[-1] == nom), None)
    if action is None:
        dispo = sorted({a.name.split("|")[-1] for a in bpy.data.actions})
        raise RuntimeError(f"animation '{nom}' introuvable (disponibles : {', '.join(dispo)})")
    debut, fin = action.frame_range
    for arm in armatures:
        ad = arm.animation_data or arm.animation_data_create()
        ad.action = None
        for piste in list(ad.nla_tracks):
            ad.nla_tracks.remove(piste)
        piste = ad.nla_tracks.new()
        bande = piste.strips.new(nom, int(debut), action)
        bande.repeat = max(1.0, 20000.0 / max(fin - debut, 1.0))  # ≈ 11 min à 30 i/s


# ----- placement -------------------------------------------------------------------------------
def _boite_monde(objets: list[bpy.types.Object]) -> tuple[Vector, Vector] | None:
    """Boîte englobante (coordonnées monde) des maillages évalués : tient compte de la pose."""
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    mn, mx, trouve = Vector((1e18,) * 3), Vector((-1e18,) * 3), False
    for o in objets:
        if o.type != "MESH":
            continue
        ev = o.evaluated_get(deps)
        for coin in ev.bound_box:
            w = ev.matrix_world @ Vector(coin)
            mn, mx, trouve = Vector(map(min, mn, w)), Vector(map(max, mx, w)), True
    return (mn, mx) if trouve else None


def _transformer_racines(objets: list[bpy.types.Object], matrice: Matrix) -> None:
    for o in objets:
        if o.parent is None:
            o.matrix_world = matrice @ o.matrix_world


def _placer(objets: list[bpy.types.Object], entree: dict, asset_id: str) -> None:
    if entree.get("rotation_z"):
        _transformer_racines(objets, Matrix.Rotation(math.radians(entree["rotation_z"]), 4, "Z"))
    boite = _boite_monde(objets)
    if boite is None:
        return
    mn, mx = boite
    if entree.get("hauteur"):
        h = mx.z - mn.z
        if h <= 1e-6:
            raise RuntimeError(f"asset {asset_id} : hauteur nulle, impossible de le mettre à l'échelle")
        s = float(entree["hauteur"]) / h
    else:
        s = float(entree.get("echelle", 1.0))
    centre = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    if entree.get("poser_au_sol", bool(entree.get("hauteur"))):
        m = Matrix.Diagonal((s, s, s, 1.0)) @ Matrix.Translation(-centre)
    else:
        m = Matrix.Diagonal((s, s, s, 1.0))
    _transformer_racines(objets, m)


# ----- dégâts ------------------------------------------------------------------------------------
def _caillou(rng: random.Random, rayon: float, irregularite: float = 0.35) -> bmesh.types.BMesh:
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=rayon)
    for v in bm.verts:
        v.co *= 1.0 + irregularite * (rng.random() * 2 - 1)
    return bm


def abimer(objets: list[bpy.types.Object], degats: dict, asset_id: str) -> list[bpy.types.Object]:
    """Version abîmée d'un bâtiment ou d'un objet : morceaux arrachés + gravats au pied.

    Paramètres de `degats` :
      seed        même seed = mêmes dégâts (indispensable pour la continuité entre épisodes) ;
      nombre      nombre de morceaux arrachés (défaut 5) ;
      taille      rayon d'un arrachement, en fraction de la plus grande dimension (défaut 0,22) ;
      reparation  0 = ruine complète, 1 = réparé : les derniers arrachements sont « comblés » en
                  premier, donc 0,4 montre la MÊME ruine partiellement réparée (défaut 0) ;
      gravats     nombre de gravats au pied (défaut 3 × nombre), réduits avec la réparation ;
      zone_z      bande de hauteur visée, en fraction de la hauteur (défaut [0,55, 1,05] : toits et
                  angles ; [0, 0,5] pour abîmer le bas, ex. le bord d'une fontaine sans la décapiter) ;
      face_avant  vrai (défaut) : les arrachements mordent la face tournée vers -y, celle que voit la caméra.
    Les gravats sont renvoyés comme nouvelles pièces (rôle 'pierre')."""
    boite = _boite_monde(objets)
    if boite is None:
        return []
    mn, mx = boite
    dims = mx - mn
    rng = random.Random(int(degats.get("seed", 1)))
    nombre = int(degats.get("nombre", 5))
    taille = float(degats.get("taille", 0.22)) * max(dims)
    reparation = min(max(float(degats.get("reparation", 0.0)), 0.0), 1.0)
    # Tous les tirages sont faits même si une partie est réparée : la ruine reste identique.
    z_bas, z_haut = degats.get("zone_z", [0.55, 1.05])
    face_avant = degats.get("face_avant", True)
    trous = []
    for i in range(nombre):
        cote_x = mn.x if rng.random() < 0.5 else mx.x
        x = cote_x if rng.random() < 0.45 else mn.x + dims.x * rng.random()
        y = mn.y + dims.y * ((0.0 + 0.3 * rng.random()) if face_avant else (0.15 + 0.7 * rng.random()))
        z = mn.z + dims.z * (z_bas + (z_haut - z_bas) * rng.random())
        r = taille * (0.6 + 0.5 * rng.random())
        trous.append((Vector((x, y, z)), r, rng.randrange(1 << 30)))
    gardes = trous[: round(nombre * (1.0 - reparation))]
    if gardes:
        bm = bmesh.new()
        for centre, r, s in gardes:
            tmp = _caillou(random.Random(s), r, 0.3)
            bmesh.ops.translate(tmp, vec=centre, verts=tmp.verts)
            me_tmp = bpy.data.meshes.new("_trou")
            tmp.to_mesh(me_tmp)
            tmp.free()
            bm.from_mesh(me_tmp)
            bpy.data.meshes.remove(me_tmp)
        me = bpy.data.meshes.new(f"DEGATS_{asset_id}")
        bm.to_mesh(me)
        bm.free()
        coupe = bpy.data.objects.new(f"DEGATS_{asset_id}", me)
        bpy.context.scene.collection.objects.link(coupe)
        for o in objets:
            if o.type != "MESH" or any(m.type == "ARMATURE" for m in o.modifiers):
                continue
            mod = o.modifiers.new("Degats", "BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.use_hole_tolerant = True
            mod.object = coupe
            with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]):
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except RuntimeError as e:
                    o.modifiers.remove(mod)
                    journal(f"asset {asset_id} : coupe impossible sur {o.name} ({e})")
        bpy.data.objects.remove(coupe, do_unlink=True)
        bpy.data.meshes.remove(me)
    # Gravats au pied, autour de l'emprise, d'autant moins nombreux que la réparation avance.
    n_gravats = round(int(degats.get("gravats", 4 * nombre)) * (1.0 - reparation))
    gravats = []
    rng_g = random.Random(int(degats.get("seed", 1)) + 1000)
    for i in range(n_gravats):
        a = rng_g.random() * 2 * math.pi
        rx, ry = dims.x / 2 + 0.3 * taille * rng_g.random(), dims.y / 2 + 0.3 * taille * rng_g.random()
        r = taille * (0.05 + 0.08 * rng_g.random())  # petits blocs : des gravats, pas des rochers
        bm = _caillou(rng_g, r, 0.4)
        for v in bm.verts:
            v.co.z *= 0.55
        me = bpy.data.meshes.new(f"gravat_{i}")
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(f"{asset_id}_gravat_{i:02d}", me)
        o.location = ((mn.x + mx.x) / 2 + rx * math.cos(a), (mn.y + mx.y) / 2 + ry * math.sin(a), mn.z + r * 0.3)
        o.rotation_euler = (rng_g.random(), rng_g.random(), rng_g.random() * 6.28)
        bpy.context.scene.collection.objects.link(o)
        gravats.append(o)
    journal(f"asset {asset_id} : {len(gardes)}/{nombre} arrachement(s), {len(gravats)} gravat(s)")
    return gravats


def pieces_bibliotheque(racine: Path, asset_id: str) -> list[tuple[bpy.types.Object, str, bool]]:
    """Importe un asset et renvoie [(objet, role, principal)] prêts à être rangés dans un prototype."""
    entree = charger_registre(racine).get(asset_id)
    if entree is None:
        raise RuntimeError(f"asset 'bibliotheque:{asset_id}' absent du registre")
    fichier = racine / entree["fichier"]
    if not fichier.is_file():
        raise RuntimeError(f"asset {asset_id} : fichier absent ({entree['fichier']}) — relancer l'intégration")
    objets = _retirer_parasites(_importer(fichier, entree), entree, asset_id)
    if entree.get("animation"):
        _jouer_animation(objets, entree["animation"])
    _placer(objets, entree, asset_id)
    roles = entree.get("roles", {})
    sortie = []
    if entree.get("degats"):
        for g in abimer(objets, entree["degats"], asset_id):
            sortie.append((g, "pierre", False))
    for o in objets:
        role = roles.get(o.name, entree.get("role_defaut", "accessoire"))
        sortie.append((o, role, o.name == entree.get("principal")))
    for o, _, _ in sortie:
        for col in list(o.users_collection):
            col.objects.unlink(o)
    journal(f"asset bibliotheque:{asset_id} importé ({len(sortie)} objet(s))")
    return sortie
