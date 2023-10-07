CREATE TABLE Engine IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Developer IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Branch IF NOT EXISTS (
    name       VARCHAR  NOT NULL,
    engine     INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (engine)    REFERENCES Engine(rowid),
    FOREIGN KEY (developer) REFERENCES Developer(rowid)
);


CREATE TABLE BranchFork IF NOT EXISTS (
    base  INTEGER  NOT NULL,
    fork  INTEGER  NOT NULL,
    FOREIGN KEY (base) REFERENCES Branch(rowid),
    FOREIGN KEY (fork) REFERENCES Branch(rowid)
);
