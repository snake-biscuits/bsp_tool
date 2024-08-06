from . import base

from PIL import Image


# TODO: use FACES_HDR for HDR (face_lightmaps_hdr?)
# TODO: do ORIGINAL_FACES have different lightmaps?
def face_lightmaps(bsp) -> base.LightmapCollection:
    # NOTE: each face has a single texel (4 bytes) before light_offset; we ignore it
    lightmaps = base.LightmapCollection(bsp.filename)
    has_ldr = bool(bsp.headers["LIGHTING"].length > 0)
    has_hdr = bool(bsp.headers["LIGHTING_HDR"].length > 0)
    if not has_ldr and not has_hdr:
        raise RuntimeError(f"{bsp.filename} has no lighting data")
    for i, face in enumerate(bsp.FACES):
        if face.light_offset == -1 or face.styles == -1:
            continue  # face is not lightmapped
        # TODO: if face.styles > 1: collect multiple lightmaps
        width, height = map(int, [s + 1 for s in face.lightmap.size])
        start, length = face.light_offset, width * height * 4
        if has_ldr:
            texels = bytes(bsp.LIGHTING[start:start + length])
            lightmaps[("LDR", i)] = Image.frombytes("RGBA", (width, height), texels, "raw")
        if has_hdr:
            texels = bytes(bsp.LIGHTING_HDR[start:start + length])
            lightmaps[("HDR", i)] = Image.frombytes("RGBA", (width, height), texels, "raw")
    return lightmaps
