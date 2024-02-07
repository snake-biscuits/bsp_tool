from __future__ import annotations
from collections import defaultdict
from typing import Any, Dict, List

from . import physics
from . import texture


# TODO: Curve (CoDRadiant)
# TODO: Displacement (Source)
# TODO: Patch (IdTech 3)
# TODO: Tricoll (Titanfall) [for MRVN-Radiant]
# -- misc_model (embeds a .mdl for lightmapping)
# -- .gltf? iirc Respawn builds terrain in Autodesk Maya [citation needed]


class Brush:
    sides: List[BrushSide]

    def __init__(self, sides=None):
        self.sides = sides if sides is not None else list()

    def __repr__(self) -> str:
        return f"<Brush {len(self.sides)} sides @ 0x{id(self):012X}>"

    def as_physics(self) -> physics.Brush:
        # need to calculate brush bounds from sides
        # also need to confirm brush is valid (convex & closed)
        raise NotImplementedError()


class BrushSide:
    plane: physics.Plane
    shader: str
    texture_vector: texture.TextureVector
    # TODO: include rotation in texture.TextureVector
    texture_rotation: float

    def __init__(self, plane=physics.Plane((0, 0, 1), 0), shader="__TB_empty", texture_vector=None, rotation=0):
        self.plane = plane
        self.shader = shader
        if texture_vector is None:
            self.texture_vector = texture.TextureVector.from_normal(self.plane.normal)
        else:
            self.texture_vector = texture_vector
        self.texture_rotation = rotation

    def __repr__(self) -> str:
        # TODO: kwargs for texture axis & rotation (if shorter)
        return f"BrushSide({self.plane!r}, {self.shader!r}, ...)"


class Entity:
    # could do a class for each classname & use fgd-tool for type conversion...
    classname: str  # must be defined
    # NOT KEYVALUES
    brushes: List[Brush]
    _keys: List[str]  # key-value pairs to write
    # NOTE: keys will be stored w/ setattr

    def __init__(self, **kwargs):
        self.brushes = list()
        self._keys = list()
        for key, value in kwargs.items():
            self[key] = value

    def __delitem__(self, key: str):
        assert key in self._keys, f'cannot delete key "{key}"'
        self._keys.remove(key)
        delattr(self, key)

    def __getitem__(self, key: str) -> str:
        return getattr(self, key)

    def __repr__(self) -> str:
        lines = [
            "{",
            *[f'"{k}" "{self[k]}"' for k in self._keys],
            f"...skipped {len(self.brushes)} brushes...",
            "}"]
        return "\n".join(lines)

    def __setitem__(self, key: str, value: str):
        assert key not in ("_keys", "brushes"), f'cannot set key "{key}"'
        self._keys.append(key)
        setattr(self, key, value)

    def __str__(self):
        lines = [
            "{",
            *[f'"{k}" "{self[k]}"' for k in self._keys],
            *map(str, self.brushes),
            "}"]
        return "\n".join(lines)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class MapFile:
    comments: Dict[int, str]
    # ^ {line_no: "comment"}
    entities: List[Entity]
    worldspawn: Entity = property(lambda s: s.entities[0])

    def __init__(self):
        self.comments = dict()
        self.entities = list()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {len(self.entities)} entities>"

    def search(self, **search: Dict[str, str]) -> List[Entity]:
        """Search for entities by key-values; e.g. .search(key=value) -> [{"key": value, ...}, ...]"""
        return [e for e in self.entities if all([e.get(k, "") == v for k, v in search.items()])]

    def entities_by_classname(self) -> Dict[str, List[Entity]]:
        out = defaultdict(str)
        for entity in self.entities:
            out[entity.classname].append(entity)
        return dict(out)

    def save_as(self, filename: str):
        raise NotImplementedError()
