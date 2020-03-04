import math
import struct

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
drydock = bsp_tool.bsp(f"{titanfall_dir}/maps/mp_drydock.bsp",
                       mod=bsp_tool.titanfall2, lump_files=True)

### export vertices to .obj file
##with open("drydock.obj", "w") as obj_file:
##    obj_file.write("# mp_drydock.bsp\n")
##    obj_file.write("# extracted with bsp_tool\n")
##    obj_file.write("\n".join(f"v {x} {y} {z}" for x, y, x in drydock.VERTICES))

for attrib in dir(drydock):
    if attrib.startswith("RAW_"):
        lump = getattr(drydock, attrib)
        lump_size = len(lump)
        lump_name = attrib[4:]
        lump_id = getattr(bsp_tool.titanfall2.LUMP, lump_name)
        hex_id = f"{lump_id.value:04x}"
        print(hex_id, lump_name, denominators_of(lump_size))

# OUTPUT:
##006b CELLS [8, 12, 16, 20, 24, 30, 40, 60]
##0077 CELL_AABB_NODES [8, 16, 32, 64, 7789, 15578, 31156, 62312]
##006a CELL_BSP_NODES [8, 149]
##005c CM_BRUSHES [8, 12, 16, 24, 32, 36, 48, 64, 72, 96, 144, 192, 303, 404, 606, 808, 909, 1212, 1616, 1818, 2424, 3636, 4848, 7272]
##005d CM_BRUSH_SIDE_PLANE_OFFSETS found no denomimnators for 56894
##005e CM_BRUSH_SIDE_PROPS found no denomimnators for 78710
##005f CM_BRUSH_TEX_VECS [8, 16, 20, 32, 40, 68, 80, 136, 160, 272, 340, 544, 680, 1852, 2315, 3704, 4630, 7871, 9260, 15742, 18520, 31484, 39355, 62968, 78710, 157420]
##0057 CM_GEO_SETS [8, 12, 16, 24, 44, 48, 88, 132, 176, 309, 412, 618, 1133, 1236, 2266, 3399, 4532, 6798]
##0058 CM_GEO_SET_BOUNDS [8, 12, 16, 24, 32, 44, 48, 88, 96, 132, 176, 264, 412, 618, 824, 1133, 1236, 2266, 2472, 3399, 4532, 6798, 9064, 13596]
##0055 CM_GRID found no denomimnators for 28
##0056 CM_GRIDCELLS [8, 16, 32, 64, 116, 232, 464, 928]
##0059 CM_PRIMS [8, 16, 3637, 7274]
##005a CM_PRIM_BOUNDS [8, 16, 32, 64, 3637, 7274, 14548, 29096]
##005b CM_UNIQUE_CONTENTS found no denomimnators for 140
##0063 CSM_AABB_NODES [8, 16, 20, 32, 40, 64, 80, 128, 160, 320, 358, 716, 895, 1432, 1790, 2864, 3580, 5728, 7160, 14320]
##0064 CSM_OBJ_REFS found no denomimnators for 7462
##002a CUBEMAPS found no denomimnators for 48
##0018 ENTITY_PARTITIONS found no denomimnators for 28
##0023 GAME_LUMP [8, 164, 328, 2029, 4058, 83189]
##0024 LEAF_WATERDATA [8, 164, 328, 2029, 4058, 83189]
##007b LEVEL_INFO found no denomimnators for 28
##0069 LIGHTMAP_DATA_REAL_TIME_LIGHTS [8, 12, 16, 24, 32, 36, 48, 64, 72, 96, 108, 128, 144, 192, 216, 256, 288, 324, 384, 432, 512, 576, 648, 768, 864, 1024, 1152, 1296, 1536, 1728, 2048, 2304, 2592, 3072, 3456, 4096, 4608, 5184, 6144, 6912, 8192, 9216, 10368, 12288, 13824, 16384, 18432, 20736, 24576, 27648, 32768, 36864, 41472, 49152, 55296, 65536, 73728, 82944, 98304, 110592, 131072, 147456, 165888, 196608, 221184, 294912, 331776, 393216, 442368, 589824, 663552, 884736, 1179648, 1327104, 1769472, 2654208, 3538944, 5308416]
##0062 LIGHTMAP_DATA_SKY [8, 12, 16, 24, 32, 36, 48, 64, 72, 96, 108, 128, 144, 192, 216, 256, 288, 324, 384, 432, 512, 576, 648, 768, 864, 1024, 1152, 1296, 1536, 1728, 2048, 2304, 2592, 3072, 3456, 4096, 4608, 5184, 6144, 6912, 8192, 9216, 10368, 12288, 13824, 16384, 18432, 20736, 24576, 27648, 32768, 36864, 41472, 49152, 55296, 65536, 73728, 82944, 98304, 110592, 131072, 147456, 165888, 196608, 221184, 294912, 331776, 393216, 442368, 589824, 663552, 884736, 1179648, 1327104, 1769472, 2654208, 3538944, 5308416]
##0053 LIGHTMAP_HEADERS found no denomimnators for 48
##0065 LIGHTPROBES [8, 12, 16, 24, 32, 36, 48, 64, 72, 96, 108, 128, 144, 192, 216, 256, 284, 288, 384, 432, 512, 568, 576, 768, 852, 864, 1024, 1136, 1152, 1704, 1728, 1917, 2272, 2304, 2556, 3408, 3456, 3834, 4544, 5112, 6816, 6912, 7668, 9088, 10224, 13632, 15336, 18176, 20448, 27264, 30672, 40896, 54528, 61344, 81792, 122688, 163584, 245376]
##0068 LIGHTPROBE_REFS [8, 20, 40, 50971, 101942, 254855]
##0067 LIGHTPROBE_TREE [8, 12, 24, 36, 68, 72, 136, 204, 408, 612, 694, 1041, 2082, 3123, 5899, 6246, 11798, 17697, 35394, 53091]
##0052 MATERIAL_SORT [8, 12, 16, 24, 36, 48, 72, 94, 141, 188, 282, 423, 564, 846]
##0050 MESHES [8, 28, 44, 56, 88, 308, 698, 2443, 3839, 4886, 7678, 26873]
##0051 MESH_BOUNDS [8, 16, 32, 44, 64, 88, 176, 352, 698, 1396, 2792, 3839, 5584, 7678, 15356, 30712]
##004f MESH_INDICES [8, 12, 20, 24, 40, 60, 120, 596, 956, 1192, 1788, 1912, 2235, 2390, 3585, 4470, 7170, 35611, 71222, 106833, 178055, 213666, 356110, 534165]
##0078 OBJ_REFS found no denomimnators for 39578
##0079 OBJ_REF_BOUNDS [8, 16, 28, 32, 44, 56, 88, 112, 176, 224, 308, 352, 616, 1028, 1799, 2056, 2827, 3598, 5654, 7196, 11308, 14392, 19789, 22616, 39578, 79156]
##0076 OCCLUSION_MESH_INDICES [8, 12, 24, 68, 102, 289, 578, 867]
##0075 OCCLUSION_MESH_VERTS [12, 36, 177, 531]
##0028 PAKFILE found no denomimnators for 1573678
##001d PHYS_COLLIDE found no denomimnators for 16
##0001 PLANES [8, 16, 116, 232, 464, 881, 1762, 3524, 25549, 51098]
##006c PORTALS [12, 20, 60, 127, 381, 635]
##006e PORTAL_EDGES [8, 16, 32, 53, 106, 212]
##0073 PORTAL_EDGE_ISECT_AT_VERT [8, 16, 32, 241, 482, 964]
##0072 PORTAL_EDGE_ISECT_EDGE [8, 16, 32, 241, 482, 964]
##0074 PORTAL_EDGE_ISECT_HEADER [8, 16, 32, 106, 212, 424]
##0071 PORTAL_EDGE_REFS [8, 12, 20, 24, 40, 69, 115, 138, 230, 345]
##006d PORTAL_VERTS [12, 619]
##006f PORTAL_VERT_EDGES [8, 16, 619, 1238]
##0070 PORTAL_VERT_REFS [8, 12, 20, 24, 40, 69, 115, 138, 230, 345]
##007d SHADOW_MESH_ALPHA_VERTS [20, 1237]
##007e SHADOW_MESH_INDICES [8, 12, 16, 24, 32, 48, 64, 76, 96, 128, 152, 192, 212, 228, 256, 304, 384, 424, 456, 608, 636, 768, 848, 912, 1007, 1216, 1272, 1696, 1824, 2014, 2544, 3021, 3392, 3648, 4028, 5088, 6042, 8056, 10176, 12084, 16112, 24168, 32224, 48336, 64448, 96672]
##007f SHADOW_MESH_MESHES [12, 23]
##007c SHADOW_MESH_OPAQUE_VERTS [8, 12, 24, 48491, 96982, 145473]
##0066 STATIC_PROP_LIGHTPROBE_INDEX [8, 16, 32, 64, 128, 284, 568, 1136, 2272, 4544]
##0002 TEXDATA [8, 12, 24, 36, 72, 151, 302, 453, 906, 1359]
##002b TEXDATA_STRING_DATA found no denomimnators for 12203
##002c TEXDATA_STRING_TABLE [8, 151]
##0061 TRICOLL_BEVEL_INDEXE [8, 16, 28, 32, 56, 64, 112, 224, 448, 4079, 8158, 16316, 28553, 32632, 57106, 65264, 114212, 228424]
##0060 TRICOLL_BEVEL_STARTS found no denomimnators for 1302506
##0045 TRICOLL_HEADERS [8, 16, 20, 40, 44, 68, 80, 88, 136, 176, 220, 272, 340, 440, 578, 748, 935, 1156, 1445, 1870, 2890, 3179, 3740, 5780, 6358, 12716, 15895, 31790]
##0044 TRICOLL_NODES [8, 16, 32, 64, 108503, 217006, 434012, 868024]
##0042 TRICOLL_TRIS [68, 116, 22457, 38309]
##0019 UNKNOWN_25 found no denomimnators for 28
##001f UNKNOWN_31 [8, 12, 16, 20, 24, 32, 36, 40, 48, 60, 72, 80, 96, 108, 120, 144, 160, 180, 216, 240, 288, 360, 432, 480, 540, 720, 864, 1080, 1440, 2160, 3326, 4989, 6652, 8315, 9978, 13304, 14967, 16630, 19956, 24945, 29934, 33260, 39912, 44901, 49890, 59868, 66520, 74835, 89802, 99780, 119736, 149670, 179604, 199560, 224505, 299340, 359208, 449010, 598680, 898020]
##0004 UNKNOWN_4 found no denomimnators for 28
##0005 UNKNOWN_5 [8, 9]
##003b UNKNOWN_59 [8, 16, 28, 56, 112, 503, 1006, 2012, 3521, 7042]
##0006 UNKNOWN_6 [8, 12, 24, 164, 328, 492, 566, 849, 1698, 11603, 23206, 34809]
##0007 UNKNOWN_7 [20, 44, 92, 116, 220, 460, 484, 580, 1012, 1595, 2783, 3335, 3509, 7337, 13915, 17545, 36685, 80707]
##007a UNUSED_122 found no denomimnators for 2394
##0029 UNUSED_41 found no denomimnators for 1573678
##002d UNUSED_45 [8, 151]
##001e VERTEX_NORMALS [8, 12, 16, 20, 24, 32, 36, 40, 48, 60, 72, 80, 96, 108, 120, 144, 160, 180, 216, 240, 288, 360, 432, 480, 540, 720, 864, 1080, 1440, 2160, 3326, 4989, 6652, 8315, 9978, 13304, 14967, 16630, 19956, 24945, 29934, 33260, 39912, 44901, 49890, 59868, 66520, 74835, 89802, 99780, 119736, 149670, 179604, 199560, 224505, 299340, 359208, 449010, 598680, 898020]
##004b VERTS_BLINN_PHONG [8, 16, 32, 64, 108503, 217006, 434012, 868024]
##0049 VERTS_LIT_BUMP [8, 20, 40, 44, 88, 124, 220, 248, 440, 620, 1240, 1364, 2728, 13985, 27970, 30767, 61534, 86707, 153835, 173414, 307670, 433535, 867070, 953777, 1907554, 4768885]
##004c VERTS_RESERVED_5 [8, 16, 20, 40, 44, 68, 80, 88, 136, 176, 220, 272, 340, 440, 578, 748, 935, 1156, 1445, 1870, 2890, 3179, 3740, 5780, 6358, 12716, 15895, 31790]
##004e VERTS_RESERVED_7 [8, 16, 20, 40, 44, 100, 110, 220, 275, 550]
##0047 VERTS_UNLIT [8, 16, 20, 40, 44, 100, 110, 220, 275, 550]
##004a VERTS_UNLIT_TS [8, 28, 56, 5113, 10226, 35791]
##0036 WORLDLIGHTS_HDR [8, 16, 28, 56, 112, 503, 1006, 2012, 3521, 7042]


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
