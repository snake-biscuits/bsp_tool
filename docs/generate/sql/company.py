import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "table_game.sql")
    common.run_script(db, "table_branch.sql")
    common.run_script(db, "table_release.sql")
    common.run_script(db, "table_company.sql")

    # Company
    ...

    # CompanyMerge
    ...

    # CompanyFork
    ...

    # M:N linkers
    # PlatformCompany
    ...

    # ReleaseDeveloper
    # "data_company.developer.json"
    ...

    # ReleasePublisher
    ...

    common.tables_to_file(db, "data_company.sql", (...))


def load_into(database: sqlite3.Connection):
    common.run_script("table_company.sql")
    common.run_script("data_company.sql")
