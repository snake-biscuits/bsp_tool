import fnmatch
import os

import pytest

from bsp_tool.archives import id_software

from ... import utils


paks = dict()
archive = utils.archive_dirs()
if archive.steam_dir is not None or archive.gog_dir is not None:
    # {"top_dir", {"game": {"mod": ["pak_dirs"]}}}
    pak_dirs = {
        archive.steam_dir: {
            "Hexen 2": {
                "Core Game": ["data1"]},
            "Quake": {
                "Alkaline": ["alk1.1", "alkaline", "alkaline_dk"],
                "Arcane Dimensions": ["ad"],
                "Copper": ["copper"],  # Underdark Overbright
                "Core Game": ["hipnotic", "Id1", "rogue"],
                "Prototype Jam #3": ["sm220"]},
            "Quake/rerelease": {
                "Core Game": ["hipnotic", "id1", "rogue"],
                "Dimension of the Past": ["dopa"],
                "New": ["ctf", "mg1"]},
            "Quake 2": {
                "Core Game": ["baseq2", "ctf", "rogue", "xatrix", "zaero"]},
            "Quake 2/rerelease": {
                "Core Game": ["baseq2"]}},
        archive.gog_dir: {
            "Soldier of Fortune": {
                "Core Game": ["base"]}}}
    if None in pak_dirs:  # skip top_dirs not in this ArchivistStash
        pak_dirs.pop(None)
    # NOTE: "mod" is to give clear names to each group of mod folders
    # -- not part of the path
    # NOTE: Daikatana uses a different .pak format
    # TODO: Heretic II
    # TODO: Quake64 in %USERPROFILE%

    def paks_of(top_dir: str, game: str, pak_dir: str):
        full_dir = os.path.join(top_dir, game, pak_dir)
        pak_filenames = fnmatch.filter(os.listdir(full_dir), "*.pak")
        pak_full_paths = [
            os.path.join(full_dir, pak_filename)
            for pak_filename in pak_filenames]
        return list(zip(pak_filenames, pak_full_paths))

    paks = {
        f"{game} | {mod} ({pak_dir}) | {pak_filename}": pak_full_path
        for top_dir, games in pak_dirs.items()
        for game, mods in games.items()
        for mod, pak_dirs in mods.items()
        for pak_dir in pak_dirs
        for pak_filename, pak_full_path in paks_of(top_dir, game, pak_dir)}
    # TODO: if a game is not installed on this device, skip it


@pytest.mark.parametrize("filename", paks.values(), ids=paks.keys())
def test_from_file(filename: str):
    pak = id_software.Pak.from_file(filename)
    namelist = pak.namelist()
    assert isinstance(namelist, list), ".namelist() failed"
    if len(namelist) != 0:
        first_file = pak.read(namelist[0])
        assert isinstance(first_file, bytes), ".read() failed"
