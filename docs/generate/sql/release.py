import json
import sqlite3

import branch
import common
import game


def generate():
    db = sqlite3.connect(":memory:")
    game.load_into(db)
    branch.load_into(db)
    common.run_script(db, "release.tables.sql")

    raise NotImplementedError()
    tables = list()

    tables.append("Platform")
    with open("release.data.platform.json") as json_file:
        json_data = json.load(json_file)  # {"Company": ["Platform"]}
        db.executemany("INSERT INTO Platform(name) VALUES(?)", [v for vs in json_data.values() for v in vs])
    # NOTE: PlatformCompany comes later in CompanyDB

    tables.append("Region")
    with open("release.data.region.json") as json_file:
        db.executemany("INSERT INTO Region(short, name) VALUES(?, ?)", json.load(json_file).items())

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
