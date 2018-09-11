import mapcycle
import os
import struct

TF2 = 'E:/Steam/SteamApps/common/Team Fortress 2/tf/maps/'

official_maps = mapcycle.load_maplist()

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

props = {}
for MAP in official_maps:
    try:
        bsp = open(f'{TF2}{MAP}.bsp', 'rb')
        bsp.seek(568) #LUMP_GAME_LUMP
        offset = int.from_bytes(bsp.read(4), 'little')
        length = int.from_bytes(bsp.read(4), 'little')
        lump_version = int.from_bytes(bsp.read(4), 'little')
        fourCC = int.from_bytes(bsp.read(4), 'little')
        if fourCC != 0:
            raise NotImplemented("Can't decompress gamelumps just yet, use:\nbspzip -repack <bspfile> and try again")
        bsp.seek(offset)

        glump_headers = []
        glump_count = int.from_bytes(bsp.read(4), 'little')
        for i in range(glump_count):
            glump = bsp.read(16)
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
            bsp.seek(sprp_offset)
        except NameError:
            raise RuntimeError('.bsp file has no static prop game lump')

        if sprp_flags == 1:
            print(bsp.name)
            raise NotImplementedError("Can't decompress the sprp lump just yet, use:\nbspzip -repack <bspfile> and try again")

        sprp_dict_len = int.from_bytes(bsp.read(4), 'little') * 128
        try:
            sprp_dict = bsp.read(sprp_dict_len)
        except MemoryError:
            raise RuntimeError("You can't just load " + str(round(sprp_dict_len / 1024**2, 2)) + 'MB!')
        sprp_dict = struct.iter_unpack('128s', sprp_dict)
        sprp_names = [name[0].decode().strip('\x00') for name in sprp_dict] #sprp_names
        sprp_leaves_len = int.from_bytes(bsp.read(4), 'little') * 2
        sprp_leaves = bsp.read(sprp_leaves_len)
        sprp_leaves = struct.iter_unpack('H', sprp_leaves)
        sprp_lump_len = int.from_bytes(bsp.read(4), 'little')
        static_props = []
        for i in range(sprp_lump_len):
            splump = bsp.read(72) #assuming sprp_version 10 (new maps should be OK)
            splump = struct.unpack('6f3H2Bi6f8Bf', splump) #no X360 bool or DXlevel
            static_props.append({
                'pos': splump[:3],
                #'angles': splump[3:6], #Y (yaw), Z (pitch), X (roll)
                'angles': [splump[3:6][0], -splump[3:6][2], splump[3:6][1] + 90], #XYZ >>> Y -X Z+90
                'model': splump[6],
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

        bsp.seek(8)
        offset = int.from_bytes(bsp.read(4), 'little')
        length = int.from_bytes(bsp.read(4), 'little')
        lump_version = int.from_bytes(bsp.read(4), 'little')
        fourCC = int.from_bytes(bsp.read(4), 'little')
        if fourCC != 0:
            raise NotImplemented("can't decompress entitiy lumps just yet")
        bsp.seek(offset)
##        entities = bsp.read(length)
##        entities.remove('\n\x00') #could still be cleaner
##        prop_entities = []
        entities = bsp.read(length).decode('ascii').replace('{', '').split('}')[:-1]
        new_entities = []
        for entity in entities:
            entity = entity.lstrip('\n').rstrip('\n')
            entity = entity.split('\n')
            new_entities.append(dict())
            for line in entity:
                key, value = line.split('" "')
                key, value = key[1:], value[:-1]
                new_entities[-1][key] = value
        entities = new_entities
        prop_entities = filter(lambda x: x['classname'].startswith('prop_'), entities)

        ent_prop_names = []
        for x in prop_entities:
            try:
                ent_prop_names.append(x['model'])
            except:
                pass
                #cp_junction has a prop_dynamic with no model
##                print(bsp.name)
##                print('\n'.join([f'{key}: {value}' for key, value in x.items()]))
##                print(x.keys())
##                raise RuntimeError()

        all_sprp_names = []
        for x in static_props:
            try:
                all_sprp_names.append(sprp_names[x['model']])
            except:
                pass
                #occasionally the index massively exceeds expected values
        all_prop_names = all_sprp_names + ent_prop_names
##        all_prop_names = sprp_names + ent_prop_names
        all_prop_names = [*map(lambda x: x[7:-4], all_prop_names)]
        props[MAP] = {x: all_prop_names.count(x) for x in list(set(all_prop_names))}
    except Exception as exc:
        print(exc, MAP)
        raise exc

outfile = open('props.csv', 'w')
outfile.write('MAP, PROPS\n')
for MAP in props:
    ranked_props = sorted(props[MAP], key=lambda x: props[MAP][x], reverse=True)
    outfile.write(f'{MAP}, ')
    outfile.write(','.join([f'{props[MAP][x]},{x}' for x in ranked_props]))
    outfile.write('\n')
##outfile.close()

import itertools
all_props = {}
for MAP in props:
    for p in props[MAP]:
        if p in all_props:
            all_props[p] += props[MAP][p]
        else:
            all_props[p] = props[MAP][p]
ranked_props = sorted(all_props, key=lambda p: all_props[p], reverse=True)
##print('\n'.join([f'{all_props[prop]} {prop}' for prop in ranked_props[:50]]))

outfile.write('TOTAL\n,')
outfile.write(','.join([f'{all_props[prop]},{prop}' for prop in ranked_props]))
outfile.close()
