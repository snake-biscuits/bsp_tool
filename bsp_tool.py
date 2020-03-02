# www.gamedev.net/forums/topic/230012-eliminating-discontinuities-t-junctions-in-bsp/
# what impact would rewriting a bsp with fixed t-juncts have?
#
# source_sdk_2013/mp/src/public/bspfile.h
# source_sdk_2013/mp/src/utils/vbsp/writebsp.cpp
# source_sdk_2013/mp/src/utils/vbsp/map.cpp
#
# LUMP_PAKFILE is never compressed. ? really ?
# LUMP_GAME_LUMP is compressed in individual segments.
# The compressed size of a game lump can be determined by subtracting the
# current game lump's offset with that of the next entry. For this reason,
# the last game lump is always an empty dummy which only contains the offset.
import collections
import copy
import enum
import itertools
import lzma
import os
import struct
import time

import vector
import vmf_tool

from mods import team_fortress2, titanfall2, vindictus


def read_lump(file, header_address):
    file.seek(header_address)
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
    def __init__(self, filename, mod=team_fortress2, lump_files=True):
        self.mod = mod # should autodetect from errors and bsp version
        if not filename.endswith('.bsp'):
            filename += '.bsp'
        filename.replace('\\', '/')
        split_filename = filename.rpartition('/')
        self.filename = split_filename[-1] # with .bsp extension
        self.filepath = f'{split_filename[0]}/'
        local_files = os.listdir(self.filepath)
        self.associated_files = [f for f in local_files if f.startswith(self.filename[:-3])]
        file = open(filename, 'rb')
        file_magic = file.read(4)
        if file_magic not in (b"VBSP", b"rBSP"): # rBSP = Respawn BSP (Titanfall)
            # ^ ignores the reversed file_magic (big endian)
            raise RuntimeError(f"{file} is not a .bsp!")
        self.bsp_version = int.from_bytes(file.read(4), "little")
        #rBSP map revision is before headers, VBSP is after
        self.bytesize = len(file.read()) + 8
            
        self.lump_map = {}
        start_time = time.time()
        for ID in self.mod.LUMP:
            lump_filename = f"{self.filepath}{self.filename}.{ID:04x}.bsp_lump" # rBSP style .bsp_lump naming convention
            if lump_files == True and lump_filename in self.associated_files:
                # vBSP lumpfiles have headers, rBSP lumpfiles do not
                # mp_drydock only has 72 bsp_lump files
                data = open(lump_filename, "rb").read()
            else:
                data = read_lump(file, self.mod.lump_header_address[ID])          
            if data is not None: # record the .bsp lump headers (could be implemented better)
                file.seek(self.mod.lump_header_address[ID])
                self.lump_map[ID] = lump_header(*[int.from_bytes(file.read(4), 'little') for i in range(4)])
                setattr(self, 'RAW_' + ID.name, data)
            # else lump is empty

        self.log = [] # begin processing lumps
        lump_classes = self.mod.lump_classes # self.mod is a module
        for LUMP, lump_class in lump_classes.items():
            if not hasattr(self, f"RAW_{LUMP}"):
                continue # skip unused lumps
            try: # implement -Warn system here
                setattr(self, LUMP, [])
                RAW_LUMP = getattr(self, f"RAW_{LUMP}")
                for data in struct.iter_unpack(lump_class._format, RAW_LUMP):
                    getattr(self, LUMP).append(lump_class(data))
                exec(f"del self.RAW_{LUMP}")
            except struct.error as exc:
                self.log.append(f"ERROR PARSING {LUMP}:\n{LUMP} lump is an unusual size. Wrong mod?")
##                raise exc
            except Exception as exc:
                self.log.append(f"ERROR PARSING {LUMP}:\n{exc.__class__.__name__}: {exc}")
