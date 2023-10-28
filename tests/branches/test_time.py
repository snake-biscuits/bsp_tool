import datetime

from bsp_tool.branches import time


# TODO: leapseconds


class TestSystemTime:
    def test_datetime(self):
        now = datetime.datetime.now()
        # TODO: use Unix Epoch rather than .now()
        # NOTE: in some contexts this can break unexpectedly
        st = time.SystemTime.from_datetime(now)
        # TODO: test day_of_week without assuming "en" Locale
        # assert now.strftime("%A") == st.day_of_week.name
        st_dt = st.as_datetime()
        assert st_dt.year == now.year
        assert st_dt.month == now.month
        assert st_dt.day == now.day
        assert st_dt.hour == now.hour
        assert st_dt.minute == now.minute
        assert st_dt.second == now.second
        assert st_dt.microsecond // 1000 == now.microsecond // 1000
