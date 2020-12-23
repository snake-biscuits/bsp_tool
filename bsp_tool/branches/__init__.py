from .respawn import apex_legends, titanfall2
from .valve import orange_box, vindictus


by_name = {
    # RESPAWN
    "Apex Legends": apex_legends,
    "Apex": apex_legends,
    "TF|2": titanfall2,
    "TitanFall 2": titanfall2,
    "TitanFall2": titanfall2,
    # VALVE
    "Orange Box": orange_box,
    "TF2": orange_box,  # Team Fortress 2
    "Team Fortress 2": orange_box,
    "Team Fortress2": orange_box,
    "Vindictus": vindictus}
# make sure to use match case-insesitively!

by_version = {
    # RESPAWN
    titanfall2.bsp_version: titanfall2,  # 37
    apex_legends.bsp_version: apex_legends,  # 47
    # VALVE
    orange_box.bsp_version: orange_box}  # 20
