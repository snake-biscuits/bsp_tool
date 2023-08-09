CREATE DATABASE GameEngineHistory;

-- TODO:
-- more historic dates:
--- date pulled from storefront (beta periods, delistings, end of service)
--- developer split / founding (IW -> Respawn)
--- acquisitions, buyouts, bancruptcies, dissolutions

-- GAMES --
CREATE TABLE IF NOT EXISTS Game (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS GameChild (  -- demos, updates, sequels, mods & expansions
    game   INTEGER  NOT NULL,
    child  INTEGER  NOT NULL,
    FOREIGN KEY (game) REFERENCES Game (id),
    FOREIGN KEY (child) REFERENCES Game (id),
);

-- RELEASES --
CREATE TABLE IF NOT EXISTS Platform (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

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
    FOREIGN KEY (game) REFERENCES Game (id),
    FOREIGN KEY (region) REFERENCES Region (id),
    FOREIGN KEY (platform) REFERENCES Platform (id)
);

-- COMPANIES --
CREATE TABLE IF NOT EXISTS Publisher (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS ReleasePublisher (
    release    INTEGER  NOT NULL,
    publisher  INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release (id),
    FOREIGN KEY (publisher) REFERENCES Platform (id)
);

CREATE TABLE IF NOT EXISTS Developer (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS ReleaseDeveloper (
    release    INTEGER  NOT NULL,
    developer  INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release (id),
    FOREIGN KEY (developer) REFERENCES Developer (id)
);

-- ENGINE BRANCHES --
CREATE TABLE IF NOT EXISTS Branch (
    id    INTEGER      PRIMARY KEY,
    name  VARCHAR(64)  NOT NULL,
);

CREATE TABLE IF NOT EXISTS ReleaseBranch (
    release  INTEGER  NOT NULL,
    branch   INTEGER  NOT NULL,
    FOREIGN KEY (release) REFERENCES Release (id),
    FOREIGN KEY (branch) REFERENCES Branch (id)
);
