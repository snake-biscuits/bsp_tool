from bsp_tool import load_bsp
from bsp_tool import IdTechBsp, ValveBsp


global bsps
bsps = dict()


def test_load_bsp():  # must run first!
    bsps["test2"] = load_bsp("tests/maps/test2.bsp")
    bsps["upward"] = load_bsp("tests/maps/pl_upward.bsp")
    bsps["bigbox"] = load_bsp("tests/maps/test_bigbox.bsp")
    assert isinstance(bsps["test2"], ValveBsp)
    assert isinstance(bsps["upward"], ValveBsp)
    assert isinstance(bsps["bigbox"], IdTechBsp)


class TestIdTechBsp:
    def test_no_errors(self):
        assert len(bsps["bigbox"].loading_errors) == 0

    def test_entities_loaded(self):
        assert bsps["bigbox"].ENTITIES[0]["classname"] == "worldspawn"


class TestValveBsp:
    def test_no_errors(self):
        assert len(bsps["test2"].loading_errors) == 0
        assert len(bsps["upward"].loading_errors) == 0

    def test_entites_loaded(self):
        assert bsps["test2"].ENTITIES[0]["classname"] == "worldspawn"
        assert bsps["upward"].ENTITIES[0]["classname"] == "worldspawn"
