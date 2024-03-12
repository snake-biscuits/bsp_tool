from . import base

from PIL import Image


# TODO: if face.styles > 1: collect multiple lightmaps
def face_lightmaps(bsp):
    """alpha channel is exponent"""
    has_ldr = bool(bsp.headers["LIGHTING"].length > 0)
    has_hdr = bool(bsp.headers["LIGHTING_HDR"].length > 0)
    if not has_ldr and not has_hdr:
        raise RuntimeError(f"{bsp.filename} has no lighting data")
    # unpacking
    lightmaps = base.LightmapCollection(bsp.filename)
    pad_length = len(f"{len(bsp.FACES) - 1}")
    for i, face in enumerate(bsp.FACES):
        if face.light_offset == -1 or face.styles == -1:
            continue  # face is not lightmapped
        width, height = map(int, [s + 1 for s in face.lightmap.size])
        start, length = face.light_offset, width * height * 4
        if has_ldr:
            texels = bytes(bsp.LIGHTING[start:length])
            lightmaps[f"LDR.{i:0{pad_length}d}"] = Image.frombytes("RGBA", (width, height), texels, "raw")
        if has_hdr:
            texels = bytes(bsp.LIGHTING_HDR[start:length])
            lightmaps[f"LDR.{i:0{pad_length}d}"] = Image.frombytes("RGBA", (width, height), texels, "raw")
    return lightmaps
