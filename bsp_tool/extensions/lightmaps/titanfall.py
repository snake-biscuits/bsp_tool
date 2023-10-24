import os

from . import base

from PIL import Image


def tiled_or_split(rbsp, image_dir="./", ext="png", split=False):
    """Saves to '<image_dir>/<rbsp.filename>.sky/rtl.png'"""
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        # REAL_TIME_LIGHTS x1
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = bytes(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        rtl_start = rtl_end
        for i in range(2):
            # SKY x2
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
    os.makedirs(image_dir, exist_ok=True)
    if split:
        for i, image in enumerate(sky_lightmaps):
            i, t = i // 2, "AB"[i % 2]
            image.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{i}.{t}.{ext}"))
        for i, image in enumerate(rtl_lightmaps):
            image.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{i}.{ext}"))
    else:
        max_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2
        sky_lightmap_page = base.pack(sky_lightmaps, max_width=max_width)
        sky_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
        rtl_lightmap_page = base.pack(rtl_lightmaps, max_width=max_width)
        rtl_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
