import os
from typing import Any, Dict, List, Tuple


class EntSpec:
    """Container for a rough description to test an ent against"""
    # NOTE: we don't do the test here, need pytest to catch asserts

    def __init__(self, classname: str, num_brushes: int = 0, **key_values: Dict[str, Any]):
        self.classname = classname
        self.num_brushes = num_brushes
        self.key_values = {k: str(v) for k, v in key_values.items()}
        # NOTE: vec3 keys are a pain to compare; use the exact string

    def __getitem__(self, key: str):
        return self.key_values[key]

    def __iter__(self):
        return iter(self.key_values)

    def __repr__(self) -> str:
        key_values = ", ".join([f"{k}={v!r}" for k, v in self.key_values.items()])
        return f"EntSpec({self.classname!r}, {self.num_brushes}, {key_values})"


MapSrc = Dict[str, Dict[str, Dict[str, List[EntSpec]]]]
# ^ {"Editor": {"Game": {"map": [entity_spec]}}}
FlatMapSrc = Dict[str, Tuple[str, List[EntSpec]]]
# ^ {"test name": ("map_path", [entity_spec])}


def flatten(mapsrc: MapSrc, extension: str) -> FlatMapSrc:
    """take a MapSrc dict and prepare it for pytest.mark.parametrize"""
    assert extension.startswith("."), "extension should start with '.'; e.g. '.map'"
    out = dict()
    mapsrc_dir = "tests/mapsrc"
    for editor, games in mapsrc.items():
        for game, maps in games.items():
            for map_, ent_specs in maps.items():
                map_path = os.path.join(mapsrc_dir, editor, game, f"{map_}{extension}")
                out[f"{editor} | {game} | {map_}"] = (map_path, ent_specs)
    return out
