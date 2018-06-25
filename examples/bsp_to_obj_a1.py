#version a1 (1st February 2018)
#made by B!scuit (Jared Ketterer)
#based on Valve's .bsp file format version 20 (for TF2)
#https://developer.valvesoftware.com/wiki/Source_BSP_File_Format
#https://github.com/ValveSoftware/source-sdk-2013/blob/master/mp/src/public/bspfile.h

#REMEMBER TO KEEP vector.py IN THE SAME FOLDER!
#ESSENTIAL FOR DISPLACEMENTS

#just drag and drop a .bsp over this script to convert to .obj

#TODO:
#  position to node / leaf (vis to draw call)
#  ibsp to vbsp and vice versa
#  class for every struct
#  skip lumps not in file
import collections
import enum
import itertools
import lzma
import struct
import time
import vector

MAX_MAP_FACES = 65536
MAX_MAP_SURFEDGES = 512000

DISPTRI_TAG_SURFACE = 0x1
DISPTRI_TAG_WALKABLE = 0x2
DISPTRI_TAG_BUILDABLE = 0x4
DISPTRI_FLAG_SURFPROP1 = 0x8
DISPTRI_FLAG_SURFPROP2 = 0x10

class LUMP(enum.Enum):
    ENTITIES = 0
    PLANES = enum.auto()
    TEXDATA = enum.auto()
    VERTICES = enum.auto()
    VISIBILITY = enum.auto()
    NODES = enum.auto()
    TEXINFO = enum.auto()
    FACES = enum.auto()
    LIGHTING = enum.auto()
    OCCLUSION = enum.auto()
    LEAVES = enum.auto()
    FACEIDS = enum.auto()
    EDGES = enum.auto()
    SURFEDGES = enum.auto()
    MODELS = enum.auto()
    WORLD_LIGHTS = enum.auto()
    LEAF_FACES = enum.auto()
    LEAF_BRUSHES = enum.auto()
    BRUSHES = enum.auto()
    BRUSH_SIDES = enum.auto()
    AREAS = enum.auto()
    AREA_PORTALS = enum.auto()
    UNUSED0 = enum.auto()
    UNUSED1 = enum.auto()
    UNUSED2 = enum.auto()
    UNUSED3 = enum.auto()
    DISP_INFO = enum.auto()
    ORIGINAL_FACES = enum.auto()
    PHYS_DISP = enum.auto()
    PHYS_COLLIDE = enum.auto()
    VERT_NORMALS = enum.auto()
    VERT_NORMAL_INDICES = enum.auto()
    DISP_LIGHTMAP_ALPHAS = enum.auto()
    DISP_VERTS = enum.auto()
    DISP_LIGHTMAP_SAMPLE_POSITIONS = enum.auto()
    GAME_LUMP = enum.auto()
    LEAF_WATER_DATA = enum.auto()
    PRIMITIVES = enum.auto()
    PRIM_VERTS = enum.auto()
    PRIM_INDICES = enum.auto()
    PAKFILE = enum.auto()
    CLIP_PORTAL_VERTS = enum.auto()
    CUBEMAPS = enum.auto()
    TEXDATA_STRING_DATA = enum.auto()
    TEXDATA_STRING_TABLE = enum.auto()
    OVERLAYS = enum.auto()
    LEAF_MIN_DIST_TO_WATER = enum.auto()
    FACE_MARCO_TEXTURE_INFO = enum.auto()
    DISP_TRIS = enum.auto()
    PHYS_COLLIDE_SURFACE = enum.auto()
    WATER_OVERLAYS = enum.auto()
    LEAF_AMBIENT_INDEX_HDR = enum.auto()
    LEAF_AMBIENT_INDEX = enum.auto()
    LIGHTING_HDR = enum.auto()
    WORLD_LIGHTS_HDR = enum.auto()
    LEAF_AMBIENT_LIGHTING_HDR = enum.auto()
    LEAF_AMBIENT_LIGHTING = enum.auto()
    XZIP_PAKFILE = enum.auto()
    FACES_HDR = enum.auto()
    MAP_FLAGS = enum.auto()
    OVERLAY_FADES = enum.auto()

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
            file.seek(offset)
            lump = file.read(length)
            #lzma header
