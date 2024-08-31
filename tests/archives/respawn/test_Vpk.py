import pytest

from bsp_tool.archives import respawn

from ... import files


vpk_dirs: files.LibraryGames
vpk_dirs = {
    "Steam": {
        "Titanfall": ["Titanfall/vpk/"],
        "Titanfall 2": ["Titanfall2/vpk/"]},
    "Mod": {
        "Titanfall (beta)": ["Titanfall/beta/vpk/"]}}

apex_season_patches = [
    ["4feb19"],
    ["19mar19", "16apr19", "4jun19"],
    ["2jul19", "13aug19", "3sep19"],
    ["1oct19"],  # TODO: get season3 5nov19 & 3dec19 vpk/ folders from rexx
    ["4feb20", "3mar20", "7apr20"],
    ["12may20", "23jun20"],
    ["18aug20", "6oct20"],
    ["3nov20", "5jan21"],
    ["2feb21", "9mar21"],
    ["4may21", "29jun21"]]
# TODO: download season10 -> season17 vpk/ folders with steamcmd
# -- ["3aug21", "10aug21", "14sep21", "24sep21"],
# -- ["2nov21", "5nov21", "17nov21"],
# -- ["8feb22", "29mar22"],
# -- ["10may22", "21jun22"],
# -- ["9aug22", "20sep22", "14oct22"],
# -- ["1nov22", "10jan23"],
# -- ["14feb23", "28mar23"],
# -- ["9may23", "19jun23", "20jul23"]]
# NOTE: season18 onwards ships with no `.vpk`s

vpk_dirs["Mod"].update({
    f"Apex Legends | Season {i} | {patch}": f"ApexLegends/season{i}/{patch}/vpk/"
    for i, season in enumerate(apex_season_patches)
    for patch in season})


library = files.game_library()
vpks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(vpk_dirs, "*_dir.vpk")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", vpks.values(), ids=vpks.keys())
def test_from_file(filename: str):
    vpk = respawn.Vpk.from_file(filename)
    assert isinstance(vpk.namelist(), list)
    # TODO: try a read
