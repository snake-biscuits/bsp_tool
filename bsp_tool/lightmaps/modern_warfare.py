from . import base
import sys
import os
import subprocess

try:
    from PIL import Image
except ImportError:
    python_exe = os.path.join(sys.prefix, "bin", "python.exe")


def extract(bsp) -> base.LightmapCollection:
    # NOTE: always 3 * (512 ** 2) * 4 bytes
    lightmaps = base.LightmapCollection(bsp.filename)
    length = 512 * 512 * 4
    for i, start in enumerate(range(0, len(bsp.LIGHTMAPS), length)):
        lightmap_data = bsp.LIGHTMAPS[start:start + length]
        lightmap = Image.frombytes("RGBA", (512, 512), lightmap_data, "raw")
        lightmaps[i] = lightmap
    return lightmaps
