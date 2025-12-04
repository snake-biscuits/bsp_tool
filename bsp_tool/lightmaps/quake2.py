from . import base
import sys
import os
import subprocess

try:
    from PIL import Image
except ImportError:
    python_exe = os.path.join(sys.prefix, "bin", "python.exe")


def face_lightmaps(bsp, lightmap_scale=16) -> base.LightmapCollection:
    # TODO: export json for uv recalculation
    # TODO: catch entity keys for alternate lightmap scale(s)
    # -- "_world_units_per_luxel" in worldspawn / model ent
    # -- "_lightmap_scale" in worldspawn
    # see ericw-tools testmaps/q2_lightmap_custom_scale.map
    lightmaps = base.LightmapCollection(bsp.filename)
    for i, face in enumerate(bsp.FACES):
        d = bsp.lightmap_of_face(i, lightmap_scale)
        if d["lighting_offset"] == -1:
            continue
        # TODO: update quake.lightmap_of_face to grab 3x as many bytes (Quake is grayscale, Quake2 is RGB)
        lightmap = Image.frombytes("RGB", (d["width"], d["height"]), bytes(d["lightmap_bytes"]), "raw")
        lightmaps[i] = lightmap
    return lightmaps
