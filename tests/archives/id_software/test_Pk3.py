import pytest

from bsp_tool.archives import id_software

from ... import files


pk3_dirs: files.LibraryGames
pk3_dirs = {
    "Steam": {
        "Call of Duty": ["Call of Duty/Main/"],
        "Quake III": ["Quake 3 Arena/baseq3/"],
        "Quake III (missionpack)": ["Quake 3 Arena/missionpack/"],
        "Quake Live": ["Quake Live/baseq3/"],
        "Real RTCW": ["RealRTCW/Main/"],
        "Real RTCW (coop)": ["RealRTCW/coop/coopmain/"],
        "Real RTCW (mp)": ["RealRTCW/mp/Main/"],
        "Real RTCW (omnibot)": ["RealRTCW/mp/omnibot/"],
        "Warfork": ["fvi/basewf/"],
        "Warfork (q3pack)": ["fvi/fvi-launcher/applications/netradiant-custom/windows/q3pack/"],
        "WRATH": ["WRATH/kp1/"],
        },
    "Mod": {
        "DOOM": ["DOOM"],  # Doom mods
        # https://github.com/eukara/freecs
        "FreeCS": ["HalfLife/FreeHL-04-18-2023/cstrike/"],
        # https://github.com/eukara/freehl
        "FreeHL": ["HalfLife/FreeHL-04-18-2023/valve/"],
        "Quake III (chronic)": ["QuakeIII/chronic/"],
        "Warsow": ["Warsow/warsow_20/basewsw/"]},
    "GoG": {
        "MoH: AA": ["Medal of Hornor - Allied Assault War Chest/main/"],
        "MoH: AA (Spearhead)": ["Medal of Hornor - Allied Assault War Chest/mainta/"],
        "MoH: AA (Breakthrough)": ["Medal of Hornor - Allied Assault War Chest/maintt/"],
        "Elite Force II": ["Star Trek Elite Force II/base/"],
        "Jedi Academy": ["Star Wars Jedi Knight - Jedi Academy/GameData/base/"],
        "Jedi Outcast": ["Star Wars Jedi Knight II - Jedi Outcast/GameData/base/"]}}
# TODO: C:/Program Files (x86)/Wolfenstein - Enemy Territory/etmain/
# TODO: C:/Program Files (x86)/Call of Duty Burnville Demo/main/
# TODO: C:/Program Files (x86)/Call of Duty Dawnville Demo/main/
# TODO: .../Xonontic/data/
# TODO: FAKK2 (.zip -> .iso -> .pk3)
# TODO: C:/Origin Games/Alice Madness Returns The Complete Collection/Game/Alice1/bin/base/
# TODO: C:/Program Files (x86)/Activision/Star Trek Elite Force II Single Player Demo/base/


library = files.game_library()
pk3s = {
    f"{section} | {game} | {short_path}": full_path
    for section, game, paths in library.scan(pk3_dirs, "*.pk3")
    for short_path, full_path in paths}


@pytest.mark.parametrize("filename", pk3s.values(), ids=pk3s.keys())
def test_from_file(filename: str):
    pk3 = id_software.Pk3.from_file(filename)
    namelist = pk3.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    first_file = pk3.read(namelist[0])
    assert isinstance(first_file, bytes), ".read() failed"
