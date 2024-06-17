import collections
import sqlite3
import sys

import branch
import common

sys.path.insert(0, "../" * 3)
import bsp_tool  # noqa E402


def subclass_tree(cls):
    for sc in cls.__subclasses__():
        yield (cls, sc)
        for entry in subclass_tree(sc):
            yield entry


def generate():
    """populate tables & save to .sql"""
    db = sqlite3.connect(":memory:")
    branch.load_into(db)
    common.run_script(db, "bsp.tables.sql")

    tables = list()

    all_bsp_classes = sorted(
        {f for b, f in subclass_tree(bsp_tool.base.Bsp)},
        key=lambda c: (c.__module__, c.__name__))

    developers = {
        name: rowid
        for name, rowid in db.execute("SELECT name, rowid FROM Developer").fetchall()}

    tables.append("BspClass")
    bsp_classes = [
        (c.__name__, developers[c.__module__.split(".")[-1]])
        for c in all_bsp_classes]
    db.executemany("INSERT INTO BspClass(name, developer) VALUES(?, ?)", bsp_classes)

    tables.append("BspClassFork")
    forks = [
        (all_bsp_classes.index(base) + 1, all_bsp_classes.index(fork) + 1)
        for base, fork in subclass_tree(bsp_tool.base.Bsp)
        if base != bsp_tool.base.Bsp]
    db.executemany("INSERT INTO BspClassFork(base, fork) VALUES(?, ?)", forks)

    branches = {
        name: rowid
        for name, rowid in db.execute("SELECT name, rowid FROM Branch").fetchall()}

    all_branch_scripts = {
        *bsp_tool.branches.quake_based,
        *bsp_tool.branches.source_based}

    branch_bsp_class = {
        branch_script: bsp_tool.BspVariant_for_magic[branch_script.FILE_MAGIC]
        for branch_script in all_branch_scripts
        if branch_script.FILE_MAGIC is not None}
    branch_bsp_class.update({  # None
        bsp_tool.branches.gearbox.blue_shift: bsp_tool.valve.GoldSrcBsp,
        bsp_tool.branches.gearbox.nightfire: bsp_tool.valve.GoldSrcBsp,
        bsp_tool.branches.id_software.quake: bsp_tool.id_software.QuakeBsp,
        bsp_tool.branches.valve.goldsrc: bsp_tool.valve.GoldSrcBsp})
    branch_bsp_class.update({  # b"VBSP"
        bsp_tool.branches.nexon.cso2: bsp_tool.nexon.NexonBsp,
        bsp_tool.branches.nexon.cso2_2018: bsp_tool.nexon.NexonBsp})
    branch_bsp_class.update({  # b"IBSP"
        branch_script: bsp_tool.infinity_ward.InfinityWardBsp
        for branch_script in bsp_tool.branches.infinity_ward.scripts})
    branch_bsp_class.update({  # b"IBSP", v22
        bsp_tool.branches.infinity_ward.modern_warfare: bsp_tool.infinity_ward.D3DBsp})

    tables.append("BspClassBranch")
    bsp_class_branches = [
        (all_bsp_classes.index(bsp_class) + 1, branches[branch_script.__name__.split(".")[-1]])
        for branch_script, bsp_class in branch_bsp_class.items()]
    db.executemany("INSERT INTO BspClassBranch(bsp_class, branch) VALUES(?, ?)", bsp_class_branches)

    common.tables_to_file(db, "bsp.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "bsp.tables.sql")
    common.run_script(database, "bsp.data.sql")


if __name__ == "__main__":
    generate()  # writes to bsp.data.sql
