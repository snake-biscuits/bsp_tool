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
    sys.path.append(blend_dir)  # mount bsp_tool

import bsp_tool  # noqa E402


importlib.reload(bsp_tool)  # bpy doesn't recompile external scripts
# NOTE: don't forget importlib.reload isn't recurcive!
importlib.reload(bsp_tool.branches.respawn.titanfall)
importlib.reload(bsp_tool.branches.respawn.titanfall2)
importlib.reload(bsp_tool.branches.respawn.apex_legends)


# TODO: log errors to a bpy.data.texts["{bsp.filename}_log"]
game_dir = "E:/Mod/TitanfallOnline/TitanFallOnline/assets_dump"

r1 = titanfall = bsp_tool.branches.respawn.titanfall
r2 = titanfall2 = bsp_tool.branches.respawn.titanfall2
r5 = apex = bsp_tool.branches.respawn.apex_legends


tool_texture_colours = {"TOOLS\\TOOLSBLACK": (0, 0, 0),
                        "TOOLS\\TOOLSOUT_OF_BOUNDS": (0.913, 0.39, 0.003),
                        "TOOLS\\TOOLSSKYBOX": (0.441, 0.742, 0.967),
                        "TOOLS\\TOOLSTRIGGER": (0.944, 0.048, 0.004),
                        "TOOLS\\TOOLSTRIGGER_CAPTUREPOINT": (0.273, 0.104, 0.409)}


def load_materials(bsp):  # -> List[BlenderMaterial]
    # TODO: OPTIONAL: load textures
    # material_dir = os.path.join(game_dir, "materials")
    # if game_dir is not "":
    #     for vmt_name in bsp.TEXTURE_DATA_STRING_DATA:
    #         try:
    #             # NOTE: only Titanfall 1 uses vtfs?
    #             # - TF|2 & Apex stream textures from .rpak (also proprietary PBR probably)
    #             bpy.ops.import_texture.vmt(filepath=material_dir, files=[{"name": f"{vmt_name}.vmt"}])
    #             # NOTE: SourceIO will print FileNotFound errors to console
    #             material = bpy.data.materials[os.path.basename(vmt_name)]
    #             # TODO: SourceIO can't find the .vtfs, even though they're right next to the .vmts
    #         except (KeyError, NameError, FileNotFoundError) as exc:
    #             material = bpy.data.materials.new(vmt_name)
    #         except Exception as exc:  # just in case something unexpected happens
    #             material = bpy.data.materials.new(vmt_name)
    #         materials.append(material)
    # else:
    materials = list()
    if bsp.branch in (r1, r2):  # Titanfall 1 & 2
        for i, vmt_name in enumerate(bsp.TEXTURE_DATA_STRING_DATA):
            material = bpy.data.materials.new(vmt_name)
            if bsp.branch == r1:
                colour = [td.reflectivity for td in bsp.TEXTURE_DATA if td.name_index == i][0]
            else:
                colour = tool_texture_colours.get(vmt_name, (.8, .8, .8))
            alpha = 1 if not vmt_name.startswith("TOOLS") else 0.25
            material.diffuse_color = (*colour, alpha)
            if alpha != 1:
                material.blend_method = "BLEND"
            materials.append(material)
        return materials
    else:  # Apex Legends
        for i, vmt_name in enumerate(bsp.SURFACE_NAMES):
            material = bpy.data.materials.new(vmt_name)
            colour = tool_texture_colours.get(vmt_name, (.8, .8, .8))
            alpha = 1 if not vmt_name.startswith("TOOLS") else 0.25
            material.diffuse_color = (*colour, alpha)
            if alpha != 1:
                material.blend_method = "BLEND"
            materials.append(material)
        return materials


# colourspace translation (for light entities)
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
        light.spot_size = math.radians(float(entity["_cone"]))
        # spot_blend = _inner_cone / _cone
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
    # TODO: use vector math nodes to mimic light curves
    if "_zero_percent_distance" in entity:
        light.use_custom_distance = True
        light.cutoff_distance = float(entity["_zero_percent_distance"])
    light.energy = light.energy / 100
    return light


# TODO: cubemaps, lightprobes, props, areaportals
ent_object_data = {"light": ent_to_light, "light_spot": ent_to_light, "light_environment": ent_to_light,
                   "ambient_generic": lambda e: bpy.data.speakers.new(e.get("targetname", e["classname"]))}
# NOTE: info_target has a "editorclass" key, allowing it to be another object (e.g. a weapon pickup)


