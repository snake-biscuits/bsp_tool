from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import (
    titanfall, titanfall2, apex_legends)

import pytest

from ... import files


# TODO: walk ApexLegends/season*/patch/maps/ tree procedurally
# -- must be split up to avoid namespace collision
# -- sorting by date would be nice
# TODO: somehow add pytest flags to limit which bsps are loaded
# NOTE: pytest can't load all these maps at once (OSError: too many open files)
# -- need to manage file streams, sounds like a job for breki
bsps = {
    **files.local_bsps(RespawnBsp, {titanfall2: ["Titanfall 2"]}),
    # NOTE: mp_crossfire only has basic Portal stubs
    **files.library_bsps(
        RespawnBsp, {
            titanfall: {"Mod": {
                "Titanfall": ["Titanfall/maps/"],
                "Titanfall: Online": ["TitanfallOnline/maps/"]}},
            titanfall2: {"Mod": {"Titanfall 2": ["Titanfall2/maps/"]}},
            apex_legends: {"Mod": {
                # rBSP v47
                "Apex Legends | Season 0 (Preseason) 04-Feb-2019": [
                    "ApexLegends/season0/4feb19/maps/"],

                "Apex Legends | Season 1 (Wild Frontier) 19-Mar-2019": [
                    "ApexLegends/season1/19mar19/maps/"],
                "Apex Legends | Season 1 (Wild Frontier) 16-Apr-2019": [
                    "ApexLegends/season1/16apr19/maps/"],
                "Apex Legends | Season 1 (Wild Frontier) 04-Jun-2019": [
                    "ApexLegends/season1/4jun19/maps/"],

                "Apex Legends | Season 2 (Battle Charge) 02-Jul-2019": [
                    "ApexLegends/season2/2jul19/maps/"],
                "Apex Legends | Season 2 (Battle Charge) 13-Aug-2019": [
                    "ApexLegends/season2/13aug19/maps/"],
                "Apex Legends | Season 2 (Battle Charge) 03-Sep-2019": [
                    "ApexLegends/season2/3sep19/maps/"],

                "Apex Legends | Season 3 (Meltdown) 01-Oct-2019": [
                    "ApexLegends/season3/1oct19/maps/"],
                "Apex Legends | Season 3 (Meltdown) 05-Nov-2019": [
                    "ApexLegends/season3/5nov19/maps/"],
                "Apex Legends | Season 3 (Meltdown) 03-Dec-2019": [
                    "ApexLegends/season3/3dec19/maps/"],

                "Apex Legends | Season 4 (Assimilation) 04-Feb-2020": [
                    "ApexLegends/season4/4feb20/maps/"],
                "Apex Legends | Season 4 (Assimilation) 03-Mar-2020": [
                    "ApexLegends/season4/3mar20/maps/"],
                "Apex Legends | Season 4 (Assimilation) 07-Apr-2020": [
                    "ApexLegends/season4/7apr20/maps/"],

                "Apex Legends | Season 5 (Fortune's Favour) 12-May-2020": [
                    "ApexLegends/season5/12may20/maps/"],
                "Apex Legends | Season 5 (Fortune's Favour) 23-Jun-2020": [
                    "ApexLegends/season5/23jun20/maps/"],

                "Apex Legends | Season 6 (Boosted) 12-Aug-2020": [
                    "ApexLegends/season6/18aug20/maps/"],
                "Apex Legends | Season 6 (Boosted) 06-Oct-2020": [
                    "ApexLegends/season6/6oct20/maps/"],

                # rBSP v48
                "Apex Legends | Season 7 (Ascension) 03-Nov-2020": [
                    "ApexLegends/season7/3nov20/maps/"],
                "Apex Legends | Season 7 (Ascension) 05-Jan-2021": [
                    "ApexLegends/season7/5jan21/maps/"],

                # rBSP v49
                "Apex Legends | Season 8 (Fight Night) 02-Feb-2021": [
                    "ApexLegends/season8/2feb21/maps/"],
                "Apex Legends | Season 8 (Fight Night) 09-Mar-2021": [
                    "ApexLegends/season8/9mar21/maps/"],

                "Apex Legends | Season 9 (Mayhem) 04-May-2021": [
                    "ApexLegends/season9/4may21/maps/"],
                "Apex Legends | Season 9 (Mayhem) 29-Jun-2021": [
                    "ApexLegends/season9/29jun21/maps/"],
            }}})}
