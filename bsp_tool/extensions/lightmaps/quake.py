import os

from . import base

from PIL import Image


def as_page(bsp, image_dir="./", lightmap_scale=16):
    """saves to <image_dir>/<bsp.filename>.lightmaps.png"""
    # TODO: export json for uv recalculation
    # TODO: catch entity keys for alternate lightmap scale(s)
    # -- "_world_units_per_luxel" in worldspawn / model ent
    # -- "_lightmap_scale" in worldspawn
    # see ericw-tools testmaps/q2_lightmap_custom_scale.map
    lightmaps = list()
    for i, face in enumerate(bsp.FACES):
        d = bsp.lightmap_of_face(i, lightmap_scale)
        if d["lighting_offset"] == -1:
            continue
        lightmap = Image.frombytes("L", (d["width"], d["height"]), bytes(d["lightmap_bytes"]), "raw")
        lightmaps.append(lightmap)
    tiled_lightmaps = base.pack(lightmaps, max_width=256)
    os.makedirs(image_dir, exist_ok=True)
    tiled_lightmaps.save(os.path.join(image_dir, f"{bsp.filename}.lightmaps.png"))
