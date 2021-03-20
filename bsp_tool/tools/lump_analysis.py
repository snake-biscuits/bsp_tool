import collections
import itertools
import fnmatch
import math
import os
import struct
from typing import Any, List

from .. import load_bsp
from ..branches import base


def test_unpack(lump, into) -> List[Any]:
    """Unpack lump (bytesarray)
    into a list of size 'into' (if an int) or type into (base.Struct / MappedArray)"""
    lump_size = len(lump)
    out = []
    if isinstance(into, int):
        chunk_length = into
        for i in range(lump_size // chunk_length):
            i *= chunk_length
            out.append(lump[i:i+chunk_length])
        # ^ if "lump_size" cannot be equally divided the tail is lost
    elif isinstance(into, (base.Struct, base.MappedArray)):
        out = struct.iter_unpack(into._format, lump)  # just the tuple, not the class
    else:
        raise NotImplementedError("into must be type <int> or subclass of <base.Struct> or <base.MappedArray>")
    return out


def denominators_of(x: int, start=8, step=4) -> List[int]:
    """For guessing lump struct sizes"""
    out = set()
    for i in range(start, math.ceil(math.sqrt(x)) + 1, step):
        if x % i == 0:
            out.add(i)
            out.add(x // i)
    if len(out) == 0:
        return f"found no denominators for {x}"
    else:
        return sorted(out)


def potential_sizes(lump_sizes, start=8, step=4) -> List[int]:
    lump_sizes = set(lump_sizes)
    for a, b in itertools.combinations(lump_sizes, 2):
        lump_sizes.add(abs(a - b))
    lump_sizes.discard(0)
    if len(lump_sizes) == 0:
        return [0]
    lump_sizes = list(lump_sizes)
    first_denoms = denominators_of(lump_sizes[0], start, step)
    if isinstance(first_denoms, str):
        return ["unknown"]
    common_denominators = set(first_denoms)
    for size in lump_sizes[1:]:
        denoms = denominators_of(size, start, step)
        common_denominators = common_denominators.intersection(denoms)
    return sorted(list(common_denominators))


def export_pointcloud(bsp, obj_filename: str):
    """bsp.VERTICES --> .obj file"""
    with open(obj_filename, "w") as obj_file:
        obj_file.write(f"# {bsp.filename}.bsp\n")
        obj_file.write("# extracted with bsp_tool\n")
        obj_file.write("\n".join(f"v {x} {y} {z}" for x, y, z in bsp.VERTICES))


def analyse(array, *indices):
    """Take a split lump and anylyse multiple instances side-by-side"""
    for index in indices:
        ints = array[index]
        raw = [i.to_bytes(4, "little", signed=True) for i in ints]
        print(f"::: INDEX = {index} :::")
        print(*[f"{i:08x}" for i in ints])  # hex
        print(*ints)  # int
        print(*[f[0] for f in struct.iter_unpack("f", b"".join(raw))])  # float
        print("=" * 80)


def sizes_csv(folder: str, csv_name: str):
    out_csv = open(csv_name, "w")
    map_folder = list(fnmatch.filter(os.listdir(folder), "*.bsp"))
    out_csv.write("LUMP," + ",".join(map_folder) + "\n")
    lump_sizes = collections.defaultdict(list)
    for bsp_filename in map_folder:
        bsp = load_bsp(os.path.join(folder, bsp_filename))
        for lump in bsp.branch.LUMP:
            header = bsp.HEADERS[lump.name]
            if hasattr(header, "filesize"):
                lump_sizes[lump.name].append(header.filesize)
            elif hasattr(header, "length"):
                lump_sizes[lump.name].append(header.length)
        del bsp

    for lump_name, sizes in lump_sizes.items():
        if set(sizes) == {0}:
            continue  # lump is unused
        out_csv.write(f"{lump_name}," + ",".join(map(str, sizes)) + "\n")

    out_csv.write(",\nLUMP,POTENTIAL SIZES\n")
    for lump_name, sizes in lump_sizes.items():
        if sizes == {0}:
            continue  # lump is unused
        could_bes = tuple(map(str, potential_sizes(sizes, start=2, step=2)))
        if len(could_bes) == 0 or could_bes in ((0,), ("unknown",)):
            continue
        out_csv.write(f"{lump_name}," + ",".join(could_bes) + "\n")
    out_csv.close()


def headers_markdown(folder: str, md_name: str):
    out_md = open(md_name, "w")
    map_folder = list(fnmatch.filter(os.listdir(folder), "*.bsp"))
    for bsp_filename in map_folder:
        bsp = load_bsp(os.path.join(folder, bsp_filename))
        map_name = os.path.splitext(bsp_filename)[0].split("_")
        if map_name[0] == "mp":
            map_name = " ".join(map_name[1:])
        else:
            map_name = " ".join(map_name)
        out_md.write(f"### {map_name.upper()}" + "\n")
        out_md.write("<details>\n  <summary>Click to expand</summary>\n\n")
        out_md.write("| Lump | External | Offset | Size | Version | FourCC |\n")
        out_md.write("| :--- | :------- | :----- | :--- | :------ | :----- |\n")
        for lump in bsp.branch.LUMP:
            header = bsp.HEADERS[lump.name]
            external = hasattr(header, "filename")
            size = header.filesize if external else header.length
            offset, version, fourCC = header.offset, header.version, header.fourCC
            if (offset, size, version, fourCC) == (0, 0, 0, 0):
                continue  # skip empty lumps
            out_md.write(f"{lump.name} | {':heavy_check_mark:' if external else ':x:'} | " +
                         f"{offset} | {size} | {version} | {fourCC} |" + "\n")
        out_md.write("</details>\n\n")
        del bsp
    out_md.close()
