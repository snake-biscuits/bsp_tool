import collections
import fnmatch
import json
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
            raise RuntimeError(f"{image!r} is too wide for {self!r}!")
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
            elif row.free_width >= width and row.height >= height:  # will fit
                x, y = (self.max_width - row.free_width), row.top
                new_row_height = row.height
                allocated = True
            i += 1
        if not allocated:
            raise RuntimeError(f"No space left in {self!r}!")
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


# TODO: quake lightmaps & darkplaces lightmaps
def save_ibsp_q3(ibsp, image_dir="./"):  # saves to image_dir/<ibsp.filename>.lightmaps.png
    """for IdTechBsp / InfinityWardBsp only"""
    # TODO: detect dimensions; iirc this is quake3 specific
    lightmap_images = list()
    for lightmap_data in ibsp.LIGHTMAPS:
        lightmap = Image.frombytes("RGB", (128, 128), lightmap_data.as_bytes(), "raw")
        lightmap_images.append(lightmap)
    tiled_lightmaps = sum(lightmap_images, start=LightmapPage(max_width=128 * 5))
    os.makedirs(image_dir, exist_ok=True)
    tiled_lightmaps.image.save(os.path.join(image_dir, f"{ibsp.filename}.lightmaps.png"))


def save_vbsp(vbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<vbsp.filename>.lightmaps.png'"""
    if not hasattr(vbsp, "LIGHTING"):
        if not hasattr(vbsp, "LIGHTING_HDR"):  # HDR only
            raise RuntimeError(f"{vbsp.filename} has no lighting data")
        else:
            lightmap_texels = vbsp.LIGHTING_HDR
    else:
        lightmap_texels = vbsp.LIGHTING
    # TODO: extract both LDR & HDR if available, & name outputs to match
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
    os.makedirs(image_dir, exist_ok=True)
    # TODO: seperate .ldr.ext & .hdr.ext
    page.image.save(os.path.join(image_dir, f"{vbsp.filename}.lightmaps.{ext}"))


def save_rbsp_r1(rbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<rbsp.filename>.sky/rtl.png'"""
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        # REAL_TIME_LIGHTS x1
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        rtl_start = rtl_end
        for i in range(2):
            # SKY x2
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end]
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
    os.makedirs(image_dir, exist_ok=True)
    max_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2
    sky_lightmap_page = sum(sky_lightmaps, start=LightmapPage(max_width=max_width))
    sky_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
    rtl_lightmap_page = sum(rtl_lightmaps, start=LightmapPage(max_width=max_width))
    rtl_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))


# NOTE: Unsure why internal LIGHTMAP_DATA_REAL_TIME_LIGHTS needs 9 bytes per texel (RTL_C)
# -- 2x RGBA32 @ header defined dimensions + 1x RGBA32 @ 1/4 dimensions (width/2, height/2) ???
def save_rbsp_r2(rbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<rbsp.filename>.sky.lightmaps.png'"""
    # NOTE: pass rbsp.external to extract from .bsp_lumps
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            # SKY_A + SKY_B
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end]
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
            # RTL_A + RTL_B
            rtl_end = rtl_start + (header.width * header.height * 4)
            rtl_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
            rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
            rtl_lightmaps.append(rtl_lightmap)
            rtl_start = rtl_end
        if not hasattr(rbsp.headers["LIGHTMAP_DATA_REAL_TIME_LIGHTS"], "filename"):  # internal only (not .bsp_lump)
            # RTL_C
            rtl_end = rtl_start + (header.width * header.height)
            rtl_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
            rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
            rtl_lightmaps.append(rtl_lightmap)
            rtl_start = rtl_end
    os.makedirs(image_dir, exist_ok=True)
    sky_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2  # SKY_A | SKY_B
    sky_lightmap_page = sum(sky_lightmaps, start=LightmapPage(max_width=sky_width))
    sky_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.sky.json"), "w") as sky_json:
        json.dump([dict(zip(AllocatedSpace._fields, c)) for c in sky_lightmap_page.children], sky_json)
    rtl_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2  # RTL_A | RTL_B
    # TODO: add a little more width if RTL_C is present
    rtl_lightmap_page = sum(rtl_lightmaps, start=LightmapPage(max_width=rtl_width))
    rtl_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.rtl.json"), "w") as rtl_json:
        json.dump([dict(zip(AllocatedSpace._fields, c)) for c in rtl_lightmap_page.children], rtl_json)