def load_entities(bsp):
    all_entities = (bsp.ENTITIES, bsp.ENTITIES_env, bsp.ENTITIES_fx,
                    bsp.ENTITIES_script, bsp.ENTITIES_snd, bsp.ENTITIES_spawn)
    block_names = ("bsp", "env", "fx", "script", "sound", "spawn")
    master_collection = bpy.data.collections[bsp.filename]
    entities_collection = bpy.data.collections.new("entities")
    master_collection.children.link(entities_collection)
    for entity_block, block_name in zip(all_entities, block_names):
        entity_collection = bpy.data.collections.new(block_name)
        entities_collection.children.link(entity_collection)
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
            position = [*map(float, entity.get("origin", "0 0 0").split())]
            entity_object.location = position
            if entity.get("model", "").startswith("*"):
                model_collection = bpy.data.collections.get(f"model #{entity['model'][1:]}")
                if model_collection is not None:
                    # TODO: rename collection to targetname
                    for o in model_collection.objects:
                        o.location = position
            # NOTE: default source orientation is facing east (+X)
            angles = [*map(lambda x: math.radians(float(x)), entity.get("angles", "0 0 0").split())]
            angles[0] = math.radians(-float(entity.get("pitch", -math.degrees(angles[0]))))
            entity_object.rotation_euler = mathutils.Euler((angles[2], angles[0], angles[1]))
            # TODO: further optimisation (props with shared worldmodel share mesh data) [ent_object_data]
            for field in entity:
                entity_object[field] = entity[field]
        # TODO: once all ents are loaded, connect paths for keyframe_rope / path_track etc.
        # TODO: identify model ent's collections and reposition them
        # TODO: apply parental relationships on a second pass


def load_static_props(bsp):
    """Requires all models to be extracted beforehand"""
    master_collection = bpy.data.collections[bsp.filename]
    prop_collection = bpy.data.collections.new("static props")
    master_collection.children.link(prop_collection)
    # model_dir = os.path.join(game_dir, "models")
    # TODO: hook into SourceIO to import .mdl files
    # TODO: make a collection for static props
    for prop in bsp.GAME_LUMP.sprp.props:
        prop_object = bpy.data.objects.new(bsp.GAME_LUMP.sprp.model_names[prop.model_name], None)
        # TODO: link mesh data by model_name
        prop_object.empty_display_type = "SPHERE"
        prop_object.empty_display_size = 64
        prop_object.location = [*prop.origin]
        prop_object.rotation_euler = mathutils.Euler((prop.angles[2], prop.angles[0], 90 + prop.angles[1]))
        prop_collection.objects.link(prop_object)
    # try:
    #     bpy.ops.source_io.mdl(filepath=model_dir, files=[{"name": "error.mdl"}])
    # except Exception as exc:
    #     print("Source IO not installed!", exc)
    # else:
    #     for mdl_name in bsp.GAME_LUMP.sprp.mdl_names:
    #         bpy.ops.source_io.mdl(filepath=model_dir, files=[{"name": mdl_name}])
    # now find it..., each model creates a collection...
    # this is gonna be real memory intensive...
    # TODO: instance each prop at listed location & rotation etc. (preserve object data)


def load_rbsp(rbsp):
    """Titanfall 1 / 2 -> Blender"""
    materials = load_materials(rbsp)
    # TODO: master collection for geometry
    # sub-collection in model[0] for skybox meshes
    # auto-hide tool textures (optional)
    master_collection = bpy.data.collections.new(rbsp.filename)
    bpy.context.scene.collection.children.link(master_collection)
    for model_index, model in enumerate(rbsp.MODELS):
        model_collection = bpy.data.collections.new(f"model #{model_index}")
        master_collection.children.link(model_collection)
        for mesh_index in range(model.first_mesh, model.first_mesh + model.num_meshes):
            mesh = rbsp.MESHES[mesh_index]
            # blender mesh assembly
            blender_mesh = bpy.data.meshes.new(f"mesh #{mesh_index}")  # mesh object
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
            texture_data = rbsp.TEXTURE_DATA[rbsp.MATERIAL_SORT[mesh.material_sort].texture_data]
            blender_mesh.materials.append(materials[texture_data.name_index])
            # TODO: isolate the worldspawn skybox in it's own layer
            blender_mesh.update()
            blender_object = bpy.data.objects.new(blender_mesh.name, blender_mesh)
            model_collection.objects.link(blender_object)
        if len(model_collection.objects) == 0:
            bpy.data.collections.remove(model_collection)


# load a mesh by selecting the vertex lump manually
def load_mesh(rbsp: bsp_tool.RespawnBsp, index: int, VERTEX_LUMP: str):
    # NOTE: skips UVs
    blender_mesh = bpy.data.meshes.new("TEST_MESH")
    blender_bmesh = bmesh.new()  # mesh data
    # vertices of mesh
    mesh = rbsp.MESHES[index]
    material_sort = rbsp.MATERIAL_SORT[mesh.material_sort]
    # NOTE: not applying material
    start = mesh.start_index
    finish = start + mesh.num_triangles * 3
    indices = [material_sort.vertex_offset + i for i in rbsp.MESH_INDICES[start:finish]]
    VERTEX_LUMP = getattr(rbsp, VERTEX_LUMP)
    mesh_vertices = [VERTEX_LUMP[i] for i in indices]
    # convert to bmesh
    bmesh_vertices = dict()
    # ^ {rbsp_vertex.position_index: BMVert}
    for triangle_index in range(0, len(mesh_vertices), 3):
        face_indices = list()
        for vert_index in reversed(range(3)):  # invert winding order for backfaces
            rbsp_vertex = mesh_vertices[triangle_index + vert_index]
            vertex = rbsp.VERTICES[rbsp_vertex.position_index]
            if rbsp_vertex.position_index not in bmesh_vertices:
                bmesh_vertices[rbsp_vertex.position_index] = blender_bmesh.verts.new(vertex)
            face_indices.append(rbsp_vertex.position_index)
        try:
            blender_bmesh.faces.new([bmesh_vertices[vpi] for vpi in face_indices])
        except ValueError:  # "face already exists"
            pass
    # skip uv
    blender_bmesh.to_mesh(blender_mesh)
    blender_bmesh.free()
    # skip texture
    blender_mesh.update()
    blender_object = bpy.data.objects.new(blender_mesh.name, blender_mesh)
    bpy.context.scene.collection.objects.link(blender_object)


