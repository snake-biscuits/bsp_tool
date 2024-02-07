from __future__ import annotations
import re
from typing import Dict, List

from ....utils import editor as generic
from ....utils import texture
from .. import base
from .. import common


# TODO: Entity connections (Entity IO)
# TODO: assert / checks / verification around Entity / Brush / BrushSide "id"
# TODO: Displacements
# TODO: `hidden` nodes
# TODO: visgroup filtering to find ents etc.


class ProjectionAxis(base.MetaPattern):
    spec = "[ x y z offset ] scale"
    patterns = {a: common.Float for a in [*"xyz", "offset", "scale"]}

    class ValueType(texture.ProjectionAxis):
        def __init__(self, x: float, y: float, z: float, offset: float = None, scale: float = None):
            texture.ProjectionAxis.__init__(self, [x, y, z], offset, scale)


class Node:
    node_type: str
    key_values: List[(str, str)]
    # NOTE: like a dict, but keys can appear more than once
    # -- add new entries w/ .append((key, value)) [.extend is also valid]
    # -- dict(key_values) will use the last occurence of each key
    nodes: List[Node]

    def __init__(self, node_type: str):
        self.node_type = node_type
        self.key_values = list()
        self.nodes = list()

    def __delitem__(self, key: str):
        index = self.key_values.index((key, self[key]))
        self.key_values.pop(index)

    def __getitem__(self, key: str) -> str:
        return dict(self.key_values)[key]

    def __repr__(self) -> str:
        return "\n".join([
            self.node_type,
            "{",
            *[f'\t"{k}" "{v}"' for k, v in self.key_values],
            *[f"\t... hid {len(ns)} {t} nodes ..." for t, ns in self.nodes_by_type().items()],
            "}"])

    def __setitem__(self, key: str, value: str):
        index = self.key_values.index((key, self[key]))
        self.key_values[index] = (key, value)

    def __str__(self) -> str:
        return "\n".join([
            self.node_type,
            "{",
            *[f'\t"{k}" "{v}"' for k, v in self.key_values],
            *map(str, self.nodes),
            "}"])

    # KEY VALUE HANDLERS

    def get(self, key: str, default=None) -> str:
        return dict(self.key_values).get(key, default)

    def items(self) -> List[(str, str)]:
        return self.key_values

    def keys(self) -> List[str]:
        return [k for k, v in self.key_values]

    def update(self, kv_dict: Dict[str, str]):
        for k, v in kv_dict.items():
            self.key_values[k] = v

    def values(self) -> List[str]:
        return [v for k, v in self.key_values]

    # CHILD NODE HANDLERS

    def nodes_by_type(self) -> Dict[str, List[Node]]:
        return {t: [n for n in self.nodes if n.node_type == t]
                for t in sorted({n.node_type for n in self.nodes})}


# TODO: class DispInfo(generic.DispInfo):


class BrushSide(generic.BrushSide):
    def as_node(self) -> Node:
        out = Node("side")
        key_values = {
            "plane": common.Plane(*self.plane.as_triangle()).value,
            "material": self.shader,
            **{f"{a}axis": ProjectionAxis(*pa.axis, pa.offset, pa.scale).value
               for a, pa in zip("uv", self.texture_vector)},
            "rotation": self.texture_rotation}
        out.update({k: str(v) for k, v in key_values.items()})
        # TODO: dispinfo child node
        return out

    @classmethod
    def from_node(cls, node: Node) -> BrushSide:
        assert node.node_type == "side"
        plane = common.Plane.from_string(node["plane"]).value
        shader = node["material"]
        uaxis, vaxis = [ProjectionAxis.from_string(node[f"{a}axis"]).value for a in "uv"]
        texture_vector = texture.TextureVector(uaxis, vaxis)
        rotation = node["rotation"]
        # TODO: node.nodes_by_type().get("dispinfo", [])
        return cls(plane, shader, texture_vector, rotation)


class Brush(generic.Brush):
    def as_node(self) -> Node:
        out = Node("solid")
        out.nodes = [b.as_node() for b in self.sides]
        # TODO: editor node & entities
        return out

    @classmethod
    def from_node(cls, node: Node) -> Brush:
        assert node.node_type == "solid"
        return cls([BrushSide.from_node(n) for n in node.nodes_by_type().get("side", [])])


class Entity(generic.Entity):
    # TODO: Connections (Entity IO)

    def as_node(self) -> Node:
        out = Node("entity")
        out.key_values = [(k, self[k]) for k in self._keys]
        out.nodes = [b.as_node() for b in self.brushes]
        return out

    @classmethod
    def from_node(cls, node: Node) -> Entity:
        assert node.node_type in ("entity", "world")
        out = cls(**dict(node.key_values))
        out.brushes = [Brush.from_node(n) for n in node.nodes_by_type().get("solid", [])]
        return out


class MapFile(generic.MapFile):
    entities: List[Entity]
    nodes: List[Node]

    def __init__(self):
        self.entities = list()
        self.nodes = list()

    def nodes_by_type(self) -> Dict[str, List[Node]]:
        return {t: [n for n in self.nodes if n.node_type == t]
                for t in sorted({n.node_type for n in self.nodes})}

    @classmethod
    def from_file(cls, filepath: str):
        out = cls()
        node_depth = 0
        node_type = None
        patterns = {"KeyValuePair": common.KeyValuePair.regex(),
                    "NodeType": r"[a-z_]+"}
        patterns = {k: re.compile(v) for k, v in patterns.items()}

        def parent() -> Node:
            parent_node = out
            for i in range(node_depth):  # off by one?
                parent_node = parent_node.nodes[-1]
            return parent_node

        with open(filepath) as source_file:
            for line_no, line in enumerate(source_file):
                line = line.strip()  # ignore indentation & trailing newline
                # TODO: assert each open curly brace is preceded by a nodetype
                if patterns["NodeType"].match(line):
                    node_type = line
                elif line == "{":
                    node = Node(node_type)
                    parent().nodes.append(node)
                    node_depth += 1
                elif patterns["KeyValuePair"].match(line):
                    kvp = common.KeyValuePair.from_string(line).value
                    node.key_values.append((kvp.key, kvp.value))
                elif line == "}":
                    node_depth -= 1
                    node = parent()
                else:
                    raise RuntimeError(f"Couldn't parse line #{line_no}: '{line}'")
            assert node_depth == 0

        # nodes -> entities
        nodes_dict = out.nodes_by_type()
        assert len(nodes_dict["world"]) == 1
        out.entities.append(nodes_dict["world"][0])
        out.entities.extend(nodes_dict.get("entity", []))
        out.entities = [Entity.from_node(e) for e in out.entities]
        # out.nodes = [n for n in out.nodes if n.node_type not in ("world", "entity")]
        # NOTE: when writing, we should try to put ents in the same-ish place (before cameras & cordons)
        return out
