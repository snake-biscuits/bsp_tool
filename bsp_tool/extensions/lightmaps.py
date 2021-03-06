import collections
import math
import os
from typing import Dict, List

from PIL import Image  # requires: pip install Pillow


AllocatedSpace = collections.namedtuple("AllocatedSpace", ["x", "y", "width", "height"])
Row = collections.namedtuple("Row", ["top", "height", "free_width"])


class LightmapPage:
    """Packs smaller images into a larger one"""
    children: Dict[AllocatedSpace, Image.Image]
    colour_mode: str
    image: Image.Image
    rows: List[Row]

    def __init__(self, max_width=1024, max_height=math.inf, colour_mode="RGBA"):
        self.max_width, self.max_height = max_width, max_height
        self.colour_mode = colour_mode
        self.rows = [Row(0, max_height, max_width)]
        self.children = dict()  # create a new dict! must be clean!

    def __add__(self, image: Image.Image):  # mutates self
        """Works best if images are sorted beforehand"""
        width, height = image.size
        if width > self.max_width:
            raise RuntimeError(f"{image} is too wide for {self}")
        # try and fit image into a row
        i, allocated = 0, False
        while not allocated and i < len(self.rows):
            row = self.rows[i]
            if row.free_width == self.max_width:  # row is empty
                x, y = 0, row.top
                new_row_height = height
                sliced_row = Row(row.top + height, row.height - height, self.max_width)
                if sliced_row.height > 0:
                    self.rows.append(sliced_row)
                allocated = True
            elif row.free_width >= width and row.height <= height:  # will fit
                x, y = (self.max_width - row.free_width), row.top
                new_row_height = row.height
                allocated = True
            i += 1
        if not allocated:
            raise RuntimeError(f"No space left in {self}!")
        # update the row allocated to
        new_row = Row(row.top, new_row_height, row.free_width - width)
        self.rows[i - 1] = new_row
        if row.free_width == 0:
            self.rows.pop(i)
        self.children[AllocatedSpace(x, y, width, height)] = image
        return self

    @property
    def image(self):
        """Composite final image"""
        if len(self.children) == 0:
            return None  # empty
        width = max([x + w for x, y, w, h in self.children])
        height = max([y + h for x, y, w, h in self.children])
        page = Image.new(self.colour_mode, (width, height))
        for space, child in self.children.items():
            x, y, width, height = space
            page.paste(child, (x, y, x + width, y + height))
        return page


def save_ibsp(ibsp, folder="./"):  # saves to a file in folder
    """for IdTechBsp / D3DBsp only"""
    lightmap_images = list()
    for lightmap_bytes in ibsp.LIGHTMAPS:
        lightmap = Image.frombytes("RGB", (128, 128), lightmap_bytes, "raw")
        lightmap_images.append(lightmap)
    tiled_lightmaps = sum(lightmap_images, start=LightmapPage(max_width=128 * 5))
    os.makedirs(folder, exist_ok=True)
    tiled_lightmaps.image.save(os.path.join(folder, f"{ibsp.filename}.lightmaps.png"))


def save_vbsp(vbsp, folder="./"):
    """Saves to '<folder>/<vbsp.filename>.lightmaps.png'"""
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
        width, height = [s + 1 for s in face.lightmap.size]
        texels = lightmap_texels[face.light_offset:face.light_offset + (width * height * 4)]
        face_lightmap = Image.frombytes("RGBA", (width, height), texels, "raw")  # Alpha is HDR exponent
        # TODO: bleed each lightmap by an extra pixel in each dimension
        lightmaps.append(face_lightmap)
    sorted_lightmaps = sorted(lightmaps, key=lambda i: -(i.size[0] * i.size[1]))
    page = sum(sorted_lightmaps, start=LightmapPage())
    os.makedirs(folder, exist_ok=True)
    page.image.save(os.path.join(folder, f"{vbsp.filename}.lightmaps.png"))


def save_rbsp(rbsp, folder="./"):  # TITANFALL 2 ONLY!
    """Saves to '<folder>/<rbsp.filename>.sky.lightmaps.png'"""
    sky_lightmaps = list()
    realtime_lightmaps = list()
    first_pixel = 0
    last_pixel = 0
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(header.count * 2):
            last_pixel = first_pixel + (header.width * header.height * 4)
            sky_bytes = rbsp.LIGHTMAP_DATA_SKY[first_pixel:last_pixel]
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            realtime_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[first_pixel:last_pixel]
            realtime_lightmap = Image.frombytes("RGBA", (header.width, header.height), realtime_bytes, "raw")
            realtime_lightmaps.append(realtime_lightmap)
            first_pixel = last_pixel
    os.makedirs(folder, exist_ok=True)
    max_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2
    sky_lightmap_page = sum(sky_lightmaps, start=LightmapPage(max_width=max_width))
    sky_lightmap_page.image.save(os.path.join(folder, f"{rbsp.filename}.sky_lightmaps.png"))
    realtime_lightmap_page = sum(realtime_lightmaps, start=LightmapPage(max_width=max_width))
    realtime_lightmap_page.image.save(os.path.join(folder, f"{rbsp.filename}.realtime_lightmaps.png"))
