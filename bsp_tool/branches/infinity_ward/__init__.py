"""Infinity Ward created the Call of Duty Franchise, built on the idTech3 (RTCW) engine.
.bsp format shares IdTech's b'IBSP' FILE_MAGIC"""
from . import call_of_duty1  # (.bsp in .pk3)
from . import call_of_duty2  # (.d3dbsp in .iwd)
from . import call_of_duty4  # (.d3dbsp in .ff)
# TODO: blops3

# NOTE: I'm not buying any CoDs until Kotick is gone


scripts = [call_of_duty1, call_of_duty2, call_of_duty4]
