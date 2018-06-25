#version a1 (5th December 2017)
#made by B!scuit (Jared Ketterer)
#based on Valve's .bsp file format version 20 (for TF2)
#https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
#https://github.com/ValveSoftware/source-sdk-2013/blob/master/mp/src/public/bspfile.h

### REQUIRED ADDONS ###:
#Import-Export Blender Source Tools
#https://steamcommunity.com/groups/BlenderSourceTools/
#Crowbar Decompiler Tool (CROWBAR_EXE = Crowbar.exe's location on your PC)
#http://steamcommunity.com/groups/CrowbarTool/

### === ALWAYS CREDIT THE MAP CREATOR AND VALVE === ###
#(plus it'd be nice if you could mention us developers,
#Crowbar, BlenderSourceTools & me)
#If you make your own additions to this code be sure to let me know!

#SHOULD HAVE SHIPPED WITH bsp_import_props.vmf & .bsp

#All loads onto active layer (so you can keep it in it's own layer easily)
#Though all imports also occupy layer 1

#Known Bugs:
#  comp_win_banner smd import takes 5 mins to fail
#  mdls in tf/ (not tf/custom/) folder do not copy

#Not implemented but planned:
#  proper .mdl locating and unpacking
#  direct .mdl to mesh data with LoDs as alternative meshdata
#  loading from pakfile
#  support for compressed maps (.bz2 and compressed lumps / pakfiles) (lump-by-lump unpacking)
#  material assignment (viewport colour too!)
#  import cameras
#  import map geometry (also materials and lightmap to texture)
#  export to three.js (with instances)
#  import speakers (soundscapes and ambient generics), also, place according to SourceEntityName(s)
#  import point entities that use props (e.g. team_capture_point, item_ammopack_small)
#  import lights (sun included)
#  delete files once decompiled & then again once imported
#  option to ignore props not compiled for their prop_type (e.g. prop_static playermodels)
#    prop_static only, all others are removed automatically
#  seperate layers for different prop_types (defaults / presets)
#  check to see if object data is loaded BEFORE importing
#  import some logic point entities as empties with their logic stored in text files
#  automatically call: bspzip -extractfiles MAP_TO_IMPORT WORK_FOLDER
#  automatically call: bspzip -repack after copying the original .bsp
#  progress bar
#  error logging to file
#  remove armature modfiers from props that don't have skeletons
#  fix odd rotation bugs

#Planned but very far away:
#  proper blender addon UI (similar to BlenderSourceTools)
#  options (checkboxes in import UI)
#  general bsp tools (lump to dict, import lightmap, lightmap to texture)
#  import geometry
#  import textures
#  threaded subprocesses (and various other performance improvements)
#  automatic decompile (waiting on Crowbar command-line update)
#  skybox
#  export to .vmf (brushes from geometry)
#  animated models (set by logic entities)
#  payload track animation(s)
#  import particles & sprites
#  automatically log errors to a file
#  e-mail log file to developer

#Never gonna happen: (unless you want to make it)
#  generate a curve, stick a camera on it, render the map in 360 degrees (4K) then upload to Youtube
#  with soundscapes and ambient animation (waterfalls, spinning pickups)
#if you're generating a curve, utilise visleaves and move from objective to objective
#or spawn to spawn, passing through the center of each visleaf
#ALWAYS UTILISE PRE-COMPILED DATA

#Use Shift + L > Object Data to select identical models
#And Shift + L > Materials for props with shared materials (e.g. railings)

import bpy
import math
import os
import shutil
import struct
from subprocess import run, PIPE, STDOUT

def filename_of(filepath): #handles folders with '.' in name but not double extensions e.g. '.bsp.old'
    if '.' not in filepath:
        return filepath
    else:    
        return '.'.join(filepath.split('.')[:-1]) #includes path

def path_above(filepath):
    filepath = filepath.split('/')
    if '' in filepath:
        filepath.remove('')
    return '/'.join(filepath[:-1]) + '/'

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

#ALL FOLDERS MUST END WITH A '/' SLASH
TF_FOLDER = 'E:/Steam/Steamapps/common/Team Fortress 2/tf/'
CROWBAR_EXE = 'F:\Modding\crowbar\Crowbar.exe'
MAP_TO_IMPORT = TF_FOLDER + 'maps/pl_upward.bsp'    #bspzip -repack first

