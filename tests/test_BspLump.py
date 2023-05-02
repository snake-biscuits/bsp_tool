import pytest

from bsp_tool import load_bsp, lumps
from bsp_tool.branches.id_software import quake, quake3

# TODO: collect valid lumps of desired type for each test, rather than hardcoded lump names

global bsps
bsps = {"q3_lobby": load_bsp("tests/maps/Quake 3 Arena/mp_lobby.bsp"),
        "tf2_test2": load_bsp("tests/maps/Team Fortress 2/test2.bsp"),
        "tf2_test_displacement_decompile": load_bsp("tests/maps/Team Fortress 2/test_displacement_decompile.bsp"),
        "tf2_test_physcollide": load_bsp("tests/maps/Team Fortress 2/test_physcollide.bsp")}


def raw_lump_of(bsp) -> lumps.RawBspLump:
    for header in bsp.headers.values():
        if header.length != 0:
            break
    else:
        raise RuntimeError(f"test .bsp {bsp.filename} has no lumps!")
    return lumps.create_RawBspLump(bsp.file, header)


class TestRawBspLump:
    raw_lumps = list(map(raw_lump_of, bsps.values()))

    def test_its_raw(self):
        for lump in self.raw_lumps:
            assert isinstance(lump, lumps.RawBspLump), f"it's not raw! it's {type(lump)}"

    def test_list_conversion(self):
        for map_name, lump in zip(bsps, self.raw_lumps):
            assert list(lump) == [int(b) for b in lump], f"{map_name} failed"

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
            LumpClass = quake.Vertex if map_name != "q3_lobby" else quake3.Vertex
            assert isinstance(lump[0], LumpClass), f"{map_name} failed"
            assert isinstance(lump[:1], list), f"{map_name} failed"
            assert len(lump[:1]) == 1, f"{map_name} failed"
            # ^ all three just look at the first byte
            # expecting behaviour the same as if lump was a bytestring
            assert len(lump[-2:]) == 2, f"{map_name} failed"
            # TODO: check negative indices line up [_remap_negative_index]
            # TODO: check slice cases (negative step, wide step, invalid slice) [_remap_slice]
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
            empty_entry = lump.LumpClass()
            lump[0] = empty_entry
            assert lump[0] == empty_entry, f"{map_name} failed"
            lump[:2] = [empty_entry, empty_entry]
            assert lump[:2] == [empty_entry, empty_entry], f"{map_name} failed"
            # TODO: allow for insert via slice & test for this
            # TODO: test changes to object attrs for Issue #23
            # -- e.g. bsp.LUMP[index].attr = val (uses soft copies)

    # TODO: test_iadd (__iadd__ method; overrides +=)


class TestExternalBspLump:  # TODO: ship bespoke RespawnBsp .bsp_lump files with tests
    pass  # ensure data is being loaded from the .bsp_lump, not the .bsp


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
