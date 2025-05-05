"""PhysicsCollide SpecialLumpClasses"""
# SourceIO/library/source1/phy/phy.py
from __future__ import annotations
import collections
import enum
import io
import struct
from typing import List, Union

from ... import core
from ...utils import binary
from ...utils import vector


# PhysicsCollide headers
class ModelHeader(core.Struct):
    """dphysmodel_t"""
    __slots__ = ["model", "data_size", "script_size", "solid_count"]
    _format = "4i"
    # (-1, -1, 0, 0) for end of lump


PhysicsObject = collections.namedtuple("PhysicsObject", ["header", "solids", "script"])
# ^ (ModelHeader, List[bytes], bytes)


class CollideLump(list):
    """[model_index: int, solids: List[bytes], script: bytes]"""
    # passed to VCollideLoad in vphysics.dll
    # TODO: List[PhysicsObject] isn't the best interface
    def __init__(self, iterable: List[PhysicsObject] = tuple()):
        return super().__init__(iterable)

    def as_bytes(self) -> bytes:
        def phy_bytes(collision_model: PhysicsObject):
            header, solids, script = collision_model
            phy_blocks = list()
            for phy_block in solids:
                collision_data = phy_block.as_bytes()
                phy_blocks.append(len(collision_data).to_bytes(4, "little"))
                phy_blocks.append(collision_data)
            phy_block_bytes = b"".join(phy_blocks)
            header = ModelHeader(header.model, len(phy_block_bytes), len(script), len(solids)).as_bytes()
            return b"".join([header, phy_block_bytes, script])
        tail = ModelHeader(-1, -1, 0, 0).as_bytes()
        return b"".join([*map(phy_bytes, self), tail])

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> List[PhysicsObject]:
        collision_models = list()
        lump = io.BytesIO(raw_lump)
        header = ModelHeader.from_stream(lump)
        while header != ModelHeader(-1, -1, 0, 0) and lump.tell() != len(raw_lump):
            start = lump.tell()
            solids = list()
            for i in range(header.solid_count):
                # CPhysCollisionEntry->WriteCollisionBinary
                cb_size = int.from_bytes(lump.read(4), "little")
                solids.append(Block.from_bytes(lump.read(cb_size)))
            assert lump.tell() - start == header.data_size
            script = lump.read(header.script_size)  # ascii
            assert len(script) == header.script_size
            collision_models.append(PhysicsObject(header, solids, script))
            # read next header (sets conditions for the while loop)
            header = ModelHeader.from_stream(lump)
        assert header == ModelHeader(-1, -1, 0, 0), "PhysicsCollide ended incorrectly"
        return cls(collision_models)


# PhysicsBlock headers
class ModelType(enum.Enum):
    SURFACE = 0
    MOPP = 1


class CollideHeader(core.Struct):
    """swapcollideheader_t"""
    __slots__ = ["id", "version", "model_type"]
    _format = "4s2h"
    _classes = {"model_type": ModelType}


class SurfaceHeader(core.Struct):
    """swapcompactsurfaceheader_t"""
    __slots__ = ["size", "drag_axis_areas", "axis_map_size"]
    _format = "i3fi"
    _arrays = {"drag_axis_areas": [*"xyz"]}
    _classes = {"drag_axis_areas": vector.vec3}


class MoppHeader(core.Struct):
    """swapmoppsurfaceheader_t"""
    # NOTE: the "swap" in the names refers to the format differing across byte-orders
    # -- Source swaps byte order for selected fields when compiled for consoles
    # -- PC is primarily little-endian, while the Xbox 360 has more big-endian fields
    __slots__ = ["size"]
    _format = "I"


BlockHeader = (CollideHeader, Union[SurfaceHeader, MoppHeader])


