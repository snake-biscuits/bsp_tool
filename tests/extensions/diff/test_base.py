from bsp_tool.extensions import diff

import pytest


old = ["a few lines",
       "i threw together",
       "for a quick test"]
new = ["A few lines I threw together",
       "for a quick test"]
sample = diff.base.Diff(old, new)


class TestDiff:
    def test_has_no_changes(self):
        assert diff.base.Diff([0, 1], [0, 1]).has_no_changes() is True
        assert diff.base.Diff([2, 3], [3, 4]).has_no_changes() is False

    def test_as_text_FAST(self):
        with pytest.raises(NotImplementedError):
            for line in sample.as_text(diff.base.LogMode.FAST):
                print(line)

    def test_as_text_VERBOSE(self):
        for i, line in enumerate(sample.as_text(diff.base.LogMode.VERBOSE)):
            assert line == sample.short_stats()
        assert i == 0, "more than one line emitted"

    def test_as_text_VERY_VERBOSE(self):
        diff_txt = sample.as_text(diff.base.LogMode.VERY_VERBOSE)
        for line, expected in zip(diff_txt, sample.unified_diff()):
            assert line == expected

    # TODO: test_short_stats
    # TODO: test_unified_diff
