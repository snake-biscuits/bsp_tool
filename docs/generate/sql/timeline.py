"""sc-im -> sql db"""
import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "table_timeline.sql")

    # TODO: populate tables
    # Game
    # GameConnection

    # Platform
    # Region
    # Release
    # TODO: sc-im releases.sc ...
    # ReleaseCitation

    # Company
    # CompanyMerge
    # CompanyFork
    # GameDeveloper
    # ReleasePublished
    ...

    common.tables_to_file(db, "data_timeline.sql", (...))


def load_into(database: sqlite3.Connection):
    common.run_script("table_timeline.sql")
    common.run_script("data_timeline.sql")
