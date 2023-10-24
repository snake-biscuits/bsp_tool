import fnmatch
import json
import os

from . import base

from PIL import Image


# NOTE: Unsure why internal LIGHTMAP_DATA_REAL_TIME_LIGHTS needs 9 bytes per texel (RTL_C)
# -- 2x RGBA32 @ header defined dimensions + 1x RGBA32 @ 1/4 dimensions (width/2, height/2) ???
def tiled_or_split(rbsp, image_dir="./", ext="png", split=False):
    """Saves to '<image_dir>/<rbsp.filename>.sky.lightmaps.png'"""
    # NOTE: pass rbsp.external to extract from .bsp_lumps
    sky_lightmaps = list()
    sky_start, sky_end = 0, 0
    rtl_lightmaps = list()
    rtl_start, rtl_end = 0, 0
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            # Sky A & B
            sky_end = sky_start + (header.width * header.height * 4)
            sky_bytes = bytes(rbsp.LIGHTMAP_DATA_SKY[sky_start:sky_end])
            sky_lightmap = Image.frombytes("RGBA", (header.width, header.height), sky_bytes, "raw")
            sky_lightmaps.append(sky_lightmap)
            sky_start = sky_end
            # RTL A & B
            rtl_end = rtl_start + (header.width * header.height * 4)
            rtl_bytes = bytes(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
            rtl_lightmap = Image.frombytes("RGBA", (header.width, header.height), rtl_bytes, "raw")
            rtl_lightmaps.append(rtl_lightmap)
            rtl_start = rtl_end
        if not hasattr(rbsp.headers["LIGHTMAP_DATA_REAL_TIME_LIGHTS"], "filename"):  # internal only (not .bsp_lump)
            # RTL C
            rtl_end = rtl_start + (header.width * header.height)
            rtl_bytes = bytes(rbsp.LIGHTMAP_DATA_REAL_TIME_LIGHTS[rtl_start:rtl_end])
            rtl_lightmap = Image.frombytes("RGBA", (header.width // 2, header.height // 2), rtl_bytes, "raw")
            rtl_lightmaps.append(rtl_lightmap)
            rtl_start = rtl_end
    os.makedirs(image_dir, exist_ok=True)
    if split:
        for i, image in enumerate(sky_lightmaps):
            i, t = i // 2, "AB"[i % 2]
            image.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{i}.{t}.{ext}"))
        c = 3 if not hasattr(rbsp.headers["LIGHTMAP_DATA_REAL_TIME_LIGHTS"], "filename") else 2
        for i, image in enumerate(rtl_lightmaps):
            i, t = i // c, "ABC"[i % c]
            image.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{i}.{t}.{ext}"))
    else:
        sky_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2  # Sky A | B
        sky_lightmap_page = base.pack(sky_lightmaps, max_width=sky_width)
        sky_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.sky.{ext}"))
        with open(os.path.join(image_dir, f"{rbsp.filename}.sky.json"), "w") as sky_json:
            json.dump([dict(zip(base.AllocatedSpace._fields, c)) for c in sky_lightmap_page.children], sky_json)
        rtl_width = max([h.width for h in rbsp.LIGHTMAP_HEADERS]) * 2  # RTL A | B
        if not hasattr(rbsp.headers["LIGHTMAP_DATA_REAL_TIME_LIGHTS"], "filename"):
            rtl_width += rtl_width // 2  # RTL A | B | C
        rtl_lightmap_page = base.pack(rtl_lightmaps, max_width=rtl_width)
        rtl_lightmap_page.save(os.path.join(image_dir, f"{rbsp.filename}.rtl.{ext}"))
        with open(os.path.join(image_dir, f"{rbsp.filename}.rtl.json"), "w") as rtl_json:
            json.dump([dict(zip(base.AllocatedSpace._fields, c)) for c in rtl_lightmap_page.children], rtl_json)


def write_back_to_file(rbsp, image_dir="./", ext="png"):
    # TODO: accept split lightmaps
    files = fnmatch.filter(os.listdir(image_dir), f"{rbsp.filename}*")
    # NOTE: only need .json if lightmaps aren't split
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

    # NOTE: easier w/ pre-split lightmaps
    print(f"Converting .{ext}(s) to bytes...")
    # crop out each lightmap and convert to bytes
    for header in rbsp.LIGHTMAP_HEADERS:
        for i in range(2):
            if write_rtl:  # RTL A & B
                rtl_bytes.append(rtl_png.crop(box_tuple(rtl_json[rtl_index])).tobytes())
                rtl_index += 1
            if write_sky:  # Sky A & B
                sky_bytes.append(sky_png.crop(box_tuple(sky_json[sky_index])).tobytes())
                sky_index += 1
        if write_rtl_c:  # RTL C
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
