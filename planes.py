import math
from typing import Dict, List

import bsp_tool.branches.respawn.titanfall as r1
from bsp_tool.branches.vector import dot, vec3
from bsp_tool.respawn import RespawnBsp


half_sqrt_2 = math.sqrt(2) / 2

# use w/ vec3_match to get a quick vector name
axes = {vec3(x=1): "+X", vec3(x=-1): "-X",
        vec3(y=1): "+Y", vec3(y=-1): "-Y",
        vec3(z=1): "+Z", vec3(z=-1): "-Z",
        vec3(x=half_sqrt_2, y=half_sqrt_2): "+X+Y",
        vec3(x=-half_sqrt_2, y=half_sqrt_2): "-X+Y",
        vec3(x=half_sqrt_2, y=-half_sqrt_2): "+X-Y",
        vec3(x=-half_sqrt_2, y=-half_sqrt_2): "-X-Y"}


def texvec_to_local_z(tv: r1.TextureVector) -> vec3:
    # NOTE: assuming square and even projection
    local_x = vec3(tv.s.x, tv.s.y, tv.s.z)
    local_y = vec3(tv.t.x, tv.t.y, tv.t.z)
    local_z = local_x * local_y
    return local_z


def brush_aabb_vertices(brush: r1.Brush) -> List[vec3]:
    # NOTE: out[0] is mins; out[-1] is maxs
    out = list()
    mins = vec3(*brush.origin) - vec3(*brush.extents)
    maxs = vec3(*brush.origin) + vec3(*brush.extents)
    xs = (mins.x, maxs.x)
    ys = (mins.y, maxs.y)
    zs = (mins.z, maxs.z)
    for i in range(8):
        out.append(vec3(xs[(i & 0b100) >> 2], ys[(i & 0b010) >> 1], zs[i & 0b001]))
    return out


def plane_range(normal: vec3, brush: r1.Brush) -> (float, float):
    verts = brush_aabb_vertices(brush)
    min_distance = dot(normal, verts[0])
    max_distance = min_distance
    for vertex in verts[1:]:
        distance = dot(normal, vertex)
        min_distance = min(distance, min_distance)
        max_distance = max(distance, max_distance)
    return min_distance, max_distance


def vec3_match(v1: vec3, v2: vec3, delta: float = 0.05) -> bool:
    for axis in "xyz":
        if not math.isclose(getattr(v1, axis), getattr(v2, axis), abs_tol=delta):
            return False
    return True


def plane_match(plane: r1.Plane, normal: vec3, min_dist: float, max_dist: float, delta: float = 0.05) -> bool:
    if not vec3_match(normal, plane.normal):
        return False
    if not min_dist - delta <= plane.distance <= max_dist + delta:
        return False
    return True


def behind_plane(point: vec3, plane: (vec3, float), delta: float = 0.05):
    # NOTE: on plane = not behind plane
    # -- this means bevel planes & axial planes are considered to intersect brushes
    normal, distance = plane
    dot_normal = dot(point, normal)
    pos_delta = bool(dot_normal <= distance + delta)
    neg_delta = bool(dot_normal <= distance - delta)
    return pos_delta and neg_delta  # {True, False} -> False if on plane


def planes_intersecting_brush(bsp: RespawnBsp, brush_index: int) -> List[int]:
    out = list()
    brush = bsp.CM_BRUSHES[brush_index]
    for i, plane in enumerate(bsp.PLANES):
        plane = (vec3(*plane.normal), plane.distance)
        if {behind_plane(v, plane) for v in brush_aabb_vertices(brush)} == {True, False}:
            out.append(i)
    return out


def brush_potential_planes(bsp: RespawnBsp, brush_index: int) -> Dict[int, List[int]]:
    # TODO: assert intersecting brush w/ plane doesn't shrink the AABB
    out = dict()
    # ^ {side_index: [plane_index]}
    brush = bsp.CM_BRUSHES[brush_index]
    planes = planes_intersecting_brush(bsp, brush_index)
    # TOOD: test axials against bounds for the first 6 sides
    for i, side_tv in enumerate(bsp.get_brush_sides(brush_index)["texture_vectors"]):
        out[i] = list()
        normal = texvec_to_local_z(side_tv)
        min_dist, max_dist = plane_range(normal, brush)
        for j in planes:
            if plane_match(bsp.PLANES[j], normal, min_dist, max_dist):
                out[i].append(j)
    return out
