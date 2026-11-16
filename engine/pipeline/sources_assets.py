"""Sources d'assets 3D libres de droits, interrogées par API (outil du bibliothécaire).

Sources :
    polyhaven   modèles, HDRI et textures CC0 — API publique sans clé (crédit « Powered by Poly Haven »)
    polypizza   modèles low-poly CC0 / CC-BY — clé gratuite POLY_PIZZA_KEY (fichier .env)
    sketchfab   très grand catalogue ; seuls CC0 et CC-BY sont acceptés — jeton SKETCHFAB_TOKEN (.env)

    3dtexel     matériaux PBR, HDRI et modèles « handmade » CC0 — recherche sans clé ; téléchargement
                avec une clé gratuite TEXEL_API_KEY (.env). Les assets IA et « premium » (payants en
                crédits ou sous licence 3DTexel) sont écartés d'office.

Poly Haven fournit aussi des textures PBR CC0 (sol, carrelage, bois…) : `texture`.

ÉTAT : écrit et testé avec des réponses simulées ; à valider au premier appel réel (le réseau de
l'environnement de développement bloque ces sites). Les noms de champs incertains sont lus avec
plusieurs variantes et signalés par 'a_verifier' dans les résultats.

Usage :
    python -m engine.pipeline.sources_assets chercher "lighthouse" --sources polyhaven,polypizza
    python -m engine.pipeline.sources_assets integrer polyhaven <id_source> --id phare_01 --role-defaut batiment
    python -m engine.pipeline.sources_assets hdri <id_polyhaven> --resolution 2k
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from . import chemins

AGENT_UTILISATEUR = "serie-animation-pipeline/1.0 (github.com/l-marque/serie-animation)"
LICENCES_ACCEPTEES = {"cc0", "cc-by", "by", "cc-by-4.0", "cc-by-3.0", "public domain", "cc0 1.0"}
DOSSIER_MODELES = chemins.ASSETS / "modeles"
DOSSIER_HDRI = chemins.ASSETS / "hdri"
DOSSIER_TEXTURES = chemins.ASSETS / "textures"


class SourceErreur(Exception):
    pass


def licence_acceptee(licence: str) -> bool:
    """CC0, domaine public ou CC-BY simple (toutes versions). Refus : NC, ND, SA, Editorial, inconnue."""
    l = re.sub(r"[\s_]+", "-", licence.strip().lower()).replace("creative-commons", "cc")
    # Libellés longs (Sketchfab : « CC Attribution-NonCommercial ») ramenés aux codes courts.
    for long, court in (("attribution", "by"), ("noncommercial", "nc"), ("sharealike", "sa"),
                        ("noderivatives", "nd"), ("noderivs", "nd"), ("public-domain", "cc0")):
        l = l.replace(long, court)
    if l in LICENCES_ACCEPTEES:
        return True
    jetons = [j for j in l.split("-") if j]
    if set(jetons) & {"nc", "nd", "sa", "editorial"}:
        return False
    neutres = {"cc", "universal", "international", "unported", "licence", "license", "deed"}
    reste = [j for j in jetons if j not in neutres and not re.fullmatch(r"\d+(\.\d+)?", j)]
    return reste in (["cc0"], ["cc0", "cc0"], ["by"], ["zero"], ["0"])


@dataclass
class Candidat:
    source: str
    id_source: str
    nom: str
    auteur: str
    licence: str
    url_page: str
    apercu: str = ""
    triangles: int | None = None
    anime: bool = False
    url_telechargement: str = ""
    a_verifier: list[str] = field(default_factory=list)

    @property
    def licence_ok(self) -> bool:
        return licence_acceptee(self.licence)

    @property
    def attribution_requise(self) -> bool:
        return "by" in self.licence.lower() and "cc0" not in self.licence.lower()


# ----- réseau ---------------------------------------------------------------------------------
# Autres noms acceptés pour une même clé (noms déjà utilisés dans les .env de l'équipe).
ALIAS_CLES = {"POLY_PIZZA_KEY": ("API_Poly_Pizza", "POLYPIZZA_KEY"),
              "TEXEL_API_KEY": ("API_3D_Texel", "API_3DTexel", "API_Texel"),
              "SKETCHFAB_TOKEN": ("API_Sketchfab", "SKETCHFAB_KEY")}


def _env(cle: str) -> str | None:
    """Lit une clé dans l'environnement ou dans le fichier .env local (jamais versionné).

    Tolère « NOM=valeur », « NOM = valeur » et « NOM : valeur » (fautes de frappe fréquentes)."""
    noms = (cle, *ALIAS_CLES.get(cle, ()))
    for nom in noms:
        if os.environ.get(nom):
            return os.environ[nom]
    env = chemins.RACINE / ".env"
    if env.is_file():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*([A-Za-z0-9_]+)\s*[=:]\s*(.*)$", ligne)
            if m and m.group(1) in noms:
                valeur = m.group(2).strip().strip('"').strip("'")
                if valeur:
                    return valeur
    return None


def _requete(url: str, entetes: dict[str, str] | None = None) -> urllib.request.Request:
    return urllib.request.Request(url, headers={"User-Agent": AGENT_UTILISATEUR, **(entetes or {})})


def _get_json(url: str, entetes: dict[str, str] | None = None) -> Any:
    try:
        with urllib.request.urlopen(_requete(url, entetes), timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001 - message actionnable pour l'agent
        raise SourceErreur(f"échec de l'appel {url.split('?')[0]} : {e}") from e


def _telecharger(url: str, destination: Path, entetes: dict[str, str] | None = None) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(_requete(url, entetes), timeout=120) as r, destination.open("wb") as f:
            while bloc := r.read(1 << 16):
                f.write(bloc)
    except Exception as e:  # noqa: BLE001
        raise SourceErreur(f"échec du téléchargement de {url} : {e}") from e
    return destination


def _premier(d: dict, *cles: str, defaut: Any = None) -> Any:
    for c in cles:
        if c in d and d[c] not in (None, ""):
            return d[c]
    return defaut


# ----- Poly Haven -----------------------------------------------------------------------------
POLYHAVEN_API = "https://api.polyhaven.com"


def chercher_polyhaven(requete: str, type_asset: str = "models", limite: int = 10) -> list[Candidat]:
    donnees = _get_json(f"{POLYHAVEN_API}/assets?t={type_asset}")
    mots = [m for m in requete.lower().split() if m]
    resultats = []
    for ident, info in donnees.items():
        texte = " ".join([ident, info.get("name", ""), *info.get("tags", []), *info.get("categories", [])]).lower()
        score = sum(m in texte for m in mots)
        if score:
            auteurs = ", ".join(info.get("authors", {}).keys()) or "Poly Haven"
            resultats.append((score, info.get("download_count", 0), Candidat(
                source="polyhaven", id_source=ident, nom=info.get("name", ident), auteur=auteurs, licence="CC0",
                url_page=f"https://polyhaven.com/a/{ident}", apercu=info.get("thumbnail_url", ""),
                triangles=info.get("polycount"))))
    resultats.sort(key=lambda t: (-t[0], -t[1]))
    return [c for _, _, c in resultats[:limite]]


def fichiers_polyhaven_gltf(id_source: str, resolution: str = "1k") -> tuple[str, dict[str, str]]:
    """Renvoie (url du .gltf, {chemin relatif: url} des fichiers inclus)."""
    f = _get_json(f"{POLYHAVEN_API}/files/{urllib.parse.quote(id_source)}")
    gltf = f.get("gltf", {})
    res = resolution if resolution in gltf else (sorted(gltf)[0] if gltf else None)
    if res is None:
        raise SourceErreur(f"Poly Haven : pas de version glTF pour '{id_source}'")
    entree = gltf[res]["gltf"]
    inclus = {chemin: v["url"] for chemin, v in entree.get("include", {}).items()}
    return entree["url"], inclus


def telecharger_hdri_polyhaven(id_source: str, resolution: str = "2k") -> Path:
    f = _get_json(f"{POLYHAVEN_API}/files/{urllib.parse.quote(id_source)}")
    hdri = f.get("hdri", {})
    if resolution not in hdri:
        raise SourceErreur(f"Poly Haven : résolution {resolution} indisponible pour '{id_source}' ({sorted(hdri)})")
    url = hdri[resolution]["hdr"]["url"]
    return _telecharger(url, DOSSIER_HDRI / f"{id_source}_{resolution}.hdr")


def telecharger_texture_polyhaven(id_source: str, resolution: str = "1k") -> Path:
    """Textures PBR (couleur, normale, rugosité) d'un matériau Poly Haven dans
    engine/assets/textures/<id>/ ; renvoie le dossier (à indiquer dans le pack : materiaux.<role>.textures)."""
    f = _get_json(f"{POLYHAVEN_API}/files/{urllib.parse.quote(id_source)}")
    cartes = {"couleur": ("Diffuse", "diff"), "normale": ("nor_gl", "nor_gl"), "rugosite": ("Rough", "rough")}
    dossier = DOSSIER_TEXTURES / id_source
    obtenues = {}
    for nom, (cle, suffixe) in cartes.items():
        par_res = f.get(cle, {})
        if resolution not in par_res:
            continue
        fichier = par_res[resolution].get("jpg") or par_res[resolution].get("png")
        if fichier:
            obtenues[nom] = _telecharger(fichier["url"], dossier / f"{id_source}_{suffixe}_{resolution}.jpg").name
    if "couleur" not in obtenues:
        raise SourceErreur(f"Poly Haven : pas de texture de couleur {resolution} pour '{id_source}'")
    (dossier / "cartes.json").write_text(json.dumps(obtenues, ensure_ascii=False, indent=2), encoding="utf-8")
    return dossier


# ----- 3DTexel -------------------------------------------------------------------------------
TEXEL_API = "https://3dtexel.com/wp-json/3dtexel-api/v1"
TEXEL_TYPES_LIBRES = {"pbr", "hdri", "3d", "decal"}  # « handmade », CC0, gratuits


def chercher_3dtexel(requete: str, limite: int = 10, type_asset: str | None = None) -> list[Candidat]:
    q = {"q": requete, "per_page": 30}
    if type_asset:
        q["type"] = type_asset
    donnees = _get_json(f"{TEXEL_API}/assets/search?{urllib.parse.urlencode(q)}")
    sortie = []
    for r in donnees.get("items", []):
        gratuit = (r.get("price") or {}).get("free") is True
        lic = r.get("license") if isinstance(r.get("license"), str) else (r.get("license") or {}).get("name", "")
        if r.get("type") not in TEXEL_TYPES_LIBRES or r.get("source") != "handmade" or not gratuit or "CC0" not in lic:
            continue  # IA, premium ou payant : jamais proposé automatiquement
        sortie.append(Candidat(source="3dtexel", id_source=str(r["id"]), nom=r.get("title", ""), auteur="3DTexel",
                               licence="CC0", url_page=r.get("url", ""), apercu=r.get("thumbnail", ""),
                               a_verifier=[f"type 3DTexel : {r.get('type')}"]))
    return sortie[:limite]


def telecharger_3dtexel(id_source: str, destination: Path) -> list[Path]:
    """Télécharge les fichiers d'un asset 3DTexel gratuit (clé TEXEL_API_KEY nécessaire)."""
    cle = _env("TEXEL_API_KEY")
    if not cle:
        raise SourceErreur("TEXEL_API_KEY absente : crée un compte gratuit sur 3dtexel.com (clé « tx_live_… »), "
                           "puis ajoute-la dans .env")
    req = urllib.request.Request(f"{TEXEL_API}/assets/{urllib.parse.quote(id_source)}/download", method="POST",
                                 headers={"User-Agent": AGENT_UTILISATEUR, "Authorization": f"Bearer {cle}",
                                          "Idempotency-Key": f"serie-animation-{id_source}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            reponse = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        raise SourceErreur(f"3DTexel : échec de la demande de téléchargement : {e}") from e
    # La réponse liste les fichiers soit en tableau, soit en dictionnaire {carte: url | {url: …}}
    # (constaté le 2026-11-16 : dictionnaire par carte PBR pour les matériaux).
    fichiers = reponse.get("files") or reponse.get("downloads") or reponse.get("urls") or []
    entrees = list(fichiers.items()) if isinstance(fichiers, dict) else [(None, f) for f in fichiers]
    chemins_locaux, cartes = [], {}
    correspondance = {"basecolor": "couleur", "base_color": "couleur", "albedo": "couleur", "diffuse": "couleur",
                      "color": "couleur", "normal": "normale", "normal_gl": "normale", "roughness": "rugosite"}
    for carte, f in entrees:
        url = f if isinstance(f, str) else ((f or {}).get("url") or (f or {}).get("signed_url"))
        if not url or not urllib.parse.urlparse(url).scheme.startswith("http"):
            continue
        nom = Path(urllib.parse.urlparse(url).path).name or f"{id_source}.bin"
        if carte:
            nom = f"{id_source}_{carte}{Path(nom).suffix}"
        chemin = _telecharger(url, destination / nom)
        chemins_locaux.append(chemin)
        if carte and str(carte).lower() in correspondance:
            cartes[correspondance[str(carte).lower()]] = chemin.name
    if not chemins_locaux:
        apercu = {k: (type(v).__name__) for k, v in (fichiers.items() if isinstance(fichiers, dict) else [])}
        raise SourceErreur(f"3DTexel : réponse sans fichier exploitable (clés {list(reponse)[:6]}, fichiers {apercu})")
    if "couleur" in cartes:  # matériau PBR : utilisable directement comme dossier de textures d'un pack
        (destination / "cartes.json").write_text(json.dumps(cartes, ensure_ascii=False, indent=2), encoding="utf-8")
    return chemins_locaux


# ----- Poly Pizza -----------------------------------------------------------------------------
POLYPIZZA_API = "https://api.poly.pizza/v1"


def chercher_polypizza(requete: str, limite: int = 10) -> list[Candidat]:
    cle = _env("POLY_PIZZA_KEY")
    if not cle:
        raise SourceErreur("POLY_PIZZA_KEY absente : crée un compte gratuit sur poly.pizza et ajoute la clé dans .env")
    donnees = _get_json(f"{POLYPIZZA_API}/search/{urllib.parse.quote(requete)}?limit={limite}",
                        {"X-Auth-Token": cle})
    sortie = []
    for r in donnees.get("results", []):
        ident = str(_premier(r, "ID", "Id", "id", defaut=""))
        createur = _premier(r, "Creator", "creator", defaut={})
        sortie.append(Candidat(
            source="polypizza", id_source=ident, nom=_premier(r, "Title", "title", "Name", defaut=ident),
            auteur=createur.get("Username", "") if isinstance(createur, dict) else str(createur),
            licence=str(_premier(r, "Licence", "License", "licence", defaut="inconnue")),
            url_page=f"https://poly.pizza/m/{ident}", apercu=_premier(r, "Thumbnail", "thumbnail", defaut=""),
            triangles=_premier(r, "Tri Count", "TriCount", "triCount"), anime=bool(_premier(r, "Animated", defaut=False)),
            url_telechargement=_premier(r, "Download", "download", defaut=""),
            a_verifier=["noms de champs Poly Pizza à confirmer au premier appel"]))
    return sortie


# ----- Sketchfab ------------------------------------------------------------------------------
SKETCHFAB_API = "https://api.sketchfab.com/v3"


def chercher_sketchfab(requete: str, limite: int = 10) -> list[Candidat]:
    q = urllib.parse.urlencode({"type": "models", "q": requete, "downloadable": "true", "count": 24})
    donnees = _get_json(f"{SKETCHFAB_API}/search?{q}")
    sortie = []
    for r in donnees.get("results", []):
        lic = (r.get("license") or {}).get("slug") or (r.get("license") or {}).get("label", "inconnue")
        c = Candidat(source="sketchfab", id_source=r.get("uid", ""), nom=r.get("name", ""),
                     auteur=(r.get("user") or {}).get("displayName", ""), licence=str(lic),
                     url_page=r.get("viewerUrl", ""), triangles=r.get("faceCount"),
                     apercu=((r.get("thumbnails") or {}).get("images") or [{}])[0].get("url", ""))
        if c.licence_ok:  # NC, ND et licences inconnues écartées d'office
            sortie.append(c)
    return sortie[:limite]


def url_glb_sketchfab(uid: str) -> str:
    jeton = _env("SKETCHFAB_TOKEN")
    if not jeton:
        raise SourceErreur("SKETCHFAB_TOKEN absent : jeton d'API dans les réglages du compte Sketchfab, à mettre dans .env")
    d = _get_json(f"{SKETCHFAB_API}/models/{uid}/download", {"Authorization": f"Token {jeton}"})
    for fmt in ("glb", "gltf"):
        if fmt in d:
            return d[fmt]["url"]
    raise SourceErreur(f"Sketchfab : aucun format glTF téléchargeable pour {uid}")


# ----- recherche et intégration ---------------------------------------------------------------
# ----- 3DAssets.dev (CC0, GLB, sans clé) -------------------------------------------------------
TROIS_D_ASSETS_API = "https://3dassets.dev/api/v1"


def chercher_3dassets(requete: str, limite: int = 10) -> list[Candidat]:
    donnees = _get_json(f"{TROIS_D_ASSETS_API}/assets?{urllib.parse.urlencode({'q': requete})}")
    sortie = []
    for r in donnees.get("data", [])[:limite]:
        stats, lic = r.get("stats") or {}, r.get("license") or {}
        sortie.append(Candidat(
            source="3dassets", id_source=r["slug"], nom=r.get("title", r["slug"]),
            auteur=(r.get("contributor") or {}).get("name", "3DAssets.dev"), licence=lic.get("name", "inconnue"),
            url_page=r.get("url", ""), apercu=r.get("thumbnailUrl", ""), triangles=stats.get("triangles"),
            anime=bool(stats.get("animations")), url_telechargement=r.get("cdnUrl") or r.get("downloadUrl", "")))
    return sortie


# ----- Icosa Gallery (archive Google Poly, ~150 000 modèles CC-BY, sans clé) ----------------------
ICOSA_API = "https://api.icosa.gallery/v1"
_LICENCES_ICOSA = {"CREATIVE_COMMONS_BY": "CC-BY", "CREATIVE_COMMONS_0": "CC0", "CC0": "CC0"}


def _format_icosa(asset: dict) -> dict | None:
    """Meilleur format téléchargeable : GLB, puis glTF 2 hébergé par Icosa (pas l'archive web)."""
    formats = [f for f in asset.get("formats", []) if f.get("formatType") in ("GLB", "GLTF2")
               and "web.archive.org" not in f["root"]["url"]]
    formats.sort(key=lambda f: (f["formatType"] != "GLB", not f.get("isPreferredForDownload")))
    return formats[0] if formats else None


def chercher_icosa(requete: str, limite: int = 10) -> list[Candidat]:
    q = {"keywords": requete, "pageSize": max(limite * 2, 10), "curated": "true"}
    donnees = _get_json(f"{ICOSA_API}/assets?{urllib.parse.urlencode(q)}")
    sortie = []
    for r in donnees.get("assets", []):
        fmt = _format_icosa(r)
        if fmt is None:
            continue
        sortie.append(Candidat(
            source="icosa", id_source=r["assetId"], nom=r.get("displayName", r["assetId"]),
            auteur=r.get("authorName", ""), licence=_LICENCES_ICOSA.get(r.get("license", ""), r.get("license", "inconnue")),
            url_page=f"https://icosa.gallery/view/{r['assetId']}", apercu=(r.get("thumbnail") or {}).get("url", ""),
            triangles=r.get("triangleCount"), url_telechargement=fmt["root"]["url"]))
        if len(sortie) >= limite:
            break
    return sortie


def telecharger_icosa(id_source: str, dossier: Path) -> Path:
    asset = _get_json(f"{ICOSA_API}/assets/{urllib.parse.quote(id_source)}")
    fmt = _format_icosa(asset)
    if fmt is None:
        raise SourceErreur(f"Icosa : aucun format glTF 2 / GLB téléchargeable pour '{id_source}'")
    racine = fmt["root"]
    principal = _telecharger(racine["url"], dossier / (racine.get("relativePath")
                                                      or Path(urllib.parse.urlparse(racine["url"]).path).name))
    for res in fmt.get("resources", []):  # .bin et textures d'un .gltf (relativePath parfois absent)
        nom = res.get("relativePath") or Path(urllib.parse.urlparse(res["url"]).path).name
        _telecharger(res["url"], dossier / nom)
    return principal


# ----- ambientCG (textures, HDRI ; CC0, sans clé) ---------------------------------------------------
AMBIENTCG_API = "https://ambientcg.com/api/v3/assets"


def chercher_ambientcg(requete: str, limite: int = 10, type_asset: str = "material") -> list[Candidat]:
    q = {"q": requete, "type": type_asset, "limit": limite, "sort": "popular"}
    donnees = _get_json(f"{AMBIENTCG_API}?{urllib.parse.urlencode(q)}")
    return [Candidat(source="ambientcg", id_source=a["id"], nom=a.get("title") or a["id"], auteur="ambientCG (Lennart Demes)",
                     licence="CC0", url_page=f"https://ambientcg.com/view?id={a['id']}")
            for a in donnees.get("assets", [])]


def telecharger_texture_ambientcg(id_source: str, resolution: str = "1K-JPG") -> Path:
    """Textures PBR ambientCG dans engine/assets/textures/<id>/ (même format que Poly Haven : cartes.json)."""
    import io
    import zipfile
    donnees = _get_json(f"{AMBIENTCG_API}?{urllib.parse.urlencode({'id': id_source, 'include': 'downloads'})}")
    assets = donnees.get("assets", [])
    if not assets:
        raise SourceErreur(f"ambientCG : asset '{id_source}' introuvable")
    lien = next((d["url"] for d in assets[0].get("downloads", []) if d.get("attributes") == resolution), None)
    if lien is None:
        raise SourceErreur(f"ambientCG : pas de fichier {resolution} pour '{id_source}'")
    with urllib.request.urlopen(_requete(lien), timeout=120) as r:
        archive = zipfile.ZipFile(io.BytesIO(r.read()))
    dossier = DOSSIER_TEXTURES / id_source
    dossier.mkdir(parents=True, exist_ok=True)
    cartes, suffixes = {}, {"couleur": "_Color.", "normale": "_NormalGL.", "rugosite": "_Roughness."}
    for nom in archive.namelist():
        for carte, suffixe in suffixes.items():
            if suffixe in nom and "/" not in nom:  # pas de chemin dans l'archive : rien n'est écrit hors du dossier
                (dossier / nom).write_bytes(archive.read(nom))
                cartes[carte] = nom
    if "couleur" not in cartes:
        raise SourceErreur(f"ambientCG : pas de carte de couleur dans l'archive de '{id_source}'")
    (dossier / "cartes.json").write_text(json.dumps(cartes, ensure_ascii=False, indent=2), encoding="utf-8")
    return dossier


CHERCHEURS = {"polyhaven": chercher_polyhaven, "polypizza": chercher_polypizza, "sketchfab": chercher_sketchfab,
              "3dtexel": chercher_3dtexel, "3dassets": chercher_3dassets, "icosa": chercher_icosa,
              "ambientcg": chercher_ambientcg}


def chercher(requete: str, sources: list[str], limite: int = 5) -> dict[str, Any]:
    resultats, erreurs = [], {}
    for s in sources:
        try:
            resultats += [c for c in CHERCHEURS[s](requete, limite=limite) if c.licence_ok]
        except SourceErreur as e:
            erreurs[s] = str(e)
    return {"requete": requete, "candidats": [asdict(c) | {"attribution_requise": c.attribution_requise}
                                               for c in resultats], "erreurs": erreurs}


def _ecrire_registre(id_local: str, entree: dict[str, Any]) -> None:
    reg = json.loads(chemins.REGISTRE_ASSETS.read_text(encoding="utf-8"))
    if id_local in reg["assets"]:
        raise SourceErreur(f"l'id '{id_local}' existe déjà au registre : choisis-en un autre")
    reg["assets"][id_local] = entree
    chemins.REGISTRE_ASSETS.write_text(json.dumps(reg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ecrire_licence(c: Candidat, id_local: str) -> None:
    attribution = f'Modèle "{c.nom}" par {c.auteur} ({c.licence}), {c.url_page}' if c.attribution_requise else ""
    with chemins.LICENCES_ASSETS.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([id_local, c.source, c.auteur, c.licence, c.url_page, date.today().isoformat(),
                                "oui" if c.attribution_requise else "non", attribution])


def integrer(source: str, id_source: str, id_local: str, role_defaut: str = "accessoire",
             echelle: float = 1.0, candidat: Candidat | None = None, materiaux: str = "pack") -> dict[str, Any]:
    """Télécharge un asset choisi par un humain, puis l'inscrit au registre et au fichier des licences."""
    if source == "polyhaven":
        c = candidat
        if c is None:
            try:  # auteur réel pour le fichier des licences (le CC0 n'exige pas de crédit, mais on le garde)
                info = _get_json(f"{POLYHAVEN_API}/info/{urllib.parse.quote(id_source)}")
                auteur = ", ".join((info.get("authors") or {}).keys()) or "Poly Haven"
            except SourceErreur:
                auteur = "Poly Haven"
            c = Candidat("polyhaven", id_source, id_source, auteur, "CC0", f"https://polyhaven.com/a/{id_source}")
    elif source == "3dtexel":
        c = candidat or Candidat("3dtexel", id_source, id_source, "3DTexel", "CC0", f"https://3dtexel.com/?p={id_source}")
    elif source in ("sketchfab", "polypizza", "3dassets", "icosa"):
        if candidat is None:
            raise SourceErreur(f"{source} : passe par 'chercher' (licence et lien de téléchargement en dépendent)")
        c = candidat
    else:
        raise SourceErreur(f"source inconnue : {source}")
    if not c.licence_ok:  # vérifié AVANT tout téléchargement
        raise SourceErreur(f"licence refusée ({c.licence}) : seuls CC0 et CC-BY sont acceptés")
    reg = json.loads(chemins.REGISTRE_ASSETS.read_text(encoding="utf-8"))
    if id_local in reg["assets"]:
        raise SourceErreur(f"l'id '{id_local}' existe déjà au registre : choisis-en un autre")

    dossier = DOSSIER_MODELES / id_local
    if source == "polyhaven":
        url, inclus = fichiers_polyhaven_gltf(id_source)
        principal = _telecharger(url, dossier / Path(urllib.parse.urlparse(url).path).name)
        for chemin_rel, u in inclus.items():
            _telecharger(u, dossier / chemin_rel)
    elif source == "3dtexel":
        fichiers = telecharger_3dtexel(id_source, dossier)
        modeles = [f for f in fichiers if f.suffix.lower() in (".glb", ".gltf", ".fbx", ".blend")]
        if not modeles:
            raise SourceErreur(f"3DTexel : aucun modèle 3D dans les fichiers reçus ({[f.name for f in fichiers]})")
        principal = modeles[0]
    elif source == "sketchfab":
        principal = _telecharger(url_glb_sketchfab(id_source), dossier / f"{id_local}.glb")
    elif source == "icosa":
        principal = telecharger_icosa(id_source, dossier)
    else:
        if not c.url_telechargement:
            raise SourceErreur(f"{source} : pas de lien de téléchargement dans le candidat")
        principal = _telecharger(c.url_telechargement, dossier / f"{id_local}.glb")
    entree = {"fichier": principal.relative_to(chemins.RACINE).as_posix(), "echelle": echelle,
              "role_defaut": role_defaut, "roles": {}, "principal": None, "materiaux": materiaux, "source": c.url_page,
              "ajoute_le": date.today().isoformat(), "echelle_verifiee": False}
    _ecrire_registre(id_local, entree)
    _ecrire_licence(c, id_local)
    return {"id": id_local, "fichier": entree["fichier"], "licence": c.licence, "attribution_requise": c.attribution_requise}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="sources_assets", description="Recherche et intégration d'assets 3D libres.")
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("chercher")
    a.add_argument("requete")
    a.add_argument("--sources", default="polyhaven,polypizza,3dassets,icosa,sketchfab,3dtexel")
    a.add_argument("--limite", type=int, default=5)
    b = sp.add_parser("integrer", help="intègre un asset choisi par un humain")
    b.add_argument("source", choices=sorted(CHERCHEURS))
    b.add_argument("--candidat", type=Path, help="JSON d'un candidat issu de 'chercher' (obligatoire hors Poly Haven)")
    b.add_argument("id_source")
    b.add_argument("--id", required=True, dest="id_local")
    b.add_argument("--role-defaut", default="accessoire")
    b.add_argument("--echelle", type=float, default=1.0)
    b.add_argument("--materiaux", choices=["pack", "origine"], default="pack",
                   help="pack : style unifié de la DA ; origine : textures de l'asset")
    t = sp.add_parser("texture", help="textures PBR Poly Haven ou ambientCG (sol, murs, carrelage…)")
    t.add_argument("id_source")
    t.add_argument("--source", choices=["polyhaven", "ambientcg"], default="polyhaven")
    t.add_argument("--resolution", default="1k")
    h = sp.add_parser("hdri")
    h.add_argument("id_source")
    h.add_argument("--resolution", default="2k")
    args = p.parse_args(argv)
    try:
        if args.cmd == "chercher":
            sortie = chercher(args.requete, [s for s in args.sources.split(",") if s], args.limite)
            if not sortie["candidats"] and sortie["erreurs"]:
                print(json.dumps(sortie, ensure_ascii=False, indent=2))
                return 1  # aucune source n'a répondu : ce n'est pas « aucun résultat »
        elif args.cmd == "integrer":
            cand = None
            if args.candidat:
                d = json.loads(args.candidat.read_text(encoding="utf-8"))
                d.pop("attribution_requise", None)
                cand = Candidat(**d)
            sortie = integrer(args.source, args.id_source, args.id_local, args.role_defaut, args.echelle, cand, args.materiaux)
        elif args.cmd == "texture":
            if args.source == "ambientcg":
                dossier = telecharger_texture_ambientcg(args.id_source, args.resolution if "-" in args.resolution
                                                        else f"{args.resolution.upper()}-JPG")
            else:
                dossier = telecharger_texture_polyhaven(args.id_source, args.resolution)
            sortie = {"textures": dossier.relative_to(chemins.RACINE).as_posix()}
        else:
            sortie = {"hdri": str(telecharger_hdri_polyhaven(args.id_source, args.resolution).relative_to(chemins.RACINE))}
    except SourceErreur as e:
        print(json.dumps({"erreur": str(e)}, ensure_ascii=False))
        return 1
    print(json.dumps(sortie, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
