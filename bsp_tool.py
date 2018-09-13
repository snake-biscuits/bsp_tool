# www.gamedev.net/forums/topic/230012-eliminating-discontinuities-t-junctions-in-bsp/
# what impact would rewriting a bsp with fixed t-juncts have?
#
# source_sdk_2013/mp/src/utils/vbsp/writebsp.cpp
# source_sdk_2013/mp/src/utils/vbsp/map.cpp
#
# LUMP_PAKFILE is never compressed. ? really ?
# LUMP_GAME_LUMP is compressed in individual segments.
# The compressed size of a game lump can be determined by subtracting the
# current game lump's offset with that of the next entry. For this reason,
# the last game lump is always an empty dummy which only contains the offset.
# IMPLEMENT vmf_tool namespace class (visually cleaner attribute access)
import collections
import enum
import itertools
import lzma
import struct
import time
import vector

class DISPTRI(enum.Enum):
    TAG_SURFACE = 0x1
    TAG_WALKABLE = 0x2
    TAG_BUILDABLE = 0x4
    FLAG_SURFPROP1 = 0x8
    FLAG_SURFPROP2 = 0x10

class emit(enum.Enum):
    surface = 0    # 90 degree spotlight
    point = 1      # simple point light source
    spotlight = 2  # spotlight with penumbra
    skylight = 3   # directional light with no falloff (surface must trace to SKY texture)
    quakelight = 4 # linear falloff, non-lambertian
    skyambient = 5 # spherical light source with no falloff (surface must trace to SKY texture)

class LUMP(enum.Enum):
    ENTITIES = 0        # *
    PLANES = 1          # *
    TEXDATA = 2         # *
    VERTICES = 3        # *
    VISIBILITY = 4      # *
    NODES = 5           # *
    TEXINFO = 6         # *
    FACES = 7           # *
    LIGHTING = 8        # *
    OCCLUSION = 9
    LEAVES = 10         # *
    FACEIDS = 11
    EDGES = 12          # *
    SURFEDGES = 13      # *
    MODELS = 14         # *
    WORLD_LIGHTS = 15   # *
    LEAF_FACES = 16     # *
    LEAF_BRUSHES = 17   # *
    BRUSHES = 18        # *
    BRUSH_SIDES = 19    # *
    AREAS = 20          # *
    AREA_PORTALS = 21   # *
    UNUSED0 = 22
    UNUSED1 = 23
    UNUSED2 = 24
    UNUSED3 = 25
    DISP_INFO = 26
    ORIGINAL_FACES = 27
    PHYS_DISP = 28
    PHYS_COLLIDE = 29
    VERT_NORMALS = 30
    VERT_NORMAL_INDICES = 31
    DISP_LIGHTMAP_ALPHAS = 32 # WHAT?
    DISP_VERTS = 33
    DISP_LIGHTMAP_SAMPLE_POSITIONS = 34 # For each displacement
					#    For each lightmap sample
					#      byte for index
					#      if 255, then index = next byte + 255
					#      3 bytes for barycentric coordinates
    # The game lump is a method of adding game-specific lumps (tf2 props)
	# FIXME: Eventually, all lumps could use the game lump system
    GAME_LUMP = 35
    LEAF_WATER_DATA = 36
    PRIMITIVES = 37
    PRIM_VERTS = 38
    PRIM_INDICES = 39
    # A pak file can be embedded in a .bsp now, and the file system will search the pak
	#  file first for any referenced names, before deferring to the game directory
	#  file system/pak files and finally the base directory file system/pak files.
    PAKFILE = 40
    CLIP_PORTAL_VERTS = 41
    # A map can have a number of cubemap entities in it
    # which cause cubemap renders to be taken after running vrad.
    CUBEMAPS = 42
    TEXDATA_STRING_DATA = 43
    TEXDATA_STRING_TABLE = 44
    OVERLAYS = 45
    LEAF_MIN_DIST_TO_WATER = 46
    FACE_MARCO_TEXTURE_INFO = 47
    DISP_TRIS = 48
    PHYS_COLLIDE_SURFACE = 49       # deprecated.  We no longer use win32-specific havok compression on terrain
    WATER_OVERLAYS = 50
    LEAF_AMBIENT_INDEX_HDR = 51     # index of LUMP_LEAF_AMBIENT_LIGHTING_HDR
    LEAF_AMBIENT_INDEX = 52         # index of LUMP_LEAF_AMBIENT_LIGHTING
    # optional HDR lumps
    LIGHTING_HDR = 53
    WORLD_LIGHTS_HDR = 54
    LEAF_AMBIENT_LIGHTING_HDR = 55  # NOTE: this data overrides part of the data stored in LUMP_LEAFS.
    LEAF_AMBIENT_LIGHTING = 56      # NOTE: this data overrides part of the data stored in LUMP_LEAFS.

    XZIP_PAKFILE = 57               # deprecated. xbox 1: xzip version of pak file
    FACES_HDR = 58                  # HDR maps may have different face data.
    MAP_FLAGS = 59                  # extended level-wide flags. not present in all levels
    OVERLAY_FADES = 60              # Fade distances for overlays
    UNUSED4 = 61    #LUMP_OVERLAY_SYSTEM_LEVELS (L4D1)
    UNUSED5 = 62    #LUMP_PHYSLEVEL             (L4D2)
    UNUSED6 = 63    #LUMP_DISP_MULTIBLEND       (AS)

class VERSION(enum.Enum):
    LUMP_LIGHTING = 1
    LUMP_FACES = 1
    LUMP_OCCLUSION = 2
    LUMP_LEAFS = 1
    LUMP_LEAF_AMBIENT_LIGHTING = 1

lump_address = {LUMP_ID: (8 + i * 16) for i, LUMP_ID in enumerate(LUMP)}

