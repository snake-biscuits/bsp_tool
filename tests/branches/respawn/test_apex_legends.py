from bsp_tool import RespawnBsp
from bsp_tool.branches.respawn import apex_legends

import pytest

from ... import files


# TODO: walk ApexLegends/season*/patch/maps/ tree procedurally
# -- must be split up to avoid namespace collision
# -- sorting by date would be nice
# TODO: somehow allow user to set a flag that limits pytest to a specific season and/or patch
# -- before & after flags would be awesome, but a pain to implement
# -- would also be cool if we could inherit tests from a generic `respawn.test_portals`
# -- but that could get messy with how we need to parametrise tests
bsps = {
    **files.library_bsps(
        RespawnBsp, {apex_legends: {"Mod": {
            # rBSP v47
            "Apex Legends | Season 0 (Preseason) 04-Feb-2019": [
                "ApexLegends/season0/4feb19/maps/"],

            "Apex Legends | Season 1 (Wild Frontier) 19-Mar-2019": [
                "ApexLegends/season1/19mar19/maps/"],
            "Apex Legends | Season 1 (Wild Frontier) 16-Apr-2019": [
                "ApexLegends/season1/16apr19/maps/"],
            "Apex Legends | Season 1 (Wild Frontier) 04-Jun-2019": [
                "ApexLegends/season1/4jun19/maps/"],

            "Apex Legends | Season 2 (Battle Charge) 02-Jul-2019": [
                "ApexLegends/season2/2jul19/maps/"],
            "Apex Legends | Season 2 (Battle Charge) 13-Aug-2019": [
                "ApexLegends/season2/13aug19/maps/"],
            "Apex Legends | Season 2 (Battle Charge) 03-Sep-2019": [
                "ApexLegends/season2/3sep19/maps/"],

            "Apex Legends | Season 3 (Meltdown) 01-Oct-2019": [
                "ApexLegends/season3/1oct19/maps/"],
            "Apex Legends | Season 3 (Meltdown) 05-Nov-2019": [
                "ApexLegends/season3/5nov19/maps/"],
            "Apex Legends | Season 3 (Meltdown) 03-Dec-2019": [
                "ApexLegends/season3/3dec19/maps/"],

            "Apex Legends | Season 4 (Assimilation) 04-Feb-2020": [
                "ApexLegends/season4/4feb20/maps/"],
            "Apex Legends | Season 4 (Assimilation) 03-Mar-2020": [
                "ApexLegends/season4/3mar20/maps/"],
            "Apex Legends | Season 4 (Assimilation) 07-Apr-2020": [
                "ApexLegends/season4/7apr20/maps/"],

            "Apex Legends | Season 5 (Fortune's Favour) 12-May-2020": [
                "ApexLegends/season5/12may20/maps/"],
            "Apex Legends | Season 5 (Fortune's Favour) 23-Jun-2020": [
                "ApexLegends/season5/23jun20/maps/"],

            "Apex Legends | Season 6 (Boosted) 12-Aug-2020": [
                "ApexLegends/season6/18aug20/maps/"],
            "Apex Legends | Season 6 (Boosted) 06-Oct-2020": [
                "ApexLegends/season6/6oct20/maps/"],

            # rBSP v48
            "Apex Legends | Season 7 (Ascension) 03-Nov-2020": [
                "ApexLegends/season7/3nov20/maps/"],
            "Apex Legends | Season 7 (Ascension) 05-Jan-2021": [
                "ApexLegends/season7/5jan21/maps/"],

            # rBSP v49
            "Apex Legends | Season 8 (Fight Night) 02-Feb-2021": [
                "ApexLegends/season8/2feb21/maps/"],
            "Apex Legends | Season 8 (Fight Night) 09-Mar-2021": [
                "ApexLegends/season8/9mar21/maps/"],

            "Apex Legends | Season 9 (Mayhem) 04-May-2021": [
                "ApexLegends/season9/4may21/maps/"],
            "Apex Legends | Season 9 (Mayhem) 29-Jun-2021": [
                "ApexLegends/season9/29jun21/maps/"],
        }}})}
# NOTE: skipping depot/; should line up with results for maps/
# TODO: Season10 maps are v49 until depot/r5-101 & 14sep21/maps (v49.1 iirc)
# TODO: Season21 maps are v51.1 for some maps and v52.1 for others (different branch scripts)
# TODO: do vXY.1 maps need to be handled differently? (external lumps only)


class TestConstant:
    """some things never change"""
    @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
    def test_sprp_version(self, bsp: RespawnBsp):
        bsp_version = bsp.version if isinstance(bsp.version, int) else bsp.version[0]
        assert bsp.GAME_LUMP.headers["sprp"].version == bsp_version


# class TestIndex:
#     """indices into lumps are in bounds"""
#     ...


# class TestLogic:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_behaviour(self, bsp: RespawnBsp):
#         ...  # if i do x with y, we get z


# class TestLumpClass:
#     ...


# class TestMethod:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_method(self, bsp: RespawnBsp):
#         ...


# class TestParallel:
#     @pytest.mark.parametrize("bsp", bsps.values(), ids=bsps.keys())
#     def test_lumpA_lumpB(self, bsp: RespawnBsp):
#         assert len(bsp.LUMP_A) == len(bsp.LUMP_B)


# class TestSpecialLumpClass:
#     ...
