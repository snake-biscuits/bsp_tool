import functools
from typing import List

from ..branches.respawn import titanfall
from ..utils.vector import dot, vec3


def triangle_for(plane: (vec3, float), scale: float = 64) -> List[vec3]:
    """returns a counter-clockwise facing triangle on plane"""
    normal, distance = plane
    # NOTE: normal is assumed to be normalised
    non_parallel = vec3(**{"z" if abs(normal.z) != 1 else "y": -1})
    local_y = (non_parallel * normal).normalised()
    local_x = (local_y * normal).normalised()
    A = normal * distance    # C
    B = A + local_x * scale  # |\
    C = A + local_y * scale  # A-B
    return (A, B, C)


def fstr(x: float) -> str:
    """str(float) without trailing zeroes"""
    x = round(x, 2)
    if x % 1.0 == 0.0:
        return str(int(x))
    return str(x)


texture_axes = {vec3(x=1): (vec3(y=1), vec3(z=-1)),  # west / east wall
                vec3(y=1): (vec3(x=1), vec3(z=-1)),  # south / north wall
                vec3(z=1): (vec3(x=1), vec3(y=-1))}  # floor / cieling


# https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/utils/vbsp/textures.cpp#L306
def world_texture_vectors(normal: vec3) -> (vec3, vec3):
    """Gets the default world aligned texture vectors (vec3 only) for a given surface normal"""
    best_dot, best_axis = 0, vec3(z=1)
    for world_axis in [vec3(z=1), vec3(y=1), vec3(x=1)]:  # matching Source tiebreaker preference order
        world_dot = abs(dot(normal, world_axis))
        if world_dot > best_dot:
            best_dot, best_axis = world_dot, world_axis
    return texture_axes[best_axis]
# TODO: use this function to match BrushSideTextureVector(s)


def face_texture_vectors(normal: vec3) -> (vec3, vec3):
    """Gets the default face aligned texture vectors (vec3 only) for a given surface normal"""
    # NOTE: based on an assumption that world == face aligned on +ve normals
    flip_S = False
    best_dot, best_axis = 0, vec3(z=1)
    for world_axis in [vec3(z=1), vec3(y=1), vec3(x=1)]:  # matching Source tiebreaker preference order
        world_dot = dot(normal, world_axis)
        if abs(world_dot) > best_dot:
            flip_S = False
            best_dot, best_axis = abs(world_dot), world_axis
            if world_dot < 0:
                flip_S = True
    S, T = texture_axes[best_axis]
    S = -S if flip_S else S
    return S, T


def brush_valve_220(bsp, brush: titanfall.Brush, editor: str = "TrenchBroom", offset: vec3 = vec3()) -> List[str]:
    editor = editor.lower()
    # NOTE: AABB only!
    out = ["{\n"]
    origin = -vec3(*brush.origin)  # inverted for some reason? prob bad math
    extents = vec3(*brush.extents)
    mins = origin - extents
    maxs = origin + extents
    brush_planes = list()  # [(normal: vec3, distance: float)]
    # assemble base brush sides in order: +X -X +Y -Y +Z -Z
    for axis, min_dist, max_dist in zip("xyz", mins, maxs):
        brush_planes.append((vec3(**{axis: 1}), -max_dist))  # +ve axis plane
        brush_planes.append((vec3(**{axis: -1}), min_dist))  # -ve axis plane
    first_brush_side = brush.index * 6 + brush.brush_side_offset
    # add additional planes
    # TODO: some brushes become invalid, might be slicing with bad bevel planes
    for i in range(brush.num_plane_offsets):
        offset = brush.brush_side_offset + i
        brush_plane_offset = offset - bsp.CM_BRUSH_SIDE_PLANE_OFFSETS[offset]
        normal, distance = bsp.PLANES[bsp.CM_GRID.first_brush_plane + brush_plane_offset]
        brush_planes.append((-normal, -distance))
    num_brush_sides = 6 + brush.num_plane_offsets
    for j in range(num_brush_sides):
        properties = bsp.CM_BRUSH_SIDE_PROPERTIES[j + first_brush_side]
        # if properties & titanfall.BrushSideProperty.DISCARD:
        #     continue
        tri = [p + offset for p in triangle_for(brush_planes[j])]
        texdata = bsp.TEXTURE_DATA[properties & titanfall.BrushSideProperty.MASK_TEXTURE_DATA]
        texture = bsp.TEXTURE_DATA_STRING_DATA[texdata.name_index].replace("\\", "/").lower()
        tv = bsp.CM_BRUSH_SIDE_TEXTURE_VECTORS[first_brush_side + j]
        tv_str = " ".join([" ".join(["[", *map(fstr, v), "]"]) for v in tv])
        # ^ (x, y, z, offset) -> "[ x y z offset ]"  x2 [S,T]
        tri_str = " ".join([" ".join(["(", *map(fstr, p), ")"]) for p in tri])
        # ^ (x, y, z) -> "( x y z )"  x3 [A,B,C]
        scale = 4 if editor.lower() == "trenchbroom" else 1
        out.append(" ".join([tri_str, texture, tv_str, f"0 {scale} {scale}\n"]))
        # ^ "( A ) ( B ) ( C ) TEXTURE [ S ] [ T ] rotation scale_X scale_Y"
    out.append("}\n")
    return out


