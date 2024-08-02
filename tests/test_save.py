# import difflib
import fnmatch
import os
import re
import shutil
from types import ModuleType
from typing import List

# BspClasses
# from bsp_tool import D3DBsp
from bsp_tool import IdTechBsp
from bsp_tool import QuakeBsp
from bsp_tool import ReMakeQuakeBsp
from bsp_tool import RespawnBsp
from bsp_tool import ValveBsp
# branches
from bsp_tool.branches.id_software import quake
from bsp_tool.branches.id_software import quake2
from bsp_tool.branches.id_software import quake3
from bsp_tool.branches.id_software import remake_quake
# from bsp_tool.branches.infinity_ward import modern_warfare
from bsp_tool.branches.respawn import titanfall2
from bsp_tool.branches.strata import strata
from bsp_tool.branches.valve import orange_box
# extensions
import bsp_tool.extensions.diff.bsps as diff_bsps

import pytest


# utilities
def backup(map_path):
    folder, filename_ext = os.path.split(map_path)
    filename, ext = os.path.splitext(filename_ext)  # ext includes "."
    shutil.copy(map_path, os.path.join(folder, f"{filename}.bak{ext}"))
    # NOTE: RespawnBsp only
    pattern_bsp_lump = f"{filename}\\.bsp\\.00[0-7][0-9a-f]\\.bsp_lump"
    pattern_ent = f"{filename}\\_(env|fx|script|snd|spawn)\\.ent"
    pattern = re.compile("|".join([pattern_bsp_lump, pattern_ent]))
    for filename_ext in filter(pattern.fullmatch, os.listdir(folder)):
        filename_ext = os.path.join(folder, filename_ext)
        filename, ext = os.path.splitext(filename_ext)  # ext includes "."
        shutil.copy(filename_ext, f"{filename}.bak{ext}")


def restore(map_path):
    folder, filename_ext = os.path.split(map_path)
    filename, ext = os.path.splitext(filename_ext)  # ext includes "."
    shutil.move(os.path.join(folder, f"{filename}.bak{ext}"), map_path)
    # NOTE: RespawnBsp only
    pattern_bsp_lump = f"{filename}\\.bsp\\.00[0-7][0-9a-f]\\.bak\\.bsp_lump"
    pattern_ent = f"{filename}\\_(env|fx|script|snd|spawn)\\.bak\\.ent"
    pattern = re.compile("|".join([pattern_bsp_lump, pattern_ent]))
    for filename_bak_ext in filter(pattern.fullmatch, os.listdir(folder)):
        filename_bak_ext = os.path.join(folder, filename_bak_ext)
        filename_bak, ext = os.path.splitext(filename_bak_ext)  # ext includes "."
        filename, bak = os.path.splitext(filename_bak)  # bak includes "."
        shutil.move(filename_bak_ext, f"{filename}{ext}")


def map_dirs_to_test(*map_dirs: List[str], ext: str = "*.bsp"):
    """decorator for sourcing test maps"""
    map_paths, map_names = list(), list()
    for map_dir in map_dirs:
        maps = fnmatch.filter(os.listdir(os.path.join("tests/maps", map_dir)), ext)
        names = [os.path.join(map_dir, m) for m in maps]
        map_paths.extend([os.path.join("tests/maps", n) for n in names])
        map_names.extend([n.replace("\\", "/") for n in names])

    def decorator(test_function):
        """parametrize test for better logging & handle cleanup of files"""

        @pytest.mark.parametrize("map_path", map_paths, ids=map_names)
        def wrapped_test_function(map_path: str):
            """backup & restore original file"""
            backup(map_path)
            try:
                # NOTE: backup exists for the duration of the test
                test_function(map_path)
            finally:
                restore(map_path)

        return wrapped_test_function

    return decorator


