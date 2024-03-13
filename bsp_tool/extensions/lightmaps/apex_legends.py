from . import base

from PIL import Image


# TODO: different seasons use different lightmap formats
# -- which seasons does this work for then?
# TODO: calculate bytes-per-texel
def extract(bsp) -> base.LightmapCollection:
    lightmaps = base.LightmapCollection(bsp.filename)
    sky_start, sky_end = 0, 0
    rtl_start, rtl_end = 0, 0
    for i, header in enumerate(bsp.LIGHTMAP_HEADERS):
        for j in range(2):
            # Sky A & B (2x 32bpp)
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(bsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            lightmaps[("SKY", "AB"[j], i)] = sky_lightmap
            sky_start = sky_end
        # RTL A
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = bytes(bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        lightmaps[("RTL", "A", i)] = rtl_lightmap
        # RTL B
        rtl_end = rtl_end + (header.width * header.height * 2)
        rtl_bytes = bytes(bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
        rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
        lightmaps[("RTL", "B", i)] = rtl_lightmap
        rtl_start = rtl_end
    return lightmaps
