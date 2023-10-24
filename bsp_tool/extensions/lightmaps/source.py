import os

from . import base

from PIL import Image


def as_page(vbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<vbsp.filename>.lightmaps.png'"""
    # TODO: export either ".ldr.exr", ".hdr.ext" or both
    if not hasattr(vbsp, "LIGHTING"):
        if not hasattr(vbsp, "LIGHTING_HDR"):  # HDR only
            raise RuntimeError(f"{vbsp.filename} has no lighting data")
        else:
            lightmap_texels = vbsp.LIGHTING_HDR
    else:
        lightmap_texels = vbsp.LIGHTING
    lightmaps = list()
    for face in vbsp.FACES:
        if face.light_offset == -1 or face.styles == -1:
            continue  # face is not lightmapped
        # NOTE: If face.styles is >1, there are multiple lightmaps of the same size immediately after the first
        width, height = map(int, [s + 1 for s in face.lightmap.size])
        texels = bytes(lightmap_texels[face.light_offset:face.light_offset + (width * height * 4)])
        face_lightmap = Image.frombytes("RGBA", (width, height), texels, "raw")  # Alpha is HDR exponent
        lightmaps.append(face_lightmap)
    sorted_lightmaps = sorted(lightmaps, key=lambda i: (-i.size[0], -i.size[1]))
    page = base.pack(sorted_lightmaps)
    os.makedirs(image_dir, exist_ok=True)
    page.save(os.path.join(image_dir, f"{vbsp.filename}.lightmaps.{ext}"))
