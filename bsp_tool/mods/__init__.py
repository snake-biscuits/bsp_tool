from . import apex_legends
from . import team_fortress2
from . import titanfall2
from . import vindictus


by_name = {
    "Apex": apex_legends,
    "Apex Legends": apex_legends,
    "TF2": team_fortress2,
    "Team Fortress 2": team_fortress2,
    "Team Fortress2": team_fortress2,
    "Titanfall 2": titanfall2,
    "TitanFall 2": titanfall2,
    "Titanfall2": titanfall2,
    "TitanFall2": titanfall2,
    "Vindictus": vindictus,
    "Orange Box": team_fortress2
    }

by_version = {
    20: team_fortress2, # Orange Box
    # ^ for now all version 20 .bsps are assumed to be from TF2
    # - including vindictus .bsps
    # 29: titanfall,
    titanfall2.bsp_version: titanfall2,
    apex_legends.bsp_version: apex_legends
    }
