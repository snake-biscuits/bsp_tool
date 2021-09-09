__all__ = ["arkane", "gearbox", "id_software", "infinity_ward", "nexon", "respawn", "valve",
           "by_magic", "by_name", "by_version"]

from . import arkane
from . import gearbox
from . import id_software
from . import infinity_ward
from . import nexon
from . import respawn
from . import valve


__doc__ = """Index of developers of bsp format variants"""

FILE_MAGIC_developer = {b"IBSP": [id_software, infinity_ward],
                        b"rBSP": respawn,
                        b"VBSP": [nexon, valve]}

# NOTE: bsp_tool/__init__.py: load_bsp can be fed a string to select the relevant branch script
# by_name is searched with a lowercase, numbers & letters only version of that string
# NOTE: some (but not all!) games are listed here have multiple valid names (including internal mod names)
# TODO: generate from branch.GAMES (folder names)
# TODO: handle branchscripts with multiple bsp_versions elegantly


def simplify_name(name: str) -> str:
    """'Counter-Strike: Online 2' -> 'counterstrikeonline2'"""
    return "".join(filter(str.isalnum, name.lower()))


by_name = {
    # Id Software - Id Tech
    # TODO: Hexen II (no file-magic)
    "quake": id_software.quake,
    # TODO: Quake II
    # TODO: Team Fortress Quake
    "quake3": id_software.quake3,
    "quakeiii": id_software.quake3,
    # TODO: Quake 4
    # TODO: Quake Champions
    "quakelive": id_software.quake3,
    # Infinity Ward - IW Engine(s)
    "callofduty": infinity_ward.call_of_duty1,
    "cod": infinity_ward.call_of_duty1,
    # TODO: Call of Duty 2
    # TODO: Call of Duty 4
    # NEXON - Source Engine
    "counterstrikeonline2": nexon.cso2,
    "cso2": nexon.cso2,
    "csonline2": nexon.cso2,
    "mabinogi": nexon.vindictus,
    "mabinogiheroes": nexon.vindictus,
    "vindictus": nexon.vindictus,
    # Respawn Entertainment - Source Engine
    "apex": respawn.apex_legends,
    "apexlegends": respawn.apex_legends,
    "r1": respawn.titanfall,
    "r2": respawn.titanfall2,
    "r5": respawn.apex_legends,
    "titanfall": respawn.titanfall,
    "titanfall2": respawn.titanfall2,
    # Valve Software - Source Engine
    "alienswarm": valve.alien_swarm,
    "alienswarmreactivedrop": valve.alien_swarm,
    "blackmesa": valve.sdk_2013,
    "bladesymphony": valve.sdk_2013,
    "counterstrikeglobaloffensive": valve.sdk_2013,
    "counterstrikesource": valve.source,
    "csgo": valve.sdk_2013,
    "css": valve.source,
    "cssource": valve.source,
    "dayofdefeatsource": valve.orange_box,
    "dods": valve.orange_box,
    "episode1": valve.orange_box,
    "episode2": valve.orange_box,
    "episodic": valve.orange_box,
    "fortressforever": valve.orange_box,
    "garrysmod": valve.orange_box,
    "globaloffensive": valve.sdk_2013,
    "gmod": valve.orange_box,
    "gstring": valve.orange_box,  # awesome sourcemod
    "halflife1sourcedeathmatch": valve.source,
    "halflife2": valve.source,
    "halflife2ep1": valve.source,
    "halflife2ep2": valve.orange_box,
    "halflife2episode1": valve.source,
    "halflife2episode2": valve.orange_box,
    "halflife2episodic": valve.source,
    "halflife2hl1": valve.source,
    "halflifesource": valve.source,
    "hl2": valve.source,
    "hl2ep1": valve.source,
    "hl2ep2": valve.orange_box,
    "hls": valve.source,
    "hlsource": valve.source,
    "l4d": valve.left4dead,
    "l4d2": valve.left4dead2,
    "left4dead": valve.left4dead,
    "left4dead2": valve.left4dead2,
    "neotokyo": valve.orange_box,
    "orangebox": valve.orange_box,
    "portal": valve.orange_box,
    "portal2": valve.sdk_2013,
    "portalreloaded": valve.sdk_2013,
    "sourcefilmmaker": valve.sdk_2013,
    "synergy": valve.source,
    "teamfortress2": valve.orange_box,
    "tf2": valve.orange_box,
    # Valve Software - GoldSrc Engine (more mods @ https://half-life.fandom.com/wiki/Mods)
    "007nightfire": valve.goldsrc,  # untested
    "blueshift": gearbox.bshift,
    "bshift": gearbox.bshift,
    "counterstrike": valve.goldsrc,  # CS 1.6
    "counterstrikeconditionzero": valve.goldsrc,
    "counterstrikeneo": valve.goldsrc,  # obscure & untested
    "counterstrikeonline": valve.goldsrc,  # obscure & untested
    "cs": valve.goldsrc,  # CS 1.6
    "cscz": valve.goldsrc,
    "csn": valve.goldsrc,  # obscure
    "cso": valve.goldsrc,  # obscure
    "dayofdefeat": valve.goldsrc,
    "deathmatchclassic": valve.goldsrc,
    "dmc": valve.goldsrc,
    "dod": valve.goldsrc,
    "goldsrc": valve.goldsrc,
    "gunmanchronicles": valve.goldsrc,
    "halflife": valve.goldsrc,
    "halflifeblueshift": gearbox.bshift,
    "halflifebshift": gearbox.bshift,
    "halflifericochet": valve.goldsrc,
    "halflifecstrike": valve.goldsrc,
    "halflifeopposingforce": valve.goldsrc,
    "halfquaketrilogy": valve.goldsrc,
    "hlblueshift": gearbox.bshift,
    "hlopposingforce": valve.goldsrc,
    "jamesbond007nightfire": valve.goldsrc,  # untested
    "nightfire": valve.goldsrc,
    "opposingforce": valve.goldsrc,
    "ricochet": valve.goldsrc,
    "svencoop": valve.goldsrc,
    "teamfortressclassic": valve.goldsrc,
    "tfc": valve.goldsrc
          }

