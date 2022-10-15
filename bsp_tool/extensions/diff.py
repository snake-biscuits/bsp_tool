"""Run with 64-bit python! Respawn .bsp files are large!"""
import difflib
import itertools
import re
from typing import Dict, Iterable, List


r1_dir = "E:/Mod/Titanfall/maps"
r1o_dir = "E:/Mod/TitanfallOnline/maps"
r2_dir = "E:/Mod/Titanfall2/maps"

shared_maps = [("mp_angel_city", "mp_angel_city"),
               ("mp_colony", "mp_colony02"),
               ("mp_relic", "mp_relic02"),
               ("mp_rise", "mp_rise"),
               ("mp_wargames", "mp_wargames")]
# ^ r1 map name, r2 map name


def diff_bsps(bsp1, bsp2, full=False) -> str:
    """WARNING: full diffs can be incredibly large!"""
    out = []
    if bsp1.folder == bsp2.folder:
        out.append(f"Comparing {bsp1} -> {bsp2}...")
    else:
        out.append(f"Comparing {bsp1.folder}/{bsp1} -> {bsp2.folder}/{bsp2}...")
    # NOTE: comparing lumps by index, same number of lumps expected
    for lump1, lump2 in zip(bsp1.branch.LUMP, bsp2.branch.LUMP):
        lump1 = lump1.name
        lump2 = lump2.name
        # diff headers
        if lump1 not in bsp1.headers or lump2 not in bsp2.headers:
            continue  # lazy fix for rbsp externals
            # TODO: note absent headers (not just for respawn.ExternalLumpManager!)
        bsp1_header = bsp1.headers[lump1]
        bsp2_header = bsp2.headers[lump2]
        lump_name = lump1 if lump1 == lump2 else f"{lump1} -> {lump2}"
        # NOTE: fourCC (decompressed size) vs length is not calculated
        # -- in fact, no check to check opposing compressed state (one compressed, one uncompressed)
        # -- however, LZMA compressed lump contents are always decompressed before comparison
        header_diff = "".join(["Y" if bsp1_header.offset == bsp2_header.offset else "N",
                               "Y" if bsp1_header.length == bsp2_header.length else "N",
                               "Y" if bsp1_header.version == bsp2_header.version else "N",
                               "Y" if bsp1_header.fourCC == bsp2_header.fourCC else "N"])
        # diff lump contents
        try:
            lump_1_contents = bsp1.lump_as_bytes(lump1)
            lump_2_contents = bsp2.lump_as_bytes(lump2)
        except Exception as exc:
            out.append(f"{lump_name}  {header_diff} ???? {exc}")
            continue  # skip this lump
        lumps_match = bool(lump_1_contents == lump_2_contents)
        contents_diff = "YES!" if lumps_match else "NOPE"
        out.append(f"{lump_name}  {header_diff} {contents_diff}")
        # was a lump removed / added?
        if (len(lump_1_contents) == 0 or len(lump_2_contents) == 0) and not lumps_match:
            out.append(" ".join(["+" if hasattr(bsp1, lump1) else "-", f"{bsp1.filename}.{lump1}"]))
            out.append(" ".join(["+" if hasattr(bsp2, lump2) else "-", f"{bsp2.filename}.{lump2}"]))
        # detailed comparisons
        elif full:
            if not lumps_match:
                # TODO: measure the scale of the differences
                if lump1 in bsp1.branch.LUMP_CLASSES and lump2 in bsp2.branch.LUMP_CLASSES:
                    diff = difflib.unified_diff([lc.__repr__() for lc in getattr(bsp1, lump1)],
                                                [lc.__repr__() for lc in getattr(bsp2, lump2)],
                                                f"{bsp1.filename}.{lump1}",
                                                f"{bsp1.filename}.{lump1}")
                    out.extend(diff)
                # SPECIAL_LUMP_CLASSES
                elif all([ln == "ENTITIES" for ln in (lump1, lump2)]):
                    out.append(diff_entities(bsp1.ENTITIES, bsp2.ENTITIES))
                elif all([ln == "PAKFILE" for ln in (lump1, lump2)]):
                    # NOTE: this will fail on nexon.cso2 bsps, as their pakfiles are unmapped
                    out.append(diff_pakfiles(bsp1.PAKFILE, bsp2.PAKFILE))
                # TODO: GAME_LUMP diff model_names
                else:  # BASIC_LUMP_CLASSES / general raw bytes
                    # NOTE: xxd line numbers prevent accurately tracing insertions
                    diff = difflib.context_diff([*xxd(lump_1_contents, 32)],  # 32 bytes per line looks nice
                                                [*xxd(lump_2_contents, 32)],
                                                f"{bsp1.filename}.{lump1}",
                                                f"{bsp2.filename}.{lump2}")
                    # TODO: run xxd without creating line numbers
                    # -- then, generate line numbers from diff & update diff with these line numbers
                    out.extend(diff)
        else:
            out.extend([str(bsp1_header), str(bsp2_header)])
    return "\n".join(out)


