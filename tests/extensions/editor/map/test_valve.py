from typing import List

from bsp_tool.extensions.editor.map import valve

from .. import utils

import pytest


mp_lobby_spec = [
    utils.EntSpec("worldspawn", 6, mapversion=220),
    utils.EntSpec("info_player_start", origin="0 0 8", angle=90),
    utils.EntSpec("light", origin="40 48 104")]

# TODO: load crossfire entity spec from a .json
# -- copied spawnpoints from the hl1 map w/ bsp_tool
# -- shouldn't be too hard to store them as .json

mapsrc = {
    "MRVN-Radiant": {
        "Titanfall 2": {"mp_crossfire": [utils.EntSpec("worldspawn", 458, mapversion=220)]}},
    "TrenchBroom": {
        "Quake": {"mp_lobby": mp_lobby_spec},
        "Quake 2": {"mp_lobby": mp_lobby_spec},
        "ReMakeQuake": {"mp_lobby": mp_lobby_spec}}}
# ^ {"Editor": {"Game": {"map": [entity_spec]}}}
mapsrc = utils.flatten(mapsrc, ".map")


class TestMapFile:
    @pytest.mark.parametrize("path,ent_specs", mapsrc.values(), ids=mapsrc.keys())
    def test_parser(self, path: str, ent_specs: List[utils.EntSpec]):
        map_ = valve.MapFile.from_file(path)
        for entity, spec in zip(map_.entities, ent_specs):
            if spec is Ellipsis:
                continue
            assert entity.classname == spec.classname
            assert len(entity.brushes) == spec.num_brushes
            for spec_key in spec:
                assert entity[spec_key] == spec[spec_key]
