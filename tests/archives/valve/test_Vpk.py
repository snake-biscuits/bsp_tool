import pytest

from bsp_tool.archives import valve

from ... import files


vpk_dirs: files.LibraryGames
vpk_dirs = {
    "Steam": {
        "Black Mesa": ["Black Mesa/bms/"],
        "Bloody Good Time": ["Bloody Good Time/vpks/"],
        "Contagion": ["Contagion/vpks/"],
        "Dark Messiah of Might and Magic": [
            "Dark Messiah Might and Magic Single Player/vpks/",
            "Dark Messiah Might and Magic Multi-Player/vpks/"],
        "SiN Episodes: Emergence": ["SiN Episodes Emergence/vpks/"],
        "The Ship": ["The Ship/vpks/"],
        "The Ship Singleplayer": ["The Ship Single Player/vpks/"],
        "The Ship Tutorial": ["The Ship Tutorial/vpks/"]}}
# NOTE: Dark Messiah Singleplayer | depot_2109_dir.vpk is empty
# -- https://steamdb.info/depot/2109/ (mm_media)
# NOTE: The Ship | depot_2402_dir.vpk contains "umlaut e" b"\xEB" (latin_1)
# -- https://steamdb.info/depot/2402/ (The Ship Common)
# NOTE: The Ship's shares it's vpks between "games"
# -- by downloading it once for each folder...


library = files.game_library()
vpks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(vpk_dirs, "*_dir.vpk")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", vpks.values(), ids=vpks.keys())
def test_from_file(filename: str):
    vpk = valve.Vpk.from_file(filename)
    assert isinstance(vpk.namelist(), list)
    # TODO: try a read
