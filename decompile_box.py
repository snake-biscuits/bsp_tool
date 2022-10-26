import os

import bsp_tool
from bsp_tool.extensions.decompile_rbsp import decompile


game_dir = "E:/Mod"
if os.uname().sysname == "Linux":
    game_dir = "/media/bikkie/3964-3935/Mod"
box = bsp_tool.load_bsp(f"{game_dir}/TitanfallOnline/maps/mp_box.bsp")
decompile(box, "mp_box.map")
