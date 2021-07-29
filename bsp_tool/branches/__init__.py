__all__ = ["id_software", "infinity_ward", "nexon", "respawn", "valve",
           "by_magic", "by_name", "by_version"]

from . import id_software
from . import infinity_ward
from . import nexon
from . import respawn
from . import valve


__doc__ = """Index of developers of bsp format variants"""

FILE_MAGIC_developer = {b"IBSP": [id_software, infinity_ward],
                        b"rBSP": respawn,
                        b"VBSP": [nexon, valve]}

by_name = {
    # ID SOFTWARE
    "quake": id_software.quake,
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
    id_software.quake3.BSP_VERSION: id_software.quake,  # 23
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
