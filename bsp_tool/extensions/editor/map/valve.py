# https://quakewiki.org/wiki/Quake_Map_Format#Valve_variation_of_the_format
from ....utils import editor as generic
from ....utils import texture
from .. import base
from .. import common
from . import quake


class ProjectionAxis(base.MetaPattern):
    spec = "[ x y z offset ]"
    patterns = {a: common.Float for a in [*"xyz", "offset"]}

    class ValueType(texture.ProjectionAxis):
        def __init__(self, x: float, y: float, z: float, offset: float = None):
            texture.ProjectionAxis.__init__(self, [x, y, z], offset)


class BrushSide(base.MetaPattern):
    spec = "plane shader s_axis t_axis rotation s_scale t_scale"
    patterns = {"plane": common.Plane, "shader": common.Filepath, "rotation": common.Float}
    patterns.update({f"{v}_axis": ProjectionAxis for v in "st"})
    patterns.update({f"{v}_scale": common.Float for v in "st"})

    class ValueType(generic.BrushSide):
        def __init__(self, **kwargs):
            self.plane = kwargs["plane"]
            self.shader = kwargs["shader"]
            self.texture_rotation = kwargs["rotation"]
            self.texture_vector = texture.TextureVector(kwargs["s_axis"], kwargs["t_axis"])
            self.texture_vector.s.scale = kwargs["s_scale"]
            self.texture_vector.t.scale = kwargs["t_scale"]

        def __str__(self) -> str:
            plane = common.Plane()
            plane.value = self.plane
            axes = [str(ProjectionAxis(**{a: getattr(pa, a) for a in [*"xyz", "offset"]})) for pa in self.texture_vector]
            scales = [str(pa.scale) for pa in self.texture_vector]
            f"{plane} {self.shader} {' '.join(axes)} {self.texture_rotation} {' '.join(scales)}"


class MapFile(quake.MapFile):
    BrushSideClass = BrushSide
