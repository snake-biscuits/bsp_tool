from typing import Any, List

from . import base
from . import shared
# TODO: name overlap w/ bsp_tool could be useful, but rn it sucks
# -- I'd like to lookup DiffClasses based on LumpClass __name__ & __module__
from .id_software import quake2
from .valve import source

from bsp_tool import branches
from bsp_tool.lumps import BasicBspLump, RawBspLump, ExternalRawBspLump


def diff_lumps(old_lump: Any, new_lump: Any) -> base.Diff:
    """lookup table & intialiser"""
    LumpClasses = set()
    for lump in (old_lump, new_lump):
        if issubclass(lump.__class__, BasicBspLump):
            LumpClasses.add(lump.LumpClass)
        else:  # SpecialLumpClass / RawBspLump
            LumpClasses.add(lump.__class__)
    # match LumpClasses to a base.Diff subclass
    # TODO: mismatched lump type diffs (substitute defaults for alternate versions?)
    # -- should only be used for extremely similar lumps
    if len(LumpClasses) > 1:
        # AbridgedDiff?
        raise NotImplementedError("Cannot diff lumps of differring LumpClass")
    if LumpClasses == {branches.shared.Entities}:
        DiffClass = shared.EntitiesDiff
    elif LumpClasses == {branches.id_software.quake2.Visibility}:
        DiffClass = quake2.VisibilityDiff
    elif LumpClasses == {branches.valve.source.PakFile}:
        DiffClass = source.PakFileDiff
    elif RawBspLump in LumpClasses or ExternalRawBspLump in LumpClasses:
        # TODO: core.xxd diff
        raise NotImplementedError("Cannot diff raw lumps")
    # if all([issubclass(lc, branches.base.BitField) for lc in LumpClasses]):
    #     DiffClass = base.BitFieldDiff
    # if all([issubclass(lc, branches.base.MappedArray) for lc in LumpClasses]):
    #     DiffClass = base.MappedArrayDiff
    # if all([issubclass(lc, branches.base.Struct) for lc in LumpClasses]):
    #     DiffClass = base.StructDiff
    else:  # default
        DiffClass = base.Diff
    return DiffClass(old_lump, new_lump)


class NoneDiff(base.Diff):
    """for diffing against None"""
    def short_stats(self) -> str:
        brand_new = self.old is None
        assert brand_new or self.new is None
        if brand_new:
            return f"{len(self.new)} insertions(+)"
        else:
            return f"{len(self.old)} deletions(-)"

    def unified_diff(self) -> List[str]:
        return [self.short_stats()]