def load_apex_rbsp(rbsp):
    """Apex mapping of TEXTURE_DATA & MODEL lumps is incomplete"""
    # materials
    materials = load_materials(rbsp)
    # collections setup
    master_collection = bpy.data.collections.new(rbsp.filename)
    bpy.context.scene.collection.children.link(master_collection)
    geo_collection = bpy.data.collections.new("geometry")
    master_collection.children.link(geo_collection)
    for model_index, model in enumerate(rbsp.MODELS):
        model_collection = bpy.data.collections.new(f"model #{model_index}")
        geo_collection.children.link(model_collection)
        for mesh_index in range(model.first_mesh, model.first_mesh + model.num_meshes):
            blender_mesh = bpy.data.meshes.new(f"mesh #{mesh_index}")  # mesh object
            blender_bmesh = bmesh.new()  # mesh data
            mesh_vertices = rbsp.vertices_of_mesh(mesh_index)
            bmesh_vertices = dict()
            # ^ {rbsp_vertex.position_index: BMVert}
            face_uvs = list()
            # ^ [{vertex_position_index: (u, v)}]
            for triangle_index in range(0, len(mesh_vertices), 3):
                face_indices = list()
                uvs = dict()
                for vert_index in reversed(range(3)):
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
            # apply material
            material_index = rbsp.SURFACE_NAMES.index(rbsp.get_Mesh_SurfaceName(mesh_index))
            blender_mesh.materials.append(materials[material_index])
            # push to collection
            blender_mesh.update()
            blender_object = bpy.data.objects.new(blender_mesh.name, blender_mesh)
            model_collection.objects.link(blender_object)
        if len(model_collection.objects) == 0:
            bpy.data.collections.remove(model_collection)


TITANFALL = "E:/Mod/Titanfall/maps/"
TITANFALL_ONLINE = "E:/Mod/TitanfallOnline/maps/"
# bsp = bsp_tool.load_bsp(TITANFALL + "mp_corporate.bsp")  # odd model flags for breakable glass
# bsp = bsp_tool.load_bsp(TITANFALL + "mp_lobby.bsp")
# bsp = bsp_tool.load_bsp(TITANFALL + "mp_colony.bsp")  # smallest map after lobby
# bsp = bsp_tool.load_bsp(TITANFALL_ONLINE + "mp_box.bsp")

TITANFALL_2 = "E:/Mod/Titanfall2/maps/"
# bsp = bsp_tool.load_bsp(TITANFALL_2 + "sp_training.bsp")
# bsp = bsp_tool.load_bsp(TITANFALL_2 + "sp_boomtown.bsp")
# bsp = bsp_tool.load_bsp(TITANFALL_2 + "mp_lobby.bsp")
# bsp = bsp_tool.load_bsp(TITANFALL_2 + "mp_wargames.bsp")
# load_rbsp(bsp)

APEX = "E:/Mod/ApexLegends/"
S2 = "season2/maps/"
S3 = "season3_3dec19/maps/"
S10 = "season10_10aug21/maps/"
S10_PATCH = "season10_14sep21/maps/"
# bsp = bsp_tool.load_bsp(APEX + S2 + "mp_lobby.bsp")
# bsp = bsp_tool.load_bsp(APEX + S3 + "mp_rr_canyonlands_64k_x_64k.bsp")
# bsp = bsp_tool.load_bsp(APEX + "maps/mp_rr_desertlands_mu2.bsp")
# bsp = bsp_tool.load_bsp(APEX + S10 + "mp_rr_aqueduct.bsp")
# bsp = bsp_tool.load_bsp(APEX + S10 + "mp_rr_party_crasher.bsp")  # smallest map after lobby
bsp = bsp_tool.load_bsp(APEX + S10_PATCH + "mp_rr_arena_skygarden.bsp")  # new map, who dis?
load_apex_rbsp(bsp)

load_entities(bsp)

# load_static_props(bsp)

del bsp

# NOTE: remember to delete the previous import manually & purge orphans


# TODO: Shift+A > Add Entity
# -- requires .fgd to identify key-value types & ranges (which would be nice for importing too)
# TODO: Ctrl+Shift+T > To Solid Entity
