import importlib
import os
import sys

import bmesh
import bpy

blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)

import bsp_tool  # noqa E402


importlib.reload(bsp_tool)  # bpy doesn't recompile external scripts
# NOTE: don't forget importlib.reload isn't recurcive!
importlib.reload(bsp_tool.branches.respawn.titanfall)
importlib.reload(bsp_tool.branches.respawn.titanfall2)
importlib.reload(bsp_tool.branches.respawn.apex_legends)


def load_materials(bsp):  # -> List[materials]
    materials = []
    for material_name in bsp.TEXDATA_STRING_DATA:
        # TODO: check if material is already loaded
        material = bpy.data.materials.new(material_name)
        materials.append(material)
    return materials


def load_entities(rbsp):
    entity_collection = bpy.data.collections.new(f"{rbsp.filename} Entities")
    bpy.context.scene.collection.children.link(entity_collection)
    # TODO: collection for each classname
    all_entities = (*rbsp.ENTITIES, *rbsp.ENTITIES_env, *rbsp.ENTITIES_fx,
                    *rbsp.ENTITIES_script, *rbsp.ENTITIES_snd, *rbsp.ENTITIES_spawn)
    for i, entity in enumerate(all_entities):
        # bpy.data.speakers.new()  # if classname = "ambient_generic"
        # bpy.data.lights.new()  # if classname.startswith("light")  [light_environment = sun]
        reference = bpy.data.objects.new(f"{entity['classname']} [{i}]", None)
        reference.empty_display_type = "SPHERE"
        reference.empty_display_size = 64
        entity_collection.objects.link(reference)
        reference.location = [*map(float, entity.get("origin", "0 0 0").split())]
        # TODO: create different object types based on classname
        # -- further optimisation (props with shared worldmodel share mesh data)
        for field in entity:
            reference[field] = entity[field]
        if "targetname" in entity:
            reference.name = entity["targetname"]
        # TODO: apply parenting
    # TODO: once all ents are loaded, connect point for keyframe_rope / path_track etc.


def load_rbsp(rbsp):
    materials = load_materials(rbsp)
    # TODO: master collection for map
    for model_index, model in enumerate(rbsp.MODELS):
        model_collection = bpy.data.collections.new(f"{rbsp.filename} Model #{model_index}")
        bpy.context.scene.collection.children.link(model_collection)
        # model_center = (mathutils.Vector(model.mins) + mathutils.Vector(model.maxs)) / 2
        for mesh_index in range(model.first_mesh, model.first_mesh + model.num_meshes):
            mesh = rbsp.MESHES[mesh_index]
            # blender mesh assembly
            blender_mesh = bpy.data.meshes.new(f"{rbsp.filename} Mesh #{mesh_index}")  # mesh object
            blender_bmesh = bmesh.new()  # mesh data
            mesh_vertices = rbsp.vertices_of_mesh(mesh_index)
            bmesh_vertices = dict()
            # ^ {rbsp_vertex.position_index: BMVert}
            face_uvs = list()
            # ^ [{vertex_position_index: (u, v)}]
            for triangle_index in range(0, len(mesh_vertices), 3):
                face_indices = list()
                uvs = dict()
                for vert_index in range(3):
                    rbsp_vertex = mesh_vertices[triangle_index + vert_index]
                    vertex = rbsp.VERTICES[rbsp_vertex.position_index]
                    if rbsp_vertex.position_index not in bmesh_vertices:
                        bmesh_vertices[rbsp_vertex.position_index] = blender_bmesh.verts.new(vertex)
                    face_indices.append(rbsp_vertex.position_index)
                    uvs[tuple(vertex)] = rbsp_vertex.uv
                try:
                    blender_bmesh.faces.new([bmesh_vertices[vpi] for vpi in face_indices])
                    face_uvs.append(uvs)  # index must match bmesh.faces index
                except ValueError:  # "face already exists"
                    pass
            del bmesh_vertices
            # apply uv
            uv_layer = blender_bmesh.loops.layers.uv.new()
            blender_bmesh.faces.ensure_lookup_table()
            for face, uv_dict in zip(blender_bmesh.faces, face_uvs):
                for loop in face.loops:  # loops correspond to verts
                    loop[uv_layer].uv = uv_dict[tuple(loop.vert.co)]
            blender_bmesh.to_mesh(blender_mesh)
            blender_bmesh.free()
            texdata = rbsp.TEXDATA[rbsp.MATERIAL_SORT[mesh.material_sort].texdata]
            blender_mesh.materials.append(materials[texdata.string_table_index])
            blender_mesh.update()
            blender_object = bpy.data.objects.new(blender_mesh.name, blender_mesh)
            model_collection.objects.link(blender_object)
    load_entities(rbsp)


def load_apex_rbsp(rbsp):
    master_collection = bpy.data.collections.new(f"{rbsp.filename}")
    bpy.context.scene.collection.children.link(master_collection)
    # TODO: parse models
    for mesh_index, mesh in enumerate(rbsp.MESHES):
        blender_mesh = bpy.data.meshes.new(f"{rbsp.filename} Mesh #{mesh_index}")  # mesh object
        blender_bmesh = bmesh.new()  # mesh data
        mesh_vertices = rbsp.vertices_of_mesh(mesh_index)
        bmesh_vertices = dict()
        # ^ {rbsp_vertex.position_index: BMVert}
        face_uvs = list()
        # ^ [{vertex_position_index: (u, v)}]
        for triangle_index in range(0, len(mesh_vertices), 3):
            face_indices = list()
            uvs = dict()
            for vert_index in range(3):
                rbsp_vertex = mesh_vertices[triangle_index + vert_index]
                vertex = rbsp.VERTICES[rbsp_vertex.position_index]
                if rbsp_vertex.position_index not in bmesh_vertices:
                    bmesh_vertices[rbsp_vertex.position_index] = blender_bmesh.verts.new(vertex)
                face_indices.append(rbsp_vertex.position_index)
                uvs[tuple(vertex)] = rbsp_vertex.uv
            try:
                blender_bmesh.faces.new([bmesh_vertices[vpi] for vpi in face_indices])
                face_uvs.append(uvs)  # index must match bmesh.faces index
            except ValueError:  # "face already exists"
                pass
        del bmesh_vertices
        # apply uv
        uv_layer = blender_bmesh.loops.layers.uv.new()
        blender_bmesh.faces.ensure_lookup_table()
        for face, uv_dict in zip(blender_bmesh.faces, face_uvs):
            for loop in face.loops:  # loops correspond to verts
                loop[uv_layer].uv = uv_dict[tuple(loop.vert.co)]
        blender_bmesh.to_mesh(blender_mesh)
        blender_bmesh.free()
        # TODO: parse texdata to match materials
        blender_mesh.update()
        blender_object = bpy.data.objects.new(blender_mesh.name, blender_mesh)
        master_collection.objects.link(blender_object)
    load_entities(rbsp)


# NOTE: objects created by a second load may get messy
bsp = bsp_tool.load_bsp("E:/Mod/Titanfall/maps/mp_corporate.bsp")
# bsp = bsp_tool.load_bsp("E:/Mod/TitanfallOnline/maps/mp_box.bsp")  # func_breakable_surf meshes with unknown flags
# bsp = bsp_tool.load_bsp("E:/Mod/Titanfall2/maps/sp_hub_timeshift.bsp")
try:
    load_rbsp(bsp)
except Exception as exc:
    load_entities(bsp)
    raise exc

# bsp = bsp_tool.load_bsp("E:/Mod/ApexLegends/maps/mp_rr_canyonlands_64k_x_64k.bsp")
# load_apex_rbsp(bsp)

del bsp
