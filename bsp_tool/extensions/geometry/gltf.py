import enum
import json
import os
import struct
from typing import Any, Dict, List, Tuple, Union

from ...utils import geometry


# TODO: export Z-up geometry.Models as Y-up (add rotation to transform matrix?)
# TODO: scrap complex vertex * index buffer construction for a big dump of raw vertices
# -- super simple indexing; can revisit index buffers if we add those to geometry.Mesh

class Data(enum.Enum):
    """accessor.componentType"""
    BYTE = 5120
    UNSIGNED_BYTE = 5121
    SHORT = 5122
    UNSIGNED_SHORT = 5123
    UNSIGNED_INT = 5125
    FLOAT = 5126


class Buffer(enum.Enum):
    """bufferView.target"""
    ARRAY = 34962
    ELEMENT_ARRAY = 34963


Json = Dict[str, Union[str, int]]  # and List[Json]


class VertexBuffer:
    """treat as write-only"""
    # ENCODING
    format_: Dict[str, str]
    # ^ {"Vertex attr": "struct type"}
    format_string: str
    byteStride: int
    byteLength: int
    accessors: List[Json]
    vertex_attrs: Dict[str, int]
    # DATA
    vertices: List[geometry.Vertex]

    def __init__(self, **format_: Dict[str, str]):
        self.format_ = format_
        self.vertices = list()
        self.format_string = "".join(self.format_.values())
        self.byteStride = struct.calcsize(self.format_string)
        # for indexing / mapping vertex member accessors: (might need to add an offset)
        self.attributes = dict()
        num_texcoords = 0
        # TODO: num_colors = 0
        for i, attr in enumerate(self.format_):
            if attr.startswith("uv") and attr[2:].isnumeric():
                va = f"TEXCOORD_{num_texcoords}"
                num_texcoords += 1
            elif attr == "colour":  # NOTE: only one vertex colour
                va = "COLOR_0"
            else:
                va = {a: a.upper() for a in ("position", "normal")}
            self.attributes[va] = i

    def add(self, vertex: geometry.Vertex) -> int:
        # TODO: assert vertex format is valid
        if vertex in self.vertices:
            return self.vertices.index(vertex)
        else:
            self.vertices.append(vertex)
            return len(self.vertices) - 1

    def tuplify(self, vertex: geometry.Vertex) -> Tuple[Any]:
        out = list()
        for attr in self.format_:
            val = getattr(vertex, attr)
            if isinstance(val, (float, int)):
                out.append(val)
            else:
                out.extend(val)  # position -> position.x, position.y, ...
        return tuple(out)

    def as_bytes(self) -> bytes:
        return b"".join(struct.pack(self.format_string, v) for v in self.vertices)

    @property
    def accessors(self) -> List[Json]:
        component_types = {
            "f": Data.FLOAT, "I": Data.UNSIGNED_INT,
            "h": Data.SHORT, "H": Data.UNSIGNED_SHORT,
            "b": Data.BYTE, "B": Data.UNSIGNED_BYTE}
        out = list()
        offset = 0
        for attr, sub_format in self.format_.items():
            type_ = {x: f"VEC{x}" for x in (2, 3, 4)}.get(sub_format[0], "SCALAR")
            component = component_types[sub_format if len(sub_format) == 1 else sub_format[1]]
            out.append({"type": type_, "componentType": component, "byteOffset": offset, "count": len(self.vertices)})
            offset += struct.calcsize(sub_format)
        return out

    @property
    def bufferView(self) -> Json:
        return {"byteLength": self.ByteLength, "target": Buffer.ARRAY, "byteStride": self.byteStride}

    @property
    def byteLength(self) -> int:
        return len(self.vertices) * self.byteStride


class IndexBuffer:
    """treat as write-only"""
    indices: List[int]
    meshes: List[Tuple[int, int]]
    # ^ [(byteOffset, count)]
    byteLength: int

    def __init__(self):
        self.indices = list()
        self.meshes = list()

    def add(self, mesh: geometry.Mesh, vertex_buffer: VertexBuffer):
        byteOffset = len(self.indices) * 4
        new_indices = list()
        for polygon in mesh.polygons:
            loop_indices = [vertex_buffer.add(vertex) for vertex in polygon.vertices]
            fan_indices = [loop_indices[i] for i in geometry.triangle_fan(len(loop_indices))]
            new_indices.extend(fan_indices)
        self.indices.extend(new_indices)
        self.meshes.append((byteOffset, len(new_indices)))

    def as_bytes(self) -> bytes:
        return struct.pack(f"{len(self.indices)}I", *self.indices)

    @property
    def accessors(self) -> List[Json]:
        """bufferView is unset"""
        return [
            {"type": "SCALAR", "componentType": Data.UNSIGNED_INT, "byteOffset": m[0], "count": m[1]}
            for m in self.meshes]

    @property
    def bufferView(self) -> Json:
        """buffer is unset"""
        return {"byteLength": self.ByteLength, "target": Buffer.ELEMENT_ARRAY}

    @property
    def byteLength(self) -> int:
        return len(self.indices) * 4