def diff_rbsps(rbsp1, rbsp2, external=True, full=False) -> str:
    """compare internal to external lumps with diff_rbsps(bsp, bsp.external, external=False)"""
    out = ["*** .bsp files ***", diff_bsps(rbsp1, rbsp2, full)]
    # NOTE: could confirm ent_types against ENTITY_PARTITION lump
    # -- however respawn seems to always use every .ent, leaving the script file empty if unused
    # -- this makes ENTITY_PARTITION practically useless, as it never changes
    out.append("*** .ent files ***")
    for ent_type in ("env", "fx", "script", "snd", "spawn"):
        ent_lump = f"ENTITIES_{ent_type}"
        lump1 = getattr(rbsp1, ent_lump, list())
        lump2 = getattr(rbsp2, ent_lump, list())
        ents_match = "YES!" if lump1 == lump2 else "NOPE"
        out.append(f"{ent_lump}  {ents_match}")
        if full and ents_match == "NOPE":
            out.append(diff_entities(lump1, lump2))
    if external:
        out.append("*** .bsp_lump files ***")
        out.append(diff_bsps(rbsp1.external, rbsp2.external, full))
        # TODO: close each lump after reading to save memory & avoid the "Too many open files" OSError
    return "\n".join(out)


EntityLump = List[Dict[str, str]]
# ^ [{"key": "value"}]


def diff_entities(lump1: EntityLump, lump2: EntityLump) -> str:
    out = []
    for i, e1, e2 in zip(itertools.count(), lump1, lump2):
        if e1 != e2:
            out.extend([f"Entity #{i}", "  {"])
            # TODO: be a little dynamic to make sure keys align
            # -- otherwise many false negatives might appear in a relatively simple diff
            for k1, k2, v1, v2 in zip(e1.keys(), e2.keys(), e1.values(), e2.values()):
                if v1 != v2:
                    out.extend([f'-   "{k1}" "{v1}"'
                                '+   "{k2}" "{v2}"'])
                else:
                    out.append(f'    "{k1}" "{v1}"')
            out.append("  }")
    return "\n".join(out)


def diff_pakfiles(bsp1_pakfile, bsp2_pakfile) -> str:
    """Works on any ValveBsp based .bsp (excluding CSO2)"""
    out = []
    pak1_files = bsp1_pakfile.namelist()
    pak2_files = bsp2_pakfile.namelist()
    for filename in pak1_files:
        absent = filename not in pak2_files
        out.append(f"- {filename}" if absent else f"  {filename}")
        if not absent:
            file1 = bsp1_pakfile.read(filename)
            file2 = bsp2_pakfile.read(filename)
            if file1 == file2:
                continue
            out[-1] = f"~ {filename}"
            diff = difflib.context_diff([*xxd(file1, 32)],
                                        [*xxd(file2, 32)],
                                        f"bsp1_pakfile.{filename}",
                                        f"bsp2_pakfile.{filename}")
            out.extend(diff)
    out.extend([f"+ {f}" for f in pak2_files if f not in pak1_files])
    return "\n".join(out)


# binary diff helpers
def split(iterable: Iterable, chunk_size: int) -> Iterable:
    for i, _ in enumerate(iterable[::chunk_size]):
        yield iterable[i * chunk_size:(i + 1) * chunk_size]


def xxd(data: bytes, width: int = 32) -> str:
    """based on the linux hex editor"""
    # TODO: start index and length to read
    for i, _bytes in enumerate(split(data, width)):
        address = f"0x{i * width:08X}"
        hex_ = " ".join([f"{b:02X}" for b in _bytes])
        if len(hex_) < 3 * width:
            hex_ += " " * (3 * width - len(hex_))
        # TODO: expand allowed ascii chars regex to include more punctuation and compile as a global!
        ascii = "".join([chr(b) if re.match(r"[a-zA-Z0-9/\\]", chr(b)) else "." for b in _bytes])
        yield f"{address}:  {hex_}  {ascii}"


if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, r"C:\Users\Jared\Documents\GitHub\bsp_tool")
    import bsp_tool  # run from top-level

    for r1_map, r2_map in shared_maps:
        with open(f"{r1_map}.diff", "w") as log_file:
            print(f"Writing {r1_map}.diff ...")
            r1_bsp = bsp_tool.load_bsp(os.path.join(r1_dir, f"{r1_map}.bsp"))
            r2_bsp = bsp_tool.load_bsp(os.path.join(r2_dir, f"{r2_map}.bsp"))
            log_file.write(diff_rbsps(r1_bsp, r2_bsp))
