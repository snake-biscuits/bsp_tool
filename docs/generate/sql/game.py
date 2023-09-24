import sqlite3

import common


# TODO: game series groups
# Series + GameSeries
# json: {"Series": ["Game", ...]}


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "table_game.sql")    # Release FK
    common.run_script(db, "table_branch.sql")  # Release FK

    # data_game.json

    # Game
    # Relation
    # GameRelation
    # Ports (w/ different names e.g. Dark Messiah of Might & Magic: Elements)
    # Demos / Open Betas
    # Sequels
    # Mods
    # Expansion Packs
    # Remakes / Rereleases / Reboots (e.g. MW 2019)
    # Seasons / Major Updates

    common.tables_to_file(db, "data_game.sql", ("Game", "Relation", "GameRelation"))


def load_into(database: sqlite3.Connection):
    common.run_script("table_game.sql")
    common.run_script("data_game.sql")