supported_editors = ["TrenchBroom", "JACK", "MRVN",  # .map (Valve220)
                     "Hammer", "Hammer++"]  # .vmf (TODO)
supported_editors = [e.lower() for e in supported_editors]


# NOTE: only TrenchBroom & J.A.C.K. seem to like Valve220
# -- J.A.C.K. can convert to other formats including .vmf
# https://quakewiki.org/wiki/Quake_Map_Format
def decompile(bsp, map_filename: str, editor: str = "TrenchBroom"):
    """Converts a Titanfall .bsp into a Valve 220 .map file"""
    assert editor.lower() in supported_editors, f"editor: {editor} is not supported!"
    out = ["// Game: Generic\n// Format: Valve\n",  # TrenchBroom header
           '// entity 0\n{\n',  # worldspawn
           *[f'"{k}" "{v}"\n' for k, v in bsp.ENTITIES[0].items()]]
    # entity brush groups
    # TODO: some brushes / entities do not get grouped
    # -- CMGeoSet might include a count?
    # -- investigate func_breakable_surf & func_window_hint
    entity_brushes = dict()
    for i, grid_cell in enumerate(bsp.CM_GRID_CELLS[-len(bsp.MODELS):]):
        start = end = grid_cell.first_geo_set
        end += grid_cell.num_geo_sets
        entity_brushes[i] = {gs.child.index for gs in bsp.CM_GEO_SETS[start:end] if gs.child.type == 0}
    entity_brushes.pop(0)
    if len(entity_brushes) != 0:
        non_worldspawn = functools.reduce(lambda a, b: a.union(b), entity_brushes.values())
    else:
        non_worldspawn = set()
    # world brushes
    for i, brush in enumerate([b for i, b in enumerate(bsp.CM_BRUSHES) if i not in non_worldspawn]):
        out.extend([f"// brush {i}" + "\n", *brush_valve_220(bsp, brush, editor)])
    out.append("}\n")  # end worldspawn
    # entities
    # NOTE: *.bsp.0000.bsp_lump + brush entities; skipping .ents to keep filesize manageable
    included_ents = bsp.ENTITIES[1:]
    for ent_file in ("env", "fx", "script", "snd", "spawn"):
        included_ents.extend([e for e in getattr(bsp, f"ENTITIES_{ent_file}") if e.get("model", "").startswith("*")])
    for i, entity in enumerate(included_ents):
        brushes = list()
        if entity.get("model", "").startswith("*"):
            for j, brush_index in enumerate(entity_brushes[int(entity["model"][1:])]):
                brushes.append(f"// brush {j}" + "\n")
                brush = bsp.CM_BRUSHES[brush_index]
                # NOTE: brush planes may be relative to centered brush, might break this hack
                # NOTE: func_breakable_surf has * model & brushes, but no origin
                origin = vec3()
                if editor.lower() != "mrvn":  # NetRadiant / MRVN-radiant offsets brushes automatically
                    origin = vec3(*entity.get("origin", "0 0 0").split())
                brushes.extend(brush_valve_220(bsp, brush, editor, origin))
        keyvalues = [f'"{k}" "{v}"\n' for k, v in entity.items() if not v.startswith("*")]  # added by compiler
        out.extend((f"// entity {i + 1}", "\n{\n", *keyvalues, *brushes, "}\n"))
    with open(map_filename, "w") as map_file:
        map_file.write("".join(out))
