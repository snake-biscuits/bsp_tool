import sqlite3

import branch
import common


# TODO: re-use parts of old coverage generator
# -- break down into sub-functions


def generate():
    db = sqlite3.connect(":memory:")
    branch.load_into(db)
    common.run_script(db, "coverage.tables.sql")

    raise NotImplementedError()
    tables = list()

    # tables.append("BranchCoverage")
    ...

    common.tables_to_file(db, "coverage.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "coverage.tables.sql")
    common.run_script(database, "coverage.data.sql")


if __name__ == "__main__":
    generate()  # writes to coverage.data.sql
