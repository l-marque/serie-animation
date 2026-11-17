"""Crée kevin_foot.glb : copie de kevin_base.glb (Quaternius, CC0) avec une tenue de foot.

Seules les couleurs des matériaux changent (maillot rouge, bas blanc, chaussures noires, chaussettes
rouges) ; géométrie, squelette et animations sont gardés à l'identique.

    python engine/outils/kevin_tenue_foot.py
"""
import json
import struct
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SOURCE = RACINE / "engine/assets/modeles/kevin_base/kevin_base.glb"
SORTIE = RACINE / "engine/assets/modeles/kevin_foot/kevin_foot.glb"

COULEURS = {
    "LightBrown": [0.75, 0.05, 0.04, 1.0],  # maillot rouge vif
    "LightBlue": [0.85, 0.85, 0.85, 1.0],   # bas blanc
    "White": [0.02, 0.02, 0.02, 1.0],       # chaussures noires
    "Red_Dark": [0.75, 0.05, 0.04, 1.0],    # chaussettes rouges
}


def main() -> None:
    data = SOURCE.read_bytes()
    lg_json = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + lg_json])
    reste = data[20 + lg_json:]  # chunk binaire, inchangé
    for m in gltf["materials"]:
        if m["name"] in COULEURS:
            m.setdefault("pbrMetallicRoughness", {})["baseColorFactor"] = COULEURS[m["name"]]
    js = json.dumps(gltf, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    total = 12 + 8 + len(js) + len(reste)
    sortie = struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js + reste
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_bytes(sortie)
    print(f"écrit : {SORTIE}")


if __name__ == "__main__":
    main()
