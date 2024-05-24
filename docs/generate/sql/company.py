import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "game.tables.sql")
    common.run_script(db, "branch.tables.sql")
    common.run_script(db, "release.tables.sql")
    common.run_script(db, "company.tables.sql")

    raise NotImplementedError()
    tables = list()

    # tables.append("Company")
    companies = []
    db.executemany("INSERT INTO Company(name) VALUES (?)", [(c,) for c in companies])

    # tables.append("CompanyMerge")
    ...

    # tables.append("CompanyFork")
    ...

    # M:N linkers
    # tables.append("PlatformCompany")
    ...

    # tables.append("ReleaseDeveloper")
    # "data_company.developer.json"
    ...

    # tables.append("ReleasePublisher")
    ...

    common.tables_to_file(db, "company.data.sql", tables)


def load_into(database: sqlite3.Connection):
    """load after game, branch & release"""
    common.run_script(database, "company.tables.sql")
    common.run_script(database, "company.data.sql")


if __name__ == "__main__":
    generate()  # writes to company.data.sql
