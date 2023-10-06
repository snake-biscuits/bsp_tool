import sqlite3

import common


# NOTE: Citation will indirectly link to any table in the db
# -- but we still need rowid to make the link, so import everything


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "citation.tables.sql")

    raise NotImplementedError()
    tables = list()

    # TODO: "citations/company.history.md"

    # tables.append("Reference")
    ...

    # table.append("Citation")
    ...

    common.tables_to_file(db, "citation.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "citation.tables.sql")
    common.run_script(database, "citation.data.sql")


if __name__ == "__main__":
    generate()  # writes to citation.data.sql
