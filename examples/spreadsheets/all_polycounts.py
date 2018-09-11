import mapcycle
import os
import sys
import time
sys.path.insert(0, '../../')
import bsp_tool
sys.path.insert(0, '../')
from render_bsp import calcTriFanIndices

polycounts = {}
STEAM = 'E:/Steam/SteamApps/'
abbreviations = {'pl': 'Payload', 'cp': 'Capture Point', 'ctf': 'Capture the Flag', 'koth': 'King of the Hill', 'pd': 'Player Destruction', 'plr': 'Payload Race', 'arena': 'Arena', 'sd': 'Special Delivery'}
official_maps = mapcycle.load_maplist()
data_header = ', , BRUSHES, FACES, , FACE TRIANGLES, DISPLACEMENT TRIANGLES, TOTAL TRIANGLES, VERTEX COUNT, INDEX COUNT'
map_data_string = lambda map_data: f', , {map_data[0]}, {map_data[1]}, , {map_data[2]}, {map_data[3]}, {map_data[4]}, {map_data[5]}, {map_data[6]}'

def calculate_polycount(bsp_file):
    # triangle fan (num_tris + 2 = num_verts) so (num_edges - 2 = num_tris)
    face_tris = sum([f['numedges'] - 2 for f in bsp_file.FACES])
    disp_tris = 0
    try:
        disp_tris = len(list(bsp_file.DISP_TRIS))
    except AttributeError:
        ...
    # render_bsp.py vert & index counts
    vertices = []
    indices = []
    currentIndex = 0
    for face in bsp_file.FACES:
        if face["dispinfo"] == -1:
            faceVerts = bsp_file.verts_of(face)
            faceIndices = calcTriFanIndices(faceVerts, currentIndex)
        else:
            power = bsp_file.DISP_INFO[face['dispinfo']]['power']
            faceVerts = bsp_tool.disp_tris(bsp_file.dispverts_of(face), power)
            faceIndices = bsp_tool.disp_tris(range((2 ** power + 1) ** 2), power)
        vertices += faceVerts
        indices += faceIndices
        currentIndex = faceIndices[len(faceIndices) - 1] + 1
    return len(bsp_file.BRUSHES), len(bsp_file.FACES), face_tris, disp_tris, face_tris + disp_tris, len(vertices), len(indices)

def log_map(bsp_file, data):
    game_mode, sep, map_name = bsp_file.filename.partition('_')
    map_name = map_name.rstrip('.bsp')
    if game_mode not in polycounts:
        polycounts[game_mode] = {map_name: data}
    else:
        polycounts[game_mode][map_name] = data

def list_maps(folder,):
    return map(lambda y: y[:-4], filter(lambda x: x.endswith('.bsp'), os.listdir(folder)))

bytes_processed = 0
start = time.time()

print('*** /tf/maps')
TF2 = STEAM + 'common/Team Fortress 2/tf/maps/'
for MAP in list_maps(TF2):
    try:
        MAP_bsp = bsp_tool.bsp(f'{TF2}{MAP}')
        MAP_data = calculate_polycount(MAP_bsp)
        bytes_processed += MAP_bsp.bytesize
    except KeyboardInterrupt as exc:
        raise exc
    except:
        MAP_data = ['COULD NOT LOAD'] * 7
    log_map(MAP_bsp, MAP_data)

official_polycounts = {gm: {m: d for m, d in ms.items() if f'{gm}_{m}' in official_maps} for gm, ms in polycounts.items()}
official_polycounts = {gm: ms for gm, ms in official_polycounts.items() if ms != {}}
outfile = open('official_polycounts.csv', 'w')
for game_mode, maps in sorted(official_polycounts.items()):
    if game_mode in abbreviations:
        outfile.write('\n' + abbreviations[game_mode] + data_header)
    else:
        outfile.write('\n' + game_mode.upper() + '_*' + data_header)
    for map_name, map_data in sorted(maps.items()):
        outfile.write('\n' + map_name.replace('_', ' ').capitalize() + map_data_string(map_data))
outfile.close()
print('\n!!! Official Map Polycounts Logged !!!\n')
    
print('*** /tf/dowload/maps')
TF2_D = STEAM + 'common/Team Fortress 2/tf/download/maps/'
for MAP in list_maps(TF2_D):
    try:
        MAP_bsp = bsp_tool.bsp(f'{TF2_D}{MAP}')
        MAP_data = calculate_polycount(MAP_bsp)
        bytes_processed += MAP_bsp.bytesize
    except KeyboardInterrupt as exc:
        raise exc
    except:
        MAP_data = ['COULD NOT LOAD'] * 7
    log_map(MAP_bsp, MAP_data)

outfile = open('polycounts.csv', 'w')
for game_mode, maps in sorted(polycounts.items()):
    if game_mode in abbreviations:
        outfile.write('\n' + abbreviations[game_mode] + data_header)
    else:
        outfile.write('\n' + game_mode.upper() + '_*' + data_header)
    for map_name, map_data in sorted(maps.items()):
        if map_data != ['COULD NOT LOAD'] * 7:
            outfile.write('\n' + map_name + map_data_string(map_data))
outfile.close()
print('\n!!! All Map Polycounts Logged !!!\n')

#all workshop maps are compressed & currently cannot be read by bsp_tool.py
# print('*** /tf/workshop/maps')
# TF2_W = STEAM + 'workshop/content/440/'
# for folder in os.listdir(TF2_W):
#     for MAP in list_maps(f'{TF2_W}{folder}/'):
#         try:
#             MAP_bsp = bsp_tool.bsp(f'{TF2_W}{folder}/{MAP}')
#             materials[f'workshop/{MAP}'] = MAP_bsp.lump_map
#             bytes_processed += MAP_bsp.bytesize
#        except: ...

time_elapsed = time.time() - start
print(f'processed {bytes_processed / 2 ** 30:,.2f} GB in {time_elapsed // 60:.0f}:{time_elapsed % 60:.3f}')
