# McSimps Titanfall Map Exporter Tool
# Website: https://will.io/

import struct
from enum import Enum
import os

map_name = 'sp_beacon'
map_path = 'C:\\PATHNAME\\Beacon\\maps\\' + map_name + '.bsp'
dump_base = 'C:\\PATHNAME\\Exports\\textures\\'

def read_null_string(f):
    chars = []
    while True:
        c = f.read(1).decode('ascii')
        if c == chr(0):
            return ''.join(chars)
        chars.append(c)

class LumpElement:
    @staticmethod
    def get_size():
        raise NotImplementedError()

class TextureData(LumpElement):
    def __init__(self, data):
        self.string_table_index = struct.unpack_from('<I', data, 12)[0]

    @staticmethod
    def get_size():
        return 36

class BumpLitVertex(LumpElement):
    def __init__(self, data):
        self.vertex_pos_index = struct.unpack_from('<I', data, 0)[0]
        self.vertex_normal_index = struct.unpack_from('<I', data, 4)[0]
        self.texcoord0 = struct.unpack_from('<ff', data, 8) # coord into albedo, normal, gloss, spec
        self.texcoord5 = struct.unpack_from('<ff', data, 20) # coord into lightmap

    @staticmethod
    def get_size():
        return 44

class UnlitVertex(LumpElement):
    def __init__(self, data):
        self.vertex_pos_index = struct.unpack_from('<I', data, 0)[0]
        self.vertex_normal_index = struct.unpack_from('<I', data, 4)[0]
        self.texcoord0 = struct.unpack_from('<ff', data, 8)

    @staticmethod
    def get_size():
        return 20

class UnlitTSVertex(LumpElement):
    def __init__(self, data):
        self.vertex_pos_index = struct.unpack_from('<I', data, 0)[0]
        self.vertex_normal_index = struct.unpack_from('<I', data, 4)[0]
        self.texcoord0 = struct.unpack_from('<ff', data, 8)

    @staticmethod
    def get_size():
        return 28

class MaterialSortElement(LumpElement):
    def __init__(self, data):
        self.texture_index = struct.unpack_from('<H', data, 0)[0]
        self.vertex_start_index = struct.unpack_from('<I', data, 8)[0]

    @staticmethod
    def get_size():
        return 12

class VertexType(Enum):
    LIT_FLAT = 0
    UNLIT = 1
    LIT_BUMP = 2
    UNLIT_TS = 3

class MeshElement(LumpElement):
    def __init__(self, data):
        self.indices_start_index = struct.unpack_from('<I', data, 0)[0]
        self.num_triangles = struct.unpack_from('<H', data, 4)[0]
        self.material_sort_index = struct.unpack_from('<H', data, 22)[0]
        self.flags = struct.unpack_from('<I', data, 24)[0]

    def get_vertex_type(self):
        temp = 0
        if self.flags & 0x400:
            temp |= 1
        if self.flags & 0x200:
            temp |= 2
        return VertexType(temp)

    @staticmethod
    def get_size():
        return 28

