import pytest

from bsp_tool import load_bsp, lumps
from bsp_tool.branches.id_software import quake, quake3

# TODO: use maplist.installed_games + tests/maps/*.bsp
global bsps
bsps = {"test2": load_bsp("tests/maps/test2.bsp"),
        "upward": load_bsp("tests/maps/pl_upward.bsp"),
        "bigbox": load_bsp("tests/maps/test_bigbox.bsp")}
# NOTE: only orange_box ValveBsp & quake3 IdTechBsp available to test


class TestRawBspLump:
    raw_lumps = [bsps["test2"].VISIBILITY,
                 bsps["upward"].VISIBILITY]

    def test_its_raw(self):
        for lump in self.raw_lumps:
            assert isinstance(lump, lumps.RawBspLump), f"it's not raw! it's {type(lump)}"

    def test_list_conversion(self):
        for map_name, lump in zip(bsps, self.raw_lumps):
            assert list(lump) == [int(b) for b in lump], f"{map_name}.VISIBILITY failed"

    def test_indexing(self):
        for map_name, lump in zip(bsps, self.raw_lumps):
            assert isinstance(lump[0], int), f"{map_name} failed"
            assert isinstance(lump[:1], bytes), f"{map_name} failed"
            assert len(lump[:1]) == 1, f"{map_name} failed"
            # ^ all three just look at the first byte
            # expecting behaviour the same as if lump was a bytestring
            assert len(lump[-2:]) == 2, f"{map_name} failed"
            with pytest.raises(TypeError):
                assert lump["one"], f"{map_name} failed"


class TestBspLump:
    def test_list_conversion(self):
        for map_name in bsps:
            lump = bsps[map_name].VERTICES
            assert list(lump) == [b for b in lump], f"{map_name}.VERTICES failed"

    def test_indexing(self):
        for map_name in bsps:
            lump = bsps[map_name].VERTICES
            LumpClass = quake.Vertex if map_name != "bigbox" else quake3.Vertex
            assert isinstance(lump[0], LumpClass), f"{map_name} failed"
            assert isinstance(lump[:1], list), f"{map_name} failed"
            assert len(lump[:1]) == 1, f"{map_name} failed"
            # ^ all three just look at the first byte
            # expecting behaviour the same as if lump was a bytestring
            assert len(lump[-2:]) == 2, f"{map_name} failed"
            # TODO: check negative indices line up
            # TODO: check slice cases (negative step, wide step, invalid slice)
            with pytest.raises(TypeError):
                assert lump["one"], f"{map_name} failed"

    def test_del(self):
        for map_name in bsps:
            lump = bsps[map_name].VERTICES
            initial_length = len(lump)
            del lump[0]
            assert len(lump) == initial_length - 1, f"{map_name} failed"
            initial_length = len(lump)
            del lump[:2]
            assert len(lump) == initial_length - 2, f"{map_name} failed"

    def test_setitem(self):
        for map_name in bsps:
            lump = bsps[map_name].VERTICES
            empty_entry = lump.LumpClass()  # NOTE: __init__ doesn't populate with dummy entries, breaking tests
            lump[0] = empty_entry
            assert lump[0] == empty_entry, f"{map_name} failed"
            lump[:2] = [empty_entry, empty_entry]
            assert lump[:2] == [empty_entry, empty_entry], f"{map_name} failed"
            # TODO: allow for insert via slice & test for this


class TestExternalBspLump:  # TODO: ship some ORIGINAL RespawnBsp external lumps in tests/maps
    pass  # ensure data is external, not internal


class TestBasicBspLump:
    def test_its_basic(self):
        for map_name in bsps:
            lump = bsps[map_name].LEAF_FACES
            assert isinstance(lump, lumps.BasicBspLump), f"it's not basic! it's {type(lump)}"

    def test_list_conversion(self):
        for map_name in bsps:
            lump = bsps[map_name].LEAF_FACES
            assert list(lump) == [b for b in lump], f"{map_name} vis lump does not match"

    def test_indexing(self):
        for map_name in bsps:
            lump = bsps[map_name].LEAF_FACES
            LumpClass = bsps[map_name].branch.BASIC_LUMP_CLASSES["LEAF_FACES"]
            if isinstance(LumpClass, dict):  # ValveBsp branches use dicts for multiple lump versions
                LumpClass = list(LumpClass.values())[0]
            assert isinstance(lump[0], LumpClass), f"{map_name} failed"
            assert isinstance(lump[:1], list), f"{map_name} failed"
            assert len(lump[:1]) == 1, f"{map_name} failed"
            # ^ all three just look at the first byte
            # expecting behaviour the same as if lump was a bytestring
            assert len(lump[-2:]) == 2, f"{map_name} failed"
            # TODO: check negative indices line up
            # TODO: check slice cases (negative step, wide step, invalid slice)
            with pytest.raises(TypeError):
                assert lump["one"], f"{map_name} failed"
