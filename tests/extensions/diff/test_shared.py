import itertools
import zipfile

from bsp_tool.extensions import diff
from bsp_tool.branches.shared import PakFile


class TestEntitiesDiff:
    def setup_method(self, method):
        old = [dict(classname="worldspawn"),
               dict(classname="light", origin="0 0 0")]
        new = [dict(classname="worldspawn"),
               dict(classname="info_player_start", origin="0 0 0"),
               dict(classname="light", origin="0 0 64")]
        self.sample = diff.shared.EntitiesDiff(old, new)

    def test_short_stats(self):
        stats = self.sample.short_stats()
        assert stats == "2 insertions(+) 1 deletions(-)"

    def test_unified_diff(self):
        # TODO: test a multiline repr diff
        expected_lines = ["- <light @ 0 0 0>\n",
                          "+ <info_player_start @ 0 0 0>\n",
                          "+ <light @ 0 0 64>\n"]
        diff_lines = self.sample.unified_diff()
        for diff_line, expected_line in itertools.zip_longest(diff_lines, expected_lines):
            assert diff_line == expected_line


class TestPakfileDiff:
    def setup_method(self, method):
        old = PakFile()
        old.writestr("same.txt", "same hat!\n")
        old.writestr(".secret", "!!! DO NOT SHIP !!!\n")
        old.writestr("mispelt", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 1, 0, 0, 0))
        old.writestr(compile_log, "REVISION: 01\n")
        new = PakFile()
        new.writestr("same.txt", "same hat!\n")
        new.writestr("mispelled", "oops, typo\n")
        compile_log = zipfile.ZipInfo(filename="compile.log", date_time=(1980, 1, 2, 0, 0, 0))
        new.writestr(compile_log, "REVISION: 02\n")
        self.sample = diff.shared.PakFileDiff(old, new)

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