class MaterialList:
    materials: List[geometry.Material]
    json: List[Json]

    def __init__(self):
        self.materials = list()

    def add(self, material: geometry.Material) -> int:
        if material in self.materials:
            return self.materials.index(material)
        else:
            self.materials.append(material)
            return len(self.materials) - 1

    @property
    def json(self) -> List[Json]:
        # TODO: more material attributes (e.g. albedo, metalness map)
        return [{"name": m.name} for m in self.materials]


class GLTF:
    buffers: List[Tuple[VertexBuffer, IndexBuffer]]
    models: List[geometry.Models]
    # TODO: named models
    json: Json

    # TODO: @classmethod def from_models(cls, models: List[geometry.Model]) -> GLTF:
    # TODO: @classmethod def from_buffers(cls, buffers: List[Tuple[VertexBuffer, IndexBuffer]]) -> GLTF:

    def __init__(self, models=list()):
        self.models = models
        # base json
        self.json = {
            "scene": 0, "scenes": [{"nodes": []}],
            "nodes": [], "meshes": [], "materials": [],
            "buffers": [], "bufferViews": [], "accessors": [],
            "asset": {"version": "2.0"}}
        self.json["scenes"][0]["nodes"] = [*range(len(self.models))]

        # MAKE BUFFERS
        # TODO: move to another method for adding models / buffers
        # TODO: check which vertex attributes are used (not all meshes will have uvs, colour could be unused etc.)
        self.buffers = [(
            VertexBuffer(position="3f", normal="3f", uv0="2f", uv1="2f", colour="4f"),
            IndexBuffer())]
        vertex_buffer, index_buffer = self.buffers[0]
        materials = MaterialList()
        mesh_offset = 0
        for i, model in enumerate(self.models):
            self.json["nodes"].append({"mesh": i})
            # TODO: model.transform_matrix
            self.json["meshes"].append({"primitives": list()})
            for j, mesh in enumerate(model.meshes):
                material_index = materials.add(mesh.material)
                index_buffer.add(mesh, vertex_buffer)
                self.json["meshes"][-1]["primitives"].append({
                    "attributes": vertex_buffer.attributes,
                    "material": material_index,
                    "indices": mesh_offset + j})
            mesh_offset += len(model.meshes)
        self.json["materials"] = materials.json
        self.json["buffers"] = [
            {"byteLength": vertex_buffer.byteLength},
            {"byteLength": index_buffer.byteLength}]
        # NOTE: uri will be added by .save_as(filename)
        self.json["bufferViews"] = [
            {"buffer": 0, **vertex_buffer.bufferView},
            {"buffer": 1, **index_buffer.bufferView}]
        self.json["accessors"] = [
            *[{"bufferView": 0, **a} for a in vertex_buffer.accessors],
            *[{"bufferView": 1, **a} for a in index_buffer.accessors]]

    def __repr__(self) -> str:
        return f"<GLTF {len(self.models)} models {len(self.json['buffers'])} buffers @ 0x{id(self):016X}>"

    # TODO: @classmethod def from_file(cls, filename) -> GLTF:

    def save_as(self, filename):
        """.gltf only! no .glb (yet)"""
        folder, filename = os.path.split(filename)
        filename, ext = os.path.splitext(filename)
        assert ext == ".gltf", f"cannot write to '{ext}' extension"
        with open(os.path.join(folder, f"{filename}.gltf"), "wb") as json_file:
            json.dump(json_file, self.json, indent=2)
        for i, (vertex_buffer, index_buffer) in enumerate(self.buffers):
            # vertex buffer
            vertex_buffer_filename = f"{filename}.vertex.{i}.bin"
            self.json["buffers"][i * 2 + 0]["uri"] = vertex_buffer_filename
            with open(os.path.join(folder, vertex_buffer_filename), "wb") as vertex_buffer_file:
                vertex_buffer_file.write(vertex_buffer.as_bytes())
            # index buffer
            index_buffer_filename = f"{filename}.index.{i}.bin"
            self.json["buffers"][i * 2 + 1]["uri"] = index_buffer_filename
            with open(os.path.join(folder, index_buffer_filename), "wb") as index_buffer_file:
                index_buffer_file.write(index_buffer.as_bytes())
