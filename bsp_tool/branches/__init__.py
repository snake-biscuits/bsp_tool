from . import apex_legends
from . import orange_box
from . import titanfall2
from . import vindictus


by_name = {
    "Apex": apex_legends,
    "Apex Legends": apex_legends,
    "TF2": orange_box,
    "Team Fortress 2": orange_box,
    "Team Fortress2": orange_box,
    "Titanfall 2": titanfall2,
    "TitanFall 2": titanfall2,
    "Titanfall2": titanfall2,
    "TitanFall2": titanfall2,
    "Vindictus": vindictus,
    "Orange Box": orange_box
    }

by_version = {
    orange_box.bsp_version: orange_box,  # 20 (Orange Box)
    # vindictus is the same version as tf2,
    # but multiple games use a similar format to tf2
    titanfall2.bsp_version: titanfall2,  # 37
    apex_legends.bsp_version: apex_legends  # 47
    }
