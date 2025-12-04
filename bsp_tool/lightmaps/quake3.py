from . import base
import sys
import os
import subprocess

try:
    from PIL import Image
except ImportError:
    python_exe = os.path.join(sys.prefix, "bin", "python.exe")


def extract(bsp) -> base.LightmapCollection:
    # TODO: variable dimensions, iirc CoD is 256x256
    lightmaps = base.LightmapCollection(bsp.filename)
    for i, lightmap_data in enumerate(bsp.LIGHTMAPS):
        lightmap = Image.frombytes("RGB", (128, 128), lightmap_data.as_bytes(), "raw")
        lightmaps[i] = lightmap
    return lightmaps
