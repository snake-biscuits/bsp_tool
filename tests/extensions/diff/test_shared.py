import itertools

from bsp_tool.extensions import diff


old = [dict(classname="worldspawn"),
       dict(classname="light", origin="0 0 0")]
new = [dict(classname="worldspawn"),
       dict(classname="info_player_start", origin="0 0 0"),
       dict(classname="light", origin="0 0 64")]
sample = diff.shared.EntitiesDiff(old, new)


class TestEntitiesDiff:
    def test_short_stats(self):
        stats = sample.short_stats()
        assert stats == "2 insertions(+) 1 deletions(-)"

    def test_unified_diff(self):
        # TODO: test a multiline diff
        expected = ["- <light @ 0 0 0>\n",
                    "+ <info_player_start @ 0 0 0>\n",
                    "+ <light @ 0 0 64>\n"]
        for line, expected_line in itertools.zip_longest(sample.unified_diff(), expected):
            assert line == expected_line


class TestPakfileDiff:
    # TODO: generate dummy pakfiles for comparison
    ...
