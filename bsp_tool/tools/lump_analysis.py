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


def lump_size_csv(folder: str, csv_name: str):
    out_csv = open(f"{csv_name}.csv", "w")
    lump_sizes = collections.defaultdict(set)
    for bsp_filename in fnmatch.filter(os.listdir(folder), "*.bsp"):
        bsp = load_bsp(os.path.join(folder, bsp_filename))
        for lump in bsp.branch.LUMP:
            header = bsp.HEADERS[lump.name]
            if hasattr(header, "filesize"):
                lump_sizes[lump.name].add(header.filesize)
            elif hasattr(header, "length"):
                lump_sizes[lump.name].add(header.length)
        del bsp

    for lump_name, sizes in lump_sizes.items():
        if sizes == {0}:
            out_csv.write(f"{lump_name},unused" + "\n")
            continue  # lump is unused
        sizes = sorted(list(sizes))
        out_csv.write(f"{lump_name}," + ",".join(map(str, sizes)) + "\n")
    out_csv.write(",\n,\n")
    for lump_name, sizes in lump_sizes.items():
        if sizes == {0}:
            continue  # lump is unused
        out_csv.write(f"{lump_name}," + ",".join(map(str, potential_sizes(sizes))) + "\n")
        # NOTE: if potential sizes returns an empty set, try a different 'step' value
    out_csv.close()
