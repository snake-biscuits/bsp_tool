CREATE DATABASE GameEngineHistory;

-- TODO:
-- more historic dates:
--- developer split / founding (2015 Inc. -> IW -> Respawn -> IW / Gravity Well)
--- acquisitions, buyouts, bancruptcies, dissolutions

-- GAMES --
CREATE TABLE IF NOT EXISTS Game (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

-- demo / fork / update / sequel / mod / expansion / engine re-used
CREATE TABLE IF NOT EXISTS GameChild (
    game   INTEGER  NOT NULL,
    child  INTEGER  NOT NULL,
    -- child type enum? non-time-linear relationship (e.g. demo / beta)
    FOREIGN KEY (game) REFERENCES Game (id),
    FOREIGN KEY (child) REFERENCES Game (id),
);

-- RELEASES --
CREATE TABLE IF NOT EXISTS Platform (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

-- TODO: Storefront / Launcher
-- Steam, Origin, GOG
-- Nexon, PlayGra

CREATE TABLE IF NOT EXISTS Region (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS Release (
    id        INTEGER  PRIMARY KEY,
    game      INTEGER  NOT NULL,
    platform  INTEGER  NOT NULL,
    region    INTEGER  NOT NULL,
    day       DATE     NOT NULL,
    delisted  DATE,  -- can be NULL
    FOREIGN KEY (game) REFERENCES Game (id),
    FOREIGN KEY (region) REFERENCES Region (id),
    FOREIGN KEY (platform) REFERENCES Platform (id)
);

CREATE TABLE IF NOT EXISTS Delisting (
    id      INTEGER PRIMARY KEY,
    release INTEGER NOT NULL,
    day     DATE    NOT NULL,
    FOREIGN KEY (release) REFERENCES Release (id)
);

-- COMPANIES --
CREATE TABLE IF NOT EXISTS Company (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS ReleaseCompany (
    release  INTEGER  NOT NULL,
    company  INTEGER  NOT NULL,
    -- dev, publisher, platform owner etc.?
    FOREIGN KEY (release) REFERENCES Release (id),
    FOREIGN KEY (company) REFERENCES Company (id),
    PRIMARY KEY (release, company)
);

-- ENGINE BRANCHES --
CREATE TABLE IF NOT EXISTS Engine (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL
);

CREATE TABLE IF NOT EXISTS EngineFork (
    engine  INTEGER  NOT NULL,  -- forked
    fork    INTEGER  NOT NULL,  -- forker
    FOREIGN KEY (engine) REFERENCES Engine (id),
    FOREIGN KEY (fork) REFERENCES Engine (id),
    PRIMARY KEY (engine, fork)
);

CREATE TABLE IF NOT EXISTS Branch (
    id      INTEGER      PRIMARY KEY,
    name    VARCHAR(64)  NOT NULL,
    engine  INTEGER      NOT NULL,
    FOREIGN KEY (engine) REFERENCES Engine (id)
);

CREATE TABLE IF NOT EXISTS ReleaseBranch (
    release  INTEGER  NOT NULL,
    branch   INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release (id),
    FOREIGN KEY (branch) REFERENCES Branch (id)
);
