import os

from . import base

from PIL import Image


def tiled(d3dbsp, image_dir="./"):
    """saves to <image_dir>/<d3dbsp.filename>.lightmaps.png"""
    # NOTE: always 3 * (512 ** 2) * 4 bytes
    lightmaps = list()
    length = 512 * 512 * 4
    for start in range(0, len(d3dbsp.LIGHTMAPS), length):
        lightmap_data = d3dbsp.LIGHTMAPS[start:start + length]
        lightmap = Image.frombytes("RGBA", (512, 512), lightmap_data, "raw")
        lightmaps.append(lightmap)
    tiled_lightmaps = base.pack(lightmaps, max_width=512)
    os.makedirs(image_dir, exist_ok=True)
    tiled_lightmaps.save(os.path.join(image_dir, f"{d3dbsp.filename}.lightmaps.png"))
