-- relies on branch.tables.sql
-- relies on game.tables.sql


CREATE TABLE Platform IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Region IF NOT EXISTS (
    name   VARCHAR  NOT NULL,
    short  VARCHAR  NOT NULL
);


CREATE TABLE Release IF NOT EXISTS (
    game      INTEGER  NOT NULL,
    platform  INTEGER  NOT NULL,
    region    INTEGER  NOT NULL,
    day       DATE     -- if NULL: not yet released
    delisted  DATE,    -- if NULL: still available
    FOREIGN KEY (game)     REFERENCES Game(rowid),  -- game.tables.sql
    FOREIGN KEY (platform) REFERENCES Platform(rowid),
    FOREIGN KEY (region)   REFERENCES Region(rowid)
);


CREATE TABLE ReleaseBranch IF NOT EXISTS (
    release  INTEGER  NOT NULL,
    branch   INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release(rowid),
    FOREIGN KEY (branch)  REFERENCES Branch(rowid)  -- branch.tables.sql
);  -- some releases have multiple branches; so this is M:N
