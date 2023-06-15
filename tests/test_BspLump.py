from . import utils

from bsp_tool import lumps
from bsp_tool import ValveBsp, IdTechBsp
from bsp_tool.branches.id_software import quake, quake3
from bsp_tool.branches.valve import orange_box

import pytest

# TODO: collect valid lumps of desired type for each test, rather than hardcoded lump names

bsps = {**utils.get_test_maps(ValveBsp, {orange_box: ["Team Fortress 2"]}),
        **utils.get_test_maps(IdTechBsp, {quake3: ["Quake 3 Arena"]})}


def raw_lump_of(bsp) -> lumps.RawBspLump:
    for header in bsp.headers.values():
        if header.length != 0:
            break
    else:
        raise RuntimeError(f"test .bsp {bsp.filename} has no lumps!")
    return lumps.create_RawBspLump(bsp.file, header)


class TestRawBspLump:
    raw_lumps = list(map(raw_lump_of, bsps.values()))

    @pytest.mark.parametrize("raw_lump", raw_lumps, ids=bsps.keys())
    def test_its_raw(self, raw_lump):
        assert isinstance(raw_lump, lumps.RawBspLump)

    @pytest.mark.parametrize("raw_lump", raw_lumps, ids=bsps.keys())
    def test_list_conversion(self, raw_lump):
        assert list(raw_lump) == [int(b) for b in raw_lump]

    @pytest.mark.parametrize("raw_lump", raw_lumps, ids=bsps.keys())
    def test_indexing(self, raw_lump):
        assert isinstance(raw_lump[0], int)
        assert isinstance(raw_lump[:1], bytearray)
        assert len(raw_lump[:1]) == 1
        assert len(raw_lump[-2:]) == 2
        with pytest.raises(TypeError):
            assert raw_lump["one"]


class TestBspLump:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_list_conversion(self, bsp):
        lump = bsp.VERTICES
        assert list(lump) == [b for b in lump]

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_indexing(self, bsp):
        lump = bsp.VERTICES
        LumpClass = quake.Vertex if bsp.branch != quake3 else quake3.Vertex
        assert isinstance(lump[0], LumpClass)
        assert isinstance(lump[:1], list)
        assert len(lump[:1]) == 1
        assert len(lump[-2:]) == 2
        with pytest.raises(TypeError):
            assert lump["one"]

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_del(self, bsp):
        lump = bsp.VERTICES
        initial_length = len(lump)
        # delete single index
        del lump[0]
        assert len(lump) == initial_length - 1
        # delete slice
        initial_length = len(lump)
        del lump[:2]
        assert len(lump) == initial_length - 2

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_setitem(self, bsp):
        lump = bsp.VERTICES
        empty_entry = lump.LumpClass()
        lump[0] = empty_entry
        assert lump[0] == empty_entry
        lump[:2] = [empty_entry, empty_entry]
        assert lump[:2] == [empty_entry, empty_entry]
        # TODO: allow for insert via slice & test for this
        # TODO: test changes to object attrs for Issue #23
        # -- e.g. bsp.LUMP[index].attr = val (uses soft copies)


class TestExternalBspLump:  # TODO: ship bespoke RespawnBsp .bsp_lump files with tests
    pass  # ensure data is being loaded from the .bsp_lump, not the .bsp


class TestBasicBspLump:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_its_basic(self, bsp):
        lump = bsp.LEAF_FACES
        assert isinstance(lump, lumps.BasicBspLump), type(lump)

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_list_conversion(self, bsp):
        lump = bsp.LEAF_FACES
        assert list(lump) == [b for b in lump]

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_indexing(self, bsp):
        for map_name in bsps:
            lump = bsp.LEAF_FACES
            LumpClass = bsp.branch.BASIC_LUMP_CLASSES["LEAF_FACES"]
            if isinstance(LumpClass, dict):  # ValveBsp branches use dicts for multiple lump versions
                LumpClass = LumpClass[bsp.headers["LEAF_FACES"].version]
            assert isinstance(lump[0], LumpClass)
            assert isinstance(lump[:1], list)
            assert len(lump[:1]) == 1
            assert len(lump[-2:]) == 2
            with pytest.raises(TypeError):
                assert lump["one"]
