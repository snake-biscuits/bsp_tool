from ... import utils
from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake2

import pytest


bsps = utils.get_test_maps(IdTechBsp, {quake2: ["Quake 2"]})


# TODO: test LumpClasses are valid
# TODO: verify assumptions about this branch_script
# TODO: verify lumps that index other lumps are in bounds


class TestVisibility:
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_parser(self, bsp: IdTechBsp):
        num_clusters = len({leaf.cluster for leaf in bsp.LEAVES if leaf.cluster != -1})
        assert len(bsp.VISIBILITY.pvs) == num_clusters
        assert len(bsp.VISIBILITY.pas) == num_clusters
        max_value = 2 ** num_clusters - 1  # all clusters visible (fast vis)
        for pvs in bsp.VISIBILITY.pvs:
            assert int.from_bytes(pvs, "little") <= max_value
        for pas in bsp.VISIBILITY.pas:
            assert int.from_bytes(pas, "little") <= max_value
        # is it little endian? what about bit endian?

    # TODO: test_run_length_encode
    # TODO: test_run_length_decode

    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_as_bytes(self, bsp: IdTechBsp):
        # content-aware diff
        double_parsed = quake2.Visibility.from_bytes(bsp.VISIBILITY.as_bytes())
        assert bsp.VISIBILITY.pvs == double_parsed.pvs
        assert bsp.VISIBILITY.pas == double_parsed.pas
        # byte-for-byte check
        header = bsp.headers["VISIBILITY"]
        bsp.file.seek(header.offset)
        raw_lump = bsp.file.read(header.length)
        assert bsp.VISIBILITY.as_bytes() == raw_lump, "not byte-for-byte"


# @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
# def test_lighting(bsp: IdTechBsp):
#     # TODO: unmapped; like quake 1? quake 2 uses quake 1 faces...
#     ...