def write_rbsp_r2(rbsp, image_dir="./", ext="png"):
    files = fnmatch.filter(os.listdir(image_dir), f"{rbsp.filename}*")
    write_rtl = bool(f"{rbsp.filename}.rtl.{ext}" in files and f"{rbsp.filename}.rtl.json" in files)
    write_rtl_c = False
    write_sky = bool(f"{rbsp.filename}.sky.{ext}" in files and f"{rbsp.filename}.sky.json" in files)
    if write_rtl:
        rtl_index = 0
        rtl_bytes = list()
        rtl_png = Image.open(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
        print("Loading Real Time Lights .json...")
        with open(os.path.join(image_dir, f"{rbsp.filename}.rtl.json")) as rtl_json_file:
            rtl_json = json.load(rtl_json_file)
            if len(rtl_json) != len(rbsp.LIGHTMAP_HEADERS) * 2:
                assert len(rtl_json) == len(rbsp.LIGHTMAP_HEADERS) * 3, ".rtl.json doesn't match .bsp"
                # NOTE: must write to internal lump
                write_rtl_c = True
    if write_sky:
        sky_index = 0
        sky_bytes = list()
        sky_png = Image.open(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
        print("Loading Sky .json...")
        with open(os.path.join(image_dir, f"{rbsp.filename}.sky.json")) as sky_json_file:
            sky_json = json.load(sky_json_file)
            assert len(sky_json) == len(rbsp.LIGHTMAP_HEADERS) * 2, ".sky.json doesn't match .bsp"
    if not (write_rtl or write_sky):
        raise RuntimeError(f"Couldn't find any .{ext}/.json data to write!")
    # TODO: all these steps:

    def box_tuple(_dict):
        return (_dict["x"], _dict["y"], _dict["x"] + _dict["width"], _dict["y"] + _dict["height"])

    print("Converting .png(s) to bytes...")
    # crop out each lightmap and convert to bytes
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            if write_rtl:  # RTL_A + RTL_B
                rtl_bytes.append(rtl_png.crop(box_tuple(rtl_json[rtl_index])).tobytes())
                rtl_index += 1
            if write_sky:  # SKY_A + SKY_B
                sky_bytes.append(sky_png.crop(box_tuple(sky_json[sky_index])).tobytes())
                sky_index += 1
        if write_rtl_c:  # RTL_C
            rtl_bytes.append(rtl_png.crop(box_tuple(rtl_json[rtl_index])).tobytes())
            rtl_index += 1
    print("Making backups...")
    # NOTE: will override older backups
    # TODO: another function to revert the backups
    if write_rtl_c:
        with open(os.path.join(rbsp.folder, f"{rbsp.filename}.rtl.bak"), "wb") as rtl_backup:
            rtl_backup.write(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[::])
    # NOTE: rbsp.save_as duplicates every .bsp_lump
    # -- there should be an option to disable that, other than "one_file"
    # -- since we don't want to override the internal RTL, as that would cause the map to crash (9 bytes per texel)
    rbsp.save_as(os.path.join(rbsp.folder, f"{rbsp.filename}.bak"))
    # TODO: don't save every .bsp_lump as a part of the backup, only the changed lumps
    print("Writing to .bsp & .bsp_lump(s)...")
    if write_rtl:
        rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[::] = b"".join(rtl_bytes)
    if write_sky:
        rbsp.LIGHTMAP_DATA_SKY[::] = b"".join(sky_bytes)
    rbsp.save()
    print("Done!")


# Apex Legends lightmaps
# TODO: figure out which seasons do which lightmaps
# TODO: auto-detect bytes-per-texel in save_rbsp_r2 instead
def save_rbsp_r5(rbsp, image_dir="./", ext="png"):
    """Saves to '<image_dir>/<rbsp.filename>.sky.lightmaps.png'"""
    # NOTE: pass rbsp.external to extract from .bsp_lumps
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            # SKY_A + SKY_B (2x 32bpp)
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end]
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
        # RTL_A
        rtl_end = rtl_start + (header.width * header.height * 4)
        rtl_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
        rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        # RTL_B
        rtl_end = rtl_end + (header.width * header.height * 2)
        rtl_bytes = rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end]
        rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
        rtl_lightmaps.append(rtl_lightmap)
        rtl_start = rtl_end
    os.makedirs(image_dir, exist_ok=True)
    max_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS])
    sky_width = max_width * 2
    sky_lightmap_page = sum(sky_lightmaps, start=LightmapPage(max_width=sky_width))
    sky_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.sky.json"), "w") as sky_json:
        json.dump([dict(zip(AllocatedSpace._fields, c)) for c in sky_lightmap_page.children], sky_json)
    rtl_width = max_width + max_width // 2
    rtl_lightmap_page = sum(rtl_lightmaps, start=LightmapPage(max_width=rtl_width))
    rtl_lightmap_page.image.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
    with open(os.path.join(image_dir, f"{rbsp.filename}.rtl.json"), "w") as rtl_json:
        json.dump([dict(zip(AllocatedSpace._fields, c)) for c in rtl_lightmap_page.children], rtl_json)
