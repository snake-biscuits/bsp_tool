# https://openusd.org/release/glossary.html
from __future__ import annotations
import collections
import re
from typing import Any, Dict, Generator, List

from ..utils import geometry
from ..utils import vector
from . import base


reference_pattern = re.compile(r"@.*@(<.*>)?|<.*>")


# TODO: could we replicate material paths?
# -- how would blender interpret them?
def sanitise(material_name: str) -> str:
    material_name = material_name.replace("\\", "/")
    for bad_char in ".{}-":
        material_name = material_name.replace(bad_char, "_")
    return material_name.rpartition("/")[-1] if "/" in material_name else material_name


def usd_repr(value: Any) -> str:
    # NOTE: assumes lists of vectors will be converted beforehand
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        values = ", ".join(f'"{sanitise(v)}"' for v in value)
        return f"[{values}]"
    elif isinstance(value, str):
        if reference_pattern.fullmatch(value) is not None:
            return value
        else:
            return f'"{sanitise(value)}"'
    elif isinstance(value, (vector.vec2, vector.vec3)):
        return repr(tuple(value))
    else:
        return repr(value)


class Prim:
    type_: str
    name: str
    metadata: Dict[str, Any]
    properties: List[Property]
    children: List[Prim]

    def __init__(self, type_, name, metadata={}, properties=[], children=[]):
        self.type_ = type_
        self.name = name
        self.metadata = metadata
        self.properties = properties
        self.children = children

    def __repr__(self) -> str:
        descriptor = f'{self.type_} "{self.name}"'
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def lines(self) -> Generator[str, None, None]:
        # NOTE: "def" is only one specifier
        # -- but we haven't needed "over" or "class" yet
        if len(self.metadata) > 0:
            yield f'def {self.type_} "{self.name}" ('
            for name, value in self.metadata.items():
                yield f"    {name} = {usd_repr(value)}"
            yield ")"
        else:
            yield f'def {self.type_} "{self.name}"'
        yield "{"
        for property_ in self.properties:
            for line in property_.lines():
                yield f"    {line}"
        if len(self.properties) > 0 and len(self.children) > 0:
            yield ""  # newline
        for i, child in enumerate(self.children):
            if i > 0:
                yield ""  # newline
            for line in child.lines():
                yield f"    {line}" if line != "" else ""
        yield "}"

    @classmethod
    def from_lines(cls, lines: List[str]) -> Prim:
        raise NotImplementedError()
        # get type_ & name from header
        # get metadata
        # get properties
        # get child prim(s)
        # return cls(type_, name, metadata, properties, children)


class Property:
    type_: str
    name: str
    value: Any
    metadata: Dict[str, Any]

    def __init__(self, type_, name, value, **metadata):
        self.type_ = type_
        self.name = name
        self.value = value
        self.metadata = metadata

    def __repr__(self) -> str:
        if len(self.metadata) == 0:
            return f'Property("{self.type_}", "{self.name}", {usd_repr(self.value)})'
        metadata = ", ".join(f"{name}={value!r}" for name, value in self.metadata.items())
        return f'Property("{self.type_}", "{self.name}", {usd_repr(self.value)}, {metadata})'

    def lines(self) -> Generator[str, None, None]:
        value = list(map(tuple, self.value)) if self.type_[-4:] in ("2f[]", "3f[]") else self.value
        if len(self.metadata) > 0:
            yield f"{self.type_} {self.name} = {usd_repr(value)} ("
            for name, value in self.metadata.items():
                yield f"    {name} = {usd_repr(value)}"
            yield ")"
        else:
            yield f"{self.type_} {self.name} = {usd_repr(value)}"

    @classmethod
    def from_lines(cls, lines: List[str]) -> Property:
        raise NotImplementedError()
        # get type_, name & value
        # get metadata (if any)
        # return cls(type_, name, value, metadata)


