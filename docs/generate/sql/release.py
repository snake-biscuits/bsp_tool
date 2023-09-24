import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "table_game.sql")    # Release FK
    common.run_script(db, "table_branch.sql")  # Release FK
    common.run_script(db, "table_release.sql")

    # Platform
    # "data_release.platform.json"

    # Region
    # "data_release.region.json"

    # Release
    # "releases.sc"

    # ReleaseBranch
    # tests/megatest.py

    common.tables_to_file(db, "data_release.sql", (...))


def load_into(database: sqlite3.Connection):
    common.run_script("table_release.sql")
    common.run_script("data_release.sql")
