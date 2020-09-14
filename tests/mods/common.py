import bsp_tool.mods.common
import unittest

class testcase_base(unittest.TestCase)
    def setUp(self):
        class example(base):
            __slots__ = ["id", "position", "data"]
            _format = "i3f4i"
            _arrays = {"position": [*"xyz"], "data": 4}

        self.e = example((0, .1, .2, .3, 4, 5, 6, 7))

class testcase_mapped_array(untittest.TestCase):
    ma_1 = mapped_array([0, 1, 2])
    ma_2 = mapped_array([3, 4, 5], ['a', 'b', 'c'])
    ma_3 = mapped_array([6, 7, 8, 9], {"D": ['i', 'ii'], "E": ['iii' ,' iv']})
