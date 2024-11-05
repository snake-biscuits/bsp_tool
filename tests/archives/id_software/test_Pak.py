import pytest

from bsp_tool.archives import id_software

from ... import files


# TODO: Heretic II
# TODO: Quake64 in %USERPROFILE%
pak_dirs: files.LibraryGames
pak_dirs = {
    "Steam": {
        "Hexen 2": ["Hexen 2/data1"],
        "Quake": ["Quake/Id1"],
        "Quake (hipnotic)": ["Quake/hipnotic"],
        "Quake (rogue)": ["Quake/rogue"],
        "Alkaline": ["Quake/alkaline"],
        "Alkaline (alk1.1)": ["Quake/alk1.1"],
        "Alkaline (alkaline_dk)": ["Quake/alkaline_dk"],
        "Arcane Dimensions": ["Quake/ad"],
        "Underdark Overbright": ["Quake/copper"],
        "Prototype Jam #3": ["Quake/sm220"],
        "Quake Re-Release": ["Quake/rerelease/id1"],
        "Quake Re-Release (ctf)": ["Quake/rerelease/ctf"],
        "Quake Re-Release (hipnotic)": ["Quake/rerelease/hipnotic"],
        "Quake Re-Release (Machine Games)": ["Quake/rerelease/mg1"],
        "Quake Re-Release (rogue)": ["Quake/rerelease/rogue"],
        "Quake: Dimension of the Past": ["Quake/Rerelease/dopa"],
        "Quake 2": ["Quake 2/baseq2"],
        "Quake 2 (ctf)": ["Quake 2/ctf"],
        "Quake 2 (rogue)": ["Quake 2/rogue"],
        "Quake 2 (xatrix)": ["Quake 2/xatrix"],
        "Quake 2 (zaero)": ["Quake 2/zaero"],
        "Quake 2 Re-Release": ["Quake 2/rerelease/baseq2"],
        "Warfork": ["fvi/fvi-launcher/applications/netradiant-custom/windows/q1pack/"]},
    "GoG": {
        "Soldier of Fortune": ["Soldier of Fortune/base"]}}


library = files.game_library()
paks = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(pak_dirs, "*.pak")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", paks.values(), ids=paks.keys())
def test_from_file(filename: str):
    pak = id_software.Pak.from_file(filename)
    namelist = pak.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = pak.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"


# TODO: filesystem utility tests on "Steam | Quake | PAK0.PAK"
# -- pak.is_dir("sound/")
# -- pak.is_dir("sound/ambience/")

# -- pak.is_dir(".")
# -- pak.is_dir("./")
# -- pak.is_dir("./sound/")
# -- pak.is_dir("./sound/ambience/")
# TODO: is_file
# TODO: path_exists
# TODO: tree
