# https://github.com/TTimo/GtkRadiant/blob/master/tools/quake3/q3map2/game_sof2.h
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c
import enum

from .. import shared
from ..id_software import quake
from ..id_software import quake3


FILE_MAGIC = b"RBSP"

BSP_VERSION = 1

GAME_PATHS = {"Soldier of Fortune 2": "SoF2",  # .pk3 extractions
              "Star Wars Jedi Knight - Jedi Academy": "StarWarsJediKnight",
              "Star Wars Jedi Knight II - Jedi Outcast": "StarWarsJediKnightII"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


class LUMP(enum.Enum):
    ENTITIES = 0
    TEXTURES = 1
    PLANES = 2
    NODES = 3
    LEAVES = 4
    LEAF_FACES = 5  # LEAFSURFACES
    LEAF_BRUSHES = 6
    MODELS = 7
    BRUSHES = 8
    BRUSH_SIDES = 9
    VERTICES = 10  # DRAWVERTICES
    INDICES = 11  # DRAWINDICES
    EFFECTS = 12  # FOGS
    FACES = 13  # SURFACES
    LIGHTMAPS = 14
    LIGHT_GRID = 15
    VISIBILITY = 16
    LIGHT_ARRAY = 17


LumpHeader = quake.LumpHeader


# known lump changes from Quake 3 -> Raven:
#   nothing lol


# a rough map of the relationships between lumps:

# Entity -> Model -> Node -> Leaf -> LeafFace -> Face
#                                \-> LeafBrush -> Brush

# Visibility -> Node -> Leaf -> LeafFace -> Face
#                   \-> Plane

#               /-> Texture  /-> Texture
# Model -> Brush -> BrushSide -> Plane
#      \-> Face              \-> Face
# NOTE: Brush's indexed Texture is just used for Contents flags

#     /-> Texture
# Face -> Index -> Vertex
#    \--> Vertex
#     \-> Effect


# LIGHT_GRID / LIGHT_ARRAY
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c#L89
# https://github.com/TTimo/GtkRadiant/blob/master/tools/urt/tools/quake3/q3map2/bspfile_rbsp.c#L115


BASIC_LUMP_CLASSES = {"LEAF_BRUSHES": shared.Ints,
                      "LEAF_FACES":   shared.Ints,
                      "INDICES":      shared.Ints}

LUMP_CLASSES = {"BRUSHES":   quake3.Brush,
                "LEAVES":    quake3.Leaf,
                "LIGHTMAPS": quake3.Lightmap,
                "MODELS":    quake3.Model,
                "NODES":     quake3.Node,
                "PLANES":    quake3.Plane}
# NOTE: BRUSH_SIDES, VERTICES & FACES differ; related to RitualBsp?

SPECIAL_LUMP_CLASSES = {"ENTITIES":   shared.Entities,
                        "VISIBILITY": quake3.Visibility}


methods = [quake.leaves_of_node, shared.worldspawn_volume]
methods = {m.__name__: m for m in methods}
