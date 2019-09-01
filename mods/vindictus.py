import common
import enum

class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = 1
    TEXDATA = 2
    VERTICES = 3
    VISIBILITY = 4
    NODES = 5
    TEXINFO = 6
    FACES = 7
    LIGHTING = 8
    OCCLUSION = 9
    LEAVES = 10
    FACEIDS = 11
    EDGES = 12
    SURFEDGES = 13
    MODELS = 14
    WORLD_LIGHTS = 15
    LEAF_FACES = 16
    LEAF_BRUSHES = 17
    BRUSHES = 18
    BRUSH_SIDES = 19
    AREAS = 20
    AREA_PORTALS = 21
    UNUSED0 = 22
    UNUSED1 = 23
    UNUSED2 = 24
    UNUSED3 = 25
    DISP_INFO = 26
    ORIGINAL_FACES = 27
    PHYS_DISP = 28
    PHYS_COLLIDE = 29
    VERT_NORMALS = 30
    VERT_NORMAL_INDICES = 31
    DISP_LIGHTMAP_ALPHAS = 32
    DISP_VERTS = 33
    DISP_LIGHTMAP_SAMPLE_POSITIONS = 34
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIM_VERTS = 38
    PRIM_INDICES = 39
    PAKFILE = 40
    CLIP_PORTAL_VERTS = 41
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISP_TRIS = 48
    PHYS_COLLIDE_SURFACE = 49
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51
    LEAF_AMBIENT_INDEX = 52
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55
    LEAF_AMBIENT_LIGHTING = 56
    XZIP_PAKFILE = 57
    FACES_HDR = 58
    MAP_FLAGS = 59
    OVERLAY_FADES = 60
    UNUSED4 = 61
    UNUSED5 = 62 
    UNUSED6 = 63

lump_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


class game_lump(common.base):
    __slots__ = ["id", "flags", "version", "offset", "length"]
    _definition = """int id;
    int flags;
    int version;
    int fileofs;
    int filelen;"""


class node(common.base):
    __slots__ = ["planenum", "children", "mins", "maxs", "firstface",
                 "numfaces", "area", "padding"]
    _definition = """int planenum;
    int children[2];
    int mins[3];
    int maxs[3];
    int firstface;
    int numfaces;
    int unknown;"""


class leaf(common.base):
    __slots__ = ["contents", "cluster", "flags", "mins", "maxs",
                 "firstleafface", "numleaffaces", "firstleafbrush",
                 "numleafbrushes", "leafWaterDataID"]
    _definition = """int contents;
    int cluster;
    int	flags;
    int	mins[3];
    int	maxs[3];
    unsigned int firstleafface;
    unsigned int numleaffaces;
    unsigned int firstleafbrush;
    unsigned int numleafbrushes;
    int leafWaterDataID;"""


class face(common.base):
    __slots__ = ["planenum", "side", "onNode", "unknown0", "firstedge",
                 "numedges", "texinfo", "dispinfo", "surfaceFogVolumeID",
                 "unknown1", "styles", "lightofs", "area",
                 "LightmapTextureMinsInLuxels", "LightmapTextureSizeInLuxels",
                 "origFace", "numPrims", "firstPrimID", "smoothingGroups"]
    _definition = """unsigned int planenum;
    byte side;
    byte onNode;
    short unknown0;
    int firstedge;
    int numedges;
    int texinfo;
    int	dispinfo;
    int	surfaceFogVolumeID;
    int	unknown1;
    byte styles[4];
    int	lightofs;
    float area;
    int	LightmapTextureMinsInLuxels[2];
    int	LightmapTextureSizeInLuxels[2];
    unsigned int origFace;
    unsigned int numPrims;
    unsigned int firstPrimID;
    unsigned int smoothingGroups;"""


class brushside(common.base):



if __name__ == "__main__":
    print(common.get_format(node))

    import textwrap
    def def_to_slots(definition):
        result = []
        for line in definition.split(";")[:-1]:
            line = textwrap.shorten(line, 128)
            name = line.rpartition(" ")[2]
            if name.endswith("]"):
                name = name.rpartition("[")[0]
            result.append(name)
        return result
    print(def_to_slots(face._definition))
