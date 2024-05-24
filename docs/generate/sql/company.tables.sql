-- relies on release.tables.sql


CREATE TABLE IF NOT EXISTS Company (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS CompanyFork (
    base      INTEGER  NOT NULL,
    fork      INTEGER  NOT NULL,
    started   DATE     NOT NULL,
    finished  DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (base) REFERENCES Company(rowid),
    FOREIGN KEY (fork) REFERENCES Company(rowid)
);


CREATE TABLE IF NOT EXISTS CompanyMerge (
    -- "I'm into murders & executions" - Patrick Bateman
    companies  INTEGER  NOT NULL,
    started    DATE     NOT NULL,
    finished   DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (companies) REFERENCES ParentCompany(rowid)
);


-- TODO: other Company events: rebrands, layoffs, bancruptcies etc.


CREATE TABLE IF NOT EXISTS ReleaseDeveloper (
    release    INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- release.tables.sql
    FOREIGN KEY (developer) REFERENCES Company(rowid)
);


CREATE TABLE IF NOT EXISTS ReleasePublisher (
    release    INTEGER  NOT NULL,
    publisher  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- release.tables.sql
    FOREIGN KEY (publisher) REFERENCES Company(rowid)
);


CREATE TABLE IF NOT EXISTS ParentCompany (
    parent    INTEGER  NOT NULL,  -- owns the other company
    company   INTEGER  NOT NULL,
    FOREIGN KEY (parent)  REFERENCES Company(rowid),
    FOREIGN KEY (company) REFERENCES Company(rowid)
);


CREATE TABLE IF NOT EXISTS PlatformCompany (
    platform  INTEGER  NOT NULL,
    company   INTEGER  NOT NULL,
    FOREIGN KEY (platform) REFERENCES Platform(rowid),  -- release.tables.sql
    FOREIGN KEY (company)  REFERENCES Company(rowid)
);
