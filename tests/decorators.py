import fnmatch
import os

import pytest

from . import maplist


# NOTE: decorated *args = [group_path, game_name, map_dirs]
def all_maps(game_dirs: maplist.GameDirList = maplist.installed_games):
    """pass the filename of every .bsp we can find to this test one at a time"""
    params = [(*gps, ms) for gps, ms in game_dirs.items()]
    # ^ maplist.GameDirList -> [("group_path", "game_dir", ["map_dir"])]

    def decorator(function):
        def wrapper(group_path, game_name, map_dirs):
            """test all .bsps in game, raise errors (if any occured) at the end"""
            errors = dict()
            for map_dir in map_dirs:
                full_path = os.path.join(group_path, game_name, map_dir)
                maps = fnmatch.filter(os.listdir(full_path), "*bsp")  # .bsp & CoD2 .d3dbsp
                assert len(maps) != 0, f"couldn't find any maps for {game_name} in {map_dir}"
                for bsp_filename in maps:
                    try:
                        assert function(bsp_filename)  # <<< DECORATED FUNCTION CALLED HERE
                    except AssertionError as exc:
                        errors[bsp_filename] = exc
            assert len(errors) == 0, f"failed on {', '.join(errors.keys())}"

        return pytest.mark.parametrize("group_path,game_name,map_dirs", params)(wrapper)

    return decorator
