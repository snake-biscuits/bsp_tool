import difflib
from typing import Any, Dict, List, Generator

from . import base
from . import lumps

from bsp_tool.base import Bsp


class BspDiff:
    """deferred diffs of lumps & headers etc."""
    # NOTE: not a base.Diff subclass
    old: Bsp
    new: Bsp

    def __init__(self, old: Bsp, new: Bsp):
        if old.branch != new.branch:
            raise NotImplementedError("Cannot diff bsps from different branches")
        self.old = old
        self.new = new
        self.headers = HeadersDiff(old.headers, new.headers)
        # TODO: other metadata (file magic, version, revision, signature etc.)

    def __getattr__(self, lump_name: str) -> Any:
        """retrieve differ for given lump"""
        old_lump = getattr(self.old, lump_name, None)
        new_lump = getattr(self.new, lump_name, None)
        no_old_lump = old_lump is None
        no_new_lump = new_lump is None
        if no_old_lump and no_new_lump:
            raise AttributeError(f"Neither bsp has {lump_name} lump to be diffed")
        elif no_old_lump or no_new_lump:
            return lumps.NoneDiff(old_lump, new_lump)
        else:
            diff = lumps.diff_lumps(old_lump, new_lump)
            setattr(self, lump_name, diff)  # cache
            return diff

    def has_no_changes(self) -> bool:
        try:
            assert self.headers.has_no_changes()
            # TODO: other metadata
            for lump in self.old.headers:
                old_header = self.old.headers[lump]
                new_header = self.new.headers[lump]
                if old_header.length != 0 or new_header.length != 0:
                    assert getattr(self, lump).has_no_changes()
        except AssertionError:
            return False
        return True

    def what_changed(self) -> List[str]:
        check = {"headers": self.headers.has_no_changes()}
        # TODO: other metadata
        for lump in self.old.headers:
            old_header = self.old.headers[lump]
            new_header = self.new.headers[lump]
            if old_header.length != 0 or new_header.length != 0:
                check[lump] = getattr(self, lump).has_no_changes()
        return {attr for attr, unchanged in check.items() if not unchanged}

    def save(self, base_filename: str, log_mode: base.LogMode = base.LogMode.VERBOSE):
        """generate & save .diff files"""
        raise NotImplementedError()
        # self.lump.unified_diff() -> individual files
        # -- .bsp      -> filename.00.ENTITIES.diff
        # RespawnBsp format:
        # -- .bsp      -> filename.00XX.LUMP_NAME.diff
        # -- .bsp_lump -> filename.external.00XX.LUMP_NAME.diff
        # -- .ent      -> filename.external.ent.xxxxx.diff
        # should also generate a general / meta diff for metadata etc.


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
            diff = list(difflib.unified_diff([old], [new]))[3:]
            self._cache[lump_name] = diff
        return diff

    # TODO: check headers in order
    # -- sorted({(h.offset, h.length, i) for i, h in enumerate(self.old.headers.values()) if h.length > 0})
    # -- find knock-on changes
    # -- trivial differences (e.g. offset=0, length=0)

    def short_stats(self) -> str:
        # TODO: how to summarise?
        # change in any attr but "offset"
        raise NotImplementedError()

    def unified_diff(self) -> Generator[str, None, None]:
        for lump_name in self.old:
            for line in self[lump_name]:
                yield line
