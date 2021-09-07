import pytest

from . import decorators
from . import maplist


def pytest_addoption(parser):
    games = [g for s, g in maplist.installed_games]
    parser.addoption("--game", action="store", nargs="*",
                     help="Game folder(s) to test", choices=games)
    parser.addoption("--skip", action="store", nargs="*",
                     help="Game folder(s) to skip", choices=games)


@pytest.fixture
def installed_games(request) -> maplist.GameDirList:
    games = request.config.getoption("--game")
    filtered_games = filter(lambda s, g: g in games, maplist.installed_games)
    skips = request.config.getoption("--skip")
    filtered_games = filter(lambda s, g: g not in skips, filtered_games)
    return {k: maplist.installed_games[k] for k in filtered_games}


def all_maps():
    return decorators.all_maps(installed_games)
