"""Infinity Ward created the Call of Duty Franchise, built on the idTech3 (RTCW) engine.
.bsp format shares IdTech's b'IBSP' FILE_MAGIC"""
from . import call_of_duty1_demo  # (.bsp in .pk3)
from . import call_of_duty1  # (.bsp in .pk3)
from . import call_of_duty2  # (.d3dbsp in .iwd)
from . import modern_warfare  # (.d3dbsp in .ff)
# https://github.com/SE2Dev/D3DBSP_Converter
# NOTE: world_at_war is v31 & black_ops is v45
# -- neither overlaps with other IdTech titles, but only barely (both are also D3DBsp)
# TODO: blops3

# NOTE: I'm not buying any CoDs until Kotick is gone


scripts = [call_of_duty1_demo, call_of_duty1, call_of_duty2, modern_warfare]
