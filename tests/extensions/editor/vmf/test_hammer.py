from typing import List

from bsp_tool.extensions.editor.vmf import hammer

from .. import utils

import pytest


# TODO: displacements (shack, test2 & test_displacement_decompile)

mapsrc = {
    "Hammer": {
        "Half-Life 2": {
            "shack": [  # 200 brushes total
                utils.EntSpec("worldspawn", 112),
                utils.EntSpec("info_player_start", origin="0 0 -56", angles="0 0 0"),
                ...,  # will break once we catch hidden ents
                utils.EntSpec("func_detail", 88)]},
        "Momentum Mod": {
            "mp_lobby": [
                utils.EntSpec("worldspawn", 6)]},
        "Team Fortress 2": {
            "test2": [  # 80 brushes total
                utils.EntSpec("worldspawn", 70),
                *[...] * 13,  # we don't have to check everything
                utils.EntSpec("trigger_capture_area", 2),
                utils.EntSpec("func_detail", 8)],
            "test_displacement_decompile": [
                utils.EntSpec("worldspawn", 8)],
            "test_physcollide": [
                utils.EntSpec("worldspawn", 7)]}},
    "Hammer++": {
        "Team Fortress 2": {"mp_lobby": [utils.EntSpec("worldspawn", 6)]}}}
# ^ {"Editor": {"Game": {"map": [entity_spec]}}}
mapsrc = utils.flatten(mapsrc, ".vmf")


class TestMapFile:
    @pytest.mark.parametrize("path,ent_specs", mapsrc.values(), ids=mapsrc.keys())
    def test_parser(self, path: str, ent_specs: List[utils.EntSpec]):
        map_ = hammer.MapFile.from_file(path)
        for entity, spec in zip(map_.entities, ent_specs):
            if spec is Ellipsis:
                continue
            assert entity.classname == spec.classname
            assert len(entity.brushes) == spec.num_brushes
            for spec_key in spec:
                assert entity[spec_key] == spec[spec_key]
