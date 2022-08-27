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


def behind_plane(point: vec3, plane: (vec3, float), delta: float = 0.25):
    # NOTE: ONLY return True if 'point' is not on or in front of 'plane'
    # NOTE: on plane = not behind plane
    # -- this means bevel planes & axial planes are considered to intersect brushes
    # TODO: planes on axial bounds are being ignored
    # -- we need to get a pass & fail for these borderline cases to work
    normal, distance = plane
    dot_normal = dot(point, normal)
    # maybe just use math.isclose...
    case_a = bool(dot_normal + delta < distance + delta)
    case_b = bool(dot_normal - delta < distance + delta)
    case_c = bool(dot_normal + delta < distance - delta)
    case_d = bool(dot_normal - delta < distance - delta)
    case_e = dot_normal != distance
    return case_a and case_b and case_c and case_d and case_e


def planes_intersecting_brush(bsp: RespawnBsp, brush_index: int) -> List[int]:
    out = list()
    brush = bsp.CM_BRUSHES[brush_index]
    brush_verts = brush_aabb_vertices(brush)
    for i, plane in enumerate(bsp.PLANES):
        plane = (vec3(*plane.normal), plane.distance)
        # handle axial plane edge case here?
        if {behind_plane(v, plane) for v in brush_verts} == {True, False}:
            # NOTE: all false for axial overlap
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


if __name__ == "__main__":
    # testing axial & bevel planes are grouped to brushes correctly
    import functools
    import os

    import bsp_tool

    def union(*sets: List[set]) -> set:
        return functools.reduce(lambda a, b: a.union(b), sets)

    if os.uname().sysname == "Linux":
        r2l = bsp_tool.load_bsp("/home/bikkie/Documents/Mod/Titanfall2/maps/mp_lobby.bsp")
    else:
        r2l = bsp_tool.load_bsp("E:/Mod/Titanfall2/maps/mp_lobby.bsp")
    # intersect groups
    ig_0 = set(planes_intersecting_brush(r2l, 0))  # 640x640x16 @ (0, 0, -8)
    ig_1 = set(planes_intersecting_brush(r2l, 1))  # 48x48x32 @ (0, -256, 16)
    ig_2 = set(planes_intersecting_brush(r2l, 2))  # 3072x3072x3072 @ (0, 0, 0)
    # plane groups
    pg_0 = {0, 1, 2, 3, 4, 5}  # Brush 2 axial bounds
    pg_1 = {6, 7, 8, 9}        # Brush 0 bevel planes
    pg_2 = {10, 11, 12, 13}    # Brush 1 bevel planes
    pg_3 = {14, 15, 16, 17}    # Brush 2 bevel planes
    # all planes should be accounted for
    assert ig_0.intersection(pg_1) == pg_1, "brush 0: missed brush 0's bevel planes"
    assert ig_0.intersection(pg_2) == pg_2, "brush 0: missed brush 1's bevel planes"
    assert ig_0 == union(pg_1, pg_2), "brush 0: includes some incorrect planes"
    assert ig_1 == pg_2, "brush 1: missed brush 1's bevel planes"
    assert ig_2.intersection(pg_0) == pg_0, "brush 2: missed brush 2's axial bounds"
    assert ig_2.intersection(pg_1) == pg_1, "brush 2: missed brush 0's bevel planes"
    assert ig_2.intersection(pg_2) == pg_2, "brush 2: missed brush 1's bevel planes"
    assert ig_2.intersection(pg_3) == pg_3, "brush 2: missed brush 2's bevel planes"
