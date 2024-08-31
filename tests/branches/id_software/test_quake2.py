import io
import math
import struct
from typing import List

from ... import files
from bsp_tool import IdTechBsp
from bsp_tool.branches.id_software import quake2
# Quake 2 Visibility test maps
# from bsp_tool.branches.ion_storm import daikataka
# from bsp_tool.branches.raven import soldier_of_fortune
# from bsp_tool.branches.ritual import sin
# Source Engine Visibility test maps
from bsp_tool import ValveBsp
# from bsp_tool.branches.ace_team import zeno_clash
# from bsp_tool.branches.arkane import dark_messiah_mp
# from bsp_tool.branches.arkane import dark_messiah_sp
from bsp_tool.branches.strata import strata
# from bsp_tool.branches.loiste import infra
# from bsp_tool.branches.nexon import cso2
# from bsp_tool.branches.nexon import cso2_2018
# from bsp_tool.branches.nexon import vindictus
# from bsp_tool.branches.nexon import vindictus69
# from bsp_tool.branches.outerlight import outerlight
# from bsp_tool.branches.troika import vampire
# from bsp_tool.branches.utoplanet import merubasu
# from bsp_tool.branches.valve import alien_swarm
# from bsp_tool.branches.valve import left4dead
# from bsp_tool.branches.valve import left4dead2
from bsp_tool.branches.valve import orange_box
# from bsp_tool.branches.valve import sdk_2013
# from bsp_tool.branches.valve import source
# from bsp_tool.branches.valve import source_filmmaker

import pytest


bsps = files.local_bsps(
    IdTechBsp, {
        quake2: [
            "Quake 2"]})

vis_bsps = files.local_bsps(
    ValveBsp, {
        orange_box: [
            "Team Fortress 2"],
        strata: [
            "Momentum Mod"]})

vis_bsps = {**bsps, **{
    m: b
    for m, b in vis_bsps.items()
    if hasattr(b, "VISIBILITY")}}

# TODO: verify:
# -- assumptions about the format (MAXS, derived lump lengths etc.)
# -- bounds of lump members indexing other lumps
# -- valid enum bounds
# -- enum.IntFlag has no unnamed flags & no unused flags appear


class TestVisibility:
    # TODO: endianness (not implemented yet)
    @pytest.mark.parametrize("bsp", vis_bsps.values(), ids=vis_bsps.keys())
    def test_parser(self, bsp: IdTechBsp):
        num_clusters = len({leaf.cluster for leaf in bsp.LEAVES if leaf.cluster != -1})
        assert len(bsp.VISIBILITY.pvs) == num_clusters
        assert len(bsp.VISIBILITY.pas) == num_clusters
        max_value = 2 ** num_clusters - 1  # all clusters visible (fast vis)
        for pvs in bsp.VISIBILITY.pvs:
            assert int.from_bytes(pvs, "little") <= max_value
        for pas in bsp.VISIBILITY.pas:
            assert int.from_bytes(pas, "little") <= max_value

    def test_run_length_encode(self):
        run_length_encode = quake2.Visibility.run_length_encode
        for i in range(0x01, 0xFF):
            assert run_length_encode(b"\x00" * i) == bytes([0, i])
            assert run_length_encode(bytes([i])) == bytes([i])
        assert run_length_encode(b"\x00" * 256) == b"\x00\xFF\x00\x01"

    def test_run_length_decode(self):
        run_length_decode = quake2.Visibility.run_length_decode

        def stream(*data: List[int]) -> io.BytesIO:
            return io.BytesIO(bytes(data))

        for i in range(0x01, 0xFF):
            assert run_length_decode(stream(0, i), i * 8) == b"\x00" * i
            assert run_length_decode(stream(i), 8) == bytes([i])
        # TODO: ensure illegal input is caught
        # -- num_clusters reaching out of bounds
        # -- b"\x00" is always paired with a count

    @pytest.mark.parametrize("bsp", vis_bsps.values(), ids=vis_bsps.keys())
    def test_as_bytes(self, bsp: IdTechBsp):
        raw_lump = bsp.VISIBILITY.as_bytes()
        num_clusters = int.from_bytes(raw_lump[:4], "little")
        assert num_clusters == len(bsp.VISIBILITY.pvs)
        offsets = struct.unpack(f"{num_clusters * 2}I", raw_lump[4:4 + num_clusters * 8])
        assert all([o < len(raw_lump) for o in offsets])
        # confirm data is tightly packed
        assert min(offsets) == 4 + len(offsets) * 4
        max_bytes = math.ceil(num_clusters)
        sorted_offsets = sorted(set(offsets))
        for start, end in zip(sorted_offsets, [*sorted_offsets[1:], len(raw_lump)]):
            compressed_set = raw_lump[start:end]
            assert len(compressed_set) >= 1
            assert len(compressed_set) <= max_bytes
            assert b"\x00\x00" not in bytearray(compressed_set)
            # TODO: verify decompressed_set
            # -- ensure trailing bits are zero


# @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
# def test_lighting(bsp: IdTechBsp):
#     # TODO: unmapped; like quake 1? quake 2 uses quake 1 faces...
#     ...
