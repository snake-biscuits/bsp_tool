CREATE TABLE IF NOT EXISTS Engine (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS Developer (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS Branch (
    name       VARCHAR  NOT NULL,
    engine     INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    colour     VARCHAR  NOT NULL,
    FOREIGN KEY (engine)    REFERENCES Engine(rowid),
    FOREIGN KEY (developer) REFERENCES Developer(rowid)
);


CREATE TABLE IF NOT EXISTS BranchFork (
    base  INTEGER  NOT NULL,
    fork  INTEGER  NOT NULL,
    FOREIGN KEY (base) REFERENCES Branch(rowid),
    FOREIGN KEY (fork) REFERENCES Branch(rowid)
);
