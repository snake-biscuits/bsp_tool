from collections import defaultdict
import inspect
# import json
import sqlite3
import struct
import sys
from types import ModuleType
from typing import Dict, List

import branch as branch_db
import common

sys.path.insert(0, "../" * 3)
import bsp_tool  # noqa E402
from bsp_tool.branches import base  # noqa E402


def short_script_name(module: ModuleType) -> str:
    split_module = module.__name__.split(".")
    if split_module[0] == "bsp_tool" and split_module[1] in ("branches", "extensions"):
        return ".".join(split_module[2:])
    else:
        raise NotImplementedError()  # shouldn't happen but idk


def calculate_coverage(LumpClass: object) -> (int, int):  # %age is (2nd - 1st) / 2nd
    """yields (num_unknown_bits, total_bits)"""
    # NOTE: SpecialLumpClasses are tested against a table (import from .json)
    if not issubclass(LumpClass, (base.BitField, base.MappedArray, base.Struct)):
        raise RuntimeError(f"cannot process '{LumpClass}'")
    lump_class = LumpClass()
    if issubclass(LumpClass, base.Struct):
        return calculate_coverage_Struct(lump_class)
    elif issubclass(LumpClass, base.MappedArray):
        return calculate_coverage_MappedArray(lump_class)
    elif issubclass(LumpClass, base.BitField):
        return calculate_coverage_BitField(lump_class)


# TODO: catch _bitfields = {"attr.child": ...}
def calculate_coverage_Struct(lump_class: base.Struct) -> (int, int):
    total_bits = len(lump_class.as_bytes()) * 8
    num_unknown_bits = 0
    # NOTE: bits, not bytes; we care about bitfields
    format_ = base.split_format(lump_class._format)
    attr_start = 0
    for attr in lump_class.__slots__:
        child = getattr(lump_class, attr)
        attr_length = 1
        if attr in lump_class._arrays:
            attr_length = base.mapping_length(lump_class._arrays[attr])
            num_unknown_bits += calculate_coverage_MappedArray(child)[0]
        elif attr in lump_class._bitfields:
            num_unknown_bits += calculate_coverage_BitField(child)[0]
        # NOTE: it's possible to have an "unknown" attr w/ non-unknown children
        # -- that's confusing tho, so we'll count those children as unknown no matter what
        if attr.startswith("unknown"):
            attr_format = "".join(format_[attr_start:attr_start + attr_length])
            num_unknown_bits += struct.calcsize(attr_format) * 8
        attr_start += attr_length
    return (num_unknown_bits, total_bits)


def calculate_coverage_MappedArray(lump_class: base.MappedArray) -> (int, int):
    # NOTE: we recieve an instance, so attrs should be correct
    total_bits = len(lump_class.as_bytes()) * 8
    num_unknown_bits = 0
    # NOTE: bits, not bytes; we care about bitfields
    format_ = base.split_format(lump_class._format)
    attr_start = 0
    for attr in lump_class._mapping:
        attr_length = 1
        if isinstance(lump_class._mapping, dict):  # nested mappings
            child_mapping = lump_class._mapping[attr]
            attr_length = base.mapping_length(child_mapping)
            if child_mapping is not None and isinstance(child_mapping, (list, dict)):
                child = getattr(lump_class, attr)
                num_unknown_bits += calculate_coverage_MappedArray(child)[0]
        elif attr in lump_class._bitfields:
            num_unknown_bits += calculate_coverage_BitField(child)[0]
        # NOTE: it's possible to have an "unknown" attr w/ non-unknown children
        # -- that's confusing tho, so we'll count those children as unknown no matter what
        if attr.startswith("unknown"):
            attr_format = "".join(format_[attr_start:attr_start + attr_length])
            num_unknown_bits += struct.calcsize(attr_format) * 8
        attr_start += attr_length
    return (num_unknown_bits, total_bits)


def calculate_coverage_BitField(LumpClass: base.BitField) -> (int, int):
    total_bits = len(LumpClass().as_bytes()) * 8
    num_unknown_bits = sum(
        num_bits
        for attr, num_bits in LumpClass._fields.items()
        if attr.startswith("unknown"))
    return (num_unknown_bits, total_bits)