def read_lump(file, lumpid):
    file.seek(lump_address[lumpid])
    offset = int.from_bytes(file.read(4), 'little')
    length = int.from_bytes(file.read(4), 'little')
    version = int.from_bytes(file.read(4), 'little')
    fourCC = int.from_bytes(file.read(4), 'little')
    if length != 0:
        if fourCC == 0:
            file.seek(offset)
            return file.read(length)
        else:
            file.seek(offset + 17) # SKIP lzma_header_t
            try:
                decompressed_lump = lzma.decompress(file.read(fourCC))
            except:
                raise RuntimeError(f'Error decompressing {lumpid.name}!')
            if len(decompressed_lump) != fourCC:
                raise RuntimeError(f'{lumpid.name} decompressed to {len(decompressed_lump)}, not {fourCC} as expected')
            else:
                return decompressed_lump

lump_header = collections.namedtuple('lump_header', ['offset', 'length' ,'version', 'fourCC'])

class bsp():
    def __init__(self, file):
        if not file.endswith('.bsp'):
            file += '.bsp'
        file.replace('\\', '/')
        split_file = file.rpartition('/')
        self.filename = split_file[-1]
        self.filepath = f'{split_file[0]}/'
        file = open(file, 'rb')
        if file.read(4) != b'VBSP':
            raise RuntimeError(f"{''.join(split_file)} is not a .bsp!")
        self.bytesize = len(file.read()) + 4
        self.lump_map = {}
        start_time = time.time()
        for ID in LUMP:
            data = read_lump(file, ID)
            if data is not None:
                file.seek(lump_address[ID])
                self.lump_map[ID] = lump_header(*[int.from_bytes(file.read(4), 'little') for i in range(4)])
                setattr(self, 'RAW_' + ID.name, data)

        self.BRUSHES = []
        for brush in struct.iter_unpack('3i', self.RAW_BRUSHES):
            self.BRUSHES.append({
                'firstside': brush[0],
                'numsides': brush[1],
                'contents': brush[2]
                })
        del self.RAW_BRUSHES

        self.BRUSH_SIDES = []
        for brush_side in struct.iter_unpack('H3h', self.RAW_BRUSH_SIDES):
            self.BRUSH_SIDES.append({
                'planenum': brush_side[0], #faces out of leaf
                'texinfo': brush_side[1],
                'dispinfo': brush_side[2], #bspversion 7
                'bevel': brush_side[3] #is side a bevel plane? bspversion 7
                })
        del self.RAW_BRUSH_SIDES

        if hasattr(self, 'RAW_CUBEMAPS'):
            self.CUBEMAPS = []
            for cubemap_sample in struct.iter_unpack('4i', self.RAW_CUBEMAPS):
                self.CUBEMAPS.append({
                    'origin': cubemap_sample[:3],
                    'size': cubemap_sample[3]
                    })
            del self.RAW_CUBEMAPS, cubemap_sample

        if hasattr(self, 'RAW_DISP_INFO'):
            self.DISP_INFO = []
            for dispinfo in struct.iter_unpack('3f4ifiH2i88c10I', self.RAW_DISP_INFO):
                self.DISP_INFO.append({
                    'startPosition': dispinfo[:3],
                    'DispVertStart': dispinfo[3],
                    'DispTriStart': dispinfo[4],
                    'power': dispinfo[5], #subdivs = 2^power
                    'minTess': dispinfo[6],
                    'smoothingAngle': dispinfo[7],
                    'contents': dispinfo[8],
                    'MapFace': dispinfo[9],
                    'LightmapAlphaStart': dispinfo[10],
                    'LightmapSamplePositionStart': dispinfo[11],
                    #EdgeNeighbours iter_unpack
                    'EdgeNeighbours': [b''.join(dispinfo[12:23]), b''.join(dispinfo[23:34]),
                                       b''.join(dispinfo[34:45]), b''.join(dispinfo[45:56])],
                                        #bool  isValid #'?H3BH3B'
                                        #SubNeighbours[2] #'H3B'
                                        #  unsigned short  Neighbour              #DISP_INFO index
                                        #  unsigned char   NeighbourOrientation   #(CCW) rotation of the neighbor wrt this displacement
                                        #  unsigned char   Span                   #Where the neighbor fits onto this side of our displacement
                                        #  unsigned char   Neighbout Span         #Where we fit onto our neighbor
                    #CornerNeighbours iter_unpack
                    'CornerNeighbours': [b''.join(dispinfo[56:67]), b''.join(dispinfo[67:78]),
                                         b''.join(dispinfo[78:89]), b''.join(dispinfo[89:100])],
                                        #
                    'AllowedVerts': dispinfo[100:]
                })
            del self.RAW_DISP_INFO, dispinfo

        if hasattr(self, 'RAW_DISP_TRIS'):
            self.DISP_TRIS = struct.iter_unpack('H', self.RAW_DISP_TRIS)
            del self.RAW_DISP_TRIS

        if hasattr(self, 'RAW_DISP_VERTS'):
            self.DISP_VERTS = []
            for dispvert in struct.iter_unpack('5f', self.RAW_DISP_VERTS):
                self.DISP_VERTS.append({
                    'vec': dispvert[:3],
                    'dist': dispvert[3],
                    'alpha': dispvert[4]
                })
            del self.RAW_DISP_VERTS, dispvert

        self.EDGES = []
        for edge in struct.iter_unpack('2h', self.RAW_EDGES):
            self.EDGES.append(list(edge))
        del self.RAW_EDGES, edge

        self.ENTITIES = self.RAW_ENTITIES[:-2]
        self.ENTITIES = self.ENTITIES.decode()
        #convert to dictionary
        #use vmf_tool importer

        self.FACES = []
        for face in struct.iter_unpack('H2bi4h4bif5i2HI', self.RAW_FACES):
            self.FACES.append({
                'planenum': face[0],
                'side': face[1],
                'onNode': bool(face[2]),
                'firstedge': face[3],
                'numedges': face[4],
                'texinfo': face[5],
                'dispinfo': face[6],
                'surfaceFogVolumeID': face[7],
                'styles': face[8:12],
                'lightofs': face[12],
                'area': face[13],
                'LightmapTextureMinsinLuxels': face[14:16],
                'LightmapTextureSizeinLuxels': face[16:18],
                'origFace': face[18],
                'numPrims': face[19],
                'firstPrimID': face[20],
                'smoothingGroups': face[21]
            })
        del self.RAW_FACES, face

    #GAME LUMP(S)
