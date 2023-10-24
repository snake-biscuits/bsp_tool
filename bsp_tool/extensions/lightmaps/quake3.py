import os

from . import base

from PIL import Image


# TODO: split (one image per lightmap page)


def tiled(ibsp, image_dir="./"):
    """saves to <image_dir>/<ibsp.filename>.lightmaps.png"""
    # TODO: variable dimensions, iirc CoD is 256x256
    lightmaps = list()
    for lightmap_data in ibsp.LIGHTMAPS:
        lightmap = Image.frombytes("RGB", (128, 128), lightmap_data.as_bytes(), "raw")
        lightmaps.append(lightmap)
    tiled_lightmaps = base.pack(lightmaps, max_width=128 * 5)
    os.makedirs(image_dir, exist_ok=True)
    tiled_lightmaps.save(os.path.join(image_dir, f"{ibsp.filename}.lightmaps.png"))
