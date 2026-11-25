#!/usr/bin/env python3
"""Genera las texturas de infinitym a partir de las de vanilla, cambiándoles el color.

Uso:  python3 tools/recolor.py /ruta/a/26.3.jar

Lee las texturas de netherita, diamante y hierro del .jar de tu Minecraft, las pinta con la
paleta cian-violeta de infinitym y las guarda en assets/infinitym/textures/. Los archivos del
juego no se copian ni se modifican: solo se usan en tu equipo para crear las nuevas.
"""
import io
import sys
import zipfile
from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "assets" / "infinitym" / "textures"

# De oscuro a claro.
PALETTE = [(38, 20, 92), (86, 52, 190), (60, 160, 255), (120, 235, 255), (225, 255, 255)]

SOURCES = {
    # destino: (textura vanilla, qué recolorear)
    "block/infinitym_ore": ("block/deepslate_diamond_ore", "gems"),
    "block/infinitym_block": ("block/diamond_block", "all"),
    "item/infinitym_ingot": ("item/netherite_ingot", "all"),
    "item/raw_infinitym": ("item/raw_iron", "all"),
    "item/infinitym_sword": ("item/netherite_sword", "head"),
    "item/infinitym_pickaxe": ("item/netherite_pickaxe", "head"),
    "item/infinitym_axe": ("item/netherite_axe", "head"),
    "item/infinitym_shovel": ("item/netherite_shovel", "head"),
    "item/infinitym_hoe": ("item/netherite_hoe", "head"),
    "item/infinitym_helmet": ("item/netherite_helmet", "all"),
    "item/infinitym_chestplate": ("item/netherite_chestplate", "all"),
    "item/infinitym_leggings": ("item/netherite_leggings", "all"),
    "item/infinitym_boots": ("item/netherite_boots", "all"),
    # armadura puesta (casco, peto y botas en una imagen; pantalones en otra)
    "entity/equipment/humanoid/infinitym": ("entity/equipment/humanoid/netherite", "all"),
    "entity/equipment/humanoid_leggings/infinitym": ("entity/equipment/humanoid_leggings/netherite", "all"),
}


def ramp(t):
    t = max(0.0, min(1.0, t)) * (len(PALETTE) - 1)
    i = min(int(t), len(PALETTE) - 2)
    f = t - i
    a, b = PALETTE[i], PALETTE[i + 1]
    return tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))


def lum(p):
    return (0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) / 255


def is_handle(p):  # palo marrón de las herramientas
    return p[0] - p[2] > 28 and p[0] >= p[1] >= p[2]


def is_gem(p):  # gema azulada del mineral de diamante
    return p[2] - p[0] > 25


def recolor(img, mode):
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    pick = {
        "all": lambda p: True,
        "head": lambda p: not is_handle(p),
        "gems": is_gem,
    }[mode]
    target = [(x, y) for y in range(h) for x in range(w) if px[x, y][3] > 0 and pick(px[x, y])]
    if not target:
        return img
    values = sorted(lum(px[x, y]) for x, y in target)
    lo, hi = values[int(len(values) * 0.03)], values[int(len(values) * 0.97)]
    span = max(hi - lo, 1e-3)
    for x, y in target:
        r, g, b, a = px[x, y]
        px[x, y] = ramp((lum((r, g, b)) - lo) / span) + (a,)
    return img


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    jar = zipfile.ZipFile(sys.argv[1])
    for dest, (src, mode) in SOURCES.items():
        name = f"assets/minecraft/textures/{src}.png"
        try:
            data = jar.read(name)
        except KeyError:
            print(f"  no encuentro {name} en el .jar; dejo la textura que ya había")
            continue
        out = OUT / f"{dest}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        recolor(Image.open(io.BytesIO(data)), mode).save(out)
        print(f"  {dest}.png  <-  {src}.png")
    print("Listo.")


if __name__ == "__main__":
    main()