WORK_FOLDER = filename_of(MAP_TO_IMPORT) + '/'
ensure_dir(WORK_FOLDER)

VPK_EXE = path_above(TF_FOLDER) + 'bin/vpk.exe'
file = open(MAP_TO_IMPORT, 'rb')
bsp_id = file.read(4) #assumes b'VBSP', no support case for X360 maps
bsp_version = int.from_bytes(file.read(4), 'little') #assuming 20, for TF2
file.seek(568) #LUMP_GAME_LUMP
offset = int.from_bytes(file.read(4), 'little')
length = int.from_bytes(file.read(4), 'little')
lump_version = int.from_bytes(file.read(4), 'little')
fourCC = int.from_bytes(file.read(4), 'little')
if fourCC != 0:
    raise NotImplemented("Can't decompress gamelumps just yet, use:\nbspzip -repack <bspfile> and try again")
file.seek(offset)

glump_headers = []
glump_count = int.from_bytes(file.read(4), 'little')
for i in range(glump_count):
    glump = file.read(16)
    glump = struct.unpack('iHHii', glump)
    glump_headers.append({
        'id': abs(glump[0]).to_bytes(4, 'big'),
        'flags': glump[1],
        'version': glump[2],
        'fileofs': glump[3],
        'filelen': glump[4]})
    
for header in glump_headers:
    if header['id'] == b'sprp': #static prop lump
        sprp_version = header['version']
        sprp_offset = header['fileofs']
        sprp_length = header['filelen']
        sprp_flags = header['flags']
        break

try:
    file.seek(sprp_offset)
except NameError:
    raise RuntimeError('.bsp file has no static prop game lump')

if sprp_flags == 1:
    raise NotImplementedError("Can't decompress the sprp lump just yet, use:\nbspzip -repack <bspfile> and try again")

sprp_dict_len = int.from_bytes(file.read(4), 'little') * 128
try:
    sprp_dict = file.read(sprp_dict_len)
except MemoryError:
    raise RuntimeError("You can't just load " + str(round(sprp_dict_len / 1024**2, 2)) + 'MB!')
sprp_dict = struct.iter_unpack('128s', sprp_dict)
sprp_names = [name[0].decode().strip('\x00') for name in sprp_dict] #sprp_names
sprp_leaves_len = int.from_bytes(file.read(4), 'little') * 2
sprp_leaves = file.read(sprp_leaves_len)
sprp_leaves = struct.iter_unpack('H', sprp_leaves)
sprp_lump_len = int.from_bytes(file.read(4), 'little')
static_props = []
for i in range(sprp_lump_len):
    splump = file.read(72) #assuming sprp_version 10 (new maps should be OK)
    splump = struct.unpack('6f3H2Bi6f8Bf', splump) #no X360 bool or DXlevel
    static_props.append({
        'pos': splump[:3],
        #'angles': splump[3:6], #Y (yaw), Z (pitch), X (roll)
        'angles': [splump[3:6][0], -splump[3:6][2], splump[3:6][1] + 90], #XYZ >>> Y -X Z+90
        'model': sprp_names[splump[6]],
        'first leaf': splump[7],
        'leaf count': splump[8],
        'solid': splump[9],
        'flags': splump[10],
        'skin': splump[11],
        'fademindist': splump[12], #to match prop_dynamic
        'fademaxdist': splump[13],
        'lighting origin': splump[14:17],
        'force fade scale': splump[17],
        'min CPU level': splump[18],
        'max CPU level': splump[19],
        'min GPU level': splump[20],
        'max GPU level': splump[21],
        'diffuse': splump[22:26],
        'unknown': splump[26],
        'type': 'prop_static'
        })

#TODO: check prop_dynamic(s) for animations
file.seek(8)
offset = int.from_bytes(file.read(4), 'little')
length = int.from_bytes(file.read(4), 'little')
lump_version = int.from_bytes(file.read(4), 'little')
fourCC = int.from_bytes(file.read(4), 'little')
if fourCC != 0:
    raise NotImplemented("can't decompress entitiy lumps just yet")
