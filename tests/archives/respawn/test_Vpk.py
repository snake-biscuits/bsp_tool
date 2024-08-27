import fnmatch
import os

import pytest

from bsp_tool.archives import respawn

from ... import utils


vpk_dirs = dict()
archive = utils.archive_dirs()
if archive.steam_dir is not None:
    steam_games = ["Titanfall", "Titanfall2"]
    vpk_dirs.update({
        game: os.path.join(archive.steam_dir, game, "vpk/")
        for game in steam_games})

if archive.mod_dir is not None:
    vpk_dirs.update({
        "Titanfall (Beta)": os.path.join(archive.mod_dir, "Titanfall/beta/vpk/")})
    apex_archive = [
        ["4feb19"],
        ["19mar19", "16apr19", "4jun19"],
        ["2jul19", "13aug19", "3sep19"],
        # TODO: get season3 5nov19 & 3dec19 vpk/ folders from rexx
        # -- ["1oct19", "5nov19", "3dec19"],
        ["1oct19"],
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
    vpk_dirs.update({
        f"Apex Legends | Season {i} | {patch}": os.path.join(archive.mod_dir, f"ApexLegends/season{i}/{patch}/vpk/")
        for i, season in enumerate(apex_archive)
        for patch in season})


vpks = dict()
for game, vpk_dir in vpk_dirs.items():
    if not os.path.exists(vpk_dir):
        continue  # coplandbentokom-9876 only has a small subset of the archive
    for vpk_filename in fnmatch.filter(os.listdir(vpk_dir), "*_dir.vpk"):
        full_path = os.path.join(vpk_dir, vpk_filename)
        vpks[f"{game} | {vpk_filename}"] = full_path


@pytest.mark.parametrize("filename", vpks.values(), ids=vpks.keys())
def test_Vpk_from_file(filename: str):
    vpk = respawn.Vpk.from_file(filename)
    assert isinstance(vpk.namelist(), list)
    # TODO: try a read
