-- relies on branch.tables.sql


CREATE TABLE IF NOT EXISTS BspClass (
    name       VARCHAR  NOT NULL,
    developer  INTEGER  NOT NULL,  -- branch.tables.sql
    FOREIGN KEY (developer) REFERENCES Developer(rowid)
);


CREATE TABLE IF NOT EXISTS BspClassFork (
    base  INTEGER  NOT NULL,
    fork  INTEGER  NOT NULL,
    FOREIGN KEY (base) REFERENCES BspClass(rowid),
    FOREIGN KEY (fork) REFERENCES BspClass(rowid)
);


CREATE TABLE IF NOT EXISTS BspClassBranch (
    bsp_class  INTEGER NOT NULL,
    branch     INTEGER NOT NULL,
    FOREIGN KEY (bsp_class) REFERENCES BspClass(rowid),
    FOREIGN KEY (branch)    REFERENCES Branch(rowid)
);