file.seek(offset)
entities = file.read(length).decode().strip('{').split('}')
entities.remove('\n\x00') #could still be cleaner
prop_entities = []
light_entities = []
for entity in entities:
    if '"classname" "prop_' in entity:
        entity = entity.split('\n')
        entity.remove('{') #one per entity
        entity = list(filter(lambda x: x is not '', entity)) #multiple per entity
        entity_struct = {}
        for line in entity: #still have some '{}' and empty lines
            line = [string.strip('"') for string in line.split(' ')]
            if line[0] == 'classname':
                entity_struct['type'] = line[1]
            elif line[0] == 'origin':
                entity_struct['pos'] = [float(line[1]), float(line[2]), float(line[3])]
            elif line[0] == 'angles':
                entity_struct['angles'] = [float(line[1]), -float(line[3]), float(line[2]) + 90]
            else:   #generic, used for import filters
                if len(line) == 2:
                    entity_struct[line[0]] = line[1]
                else:
                    entity_struct[line[0]] = line[1:]
        try:
            prop_entities.append(entity_struct)
        except NameError:
            raise RuntimeError('Invalid prop!\n' + entity)
    #if '"classname" "light_spot"' in entity: #RECYCLE LINE SPLIT AND CLEANUP CODE
    #    entity = entity.split('\n')
    #    entity.remove('{')
    #    entity = list(filter(lambda x: x is not '', entity)) #multiple per entity
    #    entity_struct = {}
    #    for line in entity:
    #        line = [string.strip('"') for string in line.split(' ')]

ent_prop_names = list(set([x['model'] for x in prop_entities]))

all_prop_names = list(set(sprp_names + ent_prop_names))
for name in all_prop_names:
    #all models relocated to work folder for decompile
    #creating folders here prevents errors when copying
    #hopefully this can be replaced with a list passed to Crowbar.exe
    ensure_dir(WORK_FOLDER + path_above(name))

#TODO: Log props that could not be located to file

#For now use bspzip to unpack the .bsp
#SEARCH PAKFILE (uncompressed zip buffer)
#for file in dir(pakfile):
#    for prop in all_prop_names:
#        if file.beginswith() == prop[:-3]:
#            unzip to WORK_FOLDER

#SEARCH & COPY FROM /TF/ & /TF/CUSTOM/
TF_CUSTOM_FOLDER = TF_FOLDER + 'custom/'
TF_CUSTOM_MODS = filter(lambda x: os.path.isdir(os.path.join(TF_CUSTOM_FOLDER, x)), os.listdir(TF_CUSTOM_FOLDER))
#if you want to skip props from a certain pack:
#ignore_folders = ('models/props_gameplay', 'models/props_mining')
#filter(labda x: not x.startswith(ignore_folders), all_prop_names)
for prop in all_prop_names:
    work_prop = WORK_FOLDER + prop
    tf_prop_path = TF_FOLDER + prop #variable names could be better here
    prop_name = filename_of(prop.split('/')[-1])
    if os.path.exists(tf_prop_path):
        prop_folder = path_above(tf_prop_path)
        sub_path = prop_folder[len(TF_FOLDER):]
        for filename in os.listdir(prop_folder): #could reuse listed directories for lots of props
            if filename.startswith(prop_name): #MAY BE BROKEN
                filename = sub_path + filename
                shutil.copyfile(TF_FOLDER + filename, WORK_FOLDER + filename)
    for mod in list(TF_CUSTOM_MODS):
        mod += '/'
        mod_prop_path = TF_CUSTOM_FOLDER + mod + prop
        if os.path.exists(mod_prop_path):
            mod_prop_folder = os.listdir(path_above(mod_prop_path))
            for filename in mod_prop_folder:
                ensure_dir(path_above(work_prop))
                sub_path = path_above(prop)
                if filename.startswith(prop_name):
                    filename = sub_path + filename
                    shutil.copy(TF_CUSTOM_FOLDER + mod + filename, WORK_FOLDER + filename)

#SEARCH VPK FOR PROPS
VPK_LIST = [VPK_EXE, 'l', TF_FOLDER + 'tf2_misc_dir.vpk']
misc_dir_files = run(VPK_LIST, stdout=PIPE, stderr=PIPE) #takes ~.25s
if misc_dir_files.stderr:
    raise RuntimeError(misc_dir_files.std_err.decode())
