import os
import sys
import time
sys.path.insert(0, '../')
from bsp_tool import bsp

def list_maps(folder,):
    return map(lambda y: y[:-4], filter(lambda x: x.endswith('.bsp'), os.listdir(folder)))

def write_map_materials(MAP):
    outfile.write(f'{MAP}, ')
    for m in materials[MAP]:
        outfile.write(f'{m}, ')
    outfile.write('\n')

STEAM = TF2 = 'E:/Steam/SteamApps/'
TF2 = STEAM + 'common/Team Fortress 2/tf/maps/'
TF2_D = STEAM + 'common/Team Fortress 2/tf/download/maps/'
TF2_W = STEAM + 'workshop/content/440/'

outfile = open('spreadsheets/materials.csv', 'w')
outfile.write('MAP, MATERIALS,\n')
materials = {}
bytes_processed = 0
start = time.time()
print('*** /tf/maps')
for MAP in list_maps(TF2):
    try:
        MAP_bsp = bsp(f'{TF2}{MAP}')
        materials[MAP] = MAP_bsp.TEXDATA_STRING_DATA
        write_map_materials(MAP)
        bytes_processed += MAP_bsp.bytesize
    except: ...
print('*** /tf/dowload/maps')
for MAP in list_maps(TF2_D):
    try:
        MAP_bsp = bsp(f'{TF2_D}{MAP}')
        materials[f'download/{MAP}'] = MAP_bsp.TEXDATA_STRING_DATA
        write_map_materials(MAP)
        bytes_processed += MAP_bsp.bytesize
    except: ...
#all workshop maps are compressed
#therefore none can be read without modifying bsp_tool to skip compressed lumps
# print('*** /tf/workshop/maps')
# for folder in os.listdir(TF2_W):
#     for MAP in list_maps(f'{TF2_W}{folder}/'):
#         try:
#             MAP_bsp = bsp(f'{TF2_W}{folder}/{MAP}')
#             materials[f'workshop/{MAP}'] = MAP_bsp.lump_map
#             bytes_processed += MAP_bsp.bytesize
#        except: ...
time_elapsed = time.time() - start
print(f'processed {bytes_processed / 2 ** 30:,.2f} GB in {time_elapsed // 60}:{time_elapsed % 60}')
outfile.close()

maps = [m for m in materials if 'WINTER/BLENDGRAVELTOGRASS001' in materials[m]]
