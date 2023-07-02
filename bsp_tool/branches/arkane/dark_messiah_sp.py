# https://developer.valvesoftware.com/wiki/Source_BSP_File_Format/Game-Specific#Dark_Messiah_of_Might_and_Magic
from typing import List

from .. import base
from .. import vector
from ..valve import orange_box
from ..valve import source


FILE_MAGIC = b"VBSP"

BSP_VERSION = (20, 4)

GAME_PATHS = {"Dark Messiah of Might and Magic Single Player": "Dark Messiah of Might and Magic Single Player"}

GAME_VERSIONS = {GAME_NAME: BSP_VERSION for GAME_NAME in GAME_PATHS}


LUMP = orange_box.LUMP


LumpHeader = source.LumpHeader


# classes for lumps, in alphabetical order:
class Model(base.Struct):  # LUMP 14
    bounds: List[float]
    # bounds.mins: List[float]  # xyz
    # bounds.maxs: List[float]  # xyz
    origin: List[float]  # xyz
    unknown: int
    head_node: int   # top-level Node of this Model
    first_face: int  # first Face of this Model
    num_faces: int   # number of Faces after first_face in this Model
    __slots__ = ["bounds", "origin", "unknown", "head_node", "first_face", "num_faces"]
    _format = "9f4i"
    _arrays = {"bounds": {"mins": [*"xyz"], "maxs": [*"xyz"]}, "origin": [*"xyz"]}
    _classes = {"bounds.mins": vector.vec3, "bounds.maxs": vector.vec3, "origin": vector.vec3}


class TextureInfo(base.Struct):  # LUMP 6
    """Texture projection info & index into TEXTURE_DATA"""
    texture: List[List[float]]  # 2 texture projection vectors
    lightmap: List[List[float]]  # 2 lightmap projection vectors
    unknown: bytes
    flags: int  # Surface flags
    texture_data: int  # index of TextureData
    __slots__ = ["texture", "lightmap", "unknown", "flags", "texture_data"]
    _format = "16f24s2i"
    _arrays = {"texture": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]},
               "lightmap": {"s": [*"xyz", "offset"], "t": [*"xyz", "offset"]}}
    _classes = {**{"{g}.{v}.xyz": vector.vec3 for g in ("texture", "lightmap") for v in "st"},
                "flags": source.Surface}
    # TODO: TextureVector class from vmf_tool
    # TODO: .uv_at(position: vector.vec3) TextureVector projection


# classes for special lumps, in alphabetical order:
class GameLumpHeader(base.MappedArray):
    id: str
    flags: int
    version: int
    offset: int
    length: int
    unknown: int
    _mapping = ["id", "flags", "version", "offset", "length", "unknown"]
    _format = "4s2H3i"


# TODO: StaticPropLumpv6


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()

LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("MODELS")
LUMP_CLASSES.pop("TEXTURE_INFO")
LUMP_CLASSES.pop("WORLD_LIGHTS")
LUMP_CLASSES.pop("WORLD_LIGHTS_HDR")
# LUMP_CLASSES.update({"MODELS":       {0: Model},
#                      "TEXTURE_INFO": {0: TextureInfo}})

SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()

GAME_LUMP_HEADER = GameLumpHeader

# {"lump": {version: SpecialLumpClass}}
GAME_LUMP_CLASSES = {"sprp": {6: source.GameLump_SPRPv6}}


methods = [*orange_box.methods]