misc_dir_files = misc_dir_files.stdout.decode().split('\r\n')

#very messy and has a lot of repeat searches. use filter()?
#IDENTIFY FILES TO EXTRACT (.mdl .phy .vtx .ani .vvd ...)
located_files = []
prop_files = []
for filename in misc_dir_files:
    for prop in all_prop_names:
        if filename.startswith(filename_of(prop)) and not os.path.exists(WORK_FOLDER + filename):
            #skip previously extracted files? optional
            #no way to check for updates /;
            #for sprp really only need .mdl, .vtx & .vvd
            #user not told if prop not in vpk
            prop_files.append(filename)
            if prop not in located_files:
                located_files.append(prop)
##        if os.path.exists(WORK_FOLDER + filename):
##            print(filename, 'already extracted!')

#extract files from vpk
VPK_EXTRACT_MODELS = [VPK_EXE, 'x', TF_FOLDER + 'tf2_misc_dir.vpk']
#VPK_EXTRACT_MODELS += prop_files
#print('average filepath len = ', (sum([len(x) for x in prop_files]) + len(prop_files))/ len(prop_files))
#loop unroll for 8192 char cmd limit
#to hit 8000 chars, averaging 50 chars per filepath... 160 prop_files entries at a time
for i in range(0, len(prop_files), 160):
    batch = prop_files[i:i + 160]
    vpk_extract = run(VPK_EXTRACT_MODELS + batch, stdout=PIPE, cwd=WORK_FOLDER, stderr=PIPE)
    print(vpk_extract.stdout.decode())
    if vpk_extract.stderr:
        raise RuntimeError(vpk_extract.stderr.decode())

#MDL INPUT: Folder and subfolders = WORK_FOLDER
#OUTPUT TO: Subfolder of mdl input = decompiled 0.49
#OPTIONS: #older for each model
#expects each prop to be in its directory then, 'filename/files'
print('Please decompile WORK_FOLDER with CROWBAR_EXE')
#DOESN'T WORK, CROWBAR HAS NO COMMAND LINE OPTIONS YET
#I'LL CALL CROWBAR SO YOU CAN DECOMPILE THOUGH
#PAUSES THE SCRIPT SO IT'LL HAVE THE FILES IT NEEDS
decompile = run([CROWBAR_EXE], stdout=PIPE, stderr=PIPE)
if decompile.stderr:
    raise RuntimeError(decompile.stderr.decode())

decompile_folder = WORK_FOLDER + 'decompiled 0.49/' #actual folder name may change

#CREATE ERROR.MDL
#refer to handmade model
bpy.ops.object.text_add(enter_editmode = True)
bpy.context.object.name = "ERROR.mdl"
bpy.ops.font.delete(type='ALL')
bpy.ops.font.text_insert(text="ERROR")
bpy.ops.object.editmode_toggle()
bpy.context.object.data.extrude = 0.25
bpy.context.object.data.align_x = 'CENTER'
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.convert(target='MESH')
bpy.context.object.dimensions = [80, 64, 16]
bpy.ops.transform.rotate(value=math.radians(90), axis=(1, 0, 0))
bpy.ops.object.transform_apply(scale=True, rotation=True)
error_material = bpy.data.materials.new(name='ERROR.mdl')
bpy.context.object.data.materials.append(error_material)
bpy.context.object.active_material.diffuse_color = (1, 0, 0)
#need to change context to do this bit
#if bpy.context.scene.render.engine == 'CYCLES':
#    bpy.ops.cycles.use_shading_nodes()
 #   bpy.data.node_groups["Shader Nodetree"].nodes["Diffuse BSDF"].inputs[0].default_value = (1, 0, 0, 1)

