from bsp_tool import lumps
from bsp_tool import ValveBsp, IdTechBsp
from bsp_tool.branches.id_software import quake, quake3
from bsp_tool.branches.valve import orange_box
from bsp_tool.valve import decompress

import io
import pytest

from .. import files

bsps = {
    **files.local_bsps(ValveBsp, {orange_box: ["Team Fortress 2"]}),
    **files.local_bsps(IdTechBsp, {quake3: ["Quake 3 Arena"]})}


def raw_lump_of(bsp) -> lumps.RawBspLump:
    for header in bsp.headers.values():
        if header.length != 0:
            break
    else:
        raise RuntimeError(f"test .bsp {bsp.filename} has no lumps!")
    if getattr(header, "fourCC", 0) != 0:
        bsp.file.seek(header.offset)
        compressed_lump = bsp.file.read(header.length)
        stream = io.BytesIO(decompress(compressed_lump))
        offset, length = 0, header.fourCC
    else:
        stream = bsp.file
        offset, length = header.offset, header.length
    return lumps.RawBspLump.from_stream(stream, offset, length)


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


# TODO: collect valid lumps of desired type for each test
# -- rather than hardcoded lump names
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
            # NOTE: ValveBsp branches use dicts to allow multiple lump versions
            if isinstance(LumpClass, dict):
                LumpClass = LumpClass[bsp.headers["LEAF_FACES"].version]
            assert isinstance(lump[0], LumpClass)
            assert isinstance(lump[:1], list)
            assert len(lump[:1]) == 1
            assert len(lump[-2:]) == 2
            with pytest.raises(TypeError):
                assert lump["one"]
