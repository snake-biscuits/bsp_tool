"""bsp_tool.branches -> sql"""
import sqlite3
import sys

import common

sys.path.insert(0, "../" * 3)
import bsp_tool  # noqa E402


def generate():
    """populate tables & save to .sql"""
    db = sqlite3.connect(":memory:")
    common.run_script(db, "table_branch.sql")

    # Developer
    developers = [d.__name__.split(".")[-1] for d in bsp_tool.branches.developers]
    db.executemany("INSERT INTO Developer(name) VALUES(?)", [(d,) for d in developers])

    # Engine
    engines = list(bsp_tool.branches.of_engine.keys())
    db.executemany("INSERT INTO Engine(name) VALUES(?)", [(e,) for e in engines])

    # Branch
    values = list()
    engine_of = {b: e for e, bs in bsp_tool.branches.of_engine.items() for b in bs}
    for developer_index, developer in enumerate(bsp_tool.branches.developers):
        for branch in developer.scripts:
            name = branch.__name__.split(".")[-1]
            engine_index = engines.index(engine_of[branch])
            values.append((name, developer_index + 1, engine_index + 1))
    db.executemany("INSERT INTO Branch(name, developer, engine) VALUES(?, ?, ?)", values)

    # BranchFork
    # "data_branch.fork.json"

    common.tables_to_file(db, "data_branch.sql", ("Engine", "Developer", "Branch"))


def load_into(database: sqlite3.Connection):
    common.run_script(database, "table_branch.sql")
    common.run_script(database, "data_branch.sql")


if __name__ == "__main__":
    generate()  # writes to data_branch.sql
