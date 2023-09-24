-- bsp_tool.branches.developer.branch
CREATE TABLE Engine (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Developer (
    name  VARCHAR  NOT NULL
);


CREATE TABLE Branch (
    name       VARCHAR  NOT NULL,
    engine     INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (engine)    REFERENCES Engine(rowid),
    FOREIGN KEY (developer) REFERENCES Developer(rowid)
);


CREATE TABLE BranchFork (
    base  INTEGER  NOT NULL,
    fork  INTEGER  NOT NULL,
    FOREIGN KEY (base) REFERENCES Branch(rowid),
    FOREIGN KEY (fork) REFERENCES Branch(rowid)
);
