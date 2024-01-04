from typing import List

from bsp_tool.extensions.editor.map import quake

from .. import utils

import pytest


mapsrc = {
    "GtKRadiant": {
        "Quake 3 Arena": {
            "mp_lobby": [
                utils.EntSpec("worldspawn", 6),
                utils.EntSpec("light", origin="48 40 112", light=300),
                utils.EntSpec("info_player_deathmatch", origin="0 0 0", angle=90)]}}}
# ^ {"Editor": {"Game": {"map": [entity_spec]}}}
mapsrc = utils.flatten(mapsrc, ".map")


class TestMapFile:
    @pytest.mark.parametrize("path,ent_specs", mapsrc.values(), ids=mapsrc.keys())
    def test_parser(self, path: str, ent_specs: List[utils.EntSpec]):
        map_ = quake.MapFile.from_file(path)
        for entity, spec in zip(map_.entities, ent_specs):
            if spec is Ellipsis:
                continue
            assert entity.classname == spec.classname
            assert len(entity.brushes) == spec.num_brushes
            for spec_key in spec:
                assert entity[spec_key] == spec[spec_key]