class Block:
    """Editting not yet supported"""
    # byte swapper: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/utils/common/bsplib.cpp#L1677
    header: BlockHeader
    data: bytes

    def __init__(self, header: BlockHeader = (CollideHeader(), SurfaceHeader()), data: bytes = b""):
        self.header = header
        self.data = data

    def as_bytes(self) -> bytes:
        header, surface_header = self.header
        assert header.model_type in (t.value for t in ModelType), "invalid model type"
        return b"".join([header.as_bytes(), surface_header.as_bytes(), self.data])

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Block:
        return cls.from_stream(io.BytesIO(raw_lump), len(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, lump_length: int) -> Block:
        start = stream.tell()
        header = CollideHeader.from_stream(stream)
        assert header.id == b"VPHY", "if 'YHPV' byte order is flipped"
        # version isn't checked by the byteswap, probably important for VPHYSICS
        if header.model_type == ModelType.SURFACE:
            surface_header = SurfaceHeader.from_stream(stream)
            # data_start = stream.tell()
            # NOTE: the tree reads are breaking
            # self.collision_model = CollisionModel.from_stream(stream)
            # lump.seek(data_start)
        elif header.model_type == ModelType.MOPP:
            surface_header = MoppHeader.from_stream(stream)
            # yeah, no idea what this does
        else:
            raise RuntimeError("Invalid model type")
        out = cls((header, surface_header), stream.read(surface_header.size))
        assert stream.tell() - start == lump_length, "Invalid data size"
        return out


# TODO: create a structure that makes navigating the tree optional
# -- ideally just get all the triangles and make a mesh
# -- however using the tree could be useful for reverse engineering
# TODO: find what isn't mapped by these interwoven structures
# -- a linear read might be possible

# NOTE: the order of class definition matters here, since each contains the previous
class Vertex(core.MappedArray):
    """struct Vertex { float x, y, z, w };"""
    _mapping = [*"xyzw"]
    _format = "4f"
    # appear to be 1/72 vs. expected size (roughly)


class ConvexTriangle(core.MappedArray):
    """struct ConvexTriange { int padding; short edges[3][2]; };"""
    padding: int  # is it really padding? check for non-zeroes
    edges: List[int]  # 3 pairs of indices
    _mapping = {"padding": None, "edges": {"AB": 2, "BC": 2, "CA": 2}}
    _format = "i6h"


class ConvexLeaf(core.MappedArray):
    """struct ConvexLeaf { int vertex_offset, padding[2]; short triangle_count, unused; };"""
    # preceded by b"IDST" (IDSTUDIOHEADER) ?
    # -- src/utils/motionmapper/motionmapper.h
    # -- src/utils/vbsp/staticprop.cpp
    vertex_offset: int  # need to calculate vertex count from triangles
    padding: List[int]  # might have non-zeros?
    triange_count: int  # number of ConvexTriangles in this ConvexLeaf
    unused: int
    _mapping = {"vertex_offset": None, "padding": 2, "triangle_count": None, "unused": None}
    _format = "3i2h"

    # NOTE: must load with .from_stream to get these
    triangles: List[ConvexTriangle]
    vertices: List[Vertex]

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> ConvexLeaf:
        base_offset = stream.tell()
        convex_leaf = super().from_stream(stream)
        convex_leaf.triangles = [ConvexTriangle.from_stream(stream) for i in range(convex_leaf.triangle_count)]
        # NOTE: uncertain if this is the best way to gather vertices
        stream.seek(base_offset + convex_leaf.vertex_offset)
        vertex_count = len({v for tri in convex_leaf.triangles for e in tri.edges for v in e})
        convex_leaf.vertices = [Vertex.from_stream(stream) for i in range(vertex_count)]
        stream.seek(base_offset + struct.calcsize(cls._format))
        return convex_leaf


class TreeNode(core.MappedArray):
    """struct TreeNode { int right_node_offset, convex_leaf_offset; float unknown[5]; };"""
    right_node_offset: int  # has no child nodes if 0
    convex_leaf_offset: int  # index to child ConvexLeaf
    unknown: List[float]
    _mapping = {"right_node_offset": None, "convex_leaf_offset": None, "unknown": 5}
    _format = "2i5f"

    # NOTE: must load with .from_stream(); may only have 1 or the other
    children: (TreeNode, TreeNode)
    leaf: ConvexLeaf

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> TreeNode:
        base_offset = stream.tell()
        tree_node = super().from_stream(stream)
        print(base_offset, tree_node)
        if tree_node.right_node_offset == 0:
            stream.seek(base_offset + tree_node.convex_leaf_offset)
            tree_node.leaf = ConvexLeaf.from_stream(stream)
        else:
            tree_node.children = list()
            tree_node.children.append(TreeNode.from_stream(stream))
            stream.seek(tree_node.right_node_offset)
            tree_node.children.append(TreeNode.from_stream(stream))
        stream.seek(base_offset + struct.calcsize(cls._format))
        return tree_node


class CollisionModel(core.Struct):
    """struct CollisionModel { float unknown[7]; int surface, tree_offset, padding[2]; };"""
    unknown: List[float]
    surface: int  # surface type? matches script?
    tree_offset: int  # index into "IVPS" to where the tree starts
    padding: List[int]  # doesn't look like padding, got some non-zeroes in there
    __slots__ = ["unknown", "surface", "tree_offset", "padding"]
    _format = "7f4i"
    _arrays = {"unknown": 7, "padding": 2}

    tree: TreeNode  # must use .from_stream to get the tree

    @classmethod
    def from_stream(cls, stream: io.BytesIO) -> CollisionModel:
        base_offset = stream.tell()
        collision_model = super().from_stream(stream)
        stream.seek(base_offset + collision_model.tree_offset)
        # NOTE: we can't stop a bad tree from reading past the end of the block
        collision_model.tree = TreeNode.from_stream(stream)
        stream.seek(base_offset + struct.calcsize(cls._format))
        return collision_model

    def as_bytes(self) -> bytes:
        # header = super(self, CollisionModel).as_bytes()
        # TODO: handle children
        # b"IVPS"
        # regenerate tree (indexes backwards, prefill?)
        # index tree -> leaves -> tris -> verts
        raise NotImplementedError()

    # TODO: a way to navigate the tree

    def as_obj(self) -> str:
        out = ["# generated from IVPS data with bsp_tool"]
        # TODO: navigate the tree and build each leaf
        # -- vertices and triangles, make each leaf an object? how to communicate lineage?
        raise NotImplementedError()
        return "\n".join(out)


class Displacement(list):
    # TODO: https://github.com/ValveSoftware/source-sdk-2013/blob/master/mp/src/public/builddisp.cpp
    _format = "H"

    def __init__(self, iterable: List[bytes] = tuple()):
        super().__init__(iterable)

    def as_bytes(self) -> bytes:
        out = [len(self)]
        out.extend([len(b) for b in self])
        out = [struct.pack(f"{len(out)}{self._format}", *out)]
        out.extend([b for b in self])
        return b"".join(out)

    @classmethod
    def from_bytes(cls, raw_lump: bytes) -> Displacement:
        return cls.from_stream(io.BytesIO(raw_lump), len(raw_lump))

    @classmethod
    def from_stream(cls, stream: io.BytesIO, lump_length: int) -> Displacement:
        start = stream.tell()
        num_blobs = binary.read_struct(stream, cls._format)
        blob_sizes = [
            binary.read_struct(stream, cls._format)
            for i in range(num_blobs)]
        blobs = [
            stream.read(size)
            for size in blob_sizes]
        assert stream.tell() - start == lump_length
        return cls(blobs)
