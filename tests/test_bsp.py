from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, ValveBsp


def test_load_bsp():
    test2_bsp = load_bsp("tests/maps/test2.bsp")
    upward_bsp = load_bsp("tests/maps/pl_upward.bsp")
    bigbox_bsp = load_bsp("tests/maps/test_bigbox.bsp")
    assert isinstance(ValveBsp, test2_bsp)
    assert isinstance(ValveBsp, upward_bsp)
    assert isinstance(IdTechBsp, bigbox_bsp)


class TestValveBsp:
    def test_no_errors(self):
        test2_bsp = ValveBsp(filename="tests/maps/test2.bsp")
        upward_bsp = ValveBsp(filename="tests/maps/pl_upward.bsp")
        assert len(test2_bsp.loading_errors) == 0
        assert len(upward_bsp.loading_errors) == 0

    def test_entites_loaded(self):
        test2_bsp = ValveBsp(filename="tests/maps/test2.bsp")
        upward_bsp = ValveBsp(filename="tests/maps/pl_upward.bsp")
        assert test2_bsp.ENTITIES[0]["classname"] == "worldspawn"
        assert upward_bsp.ENTITIES[0]["classname"] == "worldspawn"
