import sys

import bsp_tool
from bsp_tool.extensions import upgrade


for map_name in sys.argv[1:]:
    r1_bsp = bsp_tool.load_bsp(map_name)
    assert isinstance(r1_bsp, bsp_tool.RespawnBsp) and r1_bsp.branch is bsp_tool.branches.respawn.titanfall
    upgrade.r1_to_r2(r1_bsp)  # new r2 copy will be dumped in bsp_tool dir
