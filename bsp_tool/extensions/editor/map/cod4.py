# https://wiki.zeroy.com/index.php?title=Call_of_duty_4:_.MAP_file_structure
# NOTE: might need to use Wayback Machine (web.archive.org)
import re

from ....utils import editor as generic
from ....utils import texture
from .. import base
from .. import common


# TODO: Curves & other non-brush geo

class Projection(base.MetaPattern):
    spec = " ".join(("width", "height", *[f"unknown_{i}" for i in range(4)]))
    patterns = {"width": common.Integer, "height": common.Integer}
    patterns.update({f"unknown_{i}": common.Float for i in range(4)})

    # TODO: class ValueType(texture.TextureVector): ...


class BrushSide(base.MetaPattern):
    spec = "plane shader shader_projection lightmap lightmap_projection"
    patterns = {"plane": common.Plane, "shader": common.Filepath, "lightmap": common.Filepath}
    patterns.update({f"{s}_projection": Projection for s in ("shader", "lightmap")})

    class ValueType(generic.BrushSide):
        def __init__(self, plane, shader, shader_projection, lightmap, lightmap_projection):
            self.plane = plane
            self.shader = shader
            self.texture_rotation = 0
            self.texture_vector = texture.TextureVector.from_normal(plane.normal)
            self.shader_size = [shader_projection.width, shader_projection.height]
            self.lightmap_size = [lightmap_projection.width, lightmap_projection.height]

        def __str__(self) -> str:
            plane = common.Plane()
            plane.value = self.plane
            shader_projection = Projection(*self.shader_size).value
            lightmap_projection = Projection(*self.lightmap_size).value
            return f"{plane} {self.shader} {shader_projection} {self.lightmap} {lightmap_projection}"


class MapFile(generic.MapFile):
    @classmethod
    def from_file(cls, filepath: str):
        out = cls()
        node_depth = 0
        patterns = {"Comment": common.Comment.regex,
                    "KeyValuePair": common.KeyValuePair.regex(),
                    "BrushSide": BrushSide.regex(),
                    "Flags": r'"[A-Za-z0-9_ ]+"\s+flags(\s+active)?'}
        patterns = {k: re.compile(v) for k, v in patterns.items()}
        with open(filepath) as source_file:
            assert source_file.readline().rstrip() == "iwmap 4"
            for line_no, line in enumerate(source_file):
                line = line.strip()
                if patterns["Comment"].match(line):
                    # NOTE: only catches full line comments
                    # TODO: catch trailing comments
                    out.comments[line_no] = line
                elif patterns["Flags"].match(line):
                    pass  # ignore
                elif line.strip() == "{":
                    node_depth += 1
                    if node_depth == 1:
                        entity = generic.Entity()
                        out.entities.append(entity)
                    elif node_depth == 2:
                        brush = generic.Brush()
                        entity.brushes.append(brush)
                    else:
                        raise NotImplementedError()
                elif line.strip() == "}":
                    node_depth -= 1
                elif patterns["KeyValuePair"].match(line):
                    assert node_depth == 1, "keyvalues outside of entity"
                    kvp = common.KeyValuePair.from_string(line).value
                    entity[kvp.key] = kvp.value
                elif patterns["BrushSide"].match(line):
                    assert node_depth == 2, "brushside outside of brush"
                    brush.sides.append(BrushSide.from_string(line).value)
                else:
                    raise RuntimeError(f"Couldn't parse line #{line_no}: '{line}'")
            assert node_depth == 0, f"{filepath} ends prematurely at line {line_no}"
        return out
