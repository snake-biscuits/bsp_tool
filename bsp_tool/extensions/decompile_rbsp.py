from typing import Dict, List

from ..branches.respawn import titanfall
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


# NOTE: matching in-engine texture paths to in-wad texture names
# TODO: use per-wad .json files
# mp_box_wad = {"TOOLS\\TOOLSSKYBOX": "skybox",
#               "TOOLS\\TOOLSNODRAW": "nodraw",
#               "WORLD\\FLOORS\\IMC_FLOOR_LARGE_PANEL_01": "imc_lrgpan_1",
#               "WORLD\\METAL\\METAL_GREY_WALLPANEL_01": "wallpanel_1",
#               "WORLD\\METAL\\METAL_DIAMOND_PLATE_LARGE_CLEAN": "dia_plt_lrg",
#               "WORLD\\DEV\\DEV_GROUND_512": "dev_ground_512",
#               "WORLD\\DEV\\DEV_WHITE_512": "dev_white_512",
#               "WORLD\\HAVEN\\WALLS\\RED_WALL_01": "red_wall_1",
#               "WORLD\\PLASTIC\\PLASTIC_BLUE": "plastic_blue",
#               "WORLD\\CONCRETE\\CONCRETE_ALLEY_01": "concrete",
#               "WORLD\\DEV\\DEV_ORANGE_512": "dev_orange_512",
#               "WORLD\\DEV\\WEAPON_RANGE_TARGET": "range_target",
#               "world\\signs\\sign_numbers_yellow_plastic_gasoline": "numbers",
#               "TOOLS\\TOOLSCLIP_HUMAN_CLIMBABLE": "clip_climb",
#               "WORLD\\METAL\\BEAM_IMC_METAL_GRAY_MAT": "imc_beam",
#               "TOOLS\\TOOLSTRIGGER": "trigger"}


# TODO: figure out why planes / coords are all inverted
# NOTE: only TrenchBroom & J.A.C.K. seem to like Valve220
# -- J.A.C.K. can convert to other formats including .vmf
# https://quakewiki.org/wiki/Quake_Map_Format
def decompile(bsp, map_filename: str, wad_dict: Dict[str, str] = dict()):
    """Converts a Titanfall .bsp into a Valve 220 .map file"""
    # NOTE: game is Quake, not Generic because we want to use .wad textures
    # NOTE: wad_dict should map texture filepaths to wad texture names
    out = ["// Game: Quake\n// Format: Valve\n",
           '// entity 0\n{\n',
           *[f'"{k}" "{v}"\n' for k, v in bsp.ENTITIES[0].items()]]
    first_brush_side = 0
    # HACK: r1 mp_lobby fix
    axes = (vec3(x=1), vec3(x=-1), vec3(y=1), vec3(y=-1), vec3(z=1), vec3(z=-1))
    plane_index = [i for i, p in enumerate(bsp.PLANES) if vec3(*p.normal) not in axes][0]
    PLANES = [(-vec3(*p.normal), -p.distance) for p in bsp.PLANES]
    plane_offset_index = 0  # index into bsp.CM_BRUSH_SIDE_PLANE_OFFSETS
    for i, brush in enumerate(bsp.CM_BRUSHES):
        # NOTE: had to flip planes here, really feel like I messed up the math somewhere (CW vs. CCW faces?)
        out.append(f"// brush {i}" + "\n{\n")
        origin = -vec3(*brush.origin)  # inverted for some reason? prob bad math
        extents = vec3(*brush.extents)
        mins = origin - extents
        maxs = origin + extents
        brush_planes = list()
        # ^ [(normal: vec3, distance: float)]
        # assemble base brush sides in order: +X -X +Y -Y +Z -Z
        for axis, min_dist, max_dist in zip("xyz", mins, maxs):
            brush_planes.append((vec3(**{axis: 1}), -max_dist))  # +ve axis plane
            brush_planes.append((vec3(**{axis: -1}), min_dist))  # -ve axis plane
        num_brush_sides = 6 + brush.num_plane_offsets
        for j in range(num_brush_sides):
            properties = bsp.CM_BRUSH_SIDE_PROPERTIES[j + first_brush_side]
            if j < 6:  # AABB plane (generated)
                tri = triangle_for(brush_planes[j])
            else:  # clip plane (indexed)
                # NOTE: this math works for mp_box, but not many other maps
                # NOTE: could brush.unknown_2 be used instead of accumulating?
                # -- e.g. brush.first_brush side = brush.index * 6 + brush.unknown_2 ?
                # would explain why length seems to match len(PLANE_OFFSETS) [not every map meets these criteria!]
                plane_offset = bsp.CM_BRUSH_SIDE_PLANE_OFFSETS[plane_offset_index]
                plane_offset_index += 1
                # print(f"BRUSH[{i}] SIDE #{j}: PLANES[{plane_index - plane_offset}] (-{plane_offset})", end=" ")
                # print("[DISCARDED]" if properties & titanfall.BrushSideProperty.DISCARD else "")
                tri = triangle_for(PLANES[plane_index - plane_offset])
                plane_index += 1
            if properties & titanfall.BrushSideProperty.DISCARD:
                continue  # this side doesn't have a polygon, only used for physics / vis tests
            texdata = bsp.TEXTURE_DATA[properties & titanfall.BrushSideProperty.MASK_TEXTURE_DATA]
            texture = bsp.TEXTURE_DATA_STRING_DATA[texdata.name_index].replace("\\", "/").lower()
            texture = wad_dict.get(texture, texture)
            # NOTE: .wad textures have a 15 char length limit (16 chars + '\0')
            # -- if using a .wad, provide wad_dict. e.g. {"tools/toolsnodraw": "nodraw"}
            tv = bsp.CM_BRUSH_SIDE_TEXTURE_VECTORS[first_brush_side + j]
            tv_str = " ".join([" ".join(["[", *map(fstr, v), "]"]) for v in tv])
            # ^ (x, y, z, offset) -> "[ x y z offset ]"  x2 [S,T]
            tri_str = " ".join([" ".join(["(", *map(fstr, p), ")"]) for p in tri])
            # ^ (x, y, z) -> "( x y z )"  x3 [A,B,C]
            out.append(" ".join([tri_str, texture, tv_str, "0 4 4\n"]))
            # ^ "( A ) ( B ) ( C ) TEXTURE [ S ] [ T ] rotation scale_X scale_Y"  # valve 220 texture format
        first_brush_side += num_brush_sides
        out.append("}\n")
    out.append("}\n")
    for i, entity in enumerate(bsp.ENTITIES[1:]):
        # NOTE: .bsp entity lump (*.bsp.0000.bsp_lump) only
        # TODO: identify brush entities in Titanfall 2 entities
        # -- then match brush entities to brushes; (is ent origin enough to position correctly?)
        out.extend((f"// entity {i + 1}", "\n{\n", *[f'"{k}" "{v}"\n' for k, v in entity.items()], "}\n"))
    with open(map_filename, "w") as map_file:
        map_file.write("".join(out))
