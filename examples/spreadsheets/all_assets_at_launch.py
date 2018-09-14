import lzma
import struct

TF2 = 'E:/Steam/SteamApps/common/Team Fortress 2/tf/maps/'
release_maps = ['cp_dustbowl', 'cp_granary', 'cp_gravelpit', 'cp_well',
                'ctf_2fort', 'tc_hydro']

materials = set()
props = set()
for MAP in release_maps:
    print(f'Processing {MAP}...')
    bsp = open(f'{TF2}{MAP}.bsp', 'rb')
    bsp.seek(568) # LUMP_GAME_LUMP
    offset = int.from_bytes(bsp.read(4), 'little')
    length = int.from_bytes(bsp.read(4), 'little')
    version = int.from_bytes(bsp.read(4), 'little')
    fourCC = int.from_bytes(bsp.read(4), 'little')
    if fourCC != 0:
        raise RuntimeError(f'{MAP} GAME_LUMP is compressed')
        
    bsp.seek(offset)
    game_lump_headers = []
    game_lump_count = int.from_bytes(bsp.read(4), 'little')
    for i in range(game_lump_count):
        game_lump = struct.unpack('4sHHii', bsp.read(16))
        game_lump_headers.append({
            'id': game_lump[0][::-1], # Big-Endian flip
            'flags': game_lump[1],
            'version': game_lump[2],
            'fileofs': game_lump[3],
            'filelen': game_lump[4]})

    for header in game_lump_headers:
        if header['id'] == b'sprp': # static prop game lump
            sprp_version = header['version']
            sprp_offset = header['fileofs']
            sprp_length = header['filelen']
            sprp_flags = header['flags']
            break
        
##    if sprp_flags == 1: # packed KEEP TRYING
##        raise RuntimeError(f'{MAP} SPRP_LUMP is compressed')
##        bsp.seek(sprp_offset + 8) 
##        fourCC = int.from_bytes(bsp.read(4), 'little') # lzma_header_t lzmaSize
##        bsp.seek(sprp_offset + 17)
##        lzma_header = fourCC.to_bytes(4, 'little') + sprp_length.to_bytes(4, 'little')
##        lump = lzma.decompress(lzma_header + bsp.read(fourCC))
##    else:
##        bsp.seek(offset)
##        lump = bsp.read(length)
        
    bsp.seek(sprp_offset)
    sprp_lump = bsp.read(sprp_length)
    sprp_dict_len = int.from_bytes(sprp_lump[:4], 'little') * 128
    for name in struct.iter_unpack('128s', sprp_lump[4:sprp_dict_len + 4]):
        props.add(name[0].decode('utf-8', 'ignore').strip('\x00'))

    bsp.seek(8) # LUMP_ENTITIES
    offset = int.from_bytes(bsp.read(4), 'little')
    length = int.from_bytes(bsp.read(4), 'little')
    version = int.from_bytes(bsp.read(4), 'little')
    fourCC = int.from_bytes(bsp.read(4), 'little')
    if fourCC != 0:
        raise RuntimeError(f'{MAP} ENTITIES_LUMP is Packed!')
    
    bsp.seek(offset)
    raw_entities = bsp.read(length).decode('ascii').replace('{', '').split('}')[:-1]
    entities = []
    for entity in raw_entities:
        entity = entity.lstrip('\n').rstrip('\n')
        entity = entity.split('\n')
        entity_dict = dict()
        for line in entity:
            try:
                key, value = line.strip('"').split('" "')
            except ValueError:
                key = line.strip('"').rstrip('" ""')
                value = None
            except Exception as exc:
                print(line)
                raise exc
            entity_dict[key] = value
        entities.append(entity_dict)
    prop_entities = [e for e in entities if e['classname'].startswith('prop_')]

    for prop in prop_entities:
        props.add(prop['model'])

    bsp.seek(696) # LUMP_TEXDATA_STRING_DATA
    offset = int.from_bytes(bsp.read(4), 'little')
    length = int.from_bytes(bsp.read(4), 'little')
    version = int.from_bytes(bsp.read(4), 'little')
    fourCC = int.from_bytes(bsp.read(4), 'little')
    if fourCC != 0:
        raise RuntimeError(f'{MAP} TEXDATA_STRING_DATA_LUMP is Packed!')
    bsp.seek(offset)
    for material in bsp.read(length).decode('utf-8', 'ignore').split('\0')[:-1]:
        materials.add(material)

# ALL PROPS IN 2007 RELEASE MAPS
outfile = open('2007_props.csv', 'w')
buffer = ''
for prop in props:
    buffer += f'{prop.upper()},' # slam to uppercase for compares
    if len(buffer) > 8096:
        outfile.write(buffer)
        buffer = ''
outfile.close()

# ALL MATERIALS IN 2007 RELEASE MAPS
outfile = open('2007_materials.csv', 'w')
buffer = ''
for material in materials:
    buffer += f'{material.upper()},' # slam to uppercase for compares
    if len(buffer) > 8096:
        outfile.write(buffer)
        buffer = ''
outfile.close()
