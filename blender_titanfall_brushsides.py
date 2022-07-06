import importlib
import sys

import bpy

sys.path.append("/home/bikkie/Documents/Code/GitHub/bsp_tool")
import bsp_tool  # noqa E402


importlib.reload(bsp_tool)


bsp = bsp_tool.load_bsp("/home/bikkie/Documents/Mod/Titanfall/maps/mp_box.bsp")

bpy.context.scene.tool_settings.transform_pivot_point = "CURSOR"

bpy.ops.object.empty_add(type="ARROWS", align="WORLD",
                         location=(0, 0, 0), scale=(128, 128, 128))

empty_object = bpy.context.selected_objects[0]

# TODO: linked-duplicate a base object to limit filesize
for plane in bsp.PLANES:
    bpy.ops.mesh.primitive_plane_add(size=2, enter_editmode=False,
                                     align="WORLD",
                                     location=tuple(plane.normal),
                                     scale=(1, 1, 1))
    plane_object = bpy.context.selected_objects[0]
    # NOTE: damped track means we can't really match sidedness
    bpy.ops.object.constraint_add(type="DAMPED_TRACK")
    bpy.context.object.constraints["Damped Track"].target = empty_object
    bpy.context.object.constraints["Damped Track"].track_axis = "TRACK_Z" if plane.distance < 0 else "TRACK_NEGATIVE_Z"
    bpy.ops.transform.resize(value=(plane.distance,) * 3,
                             center_override=(0, 0, 0),
                             orient_type="GLOBAL")
    # TODO: normalise the scale after applying plane distance
    # -- then scale up to some default (3680-ish)

for brush in bsp.CM_BRUSHES:
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align="WORLD",
                                    location=tuple(brush.origin),
                                    scale=tuple(brush.extents))

del bsp  # need to free
