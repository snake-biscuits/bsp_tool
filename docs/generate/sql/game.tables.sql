-- TODO: how do we catalogue "The Orange Box"? (3 games on 1 disc)
-- Quake 2 (Xbox 360) is a Disc 2 Bonus w/ Quake 4
CREATE TABLE IF NOT EXISTS Game (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS Relation (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS GameRelation (
    parent    INTEGER  NOT NULL,
    child     INTEGER  NOT NULL,
    relation  INTEGER  NOT NULL,
    FOREIGN KEY (parent)   REFERENCES Game(rowid),
    FOREIGN KEY (child)    REFERENCES Game(rowid),
    FOREIGN KEY (relation) REFERENCES Relation(rowid)
);


CREATE TABLE IF NOT EXISTS Series (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS GameSeries (
    game    INTEGER  NOT NULL,
    series  INTEGER  NOT NULL,
    FOREIGN KEY (game)   REFERENCES Game(rowid),
    FOREIGN KEY (series) REFERENCES Series(rowid)
);
