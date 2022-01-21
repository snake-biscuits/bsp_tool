"""Run with 64-bit python! Respawn .bsp files are large!"""
import difflib
import itertools
import os
import re
from typing import Iterable

from .. import RespawnBsp
from ..branches.respawn import titanfall, titanfall2


shared_maps = [("mp_angel_city", "mp_angel_city"),
               ("mp_colony", "mp_colony02"),
               ("mp_relic", "mp_relic02"),
               ("mp_rise", "mp_rise"),
               ("mp_wargames", "mp_wargames")]
# ^ r1 map name, r2 map name


def diff_bsps(bsp1, bsp2, full=False):
    for lump1, lump2 in zip(bsp1.branch.LUMP, bsp2.branch.LUMP):
        lump1 = lump1.name
        lump2 = lump2.name
        bsp1_header = bsp1.headers[lump1]
        bsp2_header = bsp2.headers[lump2]

        print(f"{lump1}", end="  ")
        print("Y" if bsp1_header.offset == bsp2_header.offset else "N", end="")
        print("Y" if bsp1_header.length == bsp2_header.length else "N", end="")
        print("Y" if bsp1_header.version == bsp2_header.version else "N", end="")
        print("Y" if bsp1_header.fourCC == bsp2_header.fourCC else "N", end="  ")

        # TODO: compare compressed lumps to uncompressed
        try:
            lump_1_contents = bsp1.lump_as_bytes(lump1)
            lump_2_contents = bsp2.lump_as_bytes(lump2)
        except Exception as exc:
            print("????", exc)  # couldn't load a lump, unsure which
            # TODO: handle edge case where one bsp has the lump, and the other does not
            continue  # skip this lump

        lumps_match = (lump_1_contents == lump_2_contents)
        print("YES!" if lumps_match else "NOPE")
        if full:
            # diff lumps
            if not lumps_match:
                # TODO: measure the scale of the differences
                if lump1 in bsp1.branch.LUMP_CLASSES and lump2 in bsp2.branch.LUMP_CLASSES:
                    difflib.unified_diff([lc.__repr__() for lc in getattr(bsp1, lump1)],
                                         [lc.__repr__() for lc in getattr(bsp2, lump2)],
                                         f"{bsp1.filename}.{lump1}", f"{bsp1.filename}.{lump1}")
                elif lump1 == "ENTIITES":
                    diff_entities(bsp1, bsp2)
                elif lump1 == "PAKFILE":
                    diff_pakfiles(bsp1, bsp2)
                else:
                    diff = difflib.diff_bytes(difflib.context_diff,
                                              [*split(lump_1_contents, 32)], [*split(lump_2_contents, 32)],
                                              f"{bsp1.filename}.{lump1}".encode(), f"{bsp1.filename}.{lump1}".encode())
                    print(*diff, sep="\n")
                    pass
        else:
            print(bsp1_header)
            print(bsp2_header)


def diff_rbsps(rbsp1, rbsp2, external=True, full=False):
    """compare internal to external lumps with diff_rbsps(bsp, bsp.external, external=False)"""
    diff_bsps(rbsp1, rbsp2, full)
    for ent_file in ["ENTITIES_env", "ENTITIES_fx", "ENTITIES_script", "ENTITIES_snd", "ENTITIES_spawn"]:
        print(ent_file, end="  ")
        print("YES!" if getattr(rbsp1, ent_file) == getattr(rbsp1, ent_file) else "NOPE")
    if external:
        diff_bsps(rbsp1.external, rbsp2.external, full)
        # TODO: close each lump after reading to save memory & avoid the "Too many open files" OSError


def diff_entities(bsp1: RespawnBsp, bsp2: RespawnBsp):
    for i, e1, e2 in zip(itertools.count(), bsp1.ENTITIES, bsp2.ENTITIES):
        # TODO: rather than print statments, generate the text & use difflib on it
        if e1 != e2:
            print(f"Entity #{i}")
            print("  {")
            for k1, k2, v1, v2 in zip(e1.keys(), e2.keys(), e1.values(), e2.values()):
                if v1 != v2:
                    print(f'-     "{k1}" "{v1}"')
                    print(f'+     "{k2}" "{v2}"')
                else:
                    print(f'      "{k1}" "{v1}"')
            print("  }")


