import collections
import os
from typing import Dict, Generator

from ...utils import geometry
from . import base


# TODO: material variants based on lightmap & cubemap indices (titanfall2)
# -- could maybe do per-polygon attributes to encode this
# TODO: catch duplicate material names ('Duplicate prim' will not load)

def sanitise(material_name: str) -> str:
    material_name = material_name.replace("\\", "/")
    for bad_char in ".{}-":
        material_name = material_name.replace(bad_char, "_")
    return material_name.rpartition("/")[-1] if "/" in material_name else material_name


class Usd(base.SceneDescription):
    """Pixar's Universal Scene Description format"""
    models: Dict[str, geometry.Model]
    meters_per_unit: float = 0.0254  # inches
    exts_txt = [".usda", ".usd"]
    # NOTE: expects .usd to be text
    # TODO: detect txt vs. binary format in from_file if ext is .usd
    exts_bin = [".usdc"]
    # NOTE: not handling .usdz here, you can use .from_archive I guess

    def lines(self) -> Generator[str, None, None]:
        yield "#usda 1.0"
        yield "("
        yield base.indent(1) + 'defaultPrim = "root"'
        yield base.indent(1) + f"metersPerUnit = {self.meters_per_unit}"
        yield base.indent(1) + 'upAxis = "Z"'
        yield ")"
        yield ""  # newline
        # root node
        yield 'def Xform "root" ('
        # TODO: metadata
        yield ")"
        yield "{"
        for model_name, model in self.models.items():
            # presort
            material_polygons = collections.defaultdict(list)
            # ^ {Material: [Polygon]}
            for mesh in model.meshes:
                material_polygons[mesh.material].extend(mesh.polygons)
            face_lengths = [
                len(polygon.vertices)
                for polygons in material_polygons.values()
                for polygon in polygons]
            vertices = [
                vertex
                for polygons in material_polygons.values()
                for polygon in polygons
                for vertex in reversed(polygon.vertices)]
            # write
            yield base.indent(1) + f'def Xform "{model_name}"'
            yield base.indent(1) + "{"

            yield base.indent(2) + f"float3 xformOp:rotateXYZ = {tuple(model.angles)}"
            yield base.indent(2) + f"float3 xformOp:scale = {tuple(model.scale)}"
            yield base.indent(2) + f"double3 xformOp:translate = {tuple(model.origin)}"
            yield base.indent(2) + "uniform token[] xformOpOrder = " + str([
                "xformOp:translate", "xformOp:rotateXYZ", "xformOp:scale"])
            yield ""  # newline
            # mesh
            yield base.indent(2) + f'def Mesh "{model_name}" ('
            yield base.indent(3) + 'prepend apiSchemas = ["MaterialBindingAPI"]'
            yield base.indent(2) + ")"
            yield base.indent(2) + "{"
            yield base.indent(3) + f"int[] faceVertexCounts = {face_lengths}"
            indices = [*range(sum(face_lengths))]
            yield base.indent(3) + f"int[] faceVertexIndices = {indices}"
            points = [tuple(vertex.position) for vertex in vertices]
            yield base.indent(2) + f"point3f[] points = {points}"
            normals = [tuple(vertex.normal) for vertex in vertices]
            yield base.indent(2) + f"normal3f[] normals = {normals}"
            # NOTE: crazy inefficient, but splitting models sucks
            num_uvs = max(len(vertex.uv) for vertex in vertices)
            for i in range(num_uvs):
                uvs = [
                    tuple(vertex.uv[i]) if i < len(v.uv) else (0, 0)
                    for vertex in vertices]
                yield base.indent(3) + f"texCoord2f[] primvars:uv{i} = {uvs} ("
                yield base.indent(4) + 'interpolation = "faceVarying"'
                yield base.indent(3) + ")"
            colours = [tuple(vertex.colour[:3]) for vertex in vertices]
            yield base.indent(3) + f"color3f[] primvars:displayColor = {colours} ("
            yield base.indent(4) + 'interpolation = "vertex"'
            yield base.indent(3) + ")"
            opacities = [1 - (vertex.colour[3] / 255) for vertex in vertices]
            yield base.indent(3) + f"float[] primvars:displayOpacity = {opacities} ("
            yield base.indent(4) + 'interpolation = "vertex"'
            yield base.indent(3) + ")"
            start = 0
            for material, polygons in material_polygons.items():
                yield ""  # newline
                yield base.indent(3) + f'def GeomSubset "{sanitise(material.name)}" ('
                yield base.indent(4) + 'prepend apiSchemas = ["MaterialBindingAPI"]'
                yield base.indent(3) + ")"
                yield base.indent(3) + "{"
                yield base.indent(4) + 'uniform token elementType = "face"'
                yield base.indent(4) + 'uniform token familyName = "materialBind"'
                indices = [*range(start, start + len(polygons))]
                yield base.indent(4) + f"int[] indices = {indices}"
                binding = f"</_materials/{sanitise(material.name)}>"
                yield base.indent(4) + f"rel material:binding = {binding}"
                yield base.indent(3) + "}"
                start += len(polygons)
            yield base.indent(2) + "}"
            yield base.indent(1) + "}"
            yield ""  # newline
        # materials
        yield base.indent(1) + 'def Scope "_materials"'
        yield "{"
        materials = {
            mesh.material
            for model in self.models.values()
            for mesh in model.meshes}
        for material in materials:
            yield base.indent(2) + f'def Material "{sanitise(material.name)}"'
            yield base.indent(2) + "{"
            # TODO: wire up uvs & import textures
            # -- will require a more sophisticated Material system
            # -- also .vmt & .rpak parsing etc.
            yield base.indent(2) + "}"
        yield base.indent(1) + "}"
        yield "}"