##            print('PROCESSING:', lumpid)
##            print('LUMP HEADER:', offset, length, version, fourCC)
            #Source Engine LZMA Header
            #id b'LZMA'     uint    (magic id)      lump[:4]
            #actualSize     uint    (uncompressed)  lump[4:8]
            #lzmaSize       uint    (dict size)     lump[8:12]
            #properties     uchr[5]                 lump[12:17]
            #what are source properties?
            source_lzma_header = struct.unpack('4s2I5B', lump[:17])
##            print('SOURCE LZMA HEADER:', source_lzma_header)
            #.lzma header
            #properties
            # - lc [0, 8]
            # - lp [0, 4]
            # - pb [0, 4]
            #properties = (pb * 5 + lp) * 9 + lc (1 byte)
            #dictionary size
            #uncompressed size
            lzma_header = lump[12:17] + lump[8:12] + lump[4:8]
            lump = lzma_header + lump[:17]
            try:
                decompressed_lump = lzma.decompress(lump, format=lzma.FORMAT_ALONE)
            except:
                raise RuntimeError("Couldn't decompress")
            if len(decompressed_lump) != fourCC:    #while > ?
                raise RuntimeError(lumpid, 'bad decompression\n',
                                   'expected', fourCC, 'bytes, got',
                                   len(decompressed_lump))
            else:
                return decompressed_lump

class bsp():
    def __init__(self, file):
        if not file.endswith('.bsp'):
            file += '.bsp'
        self.filename = file.split('/')[-1]
        file = open(file, 'rb')
        self.bytesize = len(file.read())

