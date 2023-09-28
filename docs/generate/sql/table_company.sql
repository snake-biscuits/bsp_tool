CREATE TABLE Company (
    name  VARCHAR  NOT NULL
);


CREATE TABLE CompanyFork (
    company      INTEGER  NOT NULL,  -- forked from
    new_company  INTEGER  NOT NULL,
    started      DATE     NOT NULL,
    finished     DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (company)     REFERENCES Company(rowid),
    FOREIGN KEY (new_company) REFERENCES Company(rowid)
);


CREATE TABLE CompanyMerge (
    -- "I'm into murders & executions" - Patrick Bateman
    companies  INTEGER  NOT NULL,
    started    DATE     NOT NULL,
    finished   DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (companies) REFERENCES ParentCompany(rowid)
);


-- TODO: other Company events: rebrands, bancruptcies etc.


CREATE TABLE ReleaseDeveloper (
    release    INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- table_release.sql
    FOREIGN KEY (developer) REFERENCES Company(rowid)
);


CREATE TABLE ReleasePublisher (
    release    INTEGER  NOT NULL,
    publisher  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- table_release.sql
    FOREIGN KEY (publisher) REFERENCES Company(rowid)
);


CREATE TABLE ParentCompany (
    parent    INTEGER  NOT NULL,  -- owns the other company
    company   INTEGER  NOT NULL,
    FOREIGN KEY (parent)  REFERENCES Company(rowid),
    FOREIGN KEY (company) REFERENCES Company(rowid)
);


CREATE TABLE PlatformCompany (
    platform  INTEGER  NOT NULL,
    company   INTEGER  NOT NULL,
    FOREIGN KEY (platform) REFERENCES Platform(rowid),  -- table_release.sql
    FOREIGN KEY (company)  REFERENCES Company(rowid)
);