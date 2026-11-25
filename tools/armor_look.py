#!/usr/bin/env python3
"""Hace que la armadura de infinitym se vea con textura propia al llevarla puesta.

Uso (desde la carpeta del mod):  python3 tools/armor_look.py

1. Crea assets/infinitym/equipment/infinitym.json (el "aspecto" de la armadura).
2. Cambia las 4 recetas de armadura para que el resultado salga con
   equippable.asset_id = infinitym:infinitym.
Después hay que correr tools/recolor.py para generar las texturas.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLOTS = {"helmet": "head", "chestplate": "chest", "leggings": "legs", "boots": "feet"}

equipment = {
    "layers": {
        "humanoid": [{"texture": "infinitym:infinitym"}],
        "humanoid_leggings": [{"texture": "infinitym:infinitym"}],
    }
}
out = ROOT / "assets/infinitym/equipment/infinitym.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(equipment, indent=2) + "\n")
print("creado", out.relative_to(ROOT))

for part, slot in SLOTS.items():
    f = ROOT / f"data/infinitym/recipe/infinitym_{part}.json"
    recipe = json.loads(f.read_text())
    recipe["result"]["components"] = {
        "minecraft:equippable": {
            "slot": slot,
            "asset_id": "infinitym:infinitym",
            "equip_sound": "minecraft:item.armor.equip_netherite",
        }
    }
    f.write_text(json.dumps(recipe, indent=2) + "\n")
    print("receta actualizada:", f.relative_to(ROOT))
