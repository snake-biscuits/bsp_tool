import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "game.tables.sql")
    common.run_script(db, "branch.tables.sql")
    common.run_script(db, "release.tables.sql")

    raise NotImplementedError()
    tables = list()

    tables.append("Platform")
    # "data_release.platform.json"
    ...

    tables.append("Region")
    # "data_release.region.json"
    ...

    tables.append("Release")
    # "releases.sc"
    ...

    tables.append("ReleaseBranch")
    # tests/megatest.py
    ...

    common.tables_to_file(db, "release.data.sql", tables)


def load_into(database: sqlite3.Connection):
    """load after game & branch"""
    common.run_script(database, "release.tables.sql")
    common.run_script(database, "release.data.sql")


if __name__ == "__main__":
    generate()  # writes to release.data.sql
