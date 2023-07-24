import difflib
from typing import Generator, List

from .. import base


class VisibilityDiff(base.Diff):
    # ignoring changes to offsets
    # only care if num_clusters bits are valid

    def short_stats(self) -> str:
        # are there any repeated values in PVS & PAS tables for clusters?
        raise NotImplementedError()
        old = set(self.old)  # ...
        new = set(self.new)  # ...
        added = len(new.difference(old))
        removed = len(old.difference(new))
        return f"{added} insertions(+) {removed} deletions(-)"

    def unified_diff(self) -> Generator[str, None, None]:
        # determine num_clusters and mask off excess bits
        old_num_clusters = len(self.old.pvs)
        new_num_clusters = len(self.new.pvs)
        # NOTE: big changes can mean trouble
        # mask trailing bits (0xFFDC == 0xFFFF if mask == 0xDC)
        old_mask = 1 << (old_num_clusters % 8) - 1 if old_num_clusters % 8 != 0 else 0xFF
        new_mask = 1 << (new_num_clusters % 8) - 1 if new_num_clusters % 8 != 0 else 0xFF

        def line_fmt(*data: List[int]) -> str:
            # TODO: get right side 0-padding length from num_clusters
            return f"{bytearray(data).hex().upper():<016}\n"

        # diff PVS
        old_pvs = [line_fmt(*x[:-1], x[-1] & old_mask) for x in self.old.pvs]
        new_pvs = [line_fmt(*x[:-1], x[-1] & new_mask) for x in self.new.pvs]
        for line in difflib.unified_diff(old_pvs, new_pvs, "old.pvs", "new.pvs"):
            yield line
        # diff PAS
        old_pas = [line_fmt(*x[:-1], x[-1] & old_mask) for x in self.old.pas]
        new_pas = [line_fmt(*x[:-1], x[-1] & new_mask) for x in self.new.pas]
        for line in difflib.unified_diff(old_pas, new_pas, "old.pas", "new.pas"):
            yield line
