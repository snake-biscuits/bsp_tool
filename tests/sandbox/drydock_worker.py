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

# a handy function for guessing lump sizes:
#   def ...(lump, format):
#   take bsp.lump[:struct.calcsize(format) * 3]
#   struct.iter_unpack(format, _)
#   print side-by-side to look for patterns

if __name__ == "__main__":
##    mod = bsp_tool.titanfall2
##    folder = "/media/jared/Sandisk/" # LINUX
##    folder = "E:/Mod/Titanfall2/" # WINDOWS
##    mapname = "mp_drydock"
##    filename = f"{mapname}/maps/{mapname}.bsp"

    mod = bsp_tool.apex_legends
    folder = "E:/Mod/ApexLegends/maps/"
##    filename = "mp_rr_canyonlands_mu1_night.bsp"
##    bsp = bsp_tool.bsp(folder + filename, mod, lump_files=True)
    
    filenames = ["mp_rr_canyonlands_64k_x_64k.bsp",
                 "mp_rr_canyonlands_mu1.bsp",
                 "mp_rr_canyonlands_mu1_night.bsp",
                 "mp_rr_canyonlands_mu2.bsp",
                 "mp_rr_canyonlands_staging.bsp",
                 "mp_rr_desertlands_64k_x_64k.bsp",
                 "mp_rr_desertlands_mu1.bsp"]
    
    denominators = {}
    for filename in filenames:
        bsp = bsp_tool.bsp(folder + filename, mod, lump_files=True)
        denominators[filename] = {}
        for attrib in dir(bsp):
            if attrib.startswith("RAW_"):
                lump = getattr(bsp, attrib)
                lump_size = len(lump)
                lump_name = attrib[4:]
                lump_id = getattr(bsp_tool.apex_legends.LUMP, lump_name)
                hex_id = f"{lump_id.value:04x}"
                denoms = denominators_of(lump_size, start=4, step=4)
                denominators[filename][lump_name] = denoms
    common_denominators = {L: set(ds) for L, ds in denominators[filenames[0]].items()}
    for denom_dict in denominators.values():
        for lump, ds in denom_dict.items():
            common_denominators[lump] = common_denominators[lump].union(set(ds))
    # also get the denominators of the differences in lump size
    # VERTS_BLINN_PHONG, VERTS_LIT_FLAT, TEXDATA
    # position_index, normal_index, ...
    # normal index will likely repeat 3-4 times in a row

    # .obj conversion
##    mesh_verts = lambda i: bsp_tool.titanfall2.tris_of(bsp, i)
##    mesh_types = {0x600: "UNLIT_TS", 0x400: "UNLIT",
##                  0x200: "LIT_BUMP", 0x000: "LIT_FLAT"}
##    with open("drydock_meshes.obj", "w") as obj_file:
##        obj_file.write("# mp_drydock.bsp\n")
##        obj_file.write("# extracted with bsp_tool\n")
##        vertices = []
##        for x, y, z in bsp.VERTICES:
##            vertices.append(f"v {x} {y} {z}")
##        obj_file.write("\n".join(vertices) + "\n")
##        normals = []
##        for x, y, z in bsp.VERTEX_NORMALS:
##            normals.append(f"vn {x} {y} {z}")
##        obj_file.write("\n".join(normals) + "\n")
##        for i, mesh in enumerate(bsp.MESHES):
##            buffer = [f"o MESH_{i:04d}_{mesh_types[mesh.flags & 0x600]}"]
##            material = bsp.MATERIAL_SORT[mesh.material_sort]
##            texdata = bsp.TEXDATA[material.texdata]
##            texture = bsp.TEXDATA_STRING_DATA[texdata.string_table_index]
##            buffer.append(f"usemtl {texture}")
##            vertices = mesh_verts(i)
##            for i in range(0, len(vertices), 3):
##                A = vertices[i].position_index + 1
##                B = vertices[i + 1].position_index + 1
##                C = vertices[i + 2].position_index + 1
##                An = vertices[i].normal_index + 1
##                Bn = vertices[i + 1].normal_index + 1
##                Cn = vertices[i + 2].normal_index + 1
##                buffer.append(f"f {C}//{Cn} {B}//{Bn} {A}//{An}")
##            obj_file.write("\n".join(buffer) + "\n")
