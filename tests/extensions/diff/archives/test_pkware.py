import itertools
import zipfile

from bsp_tool import archives
from bsp_tool.extensions import diff


class TestZipDiff:
    def setup_method(self, method):
        old = archives.pkware.Zip()
        old.writestr("same.txt", "same hat!\n")
        old.writestr(".secret", "!!! DO NOT SHIP !!!\n")
        old.writestr("mispelt", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 1, 0, 0, 0))
        old.writestr(compile_log, "REVISION: 01\n")
        new = archives.pkware.Zip()
        new.writestr("same.txt", "same hat!\n")
        new.writestr("mispelled", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 2, 0, 0, 0))
        new.writestr(compile_log, "REVISION: 02\n")
        # create a ZipDiff to interrogate in tests:
        self.sample = diff.archives.pkware.ZipDiff(old, new)

    def test_short_stats(self):
        stats = self.sample.short_stats()
        assert stats == "1 insertions(+) 2 deletions(-)"

    def test_unified_diff(self):
        expected_lines = [
            "  same.txt\n",
            "- .secret\n",
            "- mispelt\n",
            "?       ^\n",
            "+ mispelled\n",
            "?       ^^^\n",
            *[f"  {line}" for line in self.sample.diff_file("compile.log")]]
        diff_lines = self.sample.unified_diff()
        for diff_line, expected_line in itertools.zip_longest(diff_lines, expected_lines):
            assert diff_line == expected_line
