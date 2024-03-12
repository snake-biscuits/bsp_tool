from typing import List

from PIL import Image


def face_lightmaps(bsp, lightmap_scale=16) -> List[Image]:
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
    return lightmaps
