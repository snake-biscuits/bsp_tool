from typing import Dict, List

import bsp_tool.branches.respawn.titanfall as r1
from bsp_tool.branches.vector import dot, vec3
from bsp_tool.respawn import RespawnBsp


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


def fuzzy_match(plane: r1.Plane, normal: vec3, min_dist: float, max_dist: float, delta: float = 0.05) -> bool:
    if not normal.x - delta < plane.normal.x > normal.x + delta:
        return False
    if not normal.y - delta < plane.normal.y > normal.y + delta:
        return False
    if not normal.z - delta < plane.normal.z > normal.z + delta:
        return False
    if not min_dist - delta < plane.distance < max_dist + delta:
        return False
    return True


def behind_plane(point: vec3, plane: (vec3, float)):
    normal, distance = plane
    return bool(dot(point, normal) <= distance + 0.05)


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
    for i, side_tv in enumerate(bsp.get_brush_sides(brush_index)["texture_vectors"][6:]):
        i += 6
        out[i] = list()
        normal = texvec_to_local_z(side_tv)
        min_dist, max_dist = plane_range(normal, brush)
        for j in planes:
            if fuzzy_match(bsp.PLANES[j], normal, min_dist, max_dist):
                out[i].append(j)
    return out
