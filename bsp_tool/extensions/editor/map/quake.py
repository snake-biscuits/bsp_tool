# https://quakewiki.org/wiki/Quake_Map_Format
import re

from ....utils import editor as generic
from ....utils import texture
from .. import base
from .. import common


class BrushSide(base.MetaPattern):
    spec = "plane shader s_offset t_offset rotation s_scale t_scale"
    patterns = {"plane": common.Plane, "shader": common.Filepath, "rotation": common.Float}
    patterns.update({f"{v}_{a}": common.Float for v in "st" for a in ("offset", "scale")})

    class ValueType(generic.BrushSide):
        def __init__(self, plane, shader, s_offset, t_offset, rotation, s_scale, t_scale):
            self.plane = plane
            self.shader = shader
            self.texture_rotation = rotation
            self.texture_vector = texture.TextureVector.from_normal(self.plane.normal)
            self.texture_vector.s.offset = s_offset
            self.texture_vector.t.offset = t_offset
            self.texture_vector.s.scale = s_scale
            self.texture_vector.t.scale = t_scale

        def __str__(self) -> str:
            plane = common.Plane()
            plane.value = self.plane
            offsets = " ".join([str(pa.offset) for pa in self.texture_vector])
            scales = " ".join([str(pa.scale) for pa in self.texture_vector])
            f"{plane} {self.shader} {offsets} {self.texture_rotation} {scales}"


class MapFile(generic.MapFile):
    BrushSideClass: base.MetaPattern = BrushSide

    @classmethod
    def from_file(cls, filepath: str):
        out = cls()
        node_depth = 0
        patterns = {"Comment": common.Comment.regex,
                    "KeyValuePair": common.KeyValuePair.regex(),
                    "BrushSide": cls.BrushSideClass.regex()}
        patterns = {k: re.compile(v) for k, v in patterns.items()}
        with open(filepath) as source_file:
            for line_no, line in enumerate(source_file):
                line = line.strip()
                if line == "":
                    continue  # MRVN-Radiant
                elif patterns["Comment"].match(line):
                    # NOTE: only catches full line comments
                    # TODO: catch trailing comments
                    out.comments[line_no] = line
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
                    brush.sides.append(cls.BrushSideClass.from_string(line).value)
                else:
                    raise RuntimeError(f"Couldn't parse line #{line_no}: '{line}'")
            assert node_depth == 0, f"{filepath} ends prematurely at line {line_no}"
        return out
