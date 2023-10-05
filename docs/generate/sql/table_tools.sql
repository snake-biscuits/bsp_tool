-- relies on table_branch.sql
-- based on links etc. in "[Test Map]" GitHub Issues
-- TODO: how to represent GtKRadiant Gamepacks?
-- TODO: links to downloads & documentation
-- TODO: sort by accessibility rankings


CREATE TABLE LevelEditor (
    name      VARCHAR  NOT NULL,
    version   VARCHAR  NOT NULL,
    released  DATE
);


CREATE TABLE BranchLevelEditor (
    branch  INTEGER  NOT NULL,
    editor  INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY editor REFERENCES Editor(rowid)
);


CREATE TABLE Compiler (
    name  VARCHAR  NOT NULL
);


CREATE TABLE PostCompiler (
    name  VARCHAR  NOT NULL
);
