from . import base

from PIL import Image


def extract(bsp) -> base.LightmapCollection:
    # TODO: variable dimensions, iirc CoD is 256x256
    lightmaps = base.LightmapCollection(bsp.filename)
    for i, lightmap_data in enumerate(bsp.LIGHTMAPS):
        lightmap = Image.frombytes("RGB", (128, 128), lightmap_data.as_bytes(), "raw")
        lightmaps[i] = lightmap
    return lightmaps
