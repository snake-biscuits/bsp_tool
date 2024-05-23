import json
import sqlite3

import common


def generate():
    db = sqlite3.connect(":memory:")
    common.run_script(db, "game.tables.sql")

    tables = list()

    tables.append("Game")
    # TODO: gather from release.data.release.csv instead
    with open("game.data.game.txt") as txt_file:
        games = [x.rstrip("\n") for x in txt_file.readlines()]
    db.executemany("INSERT INTO Game(name) VALUES(?)", [(g,) for g in games])

    tables.append("Relation")
    relations = set()
    tables.append("GameRelation")
    game_relations = list()
    with open("game.data.relation.json") as json_file:
        for parent_game, groups in json.load(json_file).items():
            for relation, related_games in groups.items():
                relations.add(relation)
                for child_game in related_games:
                    parent_game_index = games.index(parent_game) + 1
                    child_game_index = games.index(child_game) + 1
                    game_relations.append((parent_game_index, child_game_index, relation))
    relations = sorted(relations)
    db.executemany("INSERT INTO Relation(name) VALUES(?)", [(r,) for r in relations])
    game_relations = [(pgi, gi, relations.index(r) + 1) for pgi, gi, r in game_relations]
    db.executemany("INSERT INTO GameRelation(parent, child, relation) VALUES(?, ?, ?)", game_relations)
    # NOTE: the Quake 4 + Quake II bundle is just the Xbox360 2nd Disc
    # -- however we're only looking at how games are related, not releases

    tables.append("Series")
    series = list()
    tables.append("GameSeries")
    game_series = list()
    with open("game.data.series.json") as json_file:
        for series_name, series_games in json.load(json_file).items():
            series.append(series_name)
            for game in series_games:
                game_series.append((len(series), games.index(game) + 1))
    db.executemany("INSERT INTO Series(name) VALUES(?)", [(s,) for s in series])
    db.executemany("INSERT INTO GameSeries(game, series) VALUES(?, ?)", game_series)

    common.tables_to_file(db, "game.data.sql", tables)


def load_into(database: sqlite3.Connection):
    common.run_script(database, "game.tables.sql")
    common.run_script(database, "game.data.sql")


if __name__ == "__main__":
    generate()  # writes to game.data.sql
