from __future__ import annotations
import enum
import json
import os
import re
import struct
from typing import Any, Dict, List, Tuple, Union

from ..utils import geometry
from ..utils import quaternion
from . import base


# TODO: export Z-up geometry.Model as Y-up (add rotation to transform matrix?)
# TODO: scrap complex vertex & index buffer construction
# -- just dump the raw vertices, don't check for duplicates
# -- keep it simple, just like in utils.geometry
# TODO: custom JSONEncoder & Decoder classes
# -- could handle converting enum.Enum

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


def split_sub_format(sub_format: str):
    count, type_ = re.match(r"([0-9]*)([fIhHbB])", sub_format).groups()
    count = int(count) if count != "" else 1
    return count, type_


class VertexBuffer:
    """treat as write-only"""
    # ENCODING
    format_: Dict[str, str]
    # ^ {"position": "3f"}
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
        # for indexing / mapping vertex member accessors:
        # -- (might need to add an offset)
        self.attributes = dict()
        num_texcoords = 0
        # NOTE: geometry.Vertex only allows one vertex colour
        for i, attr in enumerate(self.format_):
            if attr.startswith("uv") and attr[2:].isnumeric():
                va = f"TEXCOORD_{num_texcoords}"
                num_texcoords += 1
            elif attr == "colour":
                va = "COLOR_0"
            else:  # POSITION / NORMAL
                va = attr.upper()
            self.attributes[va] = i

    def __len__(self) -> int:
        """number of attributes"""
        return len(self.format_)

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
                out.extend(val)
        return tuple(out)

    def as_bytes(self) -> bytes:
        return b"".join([
            struct.pack(self.format_string, *self.tuplify(v))
            for v in self.vertices])

    @property
    def accessors(self) -> List[Json]:
        component_types = {
            "f": Data.FLOAT, "I": Data.UNSIGNED_INT,
            "h": Data.SHORT, "H": Data.UNSIGNED_SHORT,
            "b": Data.BYTE, "B": Data.UNSIGNED_BYTE}
        out = list()
        offset = 0
        for attr, sub_format in self.format_.items():
            num_data, data_type = split_sub_format(sub_format)
            type_ = {n: f"VEC{n}" for n in (2, 3, 4)}.get(num_data, "SCALAR")
            out.append({
                "type": type_,
                "componentType": component_types[data_type].value,
                "byteOffset": offset,
                "count": len(self.vertices)})
            offset += struct.calcsize(sub_format)
        return out

    @property
    def bufferView(self) -> Json:
        return {
            "byteLength": self.byteLength,
            "target": Buffer.ARRAY.value,
            "byteStride": self.byteStride}

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
            loop_indices = [
                vertex_buffer.add(vertex)
                for vertex in polygon.vertices]
            fan_indices = [
                loop_indices[i]
                for i in geometry.triangle_fan(len(loop_indices))]
            new_indices.extend(fan_indices)
        self.indices.extend(new_indices)
        self.meshes.append((byteOffset, len(new_indices)))

    def as_bytes(self) -> bytes:
        return struct.pack(f"{len(self.indices)}I", *self.indices)

    @property
    def accessors(self) -> List[Json]:
        """bufferView is unset"""  # ???
        return [
            {"type": "SCALAR",
             "componentType": Data.UNSIGNED_INT.value,
             "byteOffset": mesh[0],
             "count": mesh[1]}
            for mesh in self.meshes]

    @property
    def bufferView(self) -> Json:
        """buffer is unset"""  # ???
        return {
            "byteLength": self.byteLength,
            "target": Buffer.ELEMENT_ARRAY.value}

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
        return [
            {"name": m.name}
            for m in self.materials]


BufferPair = Tuple[VertexBuffer, IndexBuffer]


class Gltf(base.SceneDescription):
    """WebGL Transmission Format"""
    buffers: List[BufferPair]
    models: Dict[str, geometry.Model]
    # TODO: named models: Dict[str, geometry.Model]
    json: Json

    def __init__(self):
        self.models = dict()
        self.buffers = list()
        self.json = dict()

    def __repr__(self) -> str:
        descriptor = f"{len(self.models)} models {len(self.buffers)} buffers"
        return f"<Gltf {descriptor} @ 0x{id(self):016X}>"

    def save_as(self, filename):
        """.gltf only! no .glb (yet)"""
        # TODO: use relpath so we can split off "./" is no folder if given
        folder, filename = os.path.split(filename)
        filename, ext = os.path.splitext(filename)
        assert ext == ".gltf", f"cannot write to '{ext}' extension"
        # write .bin
        for i, buffer_pair in enumerate(self.buffers):
            buffer_names = ("vertex", "index")
            for j, (name, buffer) in enumerate(zip(buffer_names, buffer_pair)):
                bin_name = f"{filename}.{name}.{i}.bin"
                self.json["buffers"][i * 2 + j]["uri"] = bin_name
                with open(os.path.join(folder, bin_name), "wb") as bin_file:
                    bin_file.write(buffer.as_bytes())
        # write .gltf
        with open(os.path.join(folder, f"{filename}.gltf"), "w") as json_file:
            json.dump(self.json, json_file, indent=2)

    @classmethod
    def from_buffers(cls, buffers: List[BufferPair]) -> Gltf:
        raise NotImplementedError()

    @classmethod
    def from_models(cls, models: base.ModelList) -> Gltf:
        out = super().from_models(models)

        # base json
        out.json = {
            "scene": 0, "scenes": [{"nodes": []}],
            "nodes": [], "meshes": [], "materials": [],
            "buffers": [], "bufferViews": [], "accessors": [],
            "asset": {"version": "2.0"}}
        out.json["scenes"][0]["nodes"] = [*range(len(out.models))]

        # buffers
        # TODO: add a new BufferPair for each vertex format
        # -- check uv count for mesh
        # -- optimising for unused vertex colour would be nice
        out.buffers = [(
            VertexBuffer(
                position="3f",
                normal="3f",
                # uv0="2f",
                # uv1="2f",
                colour="4f"),
            IndexBuffer())]
        vertex_buffer, index_buffer = out.buffers[0]

        # mesh geometry
        materials = MaterialList()
        mesh_offset = len(out.buffers[0][0])  # accessor index
        for i, (name, model) in enumerate(out.models.items()):
            # metadata
            angles_quaternion = quaternion.Quaternion.from_euler(model.angles)
            out.json["nodes"].append({
                "mesh": i,
                "name": name,
                "rotation": list(angles_quaternion),
                "translation": list(model.origin)})
            # triangles
            out.json["meshes"].append({
                "primitives": list()})
            for j, mesh in enumerate(model.meshes):
                material_index = materials.add(mesh.material)
                index_buffer.add(mesh, vertex_buffer)
                out.json["meshes"][-1]["primitives"].append({
                    "attributes": vertex_buffer.attributes,
                    "material": material_index,
                    "indices": mesh_offset + j})
            mesh_offset += len(model.meshes)

        # finalise
        out.json["materials"] = materials.json
        out.json["buffers"] = [
            {"byteLength": vertex_buffer.byteLength},
            {"byteLength": index_buffer.byteLength}]
        # NOTE: uri will be added by .save_as(filename)
        out.json["bufferViews"] = [
            {"buffer": 0, **vertex_buffer.bufferView},
            {"buffer": 1, **index_buffer.bufferView}]
        out.json["accessors"] = [
            *[{"bufferView": 0, **a} for a in vertex_buffer.accessors],
            *[{"bufferView": 1, **a} for a in index_buffer.accessors]]
        return out