##        for lump in lump_address:
##            file.seek(lump_address[lump])
##            offset = int.from_bytes(file.read(4), 'little')
##            lumpSize = int.from_bytes(file.read(4), 'little')
##            if offset != 0:
##                print('LUMP_', lump, sep='')
##                print('LUMP OFFSET', offset)
##                print('LUMP SIZE:', lumpSize)
##                print('VERSION:', int.from_bytes(file.read(4), 'little'))
##                print('UNCOMPRESSED:', int.from_bytes(file.read(4), 'little'))
##                print()

        start_time = time.time()
        for ID in LUMP:
            setattr(self, 'RAW_' + ID.name, read_lump(file, ID))

        self.PLANES = []
        for plane in struct.iter_unpack('4fi', self.RAW_PLANES):
            self.PLANES.append({
                'normal': plane[:3],
                'dist': plane[3],
                'type': plane[4]
            })
        del self.RAW_PLANES, plane

        self.VERTICES = []
        for vertex in struct.iter_unpack('3f', self.RAW_VERTICES):
            self.VERTICES.append(list(vertex))
        del self.RAW_VERTICES, vertex

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

        self.LEAVES = [] #Map Version < 20 is different
        for leaf in struct.iter_unpack('i9h4Hh', self.RAW_LEAVES):
            area = bin(leaf[2])
            if len(area) < 18:
                area += '0' * (18 - len(area))
            flags = bin(leaf[3])
            if len(flags) < 18:
                flags += '0' * (18 - len(flags))
            try:
                area = int(area + flags[2], 2)
            except: #throws an error when flags is negative
                area = int(area + '1', 2)
            flags = int('0b' + flags[2:], 2) if not flags.startswith('-') else int('-0b' + flags[3:], 2)
            self.LEAVES.append({
                'contents': leaf[0],
                'cluister': leaf[1],
                'area': area, #9 bits
                'flags': flags, #7 bits
                'mins': leaf[4:7],
                'maxs': leaf[7:10],
                'firstleafface': leaf[10],
                'numleaffaces': leaf[11],
                'firstleafbrush': leaf[12],
                'numleafbrushes': leaf[13],
                'leafWaterDataID': leaf[14] #-1 for not in water
                })
        del self.RAW_LEAVES, leaf

        self.LEAF_FACES = list(itertools.chain(*struct.iter_unpack('H', self.RAW_LEAF_FACES)))
        del self.RAW_LEAF_FACES

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

        if self.RAW_DISP_INFO is not None:
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
                    'EdgeNeighbours': [b''.join(dispinfo[12:23]), b''.join(dispinfo[23:34]),
                                       b''.join(dispinfo[34:45]), b''.join(dispinfo[45:56])],
                                        #bool  isValid #'?H3BH3B'
                                        #SubNeighbours[2] #'H3B'
                                        #  unsigned short  Neighbour              #DISP_INFO index
                                        #  unsigned char   NeighbourOrientation   #(CCW) rotation of the neighbor wrt this displacement
                                        #  unsigned char   Span                   #Where the neighbor fits onto this side of our displacement
                                        #  unsigned char   Neighbout Span         #Where we fit onto our neighbor
                    'CornerNeighbours': [b''.join(dispinfo[56:67]), b''.join(dispinfo[67:78]),
                                         b''.join(dispinfo[78:89]), b''.join(dispinfo[89:100])],
                                        #
                    'AllowedVerts': dispinfo[100:]
                })
            del self.RAW_DISP_INFO, dispinfo

        if self.RAW_DISP_VERTS is not None:
            self.DISP_VERTS = []
            for dispvert in struct.iter_unpack('5f', self.RAW_DISP_VERTS):
                self.DISP_VERTS.append({
                    'vec': dispvert[:3],
                    'dist': dispvert[3],
                    'alpha': dispvert[4]
                })
            del self.RAW_DISP_VERTS, dispvert

        if self.RAW_DISP_TRIS is not None:
            self.DISP_TRIS = struct.iter_unpack('H', self.RAW_DISP_TRIS)
            del self.RAW_DISP_TRIS

        self.TEXINFO = []
        for texinfo in struct.iter_unpack('16f2i', self.RAW_TEXINFO):
            self.TEXINFO.append({
                'textureVecs': [texinfo[:4], texinfo[4:8]],
                'lightmapVecs': [texinfo[8:12], texinfo[12:16]],
                'flags': texinfo[16],
                'texdata': texinfo[17]
            })
        del self.RAW_TEXINFO, texinfo

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

        self.TEXDATA_STRING_TABLE = []
        for string_data in struct.iter_unpack('i' , self.RAW_TEXDATA_STRING_TABLE):
            self.TEXDATA_STRING_TABLE.append(string_data[0])
        del self.RAW_TEXDATA_STRING_TABLE, string_data

        self.TEXDATA_STRING_DATA = self.RAW_TEXDATA_STRING_DATA.decode('utf-8', 'ignore').split('\0')[:-1]
        del self.RAW_TEXDATA_STRING_DATA
        #occasionally contains random undecodeable bytes
        #e.g. pl_upward begins b'\xff\xff \x00\x00\x00\x00\x00\x00'

        self.LIGHTING = self.RAW_LIGHTING
        del self.RAW_LIGHTING

        self.EDGES = []
        for edge in struct.iter_unpack('2h', self.RAW_EDGES):
            self.EDGES.append(list(edge))
        del self.RAW_EDGES, edge

        self.SURFEDGES = []
        for surfedge in struct.iter_unpack('i', self.RAW_SURFEDGES):
            self.SURFEDGES.append(surfedge[0])
        del self.RAW_SURFEDGES, surfedge

        # self.WORLD_LIGHTS = []
        # for world_light in struct.iter_unpack('12f3i7f3i', self.RAW_WORLD_LIGHTS):
        #     self.WORLD_LIGHTS.append({
        #         'origin': world_light[:3],
        #         'intensity': world_light[3:6],
        #         'normal': world_light[6:9],
        #         'cluster': world_light[9],
	    #         'type': world_light[10], #enum
        #         'style': world_light[11],
        #         'stopdot': world_light[12], #start of penumbra for emit_spotlight
        #         'stopdot2': world_light[13], #end of penumbra for emit_spotlight
        #         'exponent': world_light[14],
        #         'radius': world_light[15], #cuttof distance
        #         #falloff for emit_spotlight + emit_point:
        #     	#1 / (constant_attn + linear_attn * dist + quadratic_attn * dist^2)
        #         'constant_attn': world_light[16],
        #         'linear_attn': world_light[17],
        #         'quadratic_attn': world_light[18],
        #         'flags': world_light[19], #Uses a combination of the DWL_FLAGS_ defines.
        #         'texinfo': world_light[20],
        #         'owner': world_light[21] #positional parent
        #     })
        # del self.RAW_WORLD_LIGHTS, world_light
        #
        # self.WORLD_LIGHTS_HDR = []
        # for world_light in struct.iter_unpack('12f3i7f3i', self.RAW_WORLD_LIGHTS_HDR):
        #     self.WORLD_LIGHTS.append({
        #         'origin': world_light[:3],
        #         'intensity': world_light[3:6],
        #         'normal': world_light[6:9],
        #         'cluster': world_light[9],
	    #         'type': world_light[10], #enum
        #         'style': world_light[11],
        #         'stopdot': world_light[12], #start of penumbra for emit_spotlight
        #         'stopdot2': world_light[13], #end of penumbra for emit_spotlight
        #         'exponent': world_light[14],
        #         'radius': world_light[15], #cuttof distance
        #         #falloff for emit_spotlight + emit_point:
        #     	#1 / (constant_attn + linear_attn * dist + quadratic_attn * dist^2)
        #         'constant_attn': world_light[16],
        #         'linear_attn': world_light[17],
        #         'quadratic_attn': world_light[18],
        #         'flags': world_light[19], #Uses a combination of the DWL_FLAGS_ defines.
        #         'texinfo': world_light[20],
        #         'owner': world_light[21] #positional parent
        #     })
        # del self.RAW_WORLD_LIGHTS_HDR, hdr_world_light

        self.GAME_LUMP = []
        #UTILISE bsp_import_props.py CODE

        self.PAKFILE = []
        #self.RAW_PAKFILE

        self.MAP_FLAGS = []
        #self.RAW_MAP_FLAGS

        file.close()
        unpack_time = time.time() - start_time
        print('Imported', self.filename, 'in {:0.2f} seconds'.format(unpack_time))

    def verts_of(self, face):
        verts = []
        first_edge = face['firstedge']
        surfedges = self.SURFEDGES[first_edge:first_edge + face['numedges']]
        for surfedge in surfedges:
            edge = self.EDGES[surfedge] if surfedge >= 0 else self.EDGES[-surfedge][::-1]
            verts.append(self.VERTICES[edge[0]])
            verts.append(self.VERTICES[edge[1]])
        verts = [tuple(v) for v in verts]
        verts = collections.OrderedDict.fromkeys(verts)
        verts = [list(v) for v in verts]
        return verts

    def verts_check(self, face, verts):
        plane = self.PLANES[face['planenum']]
        normal = vector.vec3(*plane['normal'])
        distance = plane['dist']
        on_plane = lambda v: -1 < vector.dot(normal, vector.vec3(*v)) -distance < 1
        return list(filter(on_plane, verts))
    
    def dispverts_of(self, face):
        verts = self.verts_of(face)
        verts = self.verts_check(face, verts)
        if len(verts) < 4:
            return []
        if face['dispinfo'] == -1:
            return verts
        dispinfo = self.DISP_INFO[face['dispinfo']]
        start = list(dispinfo['startPosition'])
        #rounding errors throw compares
        start = [round(x, 1) for x in start]
        round_verts = []
        for vert in verts:
            round_verts.append([round(x, 1) for x in vert])
        if start in round_verts:
            index = round_verts.index(start)
            verts = verts[index:] + verts[:index]
        A = vector.vec3(*verts[0])
        B = vector.vec3(*verts[1])
        C = vector.vec3(*verts[2])
        D = vector.vec3(*verts[3])
        AD = D - A
        BC = C - B
        verts = []
        power = dispinfo['power']
        power2 = 2 ** power
        start = dispinfo['DispVertStart']
        stop = dispinfo['DispVertStart'] + (power2 + 1) ** 2
        for index, dispvert in enumerate(self.DISP_VERTS[start:stop]):
            t1 = index % (power2 + 1) / power2
            t2 = index // (power2 + 1) / power2
            baryvert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
            dispvert = [x * dispvert['dist'] for x in dispvert['vec']]
            verts.append([a + b for a, b in zip(baryvert, dispvert)])
        #assemble tris
        power2A = power2 + 1
        power2B = power2 + 2
        power2C = power2 + 3
        tri_verts = []
        for line in range(power2):
            line_offset = power2A * line
            for block in range(2 ** (power - 1)):
                offset = line_offset + 2 * block
                if line % 2 == 0:
                    tri_verts.append(verts[offset + 0])
                    tri_verts.append(verts[offset + power2A])
                    tri_verts.append(verts[offset + 1])

                    tri_verts.append(verts[offset + power2A])
                    tri_verts.append(verts[offset + power2B])
                    tri_verts.append(verts[offset + 1])

                    tri_verts.append(verts[offset + power2B])
                    tri_verts.append(verts[offset + power2C])
                    tri_verts.append(verts[offset + 1])

                    tri_verts.append(verts[offset + power2C])
                    tri_verts.append(verts[offset + 2])
                    tri_verts.append(verts[offset + 1])
                else:
                    tri_verts.append(verts[offset + 0])
                    tri_verts.append(verts[offset + power2A])
                    tri_verts.append(verts[offset + power2B])

                    tri_verts.append(verts[offset + 1])
                    tri_verts.append(verts[offset + 0])
                    tri_verts.append(verts[offset + power2B])

                    tri_verts.append(verts[offset + 2])
                    tri_verts.append(verts[offset + 1])
                    tri_verts.append(verts[offset + power2B])

                    tri_verts.append(verts[offset + power2C])
                    tri_verts.append(verts[offset + 2])
                    tri_verts.append(verts[offset + power2B])
        return tri_verts

    def export_lightmap(self):
        out_filename = self.filename + '.rgbe'
        print('Writing to ', out_filename, '...', sep='', end='')
        file = open(out_filename, 'wb')
        file.write(self.LIGHTING)
        file.close()
        print(' Done!')

    def export_sprp_list(self):
        raise NotImplemented('not yet')
        out_filename = self.filename + '.props'
        print('Writing to ', out_filename, '...', sep='', end='')
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
        outfile.write(b'VBSP')
        outfile.write((20).to_bytes(4, 'little'))
        offset = 0
        length = 0
        #convert all lumps tor RAW_*
        #rebuild raw bytes for each lump
        #struct.iter_pack
        ...
        #headers
        for ID in LUMP: #entities should be written last
            outfile.write(offset.to_bytes(4, 'little'))
            length = len(getattr(self, ID.name, 'RAW_' + ID.name))
            offset += length
            outfile.write(b'0000') #lump version (actually important)
            outfile.write(b'0000') #lump fourCC
        outfile.write(b'0001') #map revision
        for ID in LUMP:
            outfile.write(getattr(self, ID.name, 'RAW_' + ID.name))
        outfile.write()

    def export_obj(self, outfile): #TODO: group by material and write .mtl for each TEXINFO
        start_time = time.time()
        out_filename = outfile.name.split('/')[-1] if '/' in outfile.name else outfile.name.split('\\')[-1]
        print('exporting', self.filename, 'to {}...'.format(out_filename), end='')
        outfile.write('# bsp_tool.py generated model\n')
        outfile.write('# source file: {}\n'.format(self.filename))
        vertices = []
        normals = []
        #skip unlightmapped faces (sky and triggers)
        filtered_faces = list(filter(lambda x: x['lightofs'] != -1, self.FACES))

        faces = []
        for face in filter(lambda x: x['dispinfo'] == -1, filtered_faces):
            faces.append([])
            normal = self.PLANES[face['planenum']]['normal']
            if normal not in normals:
                normals.append(normal)
                normal = len(normals) - 1
            else:
                normal = normals.index(normal)
            for vertex in self.verts_of(face):
                if vertex not in vertices:
                    vertices.append(vertex)
                    vertex = len(vertices) - 1
                else:
                    vertex = vertices.index(vertex)
                faces[-1].append([vertex, normal])

        dispfaces = []
        for displacement in filter(lambda x: x['dispinfo'] != -1, filtered_faces):
            dispverts = self.dispverts_of(displacement)
            normal = self.PLANES[displacement['planenum']]['normal']
            for v1, v2, v3 in zip(dispverts[0::3], dispverts[1::3], dispverts[2::3]):
                dispfaces.append([])
                for v in v1, v2, v3:
                    if v not in vertices:
                        vertices.append(v)
                        v = len(vertices) - 1
                    else:
                        v = vertices.index(v)
                    dispfaces[-1].append(v)

        for v in vertices:
            outfile.write('v {0} {1} {2}\n'.format(*v))
        for vn in normals:
            outfile.write('vn {0} {1} {2}\n'.format(*vn))
        outfile.write('s off\n')
        for f in faces:
            face_verts = ['f']
            for vert in f:
                vert = [x + 1 for x in vert]
                face_verts.append('{0}//{1}'.format(*vert))
            face_string = ' '.join(face_verts) + '\n'
            outfile.write(face_string)
            
        outfile.write('o displacements\n')
        for f in dispfaces:
            f = [v + 1 for v in f]
            outfile.write('f {0} {1} {2}\n'.format(*f))
            
        total_time = time.time() - start_time
        total_minutes = total_time // 60
        total_seconds = total_time - total_minutes * 60
        outfile.write('# file generated in {0} minutes {1:0.2f} seconds\n'.format(total_minutes, total_seconds))
        print(' Done!')

