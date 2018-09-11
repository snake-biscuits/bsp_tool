import os
import sys
sys.path.insert(0, '../')
from bsp_tool import bsp

def list_maps(folder,):
    return map(lambda y: y[:-4], filter(lambda x: x.endswith('.bsp'), os.listdir(folder)))

STEAM = TF2 = 'E:/Steam/SteamApps/'
TF2 = STEAM + 'common/Team Fortress 2/tf/maps/'
TF2_D = STEAM + 'common/Team Fortress 2/tf/download/maps/'
TF2_W = STEAM + 'workshop/content/440/'

lump_maps = {}
bytes_processed = 0
print('*** /tf/maps')
for MAP in list_maps(TF2):
    try:
        MAP_bsp = bsp(f'{TF2}{MAP}')
        lump_maps[MAP] = MAP_bsp.lump_map
        bytes_processed += MAP_bsp.bytesize
    except: ...
print('*** /tf/dowload/maps')
for MAP in list_maps(TF2_D):
    try:
        MAP_bsp = bsp(f'{TF2_D}{MAP}')
        lump_maps[f'download/{MAP}'] = MAP_bsp.lump_map
        bytes_processed += MAP_bsp.bytesize
    except: ...
#all workshop maps are compressed
#therefore none can be read without modifying bsp_tool to skip compressed lumps
# print('*** /tf/workshop/maps')
# for folder in os.listdir(TF2_W):
#     for MAP in list_maps(f'{TF2_W}{folder}/'):
#         try:
#             MAP_bsp = bsp(f'{TF2_W}{folder}/{MAP}')
#             lump_maps[f'workshop/{MAP}'] = MAP_bsp.lump_map
#             bytes_processed += MAP_bsp.bytesize
#        except: ...
print(f'processed {bytes_processed / 2 ** 30:,.2f} GB')

outfile = open('lump_maps.txt', 'w')
for MAP in lump_maps:
    outfile.write(f'{MAP}\n')
    for l_id, l_header in lump_maps[MAP].items():
        outfile.write(f'\t{l_id.name}: {*iter(l_header)}\n')
    outfile.write('\n')
outfile.close()

outfile = open('lump_maps.csv', 'w')
outfile.write('MAP, ')
outfile.write(', '.join(f'LUMP_{"0" if i < 10 else ""}{i}' for i in range(64)))
outfile.write('\n')
for MAP in lump_maps:
    outfile.write(f'{MAP}, ')
    ordered_lumps = sorted(lump_maps[MAP], key=lambda x: lump_maps[MAP][x].offset)
    for lump in ordered_lumps:
        outfile.write(f'{"0" if lump.value < 10 else ""}{lump.value} {lump.name}, ')
    outfile.write('\n')
outfile.close()
