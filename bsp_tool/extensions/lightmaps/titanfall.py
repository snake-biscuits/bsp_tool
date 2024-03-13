from . import base

from PIL import Image


def extract(bsp) -> base.LightmapCollection:
    lightmaps = base.LightmapCollection(bsp.filename)
    sky_start, sky_end = 0, 0
    rtl_start, rtl_end = 0, 0
    for i, header in enumerate(bsp.LIGHTMAP_HEADERS):
        # REAL_TIME_LIGHTS x1
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = bytes(bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        lightmaps[("RTL", i)] = rtl_lightmap
        rtl_start = rtl_end
        for j in range(2):
            # SKY x2
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(bsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            lightmaps[("SKY", "AB"[j], i)] = sky_lightmap
            sky_start = sky_end
    return lightmaps
