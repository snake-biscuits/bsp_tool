__all__ = ["id_software", "infinity_ward", "respawn", "valve",
           "by_name", "by_version"]
from . import id_software
from . import infinity_ward
from . import respawn
from . import valve


by_magic = {
        b"IBSP": [*id_software, *infinity_ward],  # id_software.FILE_MAGIC & infinity_ward.FILE_MAGIC
        b"rBSP": [*respawn],  # respawn.FILE_MAGIC
        b"VBSP": [*valve]}  # valve.FILE_MAGIC

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
    # RESPAWN
    respawn.titanfall2.bsp_version: respawn.titanfall2,  # 37
    respawn.apex_legends.bsp_version: respawn.apex_legends,  # 47
    # VALVE
    valve.orange_box.bsp_version: valve.orange_box}  # 20
