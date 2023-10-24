import json
import os

from . import base

from PIL import Image


# TODO: different seasons use different lightmap formats
# TODO: auto-detect bytes-per-texel in save_rbsp_r2 instead
def tiled(rbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<rbsp.filename>.sky.lightmaps.png'"""
    # NOTE: pass rbsp.external to extract from .bsp_lumps (essential for season 11 onwards)
    # TODO: LIGHTMAP_DATA_UNKNOWN if present
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            # Sky A & B (2x 32bpp)
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
        # RTL A
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = bytes(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        # RTL B
        rtl_end = rtl_end + (header.width * header.height * 2)
        rtl_bytes = bytes(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        rtl_start = rtl_end
    os.makedirs(image_dir, exist_ok=True)
    max_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS])
    sky_width = max_width * 2
    sky_lightmap_page = base.pack(sky_lightmaps, max_width=sky_width)
    sky_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.sky.json"), "w") as sky_json:
        json.dump([dict(zip(base.AllocatedSpace._fields, c)) for c in sky_lightmap_page.children], sky_json)
    rtl_width = max_width + max_width // 2
    rtl_lightmap_page = base.pack(rtl_lightmaps, max_width=rtl_width)
    rtl_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.rtl.json"), "w") as rtl_json:
        json.dump([dict(zip(base.AllocatedSpace._fields, c)) for c in rtl_lightmap_page.children], rtl_json)
