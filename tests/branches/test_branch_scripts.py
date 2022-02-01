"""These tests cannot fail, but they will provide warnings for unused LumpClasses"""
# TODO: identify SubLumpClasses used in some way
import inspect
from types import ModuleType
from typing import List
import warnings

import pytest

from bsp_tool import branches


# TODO: check all attrs in type hints and _arrays appear in __slots__ / list(*_mapping)

def LumpClasses_of(module: ModuleType) -> List[object]:
    attrs = dir(module)
    for a in attrs:
        LumpClass = getattr(module, a)
        if inspect.isclass(LumpClass):
            if issubclass(LumpClass, (branches.base.Struct, branches.base.MappedArray)):
                yield LumpClass


# IdTech + IW + GoldSrc Engines (no lump versions)
basic_branch_scripts = [*branches.id_software.scripts,
                        *branches.infinity_ward.scripts,
                        branches.ion_storm.daikatana,
                        *branches.gearbox.scripts,
                        *branches.raven.scripts,
                        *branches.ritual.scripts,
                        branches.valve.goldsrc]


@pytest.mark.parametrize("branch_script", basic_branch_scripts)
def test_basic_branch_script(branch_script):
    used_LumpClasses = set(branch_script.LUMP_CLASSES.values())
    # ^ {"LUMP": LumpClass}
    # TODO: verify __slots__, _format, _arrays & _mapping line up correctly
    # -- this includes missing bytes (since single byte alignment gets wierd)
    # -- also type hints
    used_LumpClasses.add(branch_script.LumpHeader)
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    # TODO: trace what happens to imported LumpClasses
    # -- do they count as unused, because they are defined elsewhere?
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:",
                                  *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(UserWarning(warning_text))
    incorrect_lump_classes = dict()
    for lump_class in used_LumpClasses:
        try:
            lump_class()
        except Exception as exc:
            incorrect_lump_classes[lump_class.__name__] = exc
    assert incorrect_lump_classes == dict(), "some LumpClasses failed to __init__"
    # TODO: catch misnamed attrs


# Source + Titanfall Engines (lump versions)
branch_scripts = [*branches.arkane.scripts,
                  *branches.nexon.scripts,
                  *branches.respawn.scripts,
                  branches.troika.vampire,
                  *[s for s in branches.valve.scripts if (s is not branches.valve.goldsrc)]]


@pytest.mark.parametrize("branch_script", branch_scripts)
def test_branch_script(branch_script):
    """Versioned lump headers & Game Lumps"""
    used_LumpClasses = {branch_script.LumpHeader}
    for version_dict in branch_script.LUMP_CLASSES.values():
        # ^ {"LUMP": {version: LumpClass}}
        used_LumpClasses.update(version_dict.values())
    # TODO: find classes used by GameLumps / SpecialLumpClasses via the inspect module
    # -- would also be handy for automated documentation
    # NOTE: respawn.titanfall uses Grid's .from_bytes method as a SpecialLumpClass
    if hasattr(branch_script, "GAME_LUMP_HEADER"):
        used_LumpClasses.add(branch_script.GAME_LUMP_HEADER)
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    unused_LumpClasses = set(filter(lambda lc: not lc.__name__.startswith("StaticProp"), unused_LumpClasses))
    # HACK: need to actually check StaticProps are actually used, but not right now...
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:", *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(UserWarning(warning_text))
    incorrect_lump_classes = dict()
    for lump_class in used_LumpClasses:
        try:
            lump_class()
        except Exception as exc:
            incorrect_lump_classes[lump_class.__name__] = exc
    assert incorrect_lump_classes == dict(), "some LumpClasses failed to __init__"
    # TODO: warn if a lump version isn't supported
    # -- e.g. FACES v1 is supported, but not v2
    # NOTE: this should only matter if the lump version is found in a .bsp for the target branch (map installed_games)
    # TODO: SpecialLumpClasses; many use other classes too
    # need to somehow detect `GAME_LUMP_CLASSES = {"sprp": {4: lambda raw_lump: GameLump_SPRP(raw_lump, StaticPropv4)}}`
    # GameLumpClass = GAME_LUMP_CLASSES[game_lump][version]
    # if isinstance(GameLumpClass, types.FunctionType):
    #     lump_class = re.search(r"raw_lump, (.*)\)", inspect.getsource(GameLumpClass)).groups()[0]
    #     # NOTE: ^ lazy solution
    #     subclass = branch_script
    #     for attr in lump_class.split("."):
    #         subclass = getattr(subclass, attr)
    # TODO: catch misnamed/unused attrs/type hints


# TODO: use maplist to look at headers to ensure UNUSED_* lumps are correctly marked

# TODO: verify __slots__, _format, _arrays & _mapping line up correctly
# -- all LumpClasses must coherently translate to and from bytes
# -- no skipped bytes! (single byte alignment gets wierd)

# TODO: ensure base.Struct is not using _mapping
# -- also ensure base.MappedArray is not using __slots__ or _arrays
