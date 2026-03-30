from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import titanfall

import pytest

from ... import files


bsps = {
    **files.library_bsps(
        RespawnBsp, {
            titanfall: {
                "Mod": {
                    "Titanfall": [
                        # NOTE: skipping depots, they should be fine
                        "Titanfall/maps/"],
                    "Titanfall: Online": [
                        "TitanfallOnline/maps/"]}}})}


# TODO: test LumpClasses are valid
# TODO: test SpecialLumpClasses are valid


class TestConstants:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_first_portal_vertex_is_origin_point(self, bsp: RespawnBsp):
        assert bsp.PORTAL_VERTICES[0] == (0, 0, 0)


class TestLumpParallel:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert len(bsp.PORTAL_EDGE_INTERSECT_HEADER) * 2 == len(bsp.PORTAL_EDGES)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_intersect(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert len(bsp.PORTAL_EDGE_INTERSECT_AT_EDGE) == len(bsp.PORTAL_EDGE_INTERSECT_AT_VERTEX)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_references(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert len(bsp.PORTAL_EDGE_REFERENCES) == len(bsp.PORTAL_VERTEX_REFERENCES)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_vertices(self, bsp: RespawnBsp):
        assert len(bsp.PORTAL_VERTEX_EDGES) == len(bsp.PORTAL_VERTICES)


# verify lumps that index other lumps are in bounds
class TestLumpIndexing:
    # TODO: Brush -> BrushSide
    # TODO: Portal -> Cell (and PortalType.SKY indexes len(Cells) + 1)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_grid_indexes_grid_cells(self, bsp: RespawnBsp):
        assert bsp.CM_GRID.count.x * bsp.CM_GRID.count.y + len(bsp.MODELS) == len(bsp.CM_GRID_CELLS)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portals_index_references(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert max(p.first_reference + p.num_edges for p in bsp.PORTALS) == len(bsp.PORTAL_EDGE_REFERENCES)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_vertex_references_index_portal_vertices(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(bsp.PORTAL_VERTEX_REFERENCES) in (0, 1)
        assert max(bsp.PORTAL_VERTEX_REFERENCES) == len(bsp.PORTAL_VERTICES) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_edge_references_index_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(bsp.PORTAL_EDGE_REFERENCES) == 0
        assert max(bsp.PORTAL_EDGE_REFERENCES) >= len(bsp.PORTAL_EDGES) - 2

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_vertex_edges_index_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_VERTEX_EDGES for i in s.index if i != -1) == 0
        assert max(i for s in bsp.PORTAL_VERTEX_EDGES for i in s.index) == len(bsp.PORTAL_EDGE_INTERSECT_HEADER) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peiae_indexes_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_EDGE_INTERSECT_AT_EDGE for i in s.index if i != -1) == 0
        assert max(i for s in bsp.PORTAL_EDGE_INTERSECT_AT_EDGE for i in s.index) == len(bsp.PORTAL_EDGE_INTERSECT_HEADER) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peiav_indexes_portal_vertices(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_EDGE_INTERSECT_AT_VERTEX for i in s.index if i != -1) in (0, 1)
        assert max(i for s in bsp.PORTAL_EDGE_INTERSECT_AT_VERTEX for i in s.index) == len(bsp.PORTAL_VERTICES) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peih_indexes_portal_intersections(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert max(h.start + h.count for h in bsp.PORTAL_EDGE_INTERSECT_HEADER) == len(bsp.PORTAL_EDGE_INTERSECT_AT_EDGE)


# class TestLumpLogic:
# TODO:
# -- use PortalVertexRefs -> PortalVerts + PortalVertexEdges to find a loop
# -- test PortalVertex[1]'s edges reference both ways in PortalVertexEdges

# class TestMethods:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_method(self, bsp: RespawnBsp):
#         ...
