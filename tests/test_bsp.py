from bsp_tool.base import Bsp


class TestBspImport:
    def test_no_errors(self):
        test2_bsp = Bsp("tests/maps/test2.bsp")
        upward_bsp = Bsp("tests/maps/pl_upward.bsp")
        assert len(test2_bsp.log) == 0
        assert len(upward_bsp.log) == 0

    def test_entites_loaded(self):
        test2_bsp = Bsp("tests/maps/test2.bsp")
        upward_bsp = Bsp("tests/maps/pl_upward.bsp")
        assert test2_bsp.ENTITIES[0]["classname"] == "worldspawn"
        assert upward_bsp.ENTITIES[0]["classname"] == "worldspawn"
