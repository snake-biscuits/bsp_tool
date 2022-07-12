import bsp_tool.branches.respawn.titanfall as r1
from bsp_tool.branches.vector import dot, vec3


def texvec_to_local_z(tv: r1.TextureVector) -> (vec3, float):
    # NOTE: assuming square and even projection
    local_x = vec3(tv.s.x, tv.s.y, tv.s.z)
    local_y = vec3(tv.t.x, tv.t.y, tv.t.z)
    local_z = local_x * local_y
    return local_z


def plane_range(normal: vec3, brush: r1.Brush) -> (float, float):
    mins = vec3(*brush.origin) - vec3(*brush.extents)
    maxs = vec3(*brush.origin) + vec3(*brush.extents)
    xs = (mins.x, maxs.x)
    ys = (mins.y, maxs.y)
    zs = (mins.z, maxs.z)
    min_distance = dot(normal, mins)
    max_distance = min_distance
    for i in range(1, 8):
        P = vec3(xs[(i & 0b100) >> 2], ys[(i & 0b010) >> 1], zs[i & 0b001])
        distance = dot(normal, P)
        min_distance = min(distance, min_distance)
        max_distance = max(distance, max_distance)
    return min_distance, max_distance


def fuzzy_match(plane: (vec3, float), normal: vec3, min_distance: float, max_distance: float, delta: float = 0.05) -> bool:
    if not normal.x - delta < plane.normal.x > normal.x + delta:
        return False
    if not normal.y - delta < plane.normal.y > normal.y + delta:
        return False
    if not normal.z - delta < plane.normal.z > normal.z + delta:
        return False
    if not min_distance - delta < plane.distance < max_distance + delta:
        return False
    return True
