import collections
import io
import struct


# PhysicsBlock headers
CollideHeader = collections.namedtuple("swapcollideheader_t", ["id", "version", "model_type"])
# struct swapcollideheader_t { int size, vphysicsID; short version, model_type; };
SurfaceHeader = collections.namedtuple("swapcompactsurfaceheader_t", ["size", "drag_axis_areas", "axis_map_size"])
# struct swapcompactsurfaceheader_t { int surfaceSize; Vector dragAxisAreas; int axisMapSize; };
MoppHeader = collections.namedtuple("swapmoppsurfaceheader_t", ["size"])
# struct swapmoppsurfaceheader_t { int moppSize; };
# NOTE: the "swap" in the names refers to the format differing across byte-orders
# -- Source swaps byte order for selected fields when compiled for consoles
# -- PC is primarily little-endian, while the Xbox 360 has more big-endian fields


class Block:  # TODO: actually process this data
    # byte swapper: https://github.com/ValveSoftware/source-sdk-2013/blob/master/sp/src/utils/common/bsplib.cpp#L1677
    def __init__(self, raw_lump: bytes):
        """Editting not yet supported"""
        self._raw = raw_lump
        lump = io.BytesIO(raw_lump)
        header = CollideHeader(*struct.unpack("4s2h", lump.read(8)))
        assert header.id == b"VPHY", "if 'YHPV' byte order is flipped"
        # version isn't checked by the byteswap, probably important for VPHYSICS
        if header.model_type == 0:
            size, *drag_axis_areas, axis_map_size = struct.unpack("i3fi", lump.read(20))
            surface_header = SurfaceHeader(size, drag_axis_areas, axis_map_size)
            # self.data = CollisionModel()

            # - CollisionModel
            #   - TreeNode (recursive) <- CollisionModel.tree_offset
            #   - TreeNode (left)  <- TreeNode<parent>._offset + sizeof(TreeNode)
            #   - TreeNode (right) <- TreeNode<parent>.right_node_offset
            #   if (TreeNode<parent>.right_node_offset == 0)
            #   - ConvexLeaf <- TreeNode<parent>.convex_offset
            #     - ConvexTriangle[ConvexLeaf.triangle_count]
            #     - Vertex[max(*ConvexTriangle<s>.edges[::])]

            # struct CollisionModel { float unknown[7]; int surface, tree_offset, padding[2]; };
            # struct TreeNode { int right_node_offset, convex_offset; float unknown[5]; };
            # struct ConvexLeaf { int vertex_offset, padding[2]; short triangle_count, unused; };
            # struct ConvexTriange { int padding; short edges[3][2]; };
            # struct Vertex { float x, y, z, w };
        elif header.model_type == 1:
            surface_header = MoppHeader(*struct.unpack("i", lump.read(4)))
            # yeah, no idea what this does
        else:
            raise RuntimeError("Invalid model type")
        self.header = (header, surface_header)
        self.data = lump.read(surface_header.size)
        assert lump.tell() == len(raw_lump)

    def as_bytes(self) -> bytes:
        header, surface_header = self.header
        if header.model_type == 0:  # SurfaceHeader (swapcompactsurfaceheader_t)
            size, drag_axis_areas, axis_map_size = surface_header
            surface_header = struct.pack("i3fi", len(self.data), *drag_axis_areas, axis_map_size)
        elif header.model_type == 1:  # MoppHeader (swapmoppsurfaceheader_t)
            surface_header = struct.pack("i", len(self.data))
        else:
            raise RuntimeError("Invalid model type")
        header = struct.pack("4s2h", *header)
        return b"".join([header, surface_header, self.data])


# PhysicsCollide headers
ModelHeader = collections.namedtuple("dphysmodel_t", ["model", "data_size", "script_size", "solid_count"])
# struct dphysmodel_t { int model_index, data_size, keydata_size, solid_count; };
PhysicsObject = collections.namedtuple("PhysicsObject", ["header", "solids", "script"])


class CollideLump(list):
    """[model_index: int, solids: List[bytes], script: bytes]"""
    # passed to VCollideLoad in vphysics.dll
    def __init__(self, raw_lump: bytes):
        collision_models = list()
        lump = io.BytesIO(raw_lump)
        header = ModelHeader(*struct.unpack("4i", lump.read(16)))
        while header != ModelHeader(-1, -1, 0, 0) and lump.tell() != len(raw_lump):
            start = lump.tell()
            solids = list()
            for i in range(header.solid_count):
                # CPhysCollisionEntry->WriteCollisionBinary
                cb_size = int.from_bytes(lump.read(4), "little")
                solids.append(Block(lump.read(cb_size)))
            assert lump.tell() - start == header.data_size
            script = lump.read(header.script_size)  # ascii
            assert len(script) == header.script_size
            collision_models.append(PhysicsObject(header, solids, script))
            # read next header (sets conditions for the while loop)
            header = ModelHeader(*struct.unpack("4i", lump.read(16)))
        assert header == ModelHeader(-1, -1, 0, 0), "PhysicsCollide ended incorrectly"
        super().__init__(collision_models)  # TODO: this is a terrible interface

    def as_bytes(self) -> bytes:
        def phy_bytes(collision_model):
            header, solids, script = collision_model
            phy_blocks = list()
            for phy_block in solids:
                collision_data = phy_block.as_bytes()
                phy_blocks.append(len(collision_data).to_bytes(4, "little"))
                phy_blocks.append(collision_data)
            phy_block_bytes = b"".join(phy_blocks)
            header = struct.pack("4i", header.model, len(phy_block_bytes), len(script), len(solids))
            return b"".join([header, phy_block_bytes, script])
        tail = struct.pack("4i", -1, -1, 0, 0)  # null header
        return b"".join([*map(phy_bytes, self), tail])
