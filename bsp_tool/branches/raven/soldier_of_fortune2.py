# https://github.com/TTimo/GtkRadiant/blob/master/tools/quake3/q3map2/game_sof2.h
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c
import enum

from .. import shared
from ..id_software import quake3


FILE_MAGIC = b"RBSP"

BSP_VERSION = 1

GAME_PATHS = {"Soldier of Fortune 2": "SoF2",  # .pk3 extractions
              "Star Wars Jedi Knight - Jedi Academy": "StarWarsJediKnight",
              "Star Wars Jedi Knight II - Jedi Outcast": "StarWarsJediKnightII"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    SHADERS = 1
    PLANES = 2
    NODES = 3
    LEAVES = 4
    LEAF_SURFACES = 5
    LEAF_BRUSHES = 6
    MODELS = 7
    BRUSHES = 8
    BRUSH_SIDES = 9
    DRAW_VERTICES = 10
    DRAW_INDICES = 11
    FOGS = 12
    SURFACES = 13
    LIGHTMAPS = 14
    LIGHT_GRID = 15
    VISIBILITY = 16
    LIGHT_ARRAY = 17


# struct RavenBspHeader { char file_magic[4]; int version; QuakeLumpHeader headers[18]; };
lump_header_address = {LUMP_ID: (8 + i * 8) for i, LUMP_ID in enumerate(LUMP)}

# Known lump changes from Quake 3 -> Raven:
# New:
#   FACES -> SURFACES
#   LEAF_FACES -> LEAF_SURFACES
#   TEXTURES -> SHADERS
#   VERTICES -> DRAW_VERTICES
#   MESH_VERTICES -> DRAW_INDICES

# a rough map of the relationships between lumps:
#
#               /-> Texture
# Model -> Brush -> BrushSide
#      \-> Face -> MeshVertex
#             \--> Texture
#              \-> Vertex


# LIGHT_GRID / LIGHT_ARRAY
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c#L89
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c#L115


BASIC_LUMP_CLASSES = {"LEAF_BRUSHES":  shared.Ints,
                      "LEAF_SURFACES": shared.Ints,
                      "DRAW_INDICES":  shared.Ints}

LUMP_CLASSES = {"BRUSHES":       quake3.Brush,
                "LEAVES":        quake3.Leaf,
                "LIGHTMAPS":     quake3.Lightmap,
                "MODELS":        quake3.Model,
                "NODES":         quake3.Node,
                "PLANES":        quake3.Plane}
# NOTE: BRUSH_SIDES, DRAW_VERTICES & SURFACES differ; related to RitualBsp?

SPECIAL_LUMP_CLASSES = {"ENTITIES":   shared.Entities,
                        "VISIBILITY": quake3.Visibility}


methods = [shared.worldspawn_volume]