# NOTE: skipping depot/; should line up with results for maps/
# TODO: APEX: Season10 maps are v49 until depot/r5-101 & 14sep21/maps (v49.1 iirc)
# TODO: APEX: Season21 maps are v51.1 for some maps and v52.1 for others (different branch scripts)
# TODO: APEX: do vXY.1 maps need to be handled differently? (external lumps only)


class TestConstants:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_first_portal_vertex_is_origin_point(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTAL_VERTICES"):
            pytest.skip("MRVN-Radiant bsp has no PortalVertices stub")
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
        assert len(bsp.PORTAL_EDGE_INTERSECT_EDGE) == len(bsp.PORTAL_EDGE_INTERSECT_VERTEX)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_references(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert len(bsp.PORTAL_EDGE_REFERENCES) == len(bsp.PORTAL_VERTEX_REFERENCES)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_vertices(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTAL_VERTICES"):
            pytest.skip("MRVN-Radiant bsp has no PortalVertexEdges stub")
        assert len(bsp.PORTAL_VERTEX_EDGES) == len(bsp.PORTAL_VERTICES)


class TestLumpIndexing:
    """verify lumps that index other lumps are in bounds"""

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portals_index_references(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert max(p.first_ref + p.num_refs for p in bsp.PORTALS) == len(bsp.PORTAL_EDGE_REFERENCES)

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
        # NOTE: -2 because the last edge will be indexed, but it could be either end of the edge
        # EXPLICIT: every edge is indexed at one or more ends of each edge
        # -- assert len({i // 2 for i in bsp.PORTAL_EDGE_REFERENCES}) == len(bsp.PORTAL_EDGES) // 2

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_portal_vertex_edges_index_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_VERTEX_EDGES for i in s.indices if i != -1) == 0
        assert max(i for s in bsp.PORTAL_VERTEX_EDGES for i in s.indices) == len(bsp.PORTAL_EDGE_INTERSECT_HEADER) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peie_indexes_portal_edges(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_EDGE_INTERSECT_EDGE for i in s.indices if i != -1) == 0
        assert max(i for s in bsp.PORTAL_EDGE_INTERSECT_EDGE for i in s.indices) == len(bsp.PORTAL_EDGE_INTERSECT_HEADER) - 1

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peiv_indexes_portal_vertices(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert min(i for s in bsp.PORTAL_EDGE_INTERSECT_VERTEX for i in s.indices if i != -1) in (0, 1)
        assert max(i for s in bsp.PORTAL_EDGE_INTERSECT_VERTEX for i in s.indices) <= len(bsp.PORTAL_VERTICES) - 1
        # NOTE: <= because not every PortalVertex is indexed (most pronounced in apex maps)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_peih_indexes_portal_intersections(self, bsp: RespawnBsp):
        if not hasattr(bsp, "PORTALS"):
            pytest.skip("bsp has no portals")
        assert max(h.first_set + h.num_sets for h in bsp.PORTAL_EDGE_INTERSECT_HEADER) == len(bsp.PORTAL_EDGE_INTERSECT_EDGE)


# TODO: class TestLumpLogic:
# -- use PortalVertexRefs -> PortalVerts + PortalVertexEdges to find a loop
# -- test PortalVertex[1]'s edges reference both ways in PortalVertexEdges
# -- test PEIE & PEIV pairs identify vertices on both edges
# -- test PVE can be transformed into PEIE & PEIV
