import importlib
import math
import os
import sys
from typing import Dict, List

import bmesh
import bpy
import mathutils

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
        # TODO: option to look for .vmt & load colour, textures etc.
        materials.append(material)
    return materials


# colourspace translation
def srgb_to_linear(*srgb: List[float]) -> List[float]:
    linear = list()
    for s in srgb:
        if s <= 0.0404482362771082:
            lin = s / 12.92
        else:
            lin = ((s + 0.055) / 1.055) ** 2.4
        linear.append(lin)
    return linear


def linear_to_srgb(*linear: List[float]) -> List[float]:
    srgb = list()
    for lin in linear:
        if lin > 0.00313066844250063:
            s = 1.055 * (lin ** (1.0 / 2.4)) - 0.055
        else:
            s = 12.92 * lin
        srgb.append(s)
    return srgb


# entity reference objects
def ent_to_light(entity: Dict[str, str]) -> bpy.types.PointLight:
    light_name = entity.get("targetname", entity["classname"])
    if entity["classname"] == "light":
        light = bpy.data.lights.new(light_name, "POINT")
    elif entity["classname"] == "light_spot":
        light = bpy.data.lights.new(light_name, "SPOT")
    elif entity["classname"] == "light_environment":
        light = bpy.data.lights.new(light_name, "SUN")
        light.angle = math.radians(float(entity.get("SunSpreadAngle", "0")))
    light.cycles.use_multiple_importance_sampling = False
    if entity.get("_lightHDR", "-1 -1 -1 1") == "-1 -1 -1 1":
        r, g, b, brightness = map(float, entity["_light"].split())
        light.color = srgb_to_linear(r, g, b)
        light.energy = brightness
    else:
        r, g, b, brightness = map(float, entity["_lightHDR"].split())
        light.color = srgb_to_linear(r, g, b)
        light.energy = brightness * float(entity.get("_lightscaleHDR", "1"))
    return light


# TODO: cubemaps, lightprobes
ent_object_data = {"light": ent_to_light, "light_spot": ent_to_light, "light_environment": ent_to_light,
                   "ambient_generic": lambda e: bpy.data.speakers.new(e.get("targetname", e["classname"]))}


def load_entities(rbsp):
    all_entities = (rbsp.ENTITIES, rbsp.ENTITIES_env, rbsp.ENTITIES_fx,
                    rbsp.ENTITIES_script, rbsp.ENTITIES_snd, rbsp.ENTITIES_spawn)
    block_names = ("Internal", "Environment", "Effects", "Script", "Sound", "Spawn")
    for entity_block, block_name in zip(all_entities, block_names):
        entity_collection = bpy.data.collections.new(f"{rbsp.filename} {block_name} Entities")
        bpy.context.scene.collection.children.link(entity_collection)
        for entity in entity_block:
            object_data = ent_object_data.get(entity["classname"], lambda e: None)(entity)
            name = entity.get("targetname", entity["classname"])
            entity_object = bpy.data.objects.new(name, object_data)
            if object_data is None:
                entity_object.empty_display_type = "SPHERE"
                entity_object.empty_display_size = 64
                if entity["classname"].startswith("info_node"):
                    entity_object.empty_display_type = "CUBE"
            entity_collection.objects.link(entity_object)
            entity_object.location = [*map(float, entity.get("origin", "0 0 0").split())]
            # NOTE: default source orientation is facing east (+Xaa)
            angles = [*map(lambda x: math.radians(float(x)), entity.get("angles", "0 0 0").split())]
            entity_object.rotation_euler = mathutils.Euler((angles[2],
                                                            -float(entity.get("pitch", -angles[0])),
                                                            angles[1] + 180))
            # TODO: apply parenting
            # TODO: further optimisation (props with shared worldmodel share mesh data)
            for field in entity:
                entity_object[field] = entity[field]
        # TODO: once all ents are loaded, connect paths for keyframe_rope / path_track etc.


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
                for vert_index in reversed(range(3)):  # invert winding order for backfaces
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
# bsp = bsp_tool.load_bsp("E:/Mod/Titanfall/maps/mp_corporate.bsp")    # func_breakable_surf meshes with unknown flags
bsp = bsp_tool.load_bsp("E:/Mod/TitanfallOnline/maps/mp_lobby_02.bsp")
# bsp = bsp_tool.load_bsp("E:/Mod/Titanfall2/maps/sp_hub_timeshift.bsp")
try:
    load_rbsp(bsp)
except Exception as exc:
    load_entities(bsp)
    raise exc

# bsp = bsp_tool.load_bsp("E:/Mod/ApexLegends/maps/mp_rr_canyonlands_64k_x_64k.bsp")
# load_apex_rbsp(bsp)

del bsp