def fuse(infile1, infile2, outfile):
    #REWRITE INTO ONE FILE WITH THE SECOND OFFSET AFTER THE FIRST
    #try to minimise doubling to reduce memory use & filesize
    """Combines two .bsp files into one
    Recommend not fusing two maps with space that overlaps
    (May reuslt in numerous Source Engine crashes)"""
    infile1 = bsp(infile1)
    infile2 = bsp
    print(dir(infile1))

    GREATEST_PLANENUM = len(infile1.PLANES)
    GREATEST_EDGE_INDEX = len(infile1.EDGES)
    GREATEST_SURFEDGE_INDEX = len(infile1.SURFEDGES)
    GREATEST_NODE = len(infile1.NODES)

    #vertex lump
    #edge lump [vertex indices]
    #surfedge lump [edge w/ direction flip]
    #face reference (start, len)

    #LIGHTING FUSION
    #ENTITIY LUMP WORLDSPAWN:
    #  COMBINE WORLD MINS & MAXS
    #LIGHT_ENVIRONMENT IS DEFAULT (WILL HDR WORK?)
    #SHADOW_CONTROL POINTS STRAIGHT DOWN (OR NONE)
    #ENV_SUN? MULTIPLE?
    #ASSUME VIS DOES NOT OVERLAP
    infile1.export_bsp(open(outfile, 'wb'))


if __name__=='__main__':
    import sys
    if len(sys.argv) > 1:
        bsp_file = bsp(sys.argv[1])
        obj_file = open(sys.argv[1] + '.obj', 'w')
        bsp_file.export_obj(obj_file)
        obj_file.close()
