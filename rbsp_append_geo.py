from typing import List

import bsp_tool


r1 = bsp_tool.branches.respawn.titanfall

TITANFALL = "E:/Mod/Titanfall/maps/"
TITANFALL_ONLINE = "E:/Mod/TitanfallOnline/maps/"
bsp = bsp_tool.load_bsp(TITANFALL_ONLINE + "mp_box.bsp")

# NOTE: selected_objects may not all have the same center
obj = bpy.context.selected_objects[0]
entity = dict(classname="func_brush",
           model=f"*{len(bsp.MODELS)}",
           targetname="orange_tower",
           origin=f"{obj.location.x} {obj.location.y} {obj.location.z}",
           # loose defaults:
           solidbsp=0, shadowdepthnocache=0,
           invert_exclusion=0, drawinfastreflection=0,
           disableshadows=0, disableshadowdepth=0,
           disableflashlight=0, startdisabled=0,
           spawnflags=2, solidity=0, vrad_brush_cast_shadows=0)

# NOTE: obj. bound_box
bound_points = itertools.chain(o.bound_box for o in bpy.context.selected_objects)
xs, ys, zs = {P[:3] for P in bound_points}
model = r1.Model(mins=[min(xs), min(ys), min(zs)],
              maxs=[max(xs), max(ys), max(zs)],
              first_mesh=len(bsp.MODELS),
              num_meshes=len(bpy.context.selected_objects))

#              /-> MaterialSort -> TextureData -> TextureDataStringTable -> TextureDataStringData
# Model -> Mesh -> MeshIndices -\-> VertexReservedX -> Vertex
#              \-> .flags (VertexReservedX)       \--> VertexNormal
#                                                  \-> .uv

for obj in bpy.context.selected_objects:
    texture_name = obj.material_slots[0].name
    bsp.TEXTURE_DATA_STRING_TABLE.append(len(bsp.TEXTURE_DATA_STRING_TABLE))
    bsp.TEXTURE_DATA_STRING_DATA.append(texture_name)
    
    texture_data = r1.TextureData(reflectivity=obj.material_slots[0].material.diffuse_color[:3],
                                  name_index=len(bsp.TEXTURE_DATA_STRING_DATA) - 1,
                                  size=[128, 128], view=[128, 128],
                                  flags=Flags.VERTEX_UNLIT)
    # hl2/hl2_misc_dir.vpk/materials/dev/dev_measure_generic01.vmt
    # hl2/hl2_misc_dir.vpk/materials/dev/dev_measure_generic01b.vmt
    # hl2/hl2_textures_dir.vpk/materials/dev/dev_measure_generic01.vtf
    # hl2/hl2_textures_dir.vpk/materials/dev/dev_measure_generic01b.vtf
    bsp.TEXTURE_DATA.append(texture_data)
    
    material_sort = dict(texture_data=len(bsp.TEXTURE_DATA) - 1,
                     lightmap_header=0, cubemap=-1, vertex_offset=0)
    bsp.MATERIAL_SORT.append(r1.MaterialSort(material_sort))
    # NOTE: expecting one mesh per material, but we could split it ourselves

    # NOTE: not checking bsp.VERTICES for reusable positions
    raw_vertices = [tuple(v.co) for v in obj.data.vertices]
    vertices = list(set(raw_vertices))
    remapped_vertices = {i: vertices.index(v) + len(bsp.VERTICES) for i, v in enumerate(raw_vertices)}
    Vertex = r1.LUMP_CLASSES["VERTICES"][0]
    bsp.VERTICES.extend([Vertex(v) for v in vertices])
    del raw_vertices, vertices, Vertex
    
    # NOTE: not checking bsp.VERTEX_NORMALS for reusable normals
    raw_normals = [tuple(v.normal)for v in obj.data.vertices]
    normals = list(set(raw_normals))
    remapped_normals = {i: normals.index(n) + len(bsp.VERTEX_NORMALS) for i, n in enumerate(raw_normals)}
    VertexNormal = r1.LUMP_CLASSES["VERTEX_NORMALS"][0]
    bsp.VERTEX_NORMALS.extend([VertexNormal(n) for n in normals])
    del raw_normals, normals, VertexNormal
    
    special_vertices: List[r1.VertexReservedX] = list()
    # [VertexReservedX(position_index, normal_index, *uv, ...)]
    mesh_indices: List[int] = list()

    # https://docs.blender.org/api/current/bpy.types.Mesh.html
    for poly in obj.data.polygons:
        for i in poly.loop_indices:
            # NOTE: could triangulate here
            vertex_index = obj.data.loops[i].vertex_index
            position_index = remapped_vertices[vertex_index]
            normal_index = remapped_normals[vertex_index]
            uv = tuple(obj.data.uv_layers.active.data[i].uv)
            
            vertex = (position_index, normal_index, *uv)
            if vertex not in special_vertices:
                mesh_indices.append(len(special_vertices))
                special_vertices.append(vertex)
            else:
                mesh_indices.append(special_vertices.index(vertex))

    mesh = (len(bsp.MESH_INDICES), len(mesh_indices) // 3,  # first_mesh_index, num_triangles
            len(bsp.VERTEX_UNLIT), len(special_vertices),  # first_vertex, num_vertices
            0, -1, -1, -1, -1, -1,  # unknown
            len(bsp.MATERIAL_SORT) - 1, r1.Flags.VERTEX_UNLIT)  # material_sort, flags
    bsp.MESHES.append(r1.Mesh(mesh))
    
    bsp.MESH_INDICES.extend(mesh_indices)
    
    # bsp.VERTEX_LIT_BUMP.extend([r1.VertexLitBump((*v, -1, 0.0, 0.0, 0, 0, 2, 9)) for v in special_vertices])
    # NOTE: crunching all uv2 to 1 point could be bad,
    # -- unknown=(0, 0, 2, 9) is mp_box.VERTEX_LIT_BUMP[0].unknown
    bsp.VERTEX_UNLIT.extend([r1.VertexUnlit((*v, -1)) for v in special_vertices])
