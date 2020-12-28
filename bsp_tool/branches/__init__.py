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
    "QuakeIII": id_software.quake3,
    "Quake 3": id_software.quake3,
    "Quake3": id_software.quake3,
    # RESPAWN
    "Apex Legends": respawn.apex_legends,
    "Apex": respawn.apex_legends,
    "TF|2": respawn.titanfall2,
    "TitanFall 2": respawn.titanfall2,
    "TitanFall2": respawn.titanfall2,
    # VALVE
    "Orange Box": valve.orange_box,
    "TF2": valve.orange_box,  # Team Fortress 2
    "Team Fortress 2": valve.orange_box,
    "Team Fortress2": valve.orange_box,
    "Vindictus": valve.vindictus}
# make sure to match case-insesitively!

by_version = {
    # ID SOFTWARE
    id_software.quake3.BSP_VERSION: id_software.quake3,  # 46
    # RESPAWN
    respawn.titanfall2.BSP_VERSION: respawn.titanfall2,  # 37
    respawn.apex_legends.BSP_VERSION: respawn.apex_legends,  # 47
    # VALVE
    valve.orange_box.BSP_VERSION: valve.orange_box}  # 20
