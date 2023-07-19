import itertools
import zipfile

from bsp_tool import branches
from bsp_tool.extensions import diff


class TestPakfileDiff:
    def setup_method(self, method):
        # TODO: parametrize PakFile baseclass (source.PakFile, cso2.PakFile)
        old = branches.valve.source.PakFile()
        old.writestr("same.txt", "same hat!\n")
        old.writestr(".secret", "!!! DO NOT SHIP !!!\n")
        old.writestr("mispelt", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 1, 0, 0, 0))
        old.writestr(compile_log, "REVISION: 01\n")
        new = branches.valve.source.PakFile()
        new.writestr("same.txt", "same hat!\n")
        new.writestr("mispelled", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 2, 0, 0, 0))
        new.writestr(compile_log, "REVISION: 02\n")
        # create a PakFile diff to interrogate in tests:
        self.sample = diff.valve.source.PakFileDiff(old, new)

    def test_short_stats(self):
        stats = self.sample.short_stats()
        assert stats == "1 insertions(+) 2 deletions(-)"

    def test_unified_diff(self):
        expected_lines = ["  same.txt\n",
                          "- .secret\n",
                          "- mispelt\n",
                          "?       ^\n",
                          "+ mispelled\n",
                          "?       ^^^\n",
                          *[f"  {line}" for line in self.sample.diff_file("compile.log")]]
        diff_lines = self.sample.unified_diff()
        for diff_line, expected_line in itertools.zip_longest(diff_lines, expected_lines):
            assert diff_line == expected_line
