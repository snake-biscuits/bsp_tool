# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Vampire_The_Masquerade_-_Bloodlines
from typing import List

from .. import base
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = 17  # technically older than HL2's Source Engine branch

GAME_PATHS = {"Vampire The Masquerade - Bloodlines": "Vampire The Masquerade - Bloodlines/Vampire"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = source.LUMP

# struct SourceBspHeader { char file_magic[4]; int version; SourceLumpHeader headers[64]; int revision; };
lump_header_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}


read_lump_header = source.read_lump_header


# classes for lumps, in alphabetical order:
class Face(base.Struct):  # LUMP 7
    """makes up Models (including worldspawn), also referenced by LeafFaces"""
    light_colours: List[List[int]]  # 8x RGBExp32
    plane: int       # index into Plane lump
    side: int        # "faces opposite to the node's plane direction"
    on_node: bool    # if False, face is in a leaf
    first_edge: int  # index into the SurfEdge lump
    num_edges: int   # number of SurfEdges after first_edge in this Face
    texture_info: int    # index into the TextureInfo lump
    displacement_info: int   # index into the DisplacementInfo lump (None if -1)
    surface_fog_volume_id: int  # t-junctions? QuakeIII vertex-lit fog?
    styles: List[List[int]]  # "switchable lighting info"; selects an additional lightmap
    light_offset: int  # index of first pixel in LIGHTING / LIGHTING_HDR
    area: float  # surface area of this face
    lightmap: List[float]
    # lightmap.mins  # dimensions of lightmap segment
    # lightmap.size  # scalars for lightmap segment
    original_face: int  # ORIGINAL_FACES index, -1 if this is an original face
    smoothing_groups: int    # lightmap smoothing group
    __slots__ = ["light_colours", "plane", "side", "on_node", "first_edge", "num_edges",
                 "texture_info", "displacement_info", "surface_fog_volume_id", "styles",
                 "light_offset", "area", "lightmap", "original_face", "smoothing_groups"]
    _format = "32BHb?i4h8b8b8bif5iI"  # 104 bytes
    # NOTE: integer keys in _arrays / MappedArray._mapping is not yet supported
    # -- intended result: light_colour = [MappedArray(_mapping=[*"rgbe"])] * 8
    _arrays = {"light_colours": {x: [*"rgbe"] for x in "abcdefgh"},
               "styles": {"base": 8, "day": 8, "night": 8},
               "lightmap": {"mins": [*"xy"], "size": ["width", "height"]}}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = source.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = source.LUMP_CLASSES.copy()
LUMP_CLASSES.update({"FACES":          {0: Face},
                     "ORIGINAL_FACES": {0: Face}})

SPECIAL_LUMP_CLASSES = source.SPECIAL_LUMP_CLASSES.copy()
SPECIAL_LUMP_CLASSES.pop("PHYSICS_COLLIDE")  # interesting, is .phy different?

GAME_LUMP_HEADER = source.GameLumpHeader

GAME_LUMP_CLASSES = source.GAME_LUMP_CLASSES.copy()


methods = [*source.methods]
