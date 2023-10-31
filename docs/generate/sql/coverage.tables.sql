-- relies on branch.tables.sql


CREATE TABLE IF NOT EXISTS Lump (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS Script (
    name   VARCHAR  NOT NULL,  -- e.g "bsp_tool.extensions.lightmaps"
    short  VARCHAR  NOT NULL   -- e.g "lightmaps"
);


CREATE TABLE IF NOT EXISTS LumpClass (
    -- NOTE: mix of BasicLumpClass, LumpClass, SpecialLumpClass & methods
    script    INTEGER  NOT NULL,  -- script the LumpClass is defined in
    name      VARCHAR  NOT NULL,
    line      INTEGER,  -- NULL for most x360 classes
    coverage  FLOAT    NOT NULL,  -- [0.0 - 100.0]
    FOREIGN KEY script REFERENCES Script(rowid)
);


CREATE TABLE IF NOT EXISTS BranchLumpClass (
    branch   INTEGER  NOT NULL,  -- branch.tables.sql
    lump     INTEGER  NOT NULL,
    class    INTEGER,  -- NULL if unmapped
    version  INTEGER,  -- NULL for quake_based, NOT NULL for source_based
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY lump REFERENCES Lump(rowid),
    FOREIGN KEY class REFERENCES LumpClass(rowid)
);
