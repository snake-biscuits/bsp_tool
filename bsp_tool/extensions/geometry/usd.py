import collections
import os
from typing import Dict

from ...utils import geometry


# TODO: material variants based on lightmap & cubemap indices
# -- could maybe do per-polygon attributes to encode this
# TODO: catch duplicate material names ('Duplicate prim' will not load)

def sanitise(material_name: str) -> str:
    material_name = material_name.replace("\\", "/")
    for bad_char in ".{}-":
        material_name = material_name.replace(bad_char, "_")
    return material_name.rpartition("/")[-1] if "/" in material_name else material_name


class USDA:
    models: Dict[str, geometry.Model]
    meters_per_unit: float = 0.0254  # inches

    def __init__(self, models=dict()):
        if isinstance(models, list):
            models = {f"model_{i:03d}": model for i, model in enumerate(models)}
        self.models = models

    def __repr__(self) -> str:
        return f"<USDA {len(self.models)} models @ 0x{id(self):016X}>"

    # TODO: @classmethod def from_file(cls, filename) -> USDA:

    def save_as(self, filename):
        folder, filename = os.path.split(filename)
        filename, ext = os.path.splitext(filename)
        assert ext == ".usda", f"cannot write to '{ext}' extension"
        # no .usdc or .usdz; .usd is ok, but .usda is more explicit
        # TODO: check shortened material names are unique across all meshes
        with open(os.path.join(folder, f"{filename}.usda"), "w") as usda_file:
            usda_file.write("\n".join([
                "#usda 1.0\n(",
                '    defaultPrim = "root"',
                f"    metersPerUnit = {self.meters_per_unit}",
                '    upAxis = "Z"',
                ")"]))
            usda_file.write("\n\n")
            # root node
            usda_file.write("\n".join([
                'def Xform "root" (',
                # TODO: metadata
                ")", "{"]))
            usda_file.write("\n")

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
                usda_file.write(" " * 4 + f'def Xform "{model_name}"\n')
                usda_file.write(" " * 4 + "{\n")
                # NOTE: columns, not rows; quite confusing
                # TODO: rotation
                matrix = [
                    (model.scale.x, 0, 0, 0),
                    (0, model.scale.y, 0, 0),
                    (0, 0, model.scale.z, 0),
                    (*model.origin, 1)]
                usda_file.write(" " * 8 + "matrix4d xformOp:transform = ( " + ", ".join(map(str, matrix)) + " )\n")
                usda_file.write(" " * 8 + 'uniform token[] xformOpOrder = ["xformOp:transform"]\n')
                usda_file.write("\n")
                # mesh
                usda_file.write(" " * 8 + f'def Mesh "{model_name}" (\n')
                usda_file.write(" " * 12 + 'prepend apiSchemas = ["MaterialBindingAPI"]\n')
                usda_file.write(" " * 8 + ")\n")
                usda_file.write(" " * 8 + "{\n")
                usda_file.write(" " * 12 + f"int[] faceVertexCounts = {face_lengths}\n")
                usda_file.write(" " * 12 + f"int[] faceVertexIndices = {[*range(sum(face_lengths))]}\n")
                usda_file.write(" " * 8 + f"point3f[] points = {[(*v.position,) for v in vertices]}\n")
                usda_file.write(" " * 8 + f"normal3f[] normals = {[(*v.normal,) for v in vertices]}\n")
                # NOTE: crazy inefficient, but splitting models sucks
                num_uvs = max(len(v.uv) for v in vertices)
                for i in range(num_uvs):
                    uvs = [(*v.uv[i],) if i < len(v.uv) else (0, 0) for v in vertices]
                    usda_file.write(" " * 12 + f"texCoord2f[] primvars:uv{i} = {uvs} (\n")
                    usda_file.write(" " * 16 + 'interpolation = "faceVarying"\n')
                    usda_file.write(" " * 12 + ")\n")
                usda_file.write(" " * 12 + f"color3f[] primvars:displayColor = {[(*v.colour[:3],) for v in vertices]} (\n")
                usda_file.write(" " * 16 + 'interpolation = "vertex"\n')
                usda_file.write(" " * 12 + ")\n")
                usda_file.write(" " * 12 + f"float[] primvars:displayOpacity = {[1 - (v.colour[3] / 255) for v in vertices]} (\n")
                usda_file.write(" " * 16 + 'interpolation = "vertex"\n')
                usda_file.write(" " * 12 + ")\n")
                start = 0
                for material, polygons in material_polygons.items():
                    usda_file.write("\n")
                    usda_file.write(" " * 12 + f'def GeomSubset "{sanitise(material.name)}" (\n')
                    usda_file.write(" " * 16 + 'prepend apiSchemas = ["MaterialBindingAPI"]\n')
                    usda_file.write(" " * 12 + ")\n")
                    usda_file.write(" " * 12 + "{\n")
                    usda_file.write(" " * 16 + 'uniform token elementType = "face"\n')
                    usda_file.write(" " * 16 + 'uniform token familyName = "materialBind"\n')
                    usda_file.write(" " * 16 + f"int[] indices = {[*range(start, start + len(polygons))]}\n")
                    usda_file.write(" " * 16 + f"rel material:binding = </_materials/{sanitise(material.name)}>\n")
                    usda_file.write(" " * 12 + "}\n")
                    start += len(polygons)
                usda_file.write(" " * 8 + "}\n")
                usda_file.write(" " * 4 + "}\n\n")
            # materials
            usda_file.write(" " * 4 + 'def Scope "_materials"\n{\n')
            materials = {me.material for mo in self.models.values() for me in mo.meshes}
            for material in materials:
                usda_file.write(" " * 8 + f'def Material "{sanitise(material.name)}"\n')
                usda_file.write(" " * 8 + "{\n")
                # TODO: wire up uvs & import textures
                # -- will require a more sophisticated Material system
                # -- also .vmt & .rpak parsing etc.
                usda_file.write(" " * 8 + "}\n")
            usda_file.write(" " * 4 + "}\n")
            usda_file.write("}\n")
