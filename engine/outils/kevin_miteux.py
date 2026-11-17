"""Crée kevin_miteux.glb : Kevin version « qui fait un peu pitié », point de départ de son évolution.

Copie de kevin_base.glb (Quaternius, CC0) dont seules les couleurs changent : t-shirt jaune moutarde
délavé, short en jean passé, chaussettes grisâtres, vieilles baskets grises. Géométrie, squelette et
animations sont gardés à l'identique (frappe, course, salut…). La petite taille (enfant) est réglée
dans le registre (« hauteur »).

    python engine/outils/kevin_miteux.py
"""
import json
import struct
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SOURCE = RACINE / "engine/assets/modeles/kevin_base/kevin_base.glb"
SORTIE = RACINE / "engine/assets/modeles/kevin_miteux/kevin_miteux.glb"

COULEURS = {
    "LightBrown": [0.50, 0.40, 0.12, 1.0],  # t-shirt jaune moutarde délavé
    "LightBlue": [0.30, 0.36, 0.48, 1.0],   # short en jean passé
    "White": [0.22, 0.21, 0.19, 1.0],       # vieilles baskets grises
    "Red_Dark": [0.55, 0.54, 0.50, 1.0],    # chaussettes grisâtres
}


def main() -> None:
    data = SOURCE.read_bytes()
    lg_json = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + lg_json])
    reste = data[20 + lg_json:]  # chunk binaire, inchangé
    for m in gltf["materials"]:
        if m["name"] in COULEURS:
            pbr = m.setdefault("pbrMetallicRoughness", {})
            pbr["baseColorFactor"] = COULEURS[m["name"]]
            pbr["roughnessFactor"] = 1.0  # tissu usé, sans reflet
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + len(reste)
    sortie = struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js + reste
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_bytes(sortie)
    print(f"écrit : {SORTIE}")


if __name__ == "__main__":
    main()
