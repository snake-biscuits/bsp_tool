from typing import List

from ..branches.vector import dot, vec3


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


# TODO: figure out why planes / coords are all inverted
# NOTE: only TrenchBroom & J.A.C.K. seem to like Valve220
# -- J.A.C.K. can convert to other formats including .vmf
# https://quakewiki.org/wiki/Quake_Map_Format
def decompile(bsp, map_filename: str):
    """Converts a Titanfall .bsp into a Valve 220 .map file"""
    out = ["// Game: Generic\n// Format: Valve\n",
           '// entity 0\n{\n',
           *[f'"{k}" "{v}"\n' for k, v in bsp.ENTITIES[0].items()]]
    first_brush_side = 0
    # cur_plane_offset = 0
    # PLANE_OFFSETS = getattr(bsp, "CM_BRUSH_SIDE_PLANE_OFFSETS", [0])
    # PLANES = [(-vec3(*p.normal), -p.distance) for p in bsp.PLANES[-max(PLANE_OFFSETS) - 1:]]
    # NOTE: had to flip planes here, really feel like I messed up the math somewhere (CW vs. CCW faces?)
    for i, brush in enumerate(bsp.CM_BRUSHES):
        out.append(f"// brush {i}" + "\n{\n")
        origin = -vec3(*brush.origin)  # inverted for some reason? prob bad math
        extents = vec3(*brush.extents)
        mins = origin - extents
        maxs = origin + extents
        brush_planes = list()
        # ^ [(normal: vec3, distance: float)]
        # assemble base brush sides in order: +X -X +Y -Y +Z -Z
        for axis, min_, max_ in zip("xyz", mins, maxs):
            brush_planes.append((vec3(**{axis: 1}), -max_))  # +ve axis
            brush_planes.append((vec3(**{axis: -1}), min_))  # -ve axis
        # TODO: check order of generated brushsides lines up w/ texture projections
        # TODO: identify non-AABB brushes
        # TODO: get indexed planes for additional brush sides
        # -- unsure how exactly PLANES lump is indexed
        # --- brush.num_plane_offsets -> CM_BRUSH_SIDE_PLANE_OFFSETS -?> PLANES
        # --- definitely some offset calculations involved, like MATERIAL_SORT
        # -- around 50% of PLANES are bevel planes; very few axial planes
        # -- r2/mp_lobby: only rendered brushes get axial planes
        # --- unrendered brushes only get bevel planes
        # --- all brushes in r2/mp_lobby are AABB brushes
        # NOTE: failed plane indexing
        # last_plane_offset = cur_plane_offset + brush.num_plane_offsets
        # brush_plane_offsets = PLANE_OFFSETS[cur_plane_offset:last_plane_offset]
        # brush_planes.extend([PLANES[i] for i in brush_plane_offsets])
        num_brush_sides = 6
        # cur_plane_offset = last_plane_offset
        for j in range(num_brush_sides):
            tri = triangle_for(brush_planes[j])
            j += first_brush_side  # for indexing BRUSH_SIDE_PROPERTIES / BRUSH_SIDE_TEXTURE_VECTORS
            # prop = bsp.CM_BRUSH_SIDE_PROPERTIES[j]
            # texdata = bsp.TEXTURE_DATA[...]
            # texture = bsp.TEXTURE_DATA_STRING_DATA[texdata.name_index]
            tv = bsp.CM_BRUSH_SIDE_TEXTURE_VECTORS[j]
            tv_str = " ".join([" ".join(["[", *map(fstr, v), "]"]) for v in tv])
            # ^ (x, y, z, offset) -> "[ x y z offset ]"  x2 [S,T]
            tri_str = " ".join([" ".join(["(", *map(fstr, p), ")"]) for p in tri])
            # ^ (x, y, z) -> "( x y z )"  x3 [A,B,C]
            # TODO: determine texture; using TrenchBroom default texture for now
            # -- current theory is that BrushSideProperties indexes TextureData, somehow
            out.append(" ".join([tri_str, "__TB_empty", tv_str, "0 4 4\n"]))
            # ^ "( A ) ( B ) ( C ) TEXTURE [ S ] [ T ] rotation scale_X scale_Y"  # valve 220 texture format
        first_brush_side += num_brush_sides + brush.num_plane_offsets
        out.append("}\n")
    out.append("}\n")
    for i, entity in enumerate(bsp.ENTITIES[1:]):
        # NOTE: .bsp entity lump only
        # TODO: identify brush entities in Titanfall 2 entities
        # TODO: match brush entities to brushes
        out.extend((f"// entity {i + 1}", "\n{\n", *[f'"{k}" "{v}"\n' for k, v in entity.items()], "}\n"))
    with open(map_filename, "w") as map_file:
        map_file.write("".join(out))
