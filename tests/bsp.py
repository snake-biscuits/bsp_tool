import unittest

from bsp_tool import Bsp


class TestBspImport(unittest.TestCase):

    def setUp(self):
        self.test2_bsp = Bsp("tests/maps/test2.bsp")
        self.upward_bsp = Bsp("tests/maps/pl_upward.bsp")

    def test_no_errors(self):
        assert len(self.test2_bsp.log) == 0

    def test_entites_loaded(self):
        assert self.test2_bsp.ENTITIES[0]["classname"] == "worldspawn"
        assert self.upward_bsp.ENTITIES[0]["classname"] == "worldspawn"

    def tearDown(self):
        del self.test2_bsp
        del self.upward_bsp