def register_classes(db: sqlite3.Connection, classes: List[object]) -> Dict[object, int]:
    indices = dict()
    lump_classes = db.execute("SELECT script, name, line, coverage FROM LumpClass").fetchall()
    scripts = db.execute("SELECT name, short FROM Script").fetchall()
    quick_check = [(scripts[s][0], n) for s, n, l, c in lump_classes]
    new_lump_classes = list()
    new_scripts_start = len(scripts)
    for c in classes:
        script_name = c.__module__
        name = c.__name__
        if (script_name, name) in quick_check:
            indices[c] = quick_check.index((script_name, name))
            continue
        script_short = short_script_name(script_name)
        # get script index
        script = (script_name, script_short)
        if script not in scripts:
            scripts.append(script)
        script = scripts.index(script)
        # get line number
        try:
            raw_code, line = inspect.getsourcelines(c)
        except Exception:  # TODO: be specific
            line = None  # probably a _x360 class
        # get coverage %age
        coverage = calculate_coverage(c)
        indices[c] = len(lump_classes) + len(new_lump_classes)
        new_lump_classes.append((script, name, line, coverage))
    if len(scripts) > new_scripts_start:
        db.executemany("INSERT INTO Script(name, short) VALUES(?)", scripts[new_scripts_start:])
    if len(new_lump_classes) > 0:
        db.executemany("INSERT INTO LumpClass(script, name, line, coverage) Values(?, ?, ?, ?)", new_lump_classes)
    return indices


def process_quake_branch(db: sqlite3.Connection, branch: ModuleType):
    lump_classes = {**branch.BASIC_LUMP_CLASSES, **branch.LUMP_CLASSES, **branch.SPECIAL_LUMP_CLASSES}
    lump_classes = {L: c for L, c in lump_classes.items() if hasattr(branch.LUMP, L)}

    lumps = [x[0] for x in db.execute("SELECT name FROM Lump").fetchall()]
    new_lumps = [L.name for L in branch.LUMP if L.name not in lumps]
    db.executemany("INSERT INTO Lump(name) VALUES(?)", new_lumps)
    lumps.extend(new_lumps)

    classes = sorted(set(lump_classes.values()), key=lambda c: (c.__module__.__name__, c.__name__))
    classes = register_classes(classes)
    branch_index = branch_db.module_index(db, branch)
    blc = [(branch_index, lumps.index(L), classes[c]) for L, c in lump_classes.items()]
    db.executemany("INSERT INTO BranchLumpClass(branch, lump, class) VALUES(?, ?, ?)", blc)


def process_source_branch(db: sqlite3.Connection, branch: ModuleType):
    all_lump_classes = {**branch.BASIC_LUMP_CLASSES, **branch.LUMP_CLASSES, **branch.SPECIAL_LUMP_CLASSES}
    all_lump_classes = {L: c for L, c in all_lump_classes.items() if hasattr(branch.LUMP, L)}
    lump_classes = defaultdict(dict)
    lump_classes.update(all_lump_classes)

    lumps = [x[0] for x in db.execute("SELECT name FROM Lump").fetchall()]
    new_lumps = [L.name for L in branch.LUMP if L.name not in lumps]
    db.executemany("INSERT INTO Lump(name) VALUES(?)", new_lumps)
    lumps.extend(new_lumps)

    classes = {c for vc in lump_classes.values() for c in vc.values()}
    glcs = {c for vc in branch.GAME_LUMP_CLASSES.values() for c in vc.values()}
    for lump, vc in branch.GAME_LUMP_CLASSES.items():
        lump_classes[f"GAME_LUMP.{lump}"] = vc
        if lump == "sprp":
            spcs = {v: c.StaticPropClass for v, c in vc.items()}
            glcs.update(set(spcs.values()))
            lump_classes["GAME_LUMP.sprp.props"] = spcs
            for v, c in vc:
                if hasattr(c, "scales"):
                    glcs.add(branch.StaticPropScales)
                    lump_classes["GAME_LUMP.sprp.scales"][v] = branch.StaticPropScales
                # TODO: update when we know what respawn.titanfall2.GameLump_SPRPvXX.unknown_3 is
                elif hasattr(c, "unknown_3"):
                    lump_classes["GAME_LUMP.sprp.unknown_3"][v] = None
    classes.update(glcs)
    classes = register_classes(sorted(classes, key=lambda c: (c.__module__.__name__, c.__name__)))
    branch_index = branch_db.module_index(db, branch)
    blcv = [(branch_index, lumps.index(L), classes[c], v)
            if c is not None else (branch_index, lumps.index(L), None, v)
            for L, vc in classes.items() for v, c in vc.items()]
    db.executemany("INSERT INTO BranchLumpClass(branch, lump, class, version) VALUES(?, ?, ?, ?)", blcv)


# TODO: branches.bspx


def generate():
    db = sqlite3.connect(":memory:")
    branch_db.load_into(db)
    common.run_script(db, "coverage.tables.sql")

    raise NotImplementedError()
    tables = list()

    # tables.append("Lump")
    # tables.append("LumpClass")
    # tables.append("BranchLumpClass")
    # coverage.data.unmapped.json
    for branch in bsp_tool.branches.quake_based:
        process_quake_branch(db, branch)
    for branch in bsp_tool.branches.source_based:
        process_source_branch(db, branch)
    ...

    # tables.append("BranchCoverage")  # VIEW
    common.tables_to_file(db, "coverage.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "coverage.tables.sql")
    common.run_script(database, "coverage.data.sql")


if __name__ == "__main__":
    generate()  # writes to coverage.data.sql
