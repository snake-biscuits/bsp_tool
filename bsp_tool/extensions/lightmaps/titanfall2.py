from . import base

from PIL import Image


# NOTE: Unsure why internal LIGHTMAP_DATA_REAL_TIME_LIGHTS needs 9 bytes per texel (RTL_C)
# -- 2x RGBA32 @ header defined dimensions + 1x RGBA32 @ 1/4 dimensions (width/2, height/2) ???
def extract(bsp) -> base.LightmapCollection:
    lightmaps = base.LightmapCollection(bsp.filename)
    sky_start, sky_end = 0, 0
    rtl_start, rtl_end = 0, 0
    for i, header in enumerate(bsp.LIGHTMAP_HEADERS):
        for j in range(2):
            # SKY A & B
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(bsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            lightmaps[("SKY", "AB"[j], i)] = sky_lightmap
            sky_start = sky_end
            # RTL A & B
            rtl_end = rtl_start + (header.width * header.height * 4)
            rtl_bytes = bytes(bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
            rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
            lightmaps[("RTL", "AB"[j], i)] = rtl_lightmap
            rtl_start = rtl_end
        if not hasattr(bsp.headers["LIGHTMAP_DATA_REAL_TIME_LIGHTS"], "filename"):  # internal only (not .bsp_lump)
            # RTL C
            rtl_end = rtl_start + (header.width * header.height)
            rtl_bytes = bytes(bsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
            rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
            lightmaps[("RTL", "C", i)] = rtl_lightmap
            rtl_start = rtl_end
    return lightmaps
