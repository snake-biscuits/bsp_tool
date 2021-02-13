from . import base


class D3DBsp(base.Bsp):
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_1:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_2:_d3dbsp
    # https://wiki.zeroy.com/index.php?title=Call_of_Duty_4:_d3dbsp
    FILE_MAGIC = b"IBSP"
    # NOTE: Call of Duty 1 has .bsp files in .pk3 archives
    # -- later games instead use .d3dbsp in .iwd archives