def save_and_diff_backup(BspClass: object, branch_script: ModuleType, map_path: str) -> str:
    """quick & lazy test; more specific tests should also be performed"""
    bsp = BspClass.from_file(branch_script, map_path)
    bsp.save()
    filename_ext = os.path.join(bsp.folder, bsp.filename)
    del bsp  # close the file & free data
    # get filename of pre-save backup
    filename, ext = os.path.splitext(filename_ext)  # ext includes "."
    filename_bak_ext = f"{filename}.bak{ext}"
    old_bsp = BspClass.from_file(branch_script, filename_bak_ext)  # original file
    new_bsp = BspClass.from_file(branch_script, filename_ext)  # saved copy
    return diff_bsps.BspDiff(old_bsp, new_bsp)


# tests
# NOTE: we could generate a bunch of tests w/ more decorators or other magic
# -- but we'll probably have different margins for error
# -- e.g. generously checking diffs, notes in xfail
# TODO: use extensions.diff for a more lenient diff
# -- will need a non-text diff format, probably json/dicts
# -- this will require comparing the backup to the saved map
# NOTE: we don't test the "save_as" method, since "save" wraps it
# -- also means we don't have to worry about name collision
# -- ... tho BspClasses will probably fail to load the ".bak" extension...
@pytest.mark.xfail(raises=NotImplementedError, reason="not implemented yet")
@map_dirs_to_test("Call of Duty 4", "Call of Duty 4/mp", ext="*.d3dbsp")
def test_D3DBsp_modern_warfare(map_path: str):
    # TODO: diff.bsps.HeadersDiff isn't ready for modern_warfare
    # bsp_diff = save_and_diff_backup(D3DBsp, modern_warfare, map_path)
    raise NotImplementedError()
    ...


@pytest.mark.xfail(raises=NotImplementedError, reason="not implemented yet")
@map_dirs_to_test("Quake 2")
def test_IdTechBsp_quake2(map_path: str):
    # bsp_diff = save_and_diff_backup(IdTechBsp, quake2, map_path)
    raise NotImplementedError()
    ...


@pytest.mark.xfail(raises=NotImplementedError, reason="not implemented yet")
@map_dirs_to_test("Quake 3 Arena")
def test_IdTechBsp_quake3(map_path: str):
    # bsp_diff = save_and_diff_backup(IdTechBsp, quake3, map_path)
    raise NotImplementedError()
    ...


@pytest.mark.xfail(raises=NotImplementedError, reason="not implemented yet")
@map_dirs_to_test("ReMakeQuake")
def test_ReMakeQuakeBsp_remake_quake(map_path: str):
    # bsp_diff = save_and_diff_backup(ReMakeQuakeBsp, remake_quake, map_path)
    raise NotImplementedError()
    ...


@pytest.mark.xfail
@map_dirs_to_test("Titanfall 2")
def test_RespawnBsp_titanfall2(map_path: str):
    # bsp_diff = save_and_diff_backup(RespawnBsp, titanfall2, map_path)
    assert False
    ...
    # manually observed:
    # -- bsp_diff.old.ENTITIES env_fog_controller: colour values separated w/ "\xA0"
    # --- MRVN-Radiant/remap bug? mapsrc/*.map is clean
    # --- might also be a "plaintext" issue, iirc \xA0 get wierd when decoded / translated
    # -- bsp_diff.new.signature: +4 bytes of padding


@pytest.mark.xfail(raises=NotImplementedError, reason="not implemented yet")
@map_dirs_to_test("Quake")
def test_QuakeBsp_quake(map_path: str):
    # bsp_diff = save_and_diff_backup(QuakeBsp, quake, map_path)
    raise NotImplementedError()
    ...


@pytest.mark.xfail
@map_dirs_to_test("Team Fortress 2")
def test_ValveBsp_orange_box(map_path: str):
    # bsp_diff = save_and_diff_backup(ValveBsp, orange_box, map_path)
    assert False
    ...


@pytest.mark.xfail
@map_dirs_to_test("Momentum Mod")
def test_ValveBsp_strata(map_path: str):
    # bsp_diff = save_and_diff_backup(ValveBsp, strata, map_path)
    assert False
    ...
