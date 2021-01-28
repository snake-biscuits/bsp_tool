__all__ = ["id_software", "infinity_ward", "respawn", "valve", "by_magic", "by_name", "by_version"]

from . import id_software
from . import infinity_ward
from . import respawn
from . import valve


by_magic = {
        # id_software.FILE_MAGIC
        b"IBSP": [id_software.quake3,
                  # infinity_ward.FILE_MAGIC
                  infinity_ward.call_of_duty1],
        # respawn.FILE_MAGIC
        b"rBSP": [respawn.apex_legends, respawn.titanfall2],
        # valve.FILE_MAGIC
        b"VBSP": [valve.orange_box, valve.vindictus]}

by_name = {
    # ID SOFTWARE
    "quakeiii": id_software.quake3,
    "quake 3": id_software.quake3,
    "quake3": id_software.quake3,
    # RESPAWN
    "apex legends": respawn.apex_legends,
    "apex": respawn.apex_legends,
    "r1": respawn.titanfall,
    "r2": respawn.titanfall2,
    "r5": respawn.apex_legends,
    "tf|2": respawn.titanfall2,
    "titanfall": respawn.titanfall,
    "titanfall 2": respawn.titanfall2,
    "titanfall2": respawn.titanfall2,
    # VALVE
    "orange box": valve.orange_box,
    "tf2": valve.orange_box,  # Team Fortress 2
    "team fortress 2": valve.orange_box,
    "team fortress2": valve.orange_box,
    "vindictus": valve.vindictus}

by_version = {
    # ID SOFTWARE
    id_software.quake3.BSP_VERSION: id_software.quake3,  # 46
    # RESPAWN
    respawn.titanfall.BSP_VERSION: respawn.titanfall,  # 29
    respawn.titanfall2.BSP_VERSION: respawn.titanfall2,  # 37
    respawn.apex_legends.BSP_VERSION: respawn.apex_legends,  # 47
    48: respawn.apex_legends,  # Introduced in Season 7 with Olympus
    # VALVE
    valve.orange_box.BSP_VERSION: valve.orange_box}  # 20
