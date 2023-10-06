-- TODO: how do we catalogue "The Orange Box"? (3 games on 1 disc)
-- Quake 2 (Xbox 360) is a Disc 2 Bonus w/ Quake 4
CREATE TABLE Game IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Relation IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE GameRelation IF NOT EXISTS (
    parent    INTEGER  NOT NULL,
    child     INTEGER  NOT NULL,
    relation  INTEGER  NOT NULL,
    FOREIGN KEY (game)     REFERENCES Game(rowid),
    FOREIGN KEY (child)    REFERENCES Game(rowid),
    FOREIGN KEY (relation) REFERENCES Relation(rowid)
);


CREATE TABLE Series IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE GameSeries IF NOT EXISTS (
    game    INTEGER  NOT NULL,
    series  INTEGER  NOT NULL,
    FOREIGN KEY game REFERENCES Game(rowid),
    FOREIGN KEY series REFERENCES Series(rowid)
);
