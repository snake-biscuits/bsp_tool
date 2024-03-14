import os
from typing import List

from ...utils import geometry


def sanitise(material_name: str) -> str:
    return material_name.replace("\\", "/").replace("/", "_").replace(".", "_")


class USDA:
    models: List[geometry.Model]
    # TODO: named models

    def __init__(self, models=list()):
        self.models = models

    def __repr__(self) -> str:
        return f"<USDA {len(self.models)} models @ 0x{id(self):016X}>"

    # TODO: @classmethod def from_file(cls, filename) -> USDA:

    def save_as(self, filename):
        folder, filename = os.path.split(filename)
        filename, ext = os.path.splitext(filename)
        assert ext == ".usda", f"cannot write to '{ext}' extension"
        # no .usdc or .usdz; .usd is ok, but .usda is more explicit
        with open(os.path.join(folder, f"{filename}.usda"), "w") as usda_file:
            usda_file.write('#usda 1.0\n(\n    upAxis = "Z"\n)\n\n\n')
            # TODO: 1x XForm & 1x Mesh per model
            # -- use GeomSubset & face indices to bind materials
            for i, model in enumerate(self.models):
                usda_file.write(f'def XForm "model_{i:03d}"\n' + "{\n")
                usda_file.write(" " * 4 + "matrix4d xformOp:transform = ( ")
                # TODO: rotation
                # NOTE: columns, not rows; quite confusing
                transform_matrix = [
                    (model.scale.x, 0, 0, 0),
                    (0, model.scale.y, 0, 0),
                    (0, 0, model.scale.z, 0),
                    (*model.origin, 1)]
                usda_file.write(", ".join(map(str, transform_matrix)))
                usda_file.write(" )\n")
                usda_file.write(" " * 4 + 'uniform token[] xformOpOrder = ["xformOp:transform"]\n')
                for j, mesh in enumerate(model.meshes):
                    # NOTE: Blender names meshes after Mesh, not XFrom when importing
                    usda_file.write(" " * 4 + f'def Mesh "mesh_{j:03d}" (\n')
                    usda_file.write(" " * 8 + 'prepend apiSchemas = ["MaterialBindingAPI"]\n')
                    usda_file.write(" " * 4 + ")\n")
                    usda_file.write(" " * 4 + "{\n")
                    usda_file.write(" " * 8 + f"rel material:binding = </_materials/{sanitise(mesh.material.name)}>\n")
                    face_lengths = [len(p.vertices) for p in mesh.polygons]
                    usda_file.write(" " * 8 + f"int[] faceVertexCounts = {face_lengths}\n")
                    usda_file.write(" " * 8 + f"int[] faceVertexIndices = {[*range(sum(face_lengths))]}\n")
                    vertices = [v for p in mesh.polygons for v in p.vertices]
                    usda_file.write(" " * 8 + f"point3f[] points = {[(*v.position,) for v in vertices]}\n")
                    # NOTE: some values include exponent, might make the importer unhappy
                    usda_file.write(" " * 8 + f"normal3f[] normals = {[(*v.normal,) for v in vertices]}\n")
                    # NOTE: assuming all vertices in mesh use the same format
                    num_uvs = len(vertices[0].uv)
                    for k in range(num_uvs):
                        usda_file.write(f"        texCoord2f[] primvars:uv{k} = {[(*v.uv[k],) for v in vertices]}\n")
                    usda_file.write(" " * 8 + f"color3f[] primvars:displayColor = {[(*v.colour[:3],) for v in vertices]} (\n")
                    usda_file.write(" " * 12 + 'interpolation = "vertex"\n' + " " * 8 + ")\n")
                    usda_file.write(" " * 8 + f"float[] primvars:displayOpacity = {[v.colour[3] for v in vertices]} (\n")
                    usda_file.write(" " * 12 + 'interpolation = "vertex"\n' + " " * 8 + ")\n")
                    usda_file.write(" " * 4 + "}\n")
                usda_file.write("}\n\n")
            # materials
            materials = sorted({sanitise(me.material.name) for mo in self.models for me in model.meshes})
            usda_file.write('def "_materials"\n{\n')
            for material_name in materials:
                usda_file.write(" " * 4 + f'def Material "{material_name}"\n')
                # TODO: wire up uvs & import textures
                # -- will require a more sophisticated Material system
                # -- also .vmt & .rpak parsing etc.
                usda_file.write(" " * 4 + "{\n" + " " * 4 + "}\n")
            usda_file.write("}\n")