##    glump_headers = []
##    glump_count = int.from_bytes(file.read(4), 'little')
##    for i in range(glump_count):
##        glump = file.read(16)
##        glump = struct.unpack('iHHii', glump)
##        glump_headers.append({
##            'id': abs(glump[0]).to_bytes(4, 'big'),
##            'flags': glump[1],
##            'version': glump[2],
##            'fileofs': glump[3],
##            'filelen': glump[4]})
##    for header in glump_headers:
##        if header['id'] == b'sprp': #static prop lump
##            sprp_version = header['version']
##            sprp_offset = header['fileofs']
##            sprp_length = header['filelen']
##            sprp_flags = header['flags']
##            break
##    try:
##        file.seek(sprp_offset)
##    except NameError:
##        raise RuntimeError('.bsp file has no static prop game lump')
##    if sprp_flags == 1:
##        raise NotImplementedError("Can't decompress the sprp lump just yet, use:\nbspzip -repack <bspfile> and try again")
##    sprp_dict_len = int.from_bytes(file.read(4), 'little') * 128
##    try:
##        sprp_dict = file.read(sprp_dict_len)
##    except MemoryError:
##        raise RuntimeError("You can't just load " + str(round(sprp_dict_len / 1024**2, 2)) + 'MB!')
##    sprp_dict = struct.iter_unpack('128s', sprp_dict)
##    sprp_names = [name[0].decode().strip('\x00') for name in sprp_dict] #sprp_names
##    sprp_leaves_len = int.from_bytes(file.read(4), 'little') * 2
##    sprp_leaves = file.read(sprp_leaves_len)
##    sprp_leaves = struct.iter_unpack('H', sprp_leaves)
##    sprp_lump_len = int.from_bytes(file.read(4), 'little')
##    self.STATIC_PROPS = []
##    for static_prop in struct.iter_unpack('6f3H2Bi6f8Bf', 'sprp_lump')
##        self.STATIC_PROPS.append({
##            'pos': static_prop[:3],
##            'angles': [static_prop[3:6][0], -static_prop[3:6][2], static_prop[3:6][1] + 90], #XYZ >>> Y -X Z+90
##            'model': sprp_names[static_prop[6]],
##            'first leaf': static_prop[7],
##            'leaf count': static_prop[8],
##            'solid': static_prop[9],
##            'flags': static_prop[10],
##            'skin': static_prop[11],
##            'fademindist': static_prop[12], #to match prop_dynamic
##            'fademaxdist': static_prop[13],
##            'lighting origin': static_prop[14:17],
##            'force fade scale': static_prop[17],
##            'min CPU level': static_prop[18],
##            'max CPU level': static_prop[19],
##            'min GPU level': static_prop[20],
##            'max GPU level': static_prop[21],
##            'diffuse': static_prop[22:26],
##            'unknown': static_prop[26],
##            'type': 'prop_static'
##            })

        self.LEAF_FACES = list(itertools.chain(*struct.iter_unpack('H', self.RAW_LEAF_FACES)))
        del self.RAW_LEAF_FACES

        self.LEAVES = [] #Map Version < 20 is different
        for leaf in struct.iter_unpack('i8h4H2h', self.RAW_LEAVES):
            self.LEAVES.append({
                    'contents': leaf[0],
                    'cluster': leaf[1],
                    'area': leaf[2] & 0xFF80 >> 7, #9 bits
                    'flags': leaf[2] & 0x007F, #7 bits
                    'mins': leaf[3:6],
                    'maxs': leaf[6:9],
                    'firstleafface': leaf[9],
                    'numleaffaces': leaf[10],
                    'firstleafbrush': leaf[11],
                    'numleafbrushes': leaf[12],
                    'leafWaterDataID': leaf[13], #-1 for not in water
                    'padding': leaf[14]
                    })
        del self.RAW_LEAVES, leaf

        self.LIGHTING = self.RAW_LIGHTING
        del self.RAW_LIGHTING

        if hasattr(self, 'RAW_LIGHTING_HDR'):
            self.LIGHTING_HDR = self.RAW_LIGHTING_HDR
            del self.RAW_LIGHTING_HDR

        self.NODES = []
        for node in struct.iter_unpack('3i6h2H2h', self.RAW_NODES):
            self.NODES.append({
                'planenum': node[0],
                'children': node[1:3],
                'mins': node[3:6],
                'maxs': node[6:9],
                'firstface': node[9],
                'numfaces': node[10],
                'area': node[11], #index
                'padding': node[12:]
            })
        del self.RAW_NODES, node

        self.ORIGINAL_FACES = [] #namedtuple?
        for original_face in struct.iter_unpack('H2bi4h4bif5i2HI', self.RAW_ORIGINAL_FACES):
            self.ORIGINAL_FACES.append({
                'planenum': original_face[0],
                'side': original_face[1],
                'onNode': bool(original_face[2]),
                'firstedge': original_face[3],
                'numedges': original_face[4],
                'texinfo': original_face[5],
                'dispinfo': original_face[6],
                'surfaceFogVolumeID': original_face[7],
                'styles': original_face[8:12],
                'lightofs': original_face[12],
                'area': original_face[13],
                'LightmapTextureMinsinLuxels': original_face[14:16],
                'LightmapTextureSizeinLuxels': original_face[16:18],
                'origFace': original_face[18],
                'numPrims': original_face[19],
                'firstPrimID': original_face[20],
                'smoothingGroups': original_face[21]
            })
        del self.RAW_ORIGINAL_FACES, original_face

