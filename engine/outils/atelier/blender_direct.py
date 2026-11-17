"""Pilote le Blender ouvert de Guillaume en direct, via le pont de l'extension « MCP » de Blender Lab.

Dans Blender : extension MCP activée, panneau « Start MCP Bridge Server » (port 9876 par défaut).
Le pont exécute du Python dans Blender et renvoie la variable `result` (un dict) en JSON.

    python engine/outils/atelier/blender_direct.py -c "result = {'objets': len(bpy.data.objects)}"
    python engine/outils/atelier/blender_direct.py fichier.py
    python engine/outils/atelier/blender_direct.py --capture vue.png      # capture de la vue 3D

Le code envoyé agit sur la scène ouverte : sauvegarder son fichier avant une grosse opération.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path

HOTE, PORT = "localhost", 9876

CAPTURE = r'''
import bpy
chemin = {chemin!r}
fen = bpy.context.window_manager.windows[0]
zone = next((a for a in fen.screen.areas if a.type == "VIEW_3D"), None)
if zone is None:
    raise RuntimeError("aucune vue 3D ouverte")
with bpy.context.temp_override(window=fen, area=zone, region=next(r for r in zone.regions if r.type == "WINDOW")):
    bpy.ops.screen.screenshot_area(filepath=chemin)
result = {{"capture": chemin}}
'''


def executer(code: str, delai: float = 600.0) -> dict:
    with socket.create_connection((HOTE, PORT), timeout=delai) as s:
        s.sendall((json.dumps({"type": "execute", "code": code, "strict_json": False}) + "\0").encode("utf-8"))
        tampon = b""
        while not tampon.endswith(b"\0"):
            morceau = s.recv(65536)
            if not morceau:
                break
            tampon += morceau
    return json.loads(tampon.rstrip(b"\0").decode("utf-8"))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("fichier", nargs="?", type=Path)
    p.add_argument("-c", "--code")
    p.add_argument("--capture", type=Path, help="capture la vue 3D dans ce PNG")
    a = p.parse_args()
    if a.capture:
        code = CAPTURE.format(chemin=str(a.capture.resolve()))
    elif a.code:
        code = a.code
    elif a.fichier:
        code = a.fichier.read_text(encoding="utf-8")
    else:
        p.error("donner du code (-c), un fichier ou --capture")
    rep = executer(code)
    sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))
    return 0 if rep.get("status") == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
