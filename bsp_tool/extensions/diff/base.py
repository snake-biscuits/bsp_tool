import difflib
import enum
from typing import Generator, Iterable, List


class LogMode(enum.Enum):
    FAST = 0  # no diff
    VERBOSE = 1  # small diff
    VERY_VERBOSE = 2  # maximum diff


class Diff:
    old: Iterable[object]
    new: Iterable[object]

    def __init__(self, old: Iterable[object], new: Iterable[object]):
        self.old = old
        self.new = new

    def has_no_changes(self) -> bool:
        return self.old == self.new

    def as_text(self, log_mode=LogMode.VERBOSE) -> Generator[str, None, None]:
        """formatted diff text, one line at a time"""
        if log_mode == LogMode.VERBOSE:
            yield self.short_stats()
        elif log_mode == LogMode.VERY_VERBOSE:  # GENERATES A LOT OF TEXT!
            for line in self.unified_diff():
                yield line
        else:  # only raised if try to pull data from the generator
            raise NotImplementedError(f"Unexpected Log Mode: {log_mode}")

    def short_stats(self) -> str:
        """mimick git diff --shortstat"""
        old = set(self.old)
        new = set(self.new)
        added = len(new.difference(old))
        removed = len(old.difference(new))
        return f"{added} insertions(+) {removed} deletions(-)"

    def unified_diff(self) -> List[str]:
        """quick & dirty diff of __repr__"""
        # NOTE: if the __repr__ is "<Classname @ 0xMEMORYADDRESS>" equality cannot be detemined
        old = [repr(x) for x in self.old]
        new = [repr(x) for x in self.new]
        # TODO: metadata
        # --- old.name
        # +++ new.name
        for line in difflib.unified_diff(old, new):
            yield line


# TODO: class BitFieldDiff(Diff):
# TODO: class MappedArrayDiff(Diff):
# TODO: class StructDiff(Diff):
