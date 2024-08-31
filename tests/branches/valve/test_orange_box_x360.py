from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box_x360

from ... import files


bsps = files.local_bsps(
    ValveBsp, {
        orange_box_x360: [
            "Xbox360/The Orange Box"]})


class TestMethods:
    ...

    # TODO:
    # -- leaves_of_node
    # -- textures_of_brush
    # -- vertices_of_displacement
    # --- NOTE: DisplacementInfo_x360 hasn't been mapped yet
    # -- vertices_of_face
    # -- worldspawn_volume