# Read all vertex position data
print("Reading vertex position data...")
with open(map_path + '.0003.bsp_lump', 'rb') as f:
    data = f.read()
    vertex_positions = [struct.unpack_from('<fff', data, i * 12) for i in range(len(data) // 12)]

# Read all vertex normals
print("Reading vertex normal data...")
with open(map_path + '.001e.bsp_lump', 'rb') as f:
    data = f.read()
    vertex_normals = [struct.unpack_from('<fff', data, i * 12) for i in range(len(data) // 12)]

# Read indices
print("Reading indices...")
with open(map_path + '.004f.bsp_lump', 'rb') as f:
    data = f.read()
    indices = [struct.unpack_from('<H', data, i * 2)[0] for i in range(len(data) // 2)]

# Read texture information
print("Reading texture information...")
with open(map_path + '.002c.bsp_lump', 'rb') as f:
    data = f.read()
    texture_string_offets = [struct.unpack_from('<I', data, i * 4)[0] for i in range(len(data) // 4)]

with open(map_path + '.002b.bsp_lump', 'rb') as f:
    texture_strings = []
    for offset in texture_string_offets:
        f.seek(offset)
        texture_strings.append(read_null_string(f))

textures = []
with open(map_path + '.0002.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = TextureData.get_size()
    for i in range(len(data) // elem_size):
        textures.append(TextureData(data[i*elem_size:(i+1)*elem_size]))

# Read bump lit vertices
print("Reading bump lit vertices...")
bump_lit_vertices = []
with open(map_path + '.0049.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = BumpLitVertex.get_size()
    for i in range(len(data) // elem_size):
        bump_lit_vertices.append(BumpLitVertex(data[i*elem_size:(i+1)*elem_size]))

# Read unlit vertices
print("Reading unlit vertices...")
unlit_vertices = []
with open(map_path + '.0047.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = UnlitVertex.get_size()
    for i in range(len(data) // elem_size):
        unlit_vertices.append(UnlitVertex(data[i*elem_size:(i+1)*elem_size]))

# Read unlit TS vertices
print("Reading unlit TS vertices...")
unlit_ts_vertices = []
with open(map_path + '.004a.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = UnlitTSVertex.get_size()
    for i in range(len(data) // elem_size):
        unlit_ts_vertices.append(UnlitTSVertex(data[i*elem_size:(i+1)*elem_size]))

vertex_arrays = [
    [],
    unlit_vertices,
    bump_lit_vertices,
    unlit_ts_vertices
]

# Read the material sort data
print("Reading material sort data...")
material_sorts = []
with open(map_path + '.0052.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = MaterialSortElement.get_size()
    for i in range(len(data) // elem_size):
        material_sorts.append(MaterialSortElement(data[i*elem_size:(i+1)*elem_size]))

# Read mesh information
print("Reading mesh data...")
meshes = []
with open(map_path + '.0050.bsp_lump', 'rb') as f:
    data = f.read()
    elem_size = MeshElement.get_size()
    for i in range(len(data) // elem_size):
        meshes.append(MeshElement(data[i*elem_size:(i+1)*elem_size]))

# Build combined model data
print("Building combined model data...")
combined_uvs = []
mesh_faces = []
texture_set = set()
for mesh_index in range(len(meshes)):
    faces = []
    mesh = meshes[mesh_index]
    mat = material_sorts[mesh.material_sort_index]
    texture_set.add(texture_strings[textures[mat.texture_index].string_table_index])
    for i in range(mesh.num_triangles * 3):
        vertex = vertex_arrays[mesh.get_vertex_type().value][mat.vertex_start_index + indices[mesh.indices_start_index + i]]
        combined_uvs.append(vertex.texcoord0)
        uv_idx = len(combined_uvs) - 1
        faces.append((vertex.vertex_pos_index + 1, uv_idx + 1, vertex.vertex_normal_index + 1))
    mesh_faces.append(faces)

# Build material files
print('Building material files...')
for i in range(len(textures)):
    texture_string = texture_strings[textures[i].string_table_index]

    # Work out the path to the actual texture
    if os.path.isfile(dump_base + texture_string + '.png'):
        path = dump_base + texture_string + '.png'
    elif os.path.isfile(dump_base + texture_string + '_col.png'):
        path = dump_base + texture_string + '_col.png'
    else:
        print('[!] Failed to find texture file for {}'.format(texture_string))
        path = 'error.png'

    # # Write the material file
    # with open('{}\\tex{}.mtl'.format(map_name, i), 'w') as f:
    #      f.write('newmtl tex{}\n'.format(i))
    #      f.write('illum 1\n')
    #      f.write('Ka 1.0000 1.0000 1.0000\n')
    #      f.write('Kd 1.0000 1.0000 1.0000\n')
    #      f.write('map_Ka {}\n'.format(path))
    #      f.write('map_Kd {}\n'.format(path))

# Create obj file
print("Writing output file...")
with open(map_name, 'w') as f:
    f.write('o {}\n'.format(map_name))
    for i in range(len(textures)):
        f.write('mtllib tex{}.mtl\n'.format(i))

    for v in vertex_positions:
        f.write('v {} {} {}\n'.format(*v))

    for v in vertex_normals:
        f.write('vn {} {} {}\n'.format(*v))

    for v in combined_uvs:
        f.write('vt {} {}\n'.format(*v))

    for i in range(len(mesh_faces)):
        f.write('g {}\n'.format(i))
        f.write('usemtl tex{}\n'.format(material_sorts[meshes[i].material_sort_index].texture_index))
        faces = mesh_faces[i]
        for i in range(len(faces) // 3):
            f.write('f {}/{}/{} {}/{}/{} {}/{}/{}\n'.format(*faces[i*3], *faces[(i*3) + 1], *faces[(i*3) + 2]))
