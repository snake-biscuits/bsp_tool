import sqlite3
from typing import Any, Generator, List, Tuple


def run_script(database: sqlite3.Connection, filename: str):
    with open(filename) as sql_script:
        database.executescript(sql_script.read())


def sql_repr(obj: Any) -> str:
    if obj is None:
        return "NULL"
    else:
        return repr(obj)


def store_table(database: sqlite3.Connection, table: str, rows: List[str], values: List[Tuple[Any]]):
    # TODO: get rows from an sql query?
    rows_ = ",".join(rows)
    template = ",".join(("?",) * len(rows))
    database.executemany(f"INSERT INTO {table}({rows_}) VALUES({template})", values)


# NOTE: might need to write tables in a specific order for Foreign Keys
def tables_as_sql(database: sqlite3.Connection, tables: List[str]) -> Generator[str, None, None]:
    """saving sqlite .db to .sql for git diffs"""
    query = ["SELECT m.name as table_name, p.name as column_name",  # ("Table", "column")
             "FROM sqlite_master AS m",  # list of tables
             "JOIN pragma_table_info(m.name) as p",  # column names & other metadata
             "WHERE m.type='table'",  # just tables
             "ORDER BY m.name, p.cid"]  # alphabetical table order, column order
    table_columns = database.execute("\n".join(query)).fetchall()
    for table in tables:
        fields = ", ".join([c for t, c in table_columns if t == table and c != "id"])
        yield f"INSERT INTO {table}({fields}) VALUES\n"
        entries = database.execute(f"SELECT {fields} FROM {table}").fetchall()
        for entry in entries[:-1]:
            yield "\t({}),\n".format(",".join(map(sql_repr, entry)))
        yield "\t({});\n\n\n".format(",".join(map(sql_repr, entries[-1])))


def tables_to_file(database: sqlite3.Connection, filename: str, tables: List[str]):
    with open(filename, "w") as data_sql:
        data_sql.write("-- Generated via python script\n")
        for line in tables_as_sql(database, tables):
            data_sql.write(line)
