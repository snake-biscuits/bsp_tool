CREATE TABLE Platform (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Region (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Release (
    game      INTEGER  NOT NULL,
    platform  INTEGER  NOT NULL,
    region    INTEGER  NOT NULL,
    day       DATE     -- if NULL: not yet released
    delisted  DATE,    -- if NULL: still available
    FOREIGN KEY (game)     REFERENCES Game(rowid),  -- table_game.sql
    FOREIGN KEY (platform) REFERENCES Platform(rowid),
    FOREIGN KEY (region)   REFERENCES Region(rowid)
);


CREATE TABLE ReleaseBranch (
    release  INTEGER  NOT NULL,
    branch   INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release(rowid),
    FOREIGN KEY (branch)  REFERENCES Branch(rowid)  -- table_branch.sql
);  -- some releases have multiple branches; so this is M:N
