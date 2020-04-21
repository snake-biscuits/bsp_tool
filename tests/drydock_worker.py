import math
import struct
import sys

sys.path.insert(0, "C:/Users/Jared/Documents/Github/bsp_tool/")
import bsp_tool


# spotting patterns in RAW_ lumps
def denominators_of(x, start=8, step=4): # multiples of 4 only
    out = set()
    for i in range(start, math.ceil(math.sqrt(x)) + 1, step):
        if x % i == 0:
            out.add(i)
            out.add(x // i)
    if len(out) == 0:
        return f"found no denomimnators for {x}"
    else:
        return sorted(out)

# titanfall_dir = "/media/jared/Sandisk/mp_drydock" # LINUX
titanfall_dir = "E:/Mod/Titanfall2/mp_drydock" # WINDOWS
# working_filename = f"{titanfall_dir}/maps/mp_drydock.bsp" # DRYDOCK
apex_legends_dir = "E:/Mod/ApexLegends/"
working_filename = f"{apex_legends_dir}/maps/mp_rr_canyonlands_64k_x_64k.bsp"
bsp = bsp_tool.bsp(working_filename, mod=bsp_tool.titanfall2, lump_files=True)

# export vertices to .obj file
with open("canyonlands.obj", "w") as obj_file:
    obj_file.write("# mp_rr_canyonlands_64k_x_64k.bsp\n")
    obj_file.write("# extracted with bsp_tool\n")
    obj_file.write("\n".join(f"v {x} {y} {z}" for x, y, z in bsp.VERTICES))

denominators = {}
for attrib in dir(bsp):
    if attrib.startswith("RAW_"):
        lump = getattr(bsp, attrib)
        lump_size = len(lump)
        lump_name = attrib[4:]
        lump_id = getattr(bsp_tool.titanfall2.LUMP, lump_name)
        hex_id = f"{lump_id.value:04x}"
        denoms = denominators_of(lump_size)
        denominators[lump_name] = denoms
##        print(hex_id, lump_name, denoms)


def split_lump(lump, split_length):
        _format = f"{split_length // 4}i"
        return list(struct.iter_unpack(_format, lump))

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
    int_stream = struct.unpack(f"{len(stream)}B", stream)
    print(" ".join(f"{i:02x}" for i in int_stream))
