import bsp_tool
from bsp_tool.extensions.decompile_rbsp import decompile


box = bsp_tool.load_bsp("E:/Mod/TitanfallOnline/maps/mp_box.bsp")
decompile(box, "mp_box.map")
