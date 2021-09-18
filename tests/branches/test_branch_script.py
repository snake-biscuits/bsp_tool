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
        if issubclass(LumpClass, (base.Struct, base.MappedArray)):
            yield LumpClass


basic_branch_scripts = [id_software.quake, gearbox.bshift, valve.goldsrc]


@pytest.mark.parametrize("branch_script", basic_branch_scripts)
def test_quake_branch_script(branch_script):
    used_LumpClasses = set(branch_script.LUMP_CLASSES.values())
    # ^ {"LUMP": LumpClass}
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:", *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(warnings.UserWarning(warning_text))


branch_scripts = [arkane.dark_messiah, gearbox.bshift,
                  id_software.quake, id_software.quake, id_software.quake,
                  infinity_ward.call_of_duty1,
                  nexon.cso2, nexon.cso2_2018, nexon.vindictus,
                  respawn.titanfall, respawn.titanfall2, respawn.apex_legends]
# TODO: Ritual Entertainment - Übertools


@pytest.mark.parametrize("branch_script", branch_scripts)
def test_branch_script(branch_script):
    used_LumpClasses = set()
    for version_dict in branch_script.LUMP_CLASSES.values():
        # ^ {"LUMP": {version: LumpClass}}
        used_LumpClasses.update(version_dict.values())
    # ignore StaticPropClass
    used_LumpClasses = set(filter(lambda lc: not lc.__name__.startswith("StaticProp", used_LumpClasses)))
    unused_LumpClasses = set(LumpClasses_of(branch_script)).difference(used_LumpClasses)
    if len(unused_LumpClasses) > 0:
        warning_text = "\n".join(["Unused LumpClasses in branch script:", *[lc.__name__ for lc in unused_LumpClasses]])
        warnings.warn(warnings.UserWarning(warning_text))


# TODO: use maplist to look at all lump headers and ensure unused lumps are correctly marked
