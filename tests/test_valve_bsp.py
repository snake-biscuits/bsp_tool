from bsp_tool import ValveBsp
from bsp_tool.branches.valve import orange_box


# TODO: use maplist to test all Source & GoldSrc dirs (of those installed)
test2 = ValveBsp(orange_box, "tests/maps/Team Fortress 2/test2.bsp")
test_displacement_decompile = ValveBsp(orange_box, "tests/maps/Team Fortress 2/test_displacement_decompile.bsp")
test_physcollide = ValveBsp(orange_box, "tests/maps/Team Fortress 2/test_physcollide.bsp")


# NOTE: this is incredibly limited
def test_no_errors():
    assert len(test2.loading_errors) == 0
    assert len(test_displacement_decompile.loading_errors) == 0
    assert len(test_physcollide.loading_errors) == 0


def test_entites_loaded():
    assert test2.ENTITIES[0]["classname"] == "worldspawn"
    assert test_displacement_decompile.ENTITIES[0]["classname"] == "worldspawn"
    assert test_physcollide.ENTITIES[0]["classname"] == "worldspawn"


# def test_save_as():  # NotImplemented
#     with open("tests/maps/Team Fortress 2/test2.bsp", "rb") as file:
#         original = file.read()
#     test2.save_as("tests/maps/Team Fortress 2/test2_save_test.bsp")
#     with open("tests/maps/Team Fortress 2/test2_save_test.bsp", "rb") as file:
#         saved = file.read()
#     os.remove("tests/maps/Team Fortress 2/test2_save_test.bsp")
#     assert original == saved
