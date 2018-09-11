TF_DIR = 'E:/Steam/SteamApps/common/Team Fortress 2/tf/'

def load_maplist(mapcycle='mapcycle_default.txt'):
    'turns a given mapcycle file in /tf/cfg/ into a list of strings'
    official_maps = []
    mapcycle_file = open(f'{TF_DIR}cfg/{mapcycle}')
    for line in mapcycle_file.readlines():
        if not line.startswith('//') and not line == '\n':
            official_maps.append(line[:-1])
    mapcycle_file.close()
    return official_maps
