import enum
import struct
from typing import List

from .. import base
from .. import shared
from . import orange_box


BSP_VERSION = 19  # & 20

GAMES = ["Counter-Strike: Source",  # counter-strike source/cstrike
         "Half-Life 1: Source - Deathmatch",
         "Half-Life 2",  # Half-Life 2/hl2
         "Half-Life 2: Episode 1"]  # Half-Life 2/episodic

LUMP = orange_box.LUMP
lump_header_address = orange_box.lump_header_address


def read_lump_header(file, LUMP: enum.Enum) -> orange_box.OrangeBoxLumpHeader:
    file.seek(lump_header_address[LUMP])
    offset, length, version, fourCC = struct.unpack("4I", file.read(16))
    header = orange_box.OrangeBoxLumpHeader(offset, length, version, fourCC)
    return header


# classes for each lump, in alphabetical order:
# classes for special lumps, in alphabetical order:
class StaticPropv4(base.Struct):  # sprp GAME LUMP (LUMP 35)
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L151"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    name_index: int  # index into AME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "flags", "skin", "fade_distance", "lighting_origin"]
    _format = "6f3H2Bi5f"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"]}


class StaticPropv5(base.Struct):  # sprp GAME LUMP (LUMP 35)
    """https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/public/gamebspfile.h#L168"""
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    name_index: int  # index into AME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    flags: int  # other flags
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "skin", "fade_distance", "lighting_origin",
                 "forced_fade_scale"]
    _format = "6f3HBi6f2Hi2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"]}


class StaticPropv6(base.Struct):  # sprp GAME LUMP (LUMP 35)
    origin: List[float]  # origin.xyz
    angles: List[float]  # origin.yzx  QAngle; Z0 = East
    name_index: int  # index into AME_LUMP.sprp.model_names
    first_leaf: int  # index into Leaf lump
    num_leafs: int  # number of Leafs after first_leaf this StaticPropv10 is in
    solid_mode: int  # collision flags enum
    skin: int  # index of this StaticProp's skin in the .mdl
    fade_distance: List[float]  # min & max distances to fade out
    lighting_origin: List[float]  # xyz position to sample lighting from
    forced_fade_scale: float  # relative to pixels used to render on-screen?
    dx_level: List[int]  # supported directX level, will not render depending on settings
    __slots__ = ["origin", "angles", "name_index", "first_leaf", "num_leafs",
                 "solid_mode", "skin", "fade_distance", "lighting_origin",
                 "forced_fade_scale", "dx_level"]
    _format = "6f3HBi6f2Hi2H"
    _arrays = {"origin": [*"xyz"], "angles": [*"yzx"], "fade_distance": ["min", "max"],
               "lighting_origin": [*"xyz"], "dx_level": ["min", "max"]}


# {"LUMP_NAME": {version: LumpClass}}
BASIC_LUMP_CLASSES = orange_box.BASIC_LUMP_CLASSES.copy()
LUMP_CLASSES = orange_box.LUMP_CLASSES.copy()
LUMP_CLASSES.pop("LEAVES")
SPECIAL_LUMP_CLASSES = orange_box.SPECIAL_LUMP_CLASSES.copy()
# GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.copy()
# GAME_LUMP_CLASSES = orange_box.GAME_LUMP_CLASSES.update({
#     4: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv4),
#     5: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv5),
#     6: lambda raw_lump: shared.GameLump_SPRP(raw_lump, StaticPropv6)})
# NOTE: having some errors with CS:S

methods = [*orange_box.methods]
