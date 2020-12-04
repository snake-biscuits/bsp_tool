from bsp_tool import Bsp


class TestBspImport:
    def set_up(self):
        self.test2_bsp = Bsp("tests/maps/test2.bsp")
        self.upward_bsp = Bsp("tests/maps/pl_upward.bsp")

    def test_no_errors(self):
        self.set_up()
        assert len(self.test2_bsp.log) == 0
        assert len(self.upward_bsp.log) == 0

    def test_entites_loaded(self):
        self.set_up()
        assert self.test2_bsp.ENTITIES[0]["classname"] == "worldspawn"
        assert self.upward_bsp.ENTITIES[0]["classname"] == "worldspawn"