all_prop_structs = prop_entities + static_props
#this is what the path to a decompiled.smd should look like:
#WORK_FOLDER/decompiled 0.49/models/props_gameplay/orange_cone001/orange_cone001_reference.smd
import time
import_start_time = time.time()
for mdl in all_prop_names:
    #if mdl in bpy.data.objects:
    #    don't import, use pre-imported
    mdl_filename = filename_of(mdl)
    filename = mdl_filename.split('/')[-1]
    try:
        smd_folder = decompile_folder + path_above(mdl) + filename + '/'
        smd_files = os.listdir(smd_folder)
        smd_path = ''
        decompiled_smds = list(filter(lambda x: x.lower().startswith(filename) and '.smd' in x, smd_files))
        decompiled_smds = list(filter(lambda x: not any(s in x for s in ('.qc', '_physics')), decompiled_smds))
        if len(decompiled_smds) == 1:
            imported_filename = decompiled_smds[0][:-4]
            smd_path = smd_folder + decompiled_smds[0]
        else:
            for smd in decompiled_smds:
                if smd.endswith(('_reference.smd', 'model.smd')) or smd.lower() == filename + '.smd': #can replace with lod1 or similar
                    imported_filename = smd[:-4]
                    smd_path = smd_folder + smd
                    break
        if smd_path == '':
            raise RuntimeError('Guessed decompiled filename wrong')
        bpy.ops.import_scene.smd(filepath=smd_path) #might make my own
        bpy.ops.object.select_all(action='DESELECT')
        #filter(lambda x: x['type'].startswith('prop_dynamic') and x['model'] == mdl, all_prop_structs)
        #if len(list(^this filter^)) != 0, duplicate skeleton (parent) with model (don't delete it either)
        if imported_filename + '_skeleton' in bpy.data.objects:
            #should delete all skeletons
            #though I'd actually like to keep dynamic skeletons
            bpy.data.objects[imported_filename + '_skeleton'].select = True
            bpy.ops.object.delete(use_global=False)
        bpy.data.objects[imported_filename].data.name = filename
        imported_model = bpy.data.objects[imported_filename]
        imported_model.data.use_auto_smooth = True
    except Exception as exc: #ERROR.mdl case
        print(mdl, 'BROKE!' + '*' * 30)
        print(exc, 'using ERROR.mdl')
        imported_model = bpy.data.objects['ERROR.mdl']
        unique_error = imported_model.copy()
        unique_error.name = mdl
        unique_error.data = imported_model.data.copy()
        unique_error.data.name = mdl
        bpy.context.scene.objects.link(unique_error)
        imported_model = unique_error
    for prop_struct in filter(lambda x: x['model'] == mdl, all_prop_structs):
        bpy.ops.object.select_all(action='DESELECT')
        imported_model.select = True
        prop = imported_model.copy()
        prop.location = prop_struct['pos']
        radian_qangle = [math.radians(axis) for axis in prop_struct['angles']]
        prop.rotation_euler = radian_qangle #QAngles sorted and in radians
        if 'targetname' in prop_struct:
            prop.name = prop_struct['targetname']
        #if prop_struct['name'].startswith(('cp', 'cap')):
        #    prop.layers[bpy.context.scene.active_layer] = False
        #    prop.layers[6] = True
        if 'parent' in prop_struct:
            #throws a KeyError if the parent hasn't been created & named yet
            prop.parent = bpy.data.objects[prop_struct['parent']]
        #add your own special options
        #EXAMPLE:
        #if 'diffuse' in prop_struct:
        #    prop.active_material.diffuse_color = prop_struct['diffuse'][:3]
        #if 'fademindist' in prop_struct:
        #    fmind = float(prop_struct['fademindist']
        #    if -1 < fmind < 1024:
        #        bpy.ops.object.delete()
        #if 'prop_dynamic' in prop_struct['type']: #gets prop_dynamic_ornament
        #    if 'anims' in prop_struct:
        #        #animate
        #        pass
        bpy.context.scene.objects.link(prop)
    if imported_model.name != 'ERROR.mdl':
        bpy.ops.object.select_all(action='DESELECT')
        imported_model.select = True
        bpy.ops.object.delete(use_global=False)

bpy.data.objects['ERROR.mdl'].select = True
bpy.ops.object.delete()

import_time_taken = time.time() - import_start_time
print("import took", import_time_taken // 60, 'minutes,',  int(import_time_taken) % 60,
      'seconds and', (round(import_time_taken, 5) * 1000) % 1000, 'milliseconds')
