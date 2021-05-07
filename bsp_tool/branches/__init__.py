__all__ = ["id_software", "infinity_ward", "nexon", "respawn", "valve",
           "by_magic", "by_name", "by_version"]

from . import id_software
from . import infinity_ward
from . import nexon
from . import respawn
from . import valve


__doc__ = """Index of developers of bsp format variants"""

by_magic = {
    # id_software.FILE_MAGIC & infinity_ward.FILE_MAGIC
    b"IBSP": [id_software.quake3, infinity_ward.call_of_duty1],
    # respawn.FILE_MAGIC
    b"rBSP": [respawn.apex_legends, respawn.titanfall2],
    # nexon.FILE_MAGIC & valve.FILE_MAGIC
    b"VBSP": [nexon.vindictus, valve.orange_box]
           }

by_name = {
    # ID SOFTWARE
    "quake3": id_software.quake3,
    "quakeiii": id_software.quake3,
    # INFINITY WARD
    "callofduty": infinity_ward.call_of_duty1,
    "cod": infinity_ward.call_of_duty1,
    # NEXON
    "counterstrikeonline2": nexon.cso2,
    "cso2": nexon.cso2,
    "csonline2": nexon.cso2,
    "mabinogi": nexon.vindictus,
    "mabinogiheroes": nexon.vindictus,
    "vindictus": nexon.vindictus,
    # RESPAWN
    "apex": respawn.apex_legends,
    "apexlegends": respawn.apex_legends,
    "r1": respawn.titanfall,
    "r2": respawn.titanfall2,
    "r5": respawn.apex_legends,
    "tf|2": respawn.titanfall2,
    "titanfall": respawn.titanfall,
    "titanfall2": respawn.titanfall2,
    # VALVE
    "csgo": valve.cs_go,
    "css": valve.cs_source,
    "cssource": valve.cs_source,
    "globaloffensive": valve.cs_go,
    "orangebox": valve.orange_box,
    "teamfortress2": valve.orange_box,
    "tf2": valve.orange_box
          }

by_version = {
    # ID SOFTWARE
    id_software.quake3.BSP_VERSION: id_software.quake3,  # 46
    # INFINITY WARD
    infinity_ward.call_of_duty1.BSP_VERSION: infinity_ward.call_of_duty1,  # 59
    # NEXON
    nexon.cso2.BSP_VERSION: nexon.cso2,  # 100?
    # skip vindictus, v20 defaults to orange_box
    # RESPAWN
    respawn.titanfall.BSP_VERSION: respawn.titanfall,  # 29
    respawn.titanfall2.BSP_VERSION: respawn.titanfall2,  # 37
    respawn.apex_legends.BSP_VERSION: respawn.apex_legends,  # 47
    48: respawn.apex_legends,  # Introduced in Season 7 with Olympus
    49: respawn.apex_legends,  # Introduced in Season 8 with Canyonlands Staging
    # VALVE
    valve.cs_source.BSP_VERSION: valve.cs_source,
    valve.cs_go.BSP_VERSION: valve.cs_go,
    valve.orange_box.BSP_VERSION: valve.orange_box  # 20 (many sub-variants)
             }


def gen_docs():  # hardcoded to RespawnBsp
    bsp_format_name = "RespawnBsp (Respawn Entertainment)"
    print(f"# {bsp_format_name} Supported Games (v0.3.0)")
    print("| Bsp version | Game | Branch script | Lumps supported |")

    game_scripts = {"Counter-Strike: Source": valve.orange_box}
    # ^ {"game": script}
    # NOTE: markdown looks the same without padding
    game_name_padding = max(len(g) for g in game_scripts.keys())
    game_script_padding = max(len(s.__name__) for s in game_scripts.values()) + 2
    print(f"| --: | {'-' * game_name_padding} | {'-' * game_script_padding} | ------: |")
    for game in sorted(game_scripts, key=lambda g: game_scripts[g].BSP_VERSION):
        game_script = game_scripts[game]
        supported_lumps = len({*game_script.BASIC_LUMP_CLASSES,
                               *game_script.LUMP_CLASSES,
                               *game_script.SPECIAL_LUMP_CLASSES})
        # TODO: Pad each line equally (optional)
        print(f"| {game_script.BSP_VERSION:>4s}",
              f"| {game} | `{game_script.__name__}`",
              f"| {supported_lumps} / {len(game_script.LUMPS)} |")

    print("| Lump index | Bsp version | Lump name | Lump version | LumpClass | % of struct mapped |")
    # TODO: print each lump entry, in order of BSP_VERSION
    # TODO: if a script uses a different format, add it to the list
    # TODO: print alternate lump names
    # TODO: don't print lump name or index if it doesn't change
    """| 4 |  20 | `VISIBILITY` | 0 | :x:                     |   0% |
       | 5 |  20 | `NODES`      | 0 | `valve.orange_box.Node` | 100% |
       |   |  20 |              | 0 | `nexon.vindictus.Node`  | 100% |"""
    # NOTE: % mapped is based on number of unknowns in format
