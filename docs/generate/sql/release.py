import csv
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

    tables = list()

    tables.append("Platform")
    platforms = list()
    with open("release.data.platform.json") as json_file:
        json_data = json.load(json_file)  # {"Company": {"P": "Platform"}}
    platforms = [
        (name, short)
        for platforms in json_data.values()
        for short, name in platforms.items()]
    db.executemany("INSERT INTO Platform(name, short) VALUES(?, ?)", platforms)
    # NOTE: same data used for PlatformCompany in CompanyDB

    tables.append("Region")
    with open("release.data.region.json") as json_file:
        regions = json.load(json_file)  # {"WW": "Worldwide"}
    db.executemany("INSERT INTO Region(short, name) VALUES(?, ?)", regions.items())
    regions = list(regions.keys())

    # BranchDB
    branches = {
        f"{developer}.{branch}": rowid
        for rowid, developer, branch in db.execute("""
            SELECT B.rowid, D.name, B.name
            FROM Branch AS B
            INNER JOIN Developer as D
            ON B.developer == D.rowid""").fetchall()}

    # GameDB
    games = {
        name: rowid
        for name, rowid in db.execute(
            "SELECT name, rowid FROM Game").fetchall()}

    platforms = {
        **{name: i + 1 for i, (name, short) in enumerate(platforms)},
        **{short: i + 1 for i, (name, short) in enumerate(platforms)}}

    tables.append("Release")
    releases = list()
    tables.append("ReleaseBranch")
    release_branches = list()
    # NOTE: dates may be fuzzy ranges / text (e.g. Cancelled, TBA)
    with open("release.data.release.csv") as csv_file:  # from .sc sc-im file
        rows = csv.reader(csv_file)
        next(rows)  # skip column names
        for row in rows:
            row = [x if x != "" else None for x in row]
            if len(row) < 7:  # pad tail
                row.extend((None,) * (7 - len(row)))
            developer, game_name, day, regions_, platforms_, delisted, branches_ = row
            # NOTE: developer is for ReleaseDeveloper in CompanyDB
            for region in regions_.split(";"):
                region_index = regions.index(region) + 1
                for platform in platforms_.split(";"):
                    releases.append((games[game_name], platforms[platform], region_index, day, delisted))
                    if branches_ is not None:
                        for branch_ in branches_.split(";"):
                            release_branches.append((len(releases), branches[branch_]))
    db.executemany("INSERT INTO Release(game, platform, region, day, delisted) VALUES(?, ?, ?, ?, ?)", releases)
    db.executemany("INSERT INTO ReleaseBranch(release, branch) VALUES(?, ?)", release_branches)

    common.tables_to_file(db, "release.data.sql", tables)


def load_into(database: sqlite3.Connection):
    """load after game & branch"""
    common.run_script(database, "release.tables.sql")
    common.run_script(database, "release.data.sql")


if __name__ == "__main__":
    generate()  # writes to release.data.sql
