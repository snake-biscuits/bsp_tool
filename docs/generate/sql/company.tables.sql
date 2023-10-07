-- relies on release.tables.sql


CREATE TABLE Company IF NOT EXISTS (
    name  VARCHAR  NOT NULL
);


CREATE TABLE CompanyFork IF NOT EXISTS (
    company      INTEGER  NOT NULL,  -- forked from
    new_company  INTEGER  NOT NULL,
    started      DATE     NOT NULL,
    finished     DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (company)     REFERENCES Company(rowid),
    FOREIGN KEY (new_company) REFERENCES Company(rowid)
);


CREATE TABLE CompanyMerge IF NOT EXISTS (
    -- "I'm into murders & executions" - Patrick Bateman
    companies  INTEGER  NOT NULL,
    started    DATE     NOT NULL,
    finished   DATE,   -- if NULL: hasn't happened yet
    FOREIGN KEY (companies) REFERENCES ParentCompany(rowid)
);


-- TODO: other Company events: rebrands, bancruptcies etc.


CREATE TABLE ReleaseDeveloper IF NOT EXISTS (
    release    INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- release.tables.sql
    FOREIGN KEY (developer) REFERENCES Company(rowid)
);


CREATE TABLE ReleasePublisher IF NOT EXISTS (
    release    INTEGER  NOT NULL,
    publisher  INTEGER  NOT NULL,
    FOREIGN KEY (release)   REFERENCES Release(rowid),  -- release.tables.sql
    FOREIGN KEY (publisher) REFERENCES Company(rowid)
);


CREATE TABLE ParentCompany IF NOT EXISTS (
    parent    INTEGER  NOT NULL,  -- owns the other company
    company   INTEGER  NOT NULL,
    FOREIGN KEY (parent)  REFERENCES Company(rowid),
    FOREIGN KEY (company) REFERENCES Company(rowid)
);


CREATE TABLE PlatformCompany IF NOT EXISTS (
    platform  INTEGER  NOT NULL,
    company   INTEGER  NOT NULL,
    FOREIGN KEY (platform) REFERENCES Platform(rowid),  -- release.tables.sql
    FOREIGN KEY (company)  REFERENCES Company(rowid)
);
