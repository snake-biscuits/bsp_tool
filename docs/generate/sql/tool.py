import sqlite3

import common


# TODO: Source SDK branches
# -- per-branch install guides for Hammer

# NOTE: using this DB chunk to generate basic setup guides
# -- download Editor X, configure Compiler Y, [use PostCompiler Z]
# -- these guides could be inserted into a page for each branch


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "tool.tables.sql")

    raise NotImplementedError()
    tables = list()

    # tables.append("LevelEditor")
    ...

    # tables.append("Compiler")
    ...

    # tables.append("Utility")
    ...

    # tables.append("CompilerUtility")
    ...

    # tables.append("PostCompiler")
    ...

    # https://developer.valvesoftware.com/wiki/MAP_(file_format)
    # https://developer.valvesoftware.com/wiki/RMF_(Rich_Map_Format)
    # https://developer.valvesoftware.com/wiki/VMF_(Valve_Map_Format)
    # tool.data.format.json
    # tables.append("ToolFileFormat")
    ...

    # tables.append("LevelEditorFormat")
    ...

    # tables.append("CompilerFormat")
    ...

    # TODO: branch lookup dict
    # tool.data.branch.json
    # table.append("BranchLevelEditor")
    ...

    # table.append("BranchCompiler")
    ...

    # table.append("BranchPostCompiler")
    ...

    common.tables_to_file(db, "tool.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "tool.tables.sql")
    common.run_script(database, "tool.data.sql")


if __name__ == "__main__":
    generate()  # writes to tool.data.sql