##        self.PAKFILE = []
        #ZIP_EndOfCentralDirRecord
	#uint	signature  b'PK\x05\x06'
	#ushort	numberOfThisDisk
	#ushort	numberOfTheDiskWithStartOfCentralDirectory
	#ushort	nCentralDirectoryEntries_ThisDisk
	#ushort	nCentralDirectoryEntries_Total
	#uint	centralDirectorySize
	#uint	startOfCentralDirOffset
	#ushort	commentLength
	#char   comment[commentLength]

	#ZIP_FileHeader
	#uint   signature  b'PK\x01\x02'
	#ushort versionMadeBy
	#ushort versionNeededtoExtract
	#ushort flags
	#ushort compressionMethod
	#ushort lastModifiedTime
	#ushort lastModifiedTime
	#uint   crc32
	#uint   compressedSize
	#uint   uncompressedSize
	#ushort fileNameLength
	#ushort extraFieldLength
	#ushort fileCommentLength
	#ushort diskNumberStart
	#ushort internalFileAttribs
	#uint   externalFileAttribs
	#uint   relativeOffestofLocalHeader
	#char   fileName[fileNameLength]
	#char   extraField[extraFieldLength]
	#char   fileComment[fileCommentLength]

	#ZIP_LocalFileHeader
	#uint   signature  b'PK\x03\x04'
	#ushort versionNeededtoExtract
	#ushort flags
	#ushort lastModifiedTime
	#ushort lastModifiedDate
	#uint   crc-32
	#uint   compressedSize
	#uint   uncompressedSize
	#ushort fileNameLength
	#ushort extraFieldLength
	#char   fileName[fileNameLength]
        #char   extraField[extraFieldLength]