def diff_pakfiles(bsp1: RespawnBsp, bsp2: RespawnBsp):
    pak1_files = bsp1.PAKFILE.namelist()
    pak2_files = bsp2.PAKFILE.namelist()
    for filename in pak1_files:
        if filename not in pak2_files:
            print(f"- {filename}")
        else:
            print(f"  {filename}")
            # compare sizes with .PAKFILE.getinfo("filename").file_size
            # compare file hashes?
    for filename in pak2_files:
        if filename not in pak1_files:
            print(f"+ {filename}")


def dump_headers(maplist):  # just for r1 / r1o / r2  (Titanfall Games)
    for r1_filename, r2_filename in maplist:
        print(r1_filename.upper())

        r1o_map_exists = os.path.exists(f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp")
        # TODO: do close matches exist?

        r1_map = RespawnBsp(titanfall, f"E:/Mod/Titanfall/maps/{r1_filename}.bsp")
        if r1o_map_exists:
            r1o_map = RespawnBsp(titanfall, f"E:/Mod/TitanfallOnline/maps/{r1_filename}.bsp")
        r2_map = RespawnBsp(titanfall2, f"E:/Mod/Titanfall2/maps/{r2_filename}.bsp")

        for i in range(128):
            r1_lump = titanfall.LUMP(i)
            r2_lump = titanfall2.LUMP(i)

            r1_header = r1_map.headers[r1_lump.name]
            if r1o_map_exists:
                r1o_header = r1o_map.headers[r1_lump.name]
                r1o_header_length = r1o_header.length
            else:
                r1o_header_length = 0
            r2_header = r2_map.headers[r2_lump.name]
            if (r1_header.length, r1o_header_length, r2_header.length) == (0, 0, 0):
                continue  # skip empty lumps
            print(r1_lump.name, "/", r2_lump.name)
            print(f"{r1_lump.value:04X}  {r1_lump.name}")
            print(f"{'r1':<8}", r1_header)
            if r1o_map_exists:
                print(f"{'r1o':<8}", r1o_header)
            print(f"{'r2':<8}", r2_header)

        del r1_map, r2_map
        if r1o_map_exists:
            del r1o_map
        print("=" * 80)


def split(iterable: Iterable, chunk_size: int) -> Iterable:
    for i, _ in enumerate(iterable[::chunk_size]):
        yield iterable[i * chunk_size:(i + 1) * chunk_size]


def xxd(data: bytes, width: int = 32) -> str:
    """based on the linux hex editor"""
    # TODO: start index and length to read
    for i, _bytes in split(data, width):
        address = f"0x{i * width:08X}"
        hex = " ".join([f"{b:02X}" for b in _bytes])
        ascii = "".join([chr(b) if re.match(r"[a-zA-Z0-9/\\]", chr(b)) else "." for b in _bytes])
        yield f"{address}:  {hex}  {ascii}"


if __name__ == "__main__":
    # r1_relic = RespawnBsp(titanfall, "E:/Mod/Titanfall/maps/mp_relic.bsp")
    # r1o_relic = RespawnBsp(titanfall, "E:/Mod/TitanfallOnline/maps/mp_relic.bsp")
    # r2_relic = RespawnBsp(titanfall2, "E:/Mod/Titanfall2/maps/mp_relic02.bsp")
    # diff_respawn_bsps(r1_relic, r1o_relic)  # IDENTICAL!

    # r1_angel = RespawnBsp(titanfall, "E:/Mod/Titanfall/maps/mp_angel_city.bsp")
    # r1o_angel = RespawnBsp(titanfall, "E:/Mod/TitanfallOnline/maps/mp_angel_city.bsp")
    # r2_angel = RespawnBsp(titanfall2, "E:/Mod/Titanfall2/maps/mp_angel_city.bsp")
    # diff_respawn_bsps(r1_angel, r1o_angel)  # slight differences! interesting!

    dump_headers(shared_maps)
