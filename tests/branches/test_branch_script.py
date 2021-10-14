import inspect
from types import ModuleType
from typing import List
import warnings

import pytest

from bsp_tool.branches import base
from bsp_tool.branches import arkane, gearbox, id_software, infinity_ward
from bsp_tool.branches import nexon, respawn, valve


def LumpClasses_of(module: ModuleType) -> List[object]:
    attrs = dir(module)
    for a in attrs:
        LumpClass = getattr(module, a)
        if inspect.isclass(LumpClass):
            if issubclass(LumpClass, (base.Struct, base.MappedArray)):
                yield LumpClass


# IdTech + IW + GoldSrc (no lump versions)
basic_branch_scripts = [id_software.quake, id_software.quake2, id_software.quake3,
                        infinity_ward.call_of_duty1, gearbox.bshift, valve.goldsrc]
# TODO: Ritual Entertainment - Übertools


@pytest.mark.parametrize("branch_script", basic_branch_scripts)
def test_quake_branch_script(branch_script):
    used_LumpClasses = set(branch_script.LUMP_CLASSES.values())
    # ^ {"LUMP": LumpClass}
    # TODO: verify __slots__, _format, _arrays & _mapping line up correctly
    # -- this includes missing bytes (since single byte alignment gets wierd)
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:", *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(UserWarning(warning_text))


# Source + Titanfall (lump versions)
branch_scripts = [arkane.dark_messiah,
                  nexon.cso2, nexon.cso2_2018, nexon.vindictus,
                  respawn.titanfall, respawn.titanfall2, respawn.apex_legends]


@pytest.mark.parametrize("branch_script", branch_scripts)
def test_branch_script(branch_script):
    used_LumpClasses = set()
    for version_dict in branch_script.LUMP_CLASSES.values():
        # ^ {"LUMP": {version: LumpClass}}
        used_LumpClasses.update(version_dict.values())
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    unused_LumpClasses = set(filter(lambda lc: not lc.__name__.startswith("StaticProp"), unused_LumpClasses))
    # HACK: need to actually check StaticProps are actually used, but not right now...
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:", *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(UserWarning(warning_text))


# TODO: use maplist to look at all lump headers and ensure unused lumps are correctly marked

# TODO: verify __slots__, _format, _arrays & _mapping line up correctly
# -- all LumpClasses must coherently translate to and from bytes
# -- no skipped bytes! (single byte alignment gets wierd)