##        del self.RAW_PAKFILE

        self.PLANES = []
        for plane in struct.iter_unpack('4fi', self.RAW_PLANES):
            self.PLANES.append({
                'normal': plane[:3],
                'dist': plane[3],
                'type': plane[4]
            })
        del self.RAW_PLANES, plane

        self.SURFEDGES =  list(itertools.chain(*struct.iter_unpack('i', self.RAW_SURFEDGES)))
        del self.RAW_SURFEDGES

        self.TEXDATA = []
        for texdata in struct.iter_unpack('3f5i', self.RAW_TEXDATA):
            self.TEXDATA.append({
                'reflectivity': texdata[:3],
                'texdata_st': texdata[3],
                'width': texdata[4],
                'height': texdata[5],
                'view_width': texdata[6],
                'view_height': texdata[7]
            })
        del self.RAW_TEXDATA, texdata

        self.TEXDATA_STRING_DATA = self.RAW_TEXDATA_STRING_DATA.decode('utf-8', 'ignore').split('\0')[:-1]
        del self.RAW_TEXDATA_STRING_DATA
        #occasionally contains random undecodeable bytes
        #e.g. pl_upward begins b'\xff\xff \x00\x00\x00\x00\x00\x00'

        self.TEXDATA_STRING_TABLE = list(itertools.chain(*struct.iter_unpack('i', self.RAW_TEXDATA_STRING_TABLE)))
        del self.RAW_TEXDATA_STRING_TABLE

        self.TEXINFO = []
        for texinfo in struct.iter_unpack('16f2i', self.RAW_TEXINFO):
            self.TEXINFO.append({
                'textureVecs': [texinfo[:4], texinfo[4:8]],      #[s/t][xyz offset]
                'lightmapVecs': [texinfo[8:12], texinfo[12:16]], #[s/t][xyz offset] - length is in units of texels/area
                'flags': texinfo[16],   #mip flags
                'texdata': texinfo[17]
            })
        del self.RAW_TEXINFO, texinfo

        self.VERTICES = []
        for vertex in struct.iter_unpack('3f', self.RAW_VERTICES):
            self.VERTICES.append(list(vertex))
        del self.RAW_VERTICES, vertex

        self.WORLD_LIGHTS = []
        for world_light in struct.iter_unpack('9f3i7f3i', self.RAW_WORLD_LIGHTS):
            self.WORLD_LIGHTS.append({
                'origin': world_light[:3],
                'intensity': world_light[3:6],
                'normal': world_light[6:9],
                'cluster': world_light[9],
	            'type': world_light[10], #emit enum
                'style': world_light[11],
                'stopdot': world_light[12], #start of penumbra for emit_spotlight
                'stopdot2': world_light[13], #end of penumbra for emit_spotlight
                'exponent': world_light[14],
                'radius': world_light[15], #cuttof distance
                 # falloff for emit_spotlight + emit_point:
            	 # 1 / (constant_attn + linear_attn * dist + quadratic_attn * dist^2)
                'constant_attn': world_light[16],
                'linear_attn': world_light[17],
                'quadratic_attn': world_light[18],
                'flags': world_light[19], #Uses a combination of the DWL_FLAGS_ defines.
                'texinfo': world_light[20],
                'owner': world_light[21] #positional parent
            })
        del self.RAW_WORLD_LIGHTS, world_light

        if hasattr(self, 'RAW_WORLD_LIGHTS_HDR'):
            self.WORLD_LIGHTS_HDR = []
            for hdr_world_light in struct.iter_unpack('9f3i7f3i', self.RAW_WORLD_LIGHTS_HDR):
                self.WORLD_LIGHTS.append({
                    'origin': hdr_world_light[:3],
                    'intensity': hdr_world_light[3:6],
                    'normal': hdr_world_light[6:9],
                    'cluster': hdr_world_light[9],
                    'type': hdr_world_light[10], #emit enum
                    'style': hdr_world_light[11],
                    'stopdot': hdr_world_light[12], #start of penumbra for emit_spotlight
                    'stopdot2': hdr_world_light[13], #end of penumbra for emit_spotlight
                    'exponent': hdr_world_light[14],
                    'radius': hdr_world_light[15], #cuttof distance
                    # falloff for emit_spotlight + emit_point:
                    # 1 / (constant_attn + linear_attn * dist + quadratic_attn * dist^2)
                    'constant_attn': hdr_world_light[16],
                    'linear_attn': hdr_world_light[17],
                    'quadratic_attn': hdr_world_light[18],
                    'flags': hdr_world_light[19], #Uses a combination of the DWL_FLAGS_ defines.
                    'texinfo': hdr_world_light[20],
                    'owner': hdr_world_light[21] #positional parent
                })
            del self.RAW_WORLD_LIGHTS_HDR, hdr_world_light

        file.close()
        unpack_time = time.time() - start_time
        print(f'Imported {self.filename} in {unpack_time:.2f} seconds')

    def verts_of(self, face): # why so many crazy faces?
        """vertex format [Position, Normal, TexCoord, LightCoord, Colour]"""
        texinfo = self.TEXINFO[face['texinfo']]
        texdata = self.TEXDATA[texinfo['texdata']]
        texvecs = texinfo['textureVecs']
        lightvecs = texinfo['lightmapVecs']
        verts, uvs, uv2s = [], [], []
        first_edge = face['firstedge']
        for surfedge in self.SURFEDGES[first_edge:first_edge + face['numedges']]:
            edge = self.EDGES[surfedge] if surfedge >= 0 else self.EDGES[-surfedge][::-1]
            verts.append(self.VERTICES[edge[0]])
            verts.append(self.VERTICES[edge[1]])
        #verts[::2] is faster. why is this approach used?
        # verts = [tuple(v) for v in verts]
        # verts = {v: None for v in verts}
        # verts = [list(v) for v in verts]
        verts = verts[::2]
        # github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
        # SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
        for vert in verts:
            uv = [vector.dot(vert, texvecs[0][:-1]) + texvecs[0][3],
                  vector.dot(vert, texvecs[1][:-1]) + texvecs[1][3]]
            uv[0] /= texdata['view_width']
            uv[1] /= texdata['view_height']
            uvs.append(vector.vec2(*uv))
            uv2 = [vector.dot(vert, lightvecs[0][:-1]) + lightvecs[0][3],
                   vector.dot(vert, lightvecs[1][:-1]) + lightvecs[1][3]]
            uv2[0] -= face['LightmapTextureMinsinLuxels'][0]
            uv2[1] -= face['LightmapTextureMinsinLuxels'][1]
            try:
                uv2[0] /= face['LightmapTextureSizeinLuxels'][0]
                uv2[1] /= face['LightmapTextureSizeinLuxels'][1]
            except ZeroDivisionError:
                uv2 = [0, 0]
            uv2s.append(uv2)
        vert_count = len(verts)
        normal = [self.PLANES[face['planenum']]['normal']] * vert_count
        colour = [texdata['reflectivity']] * vert_count
        verts = list(zip(verts, normal, uvs, uv2s, colour))
        return verts

    def dispverts_of(self, face): # add format argument (lightmap uv, 2 uvs, etc)
        """vertex format [Position, Normal, TexCoord, LightCoord, Colour]
        normal is inherited from face
        returns rows, not tris"""
        verts = self.verts_of(face)
        if len(verts) != 4:
            raise RuntimeError('face does not have 4 corners (probably t-junctions)')
        if face['dispinfo'] == -1:
            raise RuntimeError('face is not a displacement!')
        dispinfo = self.DISP_INFO[face['dispinfo']]
        start = list(dispinfo['startPosition'])
        start = [round(x, 1) for x in start] # approximate match
        round_verts = []
        for vert in [v[0] for v in verts]:
            round_verts.append([round(x, 1) for x in vert])
        if start in round_verts: # "rotate"
            index = round_verts.index(start)
            verts = verts[index:] + verts[:index]
        A, B, C, D = [vector.vec3(*v[0]) for v in verts]
        Auv, Buv, Cuv, Duv = [vector.vec2(*v[2]) for v in verts]
        Auv2, Buv2, Cuv2, Duv2 = [vector.vec2(*v[3]) for v in verts]
        AD = D - A
        ADuv = Duv - Auv
        ADuv2 = Duv2 - Auv2
        BC = C - B
        BCuv = Cuv - Buv
        BCuv2 = Cuv2 - Buv2
        power = dispinfo['power']
        power2 = 2 ** power
        full_power = (power2 + 1) ** 2
        normal = [verts[0][1]] * full_power
        colour = [verts[0][4]] * full_power
        start = dispinfo['DispVertStart']
        stop = dispinfo['DispVertStart'] + full_power
        verts, uvs, uv2s = [], [], []
        for index, dispvert in enumerate(self.DISP_VERTS[start:stop]):
            t1 = index % (power2 + 1) / power2
            t2 = index // (power2 + 1) / power2
            baryvert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
            dispvert = [x * dispvert['dist'] for x in dispvert['vec']]
            verts.append([a + b for a, b in zip(baryvert, dispvert)])
            uvs.append(vector.lerp(Auv + (ADuv * t1), Buv + (BCuv * t1), t2))
            uv2s.append(vector.lerp(Auv2 + (ADuv2 * t1), Buv2 + (BCuv2 * t1), t2))
        verts = list(zip(verts, normal, uvs, uv2s, colour))
        return verts

    def export_lightmap(self):
        out_filename = self.filename + '.rgbe'
        print(f'Writing to {out_filename} ... ', end='')
        file = open(out_filename, 'wb')
        file.write(self.LIGHTING)
        file.close()
        print('Done!')

    def export_sprp_list(self):
        raise NotImplemented('not yet')
        out_filename = self.filename + '.props'
        print(f'Writing to {out_filename}...', end='')
        file = open(out_filename, 'wb')
        #TWO PARTS
        #LIST ALL PROPS ONCE, IN A SPECIFIC CODED ORDER
        #LIST ALL POSITIONS & ROTATIONS (MATCHED TO PREVIOUS CODES)
        #WRITE
        file.close()
        print(' Done!')

    def inject(self, bspfile, lump):
        """bspfile must be opened with 'rb+'"""
        try:
            lump = getattr(self, lump)
        except:
            raise RuntimeError("couldn't find lump")
        #find lump position in bspfile
        #write new lump
        #  sort dicts with map()?
        #  struct.iter_pack
        #save all data after to memory
        #truncate
        #put the end of the file back
        #change lump lengths and startpositions


    def export(self, outfile):
        """expects outfile to be a file with write bytes capability"""
        #converts all current lumps to raw counterparts
        outfile.write(b'VBSP')
        outfile.write((20).to_bytes(4, 'little'))
        offset = 0
        length = 0
        #USE THE LUMP MAP!
        #PRESERVE SOURCE FILE LUMP ORDER
        #dicts to raw lumps
        split_bytes = lambda y: map(lambda x: x.to_bytes(1, 'big'), y)

        pack_brushes = lambda x: struct.pack('3i', x['firstside'], x['numsides'], x['contents'])
        self.RAW_BRUSHES = b''.join(map(pack_brushes, self.BRUSHES))
        pack_brush_sides = lambda x: struct.pack('H3h', x['planenum'], x['texinfo'],
                                                        x['dispinfo'], x['bevel'])
        self.RAW_BRUSH_SIDES = b''.join(map(pack_brush_sides, self.BRUSHSIDES))
        if hasattr(self, 'CUBEMAPS'):
            pack_cubemaps = lambda x: struct.pack('4i', *x['origin'], x['size'])
            self.RAW_CUBEMAPS = b''.join(map(pack_brush_sides, self.BRUSHSIDES))
        if hasattr(self, 'DISP_INFO'):
            pack_disp_info = lambda x: struct.pack('3f4ifiH2i88c10I', *x['startPosition'],
                  x['DispVertStart'], x['DispTriStart'], x['power'], x['minTess'],
                  x['smoothingAngle'], x['contents'], x['MapFace'], x['LightmapAlphaStart'],
                  x['LightmapSamplePositionStart'], *map(split_bytes, x['EdgeNeighbours']),
                  *map(split_bytes, x['CornerNeighbours']), *x['AllowedVerts'])
            self.RAW_DISP_INFO = b''.join(map(pack_brush_sides, self.DISP_INFO))
            pack_disp_tris = lambda x: struct.pack('H', x)
            self.RAW_DISP_TRIS = b''.join(map(pack_disp_tris, self.DISP_TRIS))
            pack_disp_verts = lambda x: struct.pack('5f', *x['vec'], x['dist'], x['alpha'])
            self.RAW_DISP_VERTS = b''.join(map(pack_disp_verts, self.DISP_VERTS))
        pack_edges = lambda x: struct.pack('2h', *x)
        self.RAW_EDGES = b''.join(pack_edges, self.EDGES)
        self.RAW_ENTITIES = self.ENTITIES.encode('ascii')
        pack_faces = lambda x: struct.pack('H2bi4h4bif5i2HI', x['planenum'], x['side'],
              x['onNode'], x['firstedge'], x['numedges'], x['texinfo'], x['dispinfo'],
              x['surfaceFogVolumeID'], *x['styles'], x['lightofs'], x['area'],
              *x['LightmapTextureMinsinLuxels'], *['LightmapTextureSizeinLuxels'],
              x['origFace'], x['numPrims'], x['firstPrimID'], x['smoothingGroups'])
        self.RAW_FACES = b''.join(map(pack_faces, self.FACES))
        pack_leaf_faces = lambda x: struct.pack('H', x)
        self.RAW_LEAF_FACES = b''.join(map(pack_leaf_faces, self.LEAF_FACES))
        pack_leaves = lambda x: struct.pack('i8h4H2h', x['contents'],
              x['area'] << 7 + x['flags'], #'area' is 9 bits, and 'flags' is 7
              *x['mins'], *x['maxs'], x['firstleafface'], x['firstleafbrush'],
              x['numleafbrushes'], x['leafWaterDataID'], x['padding'])
        self.RAW_LEAVES = b''.join(map(pack_leaves, self.LEAVES))
        self.RAW_LIGHTING = self.LIGHTING
        if hasattr(self, 'LIGHTING_HDR'):
            self.RAW_LIGHTING_HDR = self.LIGHTING_HDR
        pack_nodes = lambda x: struct.pack('3i6h2H2h', x['planenum'], *x['children'],
              *x['mins'], *x['maxs'], x['firstface'], x['numfaces'], x['area'], x['padding'])
        self.RAW_NODES = b''.join(map(pack_nodes, self.NODES))
        self.RAW_ORIGINAL_FACES = b''.join(map(pack_faces, self.ORIGINAL_FACES))
        pack_planes = lambda x: struct.pack('4fi', x['normal'], x['dist'], x['type'])
        self.RAW_PLANES = b''.join(map(pack_planes, self.PLANES))
        pack_surfedges = lambda x: struct.pack('i', x)
        self.RAW_SURFEDES = b''.join(map(pack_surfedges, self.SURFEDGES))
        pack_texdata = lambda x: struct.pack('3f5i', *x['reflectivity'], x['texdata_st'],
              x['width'], x['height'], x['view_width'], x['view_height'])
        self.RAW_TEXDATA = b''.join(map(pack_texdata, self.TEXDATA))
        pack_texdata_st = lambda x: struct.pack('i', x)
        self.RAW_TEXDATA_STRING_TABLE = b''.join(map(pack_texdata_st, self.TEXDATA_STRING_TABLE))
        pack_texdata_sd = lambda x: struct.pack('128s', x.encode('ascii'))
        self.RAW_TEXDATA_STRING_DATA = b''.join(map(pack_texdata_sd, self.TEXDATA_STRING_DATA))
        pack_texinfo = lambda x: struct.pack('16f2i', *x['textureVecs'][0], *x['textureVecs'][1],
              *x['lightmapVecs'][0], *x['lightmapVecs'][1], x['flags'], x['texdata'])
        self.RAW_TEXINFO = b''.join(map(pack_texinfo, self.TEXINFO))
        pack_vertices = lambda x: struct.pack('3f', *x)
        self.RAW_VERTICES = b''.join(map(pack_vertices, self.VERTICES))
        pack_world_lights = lambda x: struct.pack('9f3i7f3i', *x['origin'], *x['intensity'],
              *x['normal'], x['cluster'], x['type'], x['style'], x['stopdot'], x['stopdot2'],
              x['exponent'], x['radius'], x['constant_attn'], x['quadratic_attn'],
              x['flags'], x['texinfo'], x['owner'])
        self.RAW_WORLD_LIGHTS = b''.join(map(pack_world_lights, self.WORLD_LIGHTS))
        if hasattr(self, 'WORLD_LIGHTS_HDR'):
            self.RAW_WORLD_LIGHTS_HDR = b''.join(map(pack_world_lights, self.WORLD_LIGHTS_HDR))
        #headers
        for ID in LUMP: #entities should be written last
            outfile.write(offset.to_bytes(4, 'little'))
            length = len(getattr(self, ID.name, 'RAW_' + ID.name)) #only lumps we have
            offset += length
            outfile.write(b'0000') #lump version (actually important)
            outfile.write(b'0000') #lump fourCC
        #lump orders and spacing are very important
        for ID in LUMP:
            #these cursor locations and datasize need to go into headers
            outfile.write(getattr(self, ID.name, 'RAW_' + ID.name))
        outfile.write(b'0001') #map revision

    def export_obj(self, outfile): #TODO: write .mtl for each vmt
        start_time = time.time()
        out_filename = outfile.name.split('/')[-1] if '/' in outfile.name else outfile.name.split('\\')[-1]
        total_faces = len(self.FACES)
        print(f'Exporting {self.filename} to {out_filename} ({total_faces} faces)')
        outfile.write('# bsp_tool.py generated model\n')
        outfile.write(f'# source file: {self.filename}\n')
        vs = []
        v_count = 1
        vts = []
        vt_count = 1
        vns = []
        vn_count = 1
        faces_by_material = {} # {material: [face, ...], ...}
        disps_by_material = {} # {material: [face, ...], ...}
        for face in self.FACES:
            material = self.TEXDATA_STRING_DATA[self.TEXDATA[self.TEXINFO[face['texinfo']]['texdata']]['texdata_st']]
            if face['dispinfo'] != -1:
                if material not in disps_by_material:
                    disps_by_material[material] = []
                disps_by_material[material].append(face)
            else:
                if material not in faces_by_material:
                    faces_by_material[material] = []
                faces_by_material[material].append(face)
        face_count = 0
        current_progress = 0.1
        print('0...', end='')

        for material in faces_by_material:
            outfile.write(f'usemtl {material}\n')
            for face in faces_by_material[material]:
                face_vs = self.verts_of(face)
                vn = face_vs[0][1]
                if vn not in vns:
                    vns.append(vn)
                    outfile.write(f'vn {vector.vec3(*vn):}\n')
                    vn = vn_count
                    vn_count += 1
                else:
                    vn = vns.index(vn) + 1
                f = []
                for vertex in face_vs:
                    v = vertex[0]
                    if v not in vs:
                        vs.append(v)
                        outfile.write(f'v {vector.vec3(*v):}\n')
                        v = v_count
                        v_count += 1
                    else:
                        v = vs.index(v) + 1
                    vt = vertex[2]
                    if vt not in vts:
                        vts.append(vt)
                        outfile.write(f'vt {vector.vec2(*vt):}\n')
                        vt = vt_count
                        vt_count += 1
                    else:
                        vt = vts.index(vt) + 1
                    f.append((v, vt, vn))
                outfile.write('f ' + ' '.join([f'{v}/{vt}/{vn}' for v, vt, vn in reversed(f)]) + '\n')
                face_count += 1
                if face_count >= total_faces * current_progress:
                    print(f'{current_progress * 10:.0f}...', end='')
                    current_progress += 0.1

        disp_no = 0
        outfile.write('g displacements\n')
        for material in disps_by_material:
            outfile.write(f'usemtl {material}\n')
            for displacement in disps_by_material[material]:
                outfile.write(f'o displacement_{disp_no}\n')
                disp_no += 1
                disp_vs = self.dispverts_of(displacement)
                normal = disp_vs[0][1]
                if normal not in vns:
                    vns.append(normal)
                    outfile.write(f'vn {vector.vec3(*normal):}\n')
                    normal = vn_count
                    vn_count += 1
                else:
                    normal = vns.index(normal) + 1
                f = []
                for v, vn, vt, vt2, colour in disp_vs:
                    obj_file.write(f'v {vector.vec3(*v):}\nvt {vector.vec2(*vt):}\n')
                power = bsp_file.DISP_INFO[displacement['dispinfo']]['power']
                disp_size = (2 ** power + 1) ** 2
                tris = disp_tris(range(disp_size), power)
                for a, b, c in zip(tris[::3], tris[1::3], tris[2::3]):
                    a = (a + v_count, a + vt_count, normal)
                    b = (b + v_count, b + vt_count, normal)
                    c = (c + v_count, c + vt_count, normal)
                    a, b, c = [map(str, i) for i in (c, b, a)]
                    obj_file.write(f"f {'/'.join(a)} {'/'.join(b)} {'/'.join(c)}\n")
                v_count += disp_size
                vt_count += disp_size
                face_count += 1
                if face_count >= total_faces * current_progress:
                    print(f'{current_progress * 10:.0f}...', end='')
                    current_progress += 0.1

        total_time = time.time() - start_time
        minutes = total_time // 60
        seconds = total_time - minutes * 60
        outfile.write(f'# file generated in {minutes:.0f} minutes {seconds:2.3f} seconds')
        print('Done!')

    def tf2m_compliance_test(self, mdls, vmts):
        passes = True
        cubemaps = False
        if self.LIGHTING.replace(b'\x00', b'') == b'':
            print(self.filename[:-4], 'is fullbright')
            passes = False
        try:
            getattr(self, 'CUBEMAPS')
            cubemaps = True
        except AttributeError:
            print(self.filename, 'has no cubemaps')
            #check all samples are in pakfile
            #warn if no HDR cubemaps are present
            #maps/mapname/texdir/texture_X_Y_Z.vmt
        if self.RAW_PAKFILE == b'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x00XZP1 0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            if cubemaps:
                print(f"{self.filename[:-4]}'s cubemaps are not compiled")
            else:
                print(self.filename[:-4], 'has no packed assets')
        else:
            if b'.vhv'in self.RAW_PAKFILE:
                print(f"{self.filename[:-4]}'s cubemaps are compiled and packed!")
        #if hasattr(self, 'LIGHTING_HDR'):
        #    check for HDR lightmaps
        for material_name in self.TEXDATA_STRING_DATA:
            short_name = material_name
            material_name = 'materials/' + material_name.lower() + '.vmt'
            if material_name not in vmts:
                print('{self.filename} references {short_name} and is', end=' ')
                if bytes(material_name, 'utf-8') in self.RAW_PAKFILE:
                    print('PACKED!')
                else:
                    print('NOT_PACKED!')
                    passes = False
        for entity in self.ENTITIES:
            if 'prop' in entity['classname']:
                referenced_mdls.append(entity['model'])
        print(referenced_mdls)
        return passes

