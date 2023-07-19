import difflib
import io
import os

from typing import Generator, Tuple

from .. import base
from .. import core


class PakFileDiff(base.Diff):
    """Works on any ValveBsp based .bsp (except CS:O2)"""

    def short_stats(self) -> str:
        """quick & dirty namelist check"""
        old = set(self.old.namelist())
        new = set(self.new.namelist())
        added = len(new.difference(old))
        removed = len(old.difference(new))
        return f"{added} insertions(+) {removed} deletions(-)"

    def unified_diff(self) -> Generator[str, None, None]:
        old_filelist = [f"{fn}\n" for fn in self.old.namelist()]
        new_filelist = [f"{fn}\n" for fn in self.new.namelist()]
        meta_diff = difflib.ndiff(old_filelist, new_filelist)
        for meta_line in meta_diff:
            if meta_line.startswith(" "):  # maybe a match
                filename = meta_line.lstrip(" ").rstrip("\n")
                old_file = self.old.read(filename)
                new_file = self.new.read(filename)
                if old_file == new_file:
                    yield meta_line
                else:
                    for line in self.diff_file(filename):
                        yield f"  {line}"
            else:
                yield meta_line

    def diff_file(self, filename: str) -> Generator[str, None, None]:
        old_file = self.old.read(filename)
        new_file = self.new.read(filename)
        _, ext = os.path.splitext(filename)
        # TODO: check MegaTest .bsps for other common plaintext file formats
        if ext in (".log", ".vmt", ".txt"):
            try:
                old = io.StringIO(old_file.decode()).readlines()
                new = io.StringIO(new_file.decode()).readlines()
            except UnicodeDecodeError:  # not pure utf-8
                old = list(core.xxd(old_file))
                new = list(core.xxd(new_file))
        else:  # binary diff
            old = list(core.xxd(old_file))
            new = list(core.xxd(new_file))
        old_time = self.formatted_date_time(self.old.getinfo(filename).date_time)
        new_time = self.formatted_date_time(self.new.getinfo(filename).date_time)
        for line in difflib.unified_diff(old, new, filename, filename, old_time, new_time):
            yield line

    @staticmethod
    def formatted_date_time(zipinfo_date_time: Tuple[int]) -> str:
        year, month, day, hour, minute, second = zipinfo_date_time
        return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
