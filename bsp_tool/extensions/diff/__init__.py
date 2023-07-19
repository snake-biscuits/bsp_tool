import difflib
from typing import Any, Dict, Generator, List

from . import base
from . import shared
from .valve import source

from bsp_tool import branches
from bsp_tool.base import Bsp
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


class BspDiff:
    """deferred diffs of lumps & headers etc."""
    old: Bsp
    new: Bsp

    def __init__(self, old: Bsp, new: Bsp):
        if old.branch != new.branch:
            raise NotImplementedError("Cannot diff bsps from different branches")
        self.old = old
        self.new = new
        self.headers = HeadersDiff(old.headers, new.headers)
        # NOTE: a change in header offsets does not imply a change in lump data
        # TODO: other metadata (file magic, version, revision, signature etc.)

    def __getattr__(self, lump_name: str) -> Any:
        old_lump = getattr(self.old, lump_name, None)
        new_lump = getattr(self.new, lump_name, None)
        no_old_lump = old_lump is None
        no_new_lump = new_lump is None
        if no_old_lump and no_new_lump:
            raise AttributeError(f"Neither bsp has {lump_name} lump to be diffed")
        elif no_old_lump or no_new_lump:
            return NoneDiff(old_lump, new_lump)
        else:
            diff = diff_lumps(old_lump, new_lump)
            setattr(self, lump_name, diff)  # cache
            return diff

    def save(self, base_filename: str, log_mode: base.LogMode = base.LogMode.VERBOSE):
        """generate & save .diff files"""
        # for each lump (match by name)
        # filename.lump.00.ENTITIES.diff: old_goldsrc.ENTITIES (0) -> new_blue_shift.ENTITIES (1)
        # filename.lump.01.PLANES.diff: old_goldsrc.PLANES (1) -> new_blue_shift.PLANES (0)
        # RespawnBsp
        # -- filename.ENTITITES.fx.diff: filename_fx.ent
        # -- filename.lump.00XX.LUMP_NAME.diff
        # -- filename.lump.00XX.LUMP_NAME.bsp_lump.diff
        # filename.bsp.diff: headers & Y/N lump matches
        raise NotImplementedError()


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


class HeadersDiff(base.Diff):
    # TODO: support comparisons between different branches
    # TODO: how do we communicate a change in branch order?
    # -- modern_warfare lump order & count is unique
    # -- will probably need it's own class
    old: Dict[str, Any]
    new: Dict[str, Any]
    _cache = Dict[str, List[str]]
    # NOTE: changes on offset can be knock on affect of changes to an earlier lump

    def __init__(self, old: Dict[str, Any], new: Dict[str, Any]):
        super().__init__(old, new)
        self._cache = dict()

    def __getitem__(self, lump_name: str) -> str:
        if lump_name not in {*self.old, *self.new}:
            raise KeyError(f"No {lump_name} header to diff")
        diff = self._cache.get(lump_name)
        if diff is None:
            old = f"{lump_name} {self.old[lump_name]!r}\n"
            new = f"{lump_name} {self.new[lump_name]!r}\n"
            diff = list(difflib.unified_diff([old], [new]))
            self._cache[lump_name] = diff
        return diff

    def short_stats(self) -> str:
        raise NotImplementedError()
        # TODO: how to summarise?

    def unified_diff(self) -> Generator[str, None, None]:
        for lump_name in self.old:
            for line in self[lump_name]:
                yield line