def disp_tris(verts, power):
    """takes flat array of verts and arranges them in a patterned triangle grid
    expects verts to be an array of length ((2 ** power) + 1) ** 2"""
    power2 = 2 ** power
    power2A = power2 + 1
    power2B = power2 + 2
    power2C = power2 + 3
    tris = []
    for line in range(power2):
        line_offset = power2A * line
        for block in range(2 ** (power - 1)):
            offset = line_offset + 2 * block
            if line % 2 == 0: # |\|/|
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2A])
                tris.append(verts[offset + 1])

                tris.append(verts[offset + power2A])
                tris.append(verts[offset + power2B])
                tris.append(verts[offset + 1])

                tris.append(verts[offset + power2B])
                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 1])

                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 2])
                tris.append(verts[offset + 1])
            else: #|/|\|
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2A])
                tris.append(verts[offset + power2B])

                tris.append(verts[offset + 1])
                tris.append(verts[offset + 0])
                tris.append(verts[offset + power2B])

                tris.append(verts[offset + 2])
                tris.append(verts[offset + 1])
                tris.append(verts[offset + power2B])

                tris.append(verts[offset + power2C])
                tris.append(verts[offset + 2])
                tris.append(verts[offset + power2B])
    return tris


if __name__=='__main__':
    # USE ARGPARSE! for --help and options like -obj -stats etc.
    import sys
    if len(sys.argv) > 1: # drag drop obj converter
        for map_path in sys.argv[1:]:
            bsp_file = bsp(map_path)
            start = time.time()
            obj_file = open(map_path + '.obj', 'w')
            bsp_file.export_obj(obj_file)
            obj_file.close()
            conversion_time = time.time() - start
            print(f'Converting {bsp_file.filename} took {conversion_time // 60:.0f}:{conversion_time % 60:.3f}')
    else:
##        bsp_file = bsp('maps/pl_upward.bsp')
##        start = time.time()
##        obj_file = open('mat_test' + '.obj', 'w')
##        bsp_file.export_obj(obj_file)
##        obj_file.close()
##        conversion_time = time.time() - start
##        print(f'Converting {bsp_file.filename} took {conversion_time // 60:.0f}:{conversion_time % 60:.3f}')
        ...
    # compressed .bsp
##    bsp('maps/koth_sky_lock_b1')
    harvest = bsp('E:/Steam/SteamApps/common/Team Fortress 2/tf/maps/koth_harvest_final')
    import json
    leaf_file = open('koth_harvest_leaf_lump.json', 'w')
    leaf_file.write('[' + ',\n'.join([json.dumps(leaf) for leaf in harvest.LEAVES]) + ']')
    leaf_file.close()
    print('Leaves written to file!')
