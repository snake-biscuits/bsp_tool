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
            usda_file.write('#usda 1.0\n(\n    upAxis = "Z"\n)\n\n\n')
            # TODO: 1x XForm & 1x Mesh per model
            # -- use GeomSubset & face indices to bind materials
            for model_name, model in self.models.items():
                # presort
                polygons = collections.defaultdict(list)
                # ^ {Material: [Polygon]}
                for mesh in model.meshes:
                    polygons[mesh.material].extend(mesh.polygons)
                face_lengths = [len(p.vertices) for ps in polygons.values() for p in ps]
                vertices = [v for ps in polygons.values() for p in ps for v in p.vertices]
                # write
                usda_file.write(f'def XForm "{model_name}"\n' + "{\n")
                # NOTE: columns, not rows; quite confusing
                matrix = [
                    (model.scale.x, 0, 0, 0),
                    (0, model.scale.y, 0, 0),
                    (0, 0, model.scale.z, 0),
                    (*model.origin, 1)]
                usda_file.write(" " * 4 + "matrix4d xformOp:transform = ( " + ", ".join(map(str, matrix)) + " )\n")
                usda_file.write(" " * 4 + 'uniform token[] xformOpOrder = ["xformOp:transform"]\n')
                # BUG: blender isn't applying the tranform matrix, why?
                # usda_file.write(" " * 4 + f"double3 xformOp:translate = {(*model.origin,)}\n")
                # usda_file.write(" " * 4 + 'uniform token[] xformOpOrder = ["xformOp:translate"]\n')
                # TODO: rotation
                usda_file.write("\n")
                # mesh
                usda_file.write(" " * 4 + f'def Mesh "{model_name}" (\n')
                usda_file.write(" " * 8 + 'prepend apiSchemas = ["MaterialBindingAPI"]\n')
                usda_file.write(" " * 4 + ")\n")
                usda_file.write(" " * 4 + "{\n")
                usda_file.write(" " * 8 + f"int[] faceVertexCounts = {face_lengths}\n")
                usda_file.write(" " * 8 + f"int[] faceVertexIndices = {[*range(sum(face_lengths))]}\n")
                usda_file.write(" " * 8 + f"point3f[] points = {[(*v.position,) for v in vertices]}\n")
                usda_file.write(" " * 8 + f"normal3f[] normals = {[(*v.normal,) for v in vertices]}\n")
                # NOTE: crazy inefficient, but splitting models sucks
                num_uvs = max(len(v.uv) for v in vertices)
                for i in range(num_uvs):
                    uvs = [(*v.uv[i],) if i < len(v.uv) else (0, 0) for v in vertices]
                    usda_file.write(" " * 8 + f"texCoord2f[] primvars:uv{i} = {uvs} (\n")
                    usda_file.write(" " * 12 + 'interpolation = "faceVarying"\n')
                    usda_file.write(" " * 8 + ")\n")
                usda_file.write(" " * 8 + f"color3f[] primvars:displayColor = {[(*v.colour[:3],) for v in vertices]} (\n")
                usda_file.write(" " * 12 + 'interpolation = "vertex"\n')
                usda_file.write(" " * 8 + ")\n")
                usda_file.write(" " * 8 + f"float[] primvars:displayOpacity = {[v.colour[3] / 255 for v in vertices]} (\n")
                usda_file.write(" " * 12 + 'interpolation = "vertex"\n')
                usda_file.write(" " * 8 + ")\n")
                start = 0
                for material in polygons:
                    usda_file.write("\n")
                    usda_file.write(" " * 8 + f'def GeomSubset "{sanitise(material.name)}" (\n')
                    usda_file.write(" " * 12 + 'prepend apiSchemas = ["MaterialBindingAPI"]\n')
                    usda_file.write(" " * 8 + ")\n")
                    usda_file.write(" " * 8 + "{\n")
                    usda_file.write(" " * 12 + 'uniform token elementType = "face"\n')
                    usda_file.write(" " * 12 + 'uniform token familyName = "materialBind"\n')
                    usda_file.write(" " * 12 + f"int[] indices = {[*range(start, start + len(polygons[material]))]}\n")
                    usda_file.write(" " * 12 + f"rel material:binding = </_materials/{sanitise(material.name)}>\n")
                    usda_file.write(" " * 8 + "}\n")
                    start += len(polygons[material])
                usda_file.write(" " * 4 + "}\n")
                usda_file.write("}\n\n")
            # materials
            usda_file.write('def "_materials"\n{\n')
            materials = {me.material for mo in self.models.values() for me in mo.meshes}
            for material in materials:
                usda_file.write(" " * 4 + f'def Material "{sanitise(material.name)}"\n')
                usda_file.write(" " * 4 + "{\n")
                # TODO: wire up uvs & import textures
                # -- will require a more sophisticated Material system
                # -- also .vmt & .rpak parsing etc.
                usda_file.write(" " * 4 + "}\n")
            usda_file.write("}\n")
