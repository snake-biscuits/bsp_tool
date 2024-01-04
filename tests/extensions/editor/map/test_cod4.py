from typing import List

from bsp_tool.extensions.editor.map import cod4

from .. import utils

import pytest


mapsrc = {
    "CoD4Radiant": {
        "Call of Duty 4": {
            "mp_lobby": [
                utils.EntSpec("worldspawn", 6),
                utils.EntSpec("light", origin="56.0 48.0 96.0"),
                utils.EntSpec("mp_dm_spawn", origin="0.0 0.0 0.0")],
            "mp_test": [utils.EntSpec("worldspawn", 12)],
            "test": [utils.EntSpec("worldspawn", 12)],
            "test_traverses": [utils.EntSpec("worldspawn", 23)]}}}
# ^ {"Editor": {"Game": {"map": [entity_spec]}}}
mapsrc = utils.flatten(mapsrc, ".map")


class TestMapFile:
    @pytest.mark.parametrize("path,ent_specs", mapsrc.values(), ids=mapsrc.keys())
    def test_parser(self, path: str, ent_specs: List[utils.EntSpec]):
        map_ = cod4.MapFile.from_file(path)
        for entity, spec in zip(map_.entities, ent_specs):
            if spec is Ellipsis:
                continue
            assert entity.classname == spec.classname
            assert len(entity.brushes) == spec.num_brushes
            for spec_key in spec:
                assert entity[spec_key] == spec[spec_key]