##                raise exc

        if self.log != []: # if errors occured, print to console
            print(*self.log, sep='\n')

        ### SPECIAL LUMPS ###
        #-- ENTITIES --#
        # don't forget some .bsps have no entities
        self.ENTITIES = self.RAW_ENTITIES.decode(errors="ignore")
        self.ENTITIES = "ent" + self.ENTITIES.replace("{", "ent\n{")
        self.ENTITIES = vmf_tool.namespace_from(self.ENTITIES)["ents"]
        # top level namespace grouping classnames?
        # still index entities?
        # use fgdtools to fully unstringify entities
        # >>> type: plane | re | (x y z) (x y z) (x y z)
        del self.RAW_ENTITIES
        #-- GAME LUMP --#
        ...
        #-- SURF_EDGES --#
        try:
            _format = self.mod.surf_edge._format
        except:
            _format = team_fortess2.surf_edge._format
        self.SURFEDGES = [s[0] for s in struct.iter_unpack(_format, self.RAW_SURFEDGES)]
        del self.RAW_SURFEDGES, _format
        # - VISIBILITY
##        self.VISIBILITY = [v[0] for v in struct.iter_unpack("i", self.RAW_VISIBLITY)]
##        num_clusters = self.VISIBILITY[0]
##        for i in range(num_clusters):
##            i = (2 * i) + 1
##            pvs_offset = self.RAW_VISIBILITY[i]
##            pas_offset = self.RAW_VISIBILITY[i + 1]
##            # pointers into RLE encoded bits mapping the PVS tree

        file.close()
        unpack_time = time.time() - start_time
        print(f'Imported {self.filename} in {unpack_time:.2f} seconds')


    def verts_of(self, face): # why so many crazy faces?
        """vertex format [Position, Normal, TexCoord, LightCoord, Colour]"""
        verts, uvs, uv2s = [], [], []
        first_edge = face.first_edge
        for surfedge in self.SURFEDGES[first_edge:first_edge + face.num_edges]:
            edge = self.EDGES[surfedge] if surfedge >= 0 else self.EDGES[-surfedge][::-1] # ?
            verts.append(self.VERTICES[edge[0]])
            verts.append(self.VERTICES[edge[1]])
        verts = verts[::2] # why skip in this way?
        # github.com/VSES/SourceEngine2007/blob/master/src_main/engine/matsys_interface.cpp
        # SurfComputeTextureCoordinate & SurfComputeLightmapCoordinate
        tex_info = self.TEXINFO[face.tex_info] # index error?
        tex_data = self.TEXDATA[tex_info.tex_data]
        texture = tex_info.texture
        lightmap = tex_info.lightmap
        normal = lambda P: (P.x, P.y, P.z) # return the normal of plane (P)
        for vert in verts:
            uv = [vector.dot(vert, normal(texture.s)) + texture.s.offset,
                  vector.dot(vert, normal(texture.t)) + texture.t.offset]
            uv[0] /= tex_data.view_width
            uv[1] /= tex_data.view_height
            uvs.append(vector.vec2(*uv))
            uv2 = [vector.dot(vert, normal(lightmap.s)) + lightmap.s.offset,
                   vector.dot(vert, normal(lightmap.t)) + lightmap.t.offset]
            uv2[0] -= face.lightmap_texture_mins_in_luxels.s
            uv2[1] -= face.lightmap_texture_mins_in_luxels.t
            try:
                uv2[0] /= face.lightmap_texture_size_in_luxels.s
                uv2[1] /= face.lightmap_texture_size_in_luxels.t
            except ZeroDivisionError:
                uv2 = [0, 0]
            uv2s.append(uv2)
        vert_count = len(verts)
        normal = [self.PLANES[face.plane_num].normal] * vert_count
        colour = [tex_data.reflectivity] * vert_count
        return list(zip(verts, normal, uvs, uv2s, colour))


    def dispverts_of(self, face): # add format argument (lightmap uv, 2 uvs, etc)
        """vertex format [Position, Normal, TexCoord, LightCoord, Colour]
        normal is inherited from face
        returns rows, not tris"""
        verts = self.verts_of(face)
        if face.disp_info == -1:
            raise RuntimeError('face is not a displacement!')
        if len(verts) != 4:
            raise RuntimeError('face does not have 4 corners (probably t-junctions)')
        disp_info = self.DISP_INFO[face.disp_info]
        start = list(disp_info.start_position)
        start = [round(x, 1) for x in start] # approximate match
        round_verts = []
        for vert in [v[0] for v in verts]:
            round_verts.append([round(x, 1) for x in vert])
        if start in round_verts: # "rotate"
            index = round_verts.index(start)
            verts = verts[index:] + verts[:index]
        A, B, C, D = [vector.vec3(*v[0]) for v in verts]
        Auv, Buv, Cuv, Duv = [vector.vec2(*v[2]) for v in verts]
        Auv2, Buv2, Cuv2, Duv2 = [vector.vec2(*v[3]) for v in verts] # scale is wrong
        AD = D - A
        ADuv = Duv - Auv
        ADuv2 = Duv2 - Auv2
        BC = C - B
        BCuv = Cuv - Buv
        BCuv2 = Cuv2 - Buv2
        power2 = 2 ** disp_info.power
        full_power = (power2 + 1) ** 2
        start = disp_info.disp_vert_start
        stop = disp_info.disp_vert_start + full_power
        new_verts, uvs, uv2s = [], [], []
        for index, disp_vert in enumerate(self.DISP_VERTS[start:stop]):
            t1 = index % (power2 + 1) / power2
            t2 = index // (power2 + 1) / power2
            bary_vert = vector.lerp(A + (AD * t1), B + (BC * t1), t2)
            disp_vert = [x * disp_vert.distance for x in disp_vert.vector]
            new_verts.append([a + b for a, b in zip(bary_vert, disp_vert)])
            uvs.append(vector.lerp(Auv + (ADuv * t1), Buv + (BCuv * t1), t2))
            uv2s.append(vector.lerp(Auv2 + (ADuv2 * t1), Buv2 + (BCuv2 * t1), t2))
        normal = [verts[0][1]] * full_power
        colour = [verts[0][4]] * full_power
        verts = list(zip(new_verts, normal, uvs, uv2s, colour))
        return verts


    def export(self, outfile):
        """expects outfile to be a file with write bytes capability"""
        outfile.write(b'VBSP')
        outfile.write((20).to_bytes(4, 'little')) # engine version
        offset = 0
        length = 0
        # USE THE LUMP MAP!
        # PRESERVE SOURCE FILE LUMP ORDER
        split_bytes = lambda y: map(lambda x: x.to_bytes(1, 'big'), y)
        # convert all non_raw lumps back to raw
        for LUMP in self.mod.LUMP:
            if hasattr(self, f"RAW_{LUMP}"):
                continue
            #elif LUMP is on special list
            #  - ENTITIES
            #  - GAME_LUMP
            #  - SURF_EDGES
            #  - VISIBILITY
            elif hasattr(self, LUMP):
                lump_format = self.mod.lump_classes[LUMP]._format # use the actual lump class of LUMP[0] instead
                packer = lambda x: struct.pack(lump_format, *x.flat())
                setattr(self, f"RAW_{LUMP}", map(packer, getattr(self, LUMP)))
        # headers
        # get offsets from headers
        for ID in LUMP: # entities should be written last
            outfile.write(offset.to_bytes(4, 'little'))
            length = len(getattr(self, ID.name, 'RAW_' + ID.name)) #only lumps we have
            offset += length
            outfile.write(b'0000') # lump version (actually important)
            outfile.write(b'0000') # lump fourCC (only for compressed)
        for ID in LUMP:
            outfile.write(getattr(self, ID.name, 'RAW_' + ID.name))
        outfile.write(b'0001') # map revision



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
    import argparse
    # --game -G [teamfortress2/hl2/vindictus/titanfall2]
    # -W strict # stop if cannot load ANY chunk
    # -W lazy # ignore any and all chunks that cannot be loaded
    # --stats [options] # list various stats into a .csv file
    #                   # take an example .csv?
    # -E / --external-lumps # look for .bsp_lump files in the same folder
    # more options?
    import sys
    if len(sys.argv) > 1: # drag & drop obj converter
        for map_path in sys.argv[1:]:
            bsp_file = bsp(map_path)
            start = time.time()
            obj_file = open(map_path + '.obj', 'w')
            bsp_file.export_obj(obj_file)
            obj_file.close()
            conversion_time = time.time() - start
            print(f'Converting {bsp_file.filename} took {conversion_time // 60:.0f}:{conversion_time % 60:.3f}')
    else:
        ... # do nothing (or uncomment tests)
