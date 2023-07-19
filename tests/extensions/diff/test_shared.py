import itertools

from bsp_tool.extensions import diff


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