# NOTE: limiting because many games share version numbers
# could also be generated from loaded scripts
by_version = {
    # Id Software
    id_software.quake.BSP_VERSION: id_software.quake,  # 23
    id_software.quake2.BSP_VERSION: id_software.quake2,  # 38
    id_software.quake3.BSP_VERSION: id_software.quake3,  # 46
    # Infinity Ward
    infinity_ward.call_of_duty1.BSP_VERSION: infinity_ward.call_of_duty1,  # 59
    # Nexon
    nexon.cso2.BSP_VERSION: nexon.cso2,  # 100?
    # nexon.vindictus.BSP_VERSION: nexon.vindictus, # 20
    # Respawn Entertainment
    respawn.titanfall.BSP_VERSION: respawn.titanfall,  # 29
    respawn.titanfall2.BSP_VERSION: respawn.titanfall2,  # 37
    respawn.apex_legends.BSP_VERSION: respawn.apex_legends,  # 47
    48: respawn.apex_legends,  # Introduced in Season 7 with Olympus
    49: respawn.apex_legends,  # Introduced in Season 8 with Canyonlands Staging
    # Valve Software
    # valve.alien_swarm.BSP_VERSION: valve.alien_swarm,  # 21
    valve.sdk_2013.BSP_VERSION: valve.sdk_2013,  # 21
    valve.goldsrc.BSP_VERSION: valve.goldsrc,
    # valve.left4dead.BSP_VERSION: valve.left4dead,  # 20
    # valve.left4dead2.BSP_VERSION: valve.left4dead2,  # 21
    valve.orange_box.BSP_VERSION: valve.orange_box,  # 20 (many sub-variants)
    valve.source.BSP_VERSION: valve.source,  # 19 & 20
    # Other
    # arkane.dark_messiah.BSP_VERSION: arkane.dark_messiah,  # 20.4 ?
    gearbox.bshift.BSP_VERSION: gearbox.bshift  # 30
             }

# NOTE: ata4's bspsrc uses unique entity classnames to identify branches
