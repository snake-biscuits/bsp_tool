import math
import struct

from . import common


def test_unpack(lump, into):
    """Unpack lump (bytesarray)
    into a list of size into (int) or type into (common.base / mapped_array)"""
    lump_size = len(lump)
    out = []
    if isinstance(into, int):
        chunk_length = into
        for i in range(lump_size // chunk_length):
            i *= chunk_length
            out.append(lump[i:i+chunk_length])
        # ^ if "lump_size" cannot be equally divided the tail is lost
    elif isinstance(into, (common.base, common.mapped_array)):
        out = struct.iter_unpack(into._format, lump)
    else:
        raise NotImplemented("into must be type <int> or subclass of <common.base> or <common.mapped_array>")
    return out


def denominators_of(x, start=8, step=4): # multiples of 4 only
    """For guessing lump struct sizes"""
    out = set()
    for i in range(start, math.ceil(math.sqrt(x)) + 1, step):
        if x % i == 0:
            out.add(i)
            out.add(x // i)
    if len(out) == 0:
        return f"found no denomimnators for {x}"
    else:
        return sorted(out)


def export_pointcloud(bsp, obj_file_name):
    """bsp.VERTICES --> .obj file"""
    with open(obj_file_name, "w") as obj_file:
        obj_file.write(f"# {bsp.filename}.bsp\n")
        obj_file.write("# extracted with bsp_tool\n")
        obj_file.write("\n".join(f"v {x} {y} {z}" for x, y, z in bsp.VERTICES))


def analyse(array, *indices):
    """Take a split lump and anylyse multiple instances side-by-side"""
    for index in indices:
        ints = array[index]
        raw = [i.to_bytes(4, "little", signed=True) for i in ints]
        print(f"::: INDEX = {index} :::")
        print(*[f"{i:08x}" for i in ints]) # hex
        print(*ints) # int
        print(*[f[0] for f in struct.iter_unpack("f", b"".join(raw))]) # float
        print("=" * 80)


def hex_breakdown(stream):
    """Imagine a hex editor"""
    int_stream = struct.unpack(f"{len(stream)}B", stream)
    print(" ".join(f"{i:02x}" for i in int_stream))

# poll multiple maps of same mod, combine sets of denoms of lump_X in each
# AND denoms of the size differences between those lumps across multiple maps

# assemble all this into dict {lump_type: possible_chunksizes}
# also .csv listing lump size by map and chunksizes