class Usd(base.SceneDescription):
    """Pixar's Universal Scene Description format"""
    models: Dict[str, geometry.Model]
    exts_txt = [".usda", ".usd"]
    # NOTE: expects .usd to be text
    # TODO: detect txt vs. binary format in from_file if ext is .usd
    exts_bin = [".usdc"]
    # NOTE: not handling .usdz here, you can use .from_archive I guess
    metadata: Dict[str, Any]
    prims: List[Prim]

    def __init__(self):
        self.models = dict()
        self.metadata = dict(
            defaultPrim="root",
            metersPerUnit=0.0254,  # inches
            upAxis="Z")
        self.prims = list()

    def lines(self) -> Generator[str, None, None]:
        # generate prims if none exist & have models
        if len(self.prims) == 0 and len(self.models) > 0:
            self.regenerate_prims()
        yield "#usda 1.0"
        yield "("
        for name, value in self.metadata.items():
            yield f"    {name} = {usd_repr(value)}"
        yield ")"
        for i, prim in enumerate(self.prims):
            yield ""  # newline
            for line in prim.lines():
                yield line

    # TODO: material variants based on lightmap & cubemap indices (titanfall2)
    # -- could maybe do per-polygon attributes to encode this
    # TODO: catch duplicate material names ('Duplicate prim' will not load)
    def regenerate_prims(self):
        """build self.prims from self.models"""
        # translate models
        model_prims = list()
        for model_name, model in self.models.items():
            material_polygons = collections.defaultdict(list)
            # ^ {Material: [Polygon]}
            for mesh in model.meshes:
                material_polygons[mesh.material].extend(mesh.polygons)
            # core mesh properties
            face_lengths = [
                len(polygon.vertices)
                for polygons in material_polygons.values()
                for polygon in polygons]
            vertices = [
                vertex
                for polygons in material_polygons.values()
                for polygon in polygons
                for vertex in reversed(polygon.vertices)]
            # NOTE: crazy inefficient, but splitting models sucks
            uvs = [
                [
                    tuple(vertex.uv[i]) if i < len(vertex.uv) else (0, 0)
                    for vertex in vertices]
                for i in range(max(len(vertex.uv) for vertex in vertices))]
            # material binding spans
            start = 0
            material_bindings = list()
            for material, polygons in material_polygons.items():
                material_bindings.append(Prim(
                    "GeomSubset", sanitise(material.name),
                    metadata={
                        "prepend apiSchemas": ["MaterialBindingAPI"]},
                    properties=[
                        Property("uniform token", "elementType", "face"),
                        Property("uniform token", "familyName", "materialBind"),
                        Property("int[]", "indices", [*range(start, start + len(polygons))]),
                        Property("rel", "material:binding", "</_materials/sanitise>")]))
                start += len(polygons)
            # model prim
            model_prims.append(Prim(
                "Xform", model_name,
                properties=[
                    Property("float3", "xformOp:rotateXYZ", model.angles),
                    Property("float3", "xformOp:scale", model.scale),
                    Property("double3", "xformOp:translate", model.origin),
                    Property("uniform token[]", "xformOpOrder", [
                        "xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])],
                children=[
                    Prim(
                        "Mesh", model_name,
                        metadata={
                            "prepend apiSchemas": ["MaterialBindingAPI"]},
                        properties=[
                            Property("int[]", "faceVertexCounts", face_lengths),
                            Property("int[]", "faceVertexIndices", [*range(sum(face_lengths))]),
                            Property("point3f[]", "points", [vertex.position for vertex in vertices]),
                            Property("normal3f[]", "normals", [vertex.normal for vertex in vertices]),
                            *[
                                Property("texCoord2f[]", f"primvars:uv{i}", uv_layer, interpolation="faceVarying")
                                for i, uv_layer in enumerate(uvs)],
                            Property("color3f[]", "primvars:displayColor", [
                                tuple(vertex.colour[:3]) for vertex in vertices],
                                interpolation="vertex"),
                            Property("float[]", "primvars:displayOpacity", [
                                1 - (vertex.colour[3] / 255)
                                for vertex in vertices],
                                interpolation="vertex")],
                        children=material_bindings)]))
        # material prims
        materials = {
                mesh.material
                for model in self.models.values()
                for mesh in model.meshes}
        # TODO: try replicating the material folder structure
        material_prims = [
            Prim("Material", sanitise(material.name))
            for material in sorted(materials, key=lambda m: m.name)]
        # TODO: construct a material users can plug textures into
        # -- will require parsing .vmt, .rpak & .vpk
        # root prim
        root = Prim("Xform", "root", children=[
            *model_prims,
            Prim("Scope", "_materials", children=[
                *material_prims])])
        self.prims = [root]
