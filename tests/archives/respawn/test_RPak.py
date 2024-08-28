import fnmatch
import os

import pytest

from bsp_tool.archives import respawn

from ... import utils


rpak_dirs = dict()
archive = utils.archive_dirs()
if archive.steam_dir is not None:
    steam_games = {
        "Apex Legends": "paks/Win64/",
        "Titanfall2": "r2/paks/Win64/"}
    rpak_dirs.update({
        f"Steam | {game}": os.path.join(archive.steam_dir, game, rpak_dir)
        for game, rpak_dir in steam_games.items()})


if archive.mod_dir is not None:
    ps4_games = {
        # "Titanfall2": "r2/paks/PS4/",  # TODO: v2.0.11.0 rpaks
        "Titanfall2_tech_test": "r2/paks/PS4/"}
    rpak_dirs.update({
        f"PS4 | {game}": os.path.join(archive.mod_dir, "PS4", game, rpak_dir)
        for game, rpak_dir in ps4_games.items()})


rpaks = {
    f"{platform_game} | {rpak_filename}": os.path.join(rpak_dir, rpak_filename)
    for platform_game, rpak_dir in rpak_dirs.items()
    for rpak_filename in fnmatch.filter(os.listdir(rpak_dir), "*.rpak")}


@pytest.mark.parametrize("filename", rpaks.values(), ids=rpaks.keys())
def test_from_file(filename: str):
    rpak = respawn.RPak.from_file(filename)
    if rpak.header.compression == respawn.rpak.Compression.NONE:
        assert isinstance(rpak.namelist(), list)
        # TODO: test .read() (NotYetImplemented)
