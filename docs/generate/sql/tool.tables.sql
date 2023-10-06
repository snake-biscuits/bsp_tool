-- relies on branch.tables.sql

-- based on links etc. in "[Test Map]" GitHub Issues

-- TODO: how to represent GtKRadiant Gamepacks?
-- TODO: links to downloads & documentation (citation.tables?)
-- TODO: sort toolchains by accessibility ratings


CREATE TABLE LevelEditor IF NOT EXISTS (
    name      VARCHAR  NOT NULL,
    version   VARCHAR  NOT NULL,
    released  DATE
);


CREATE TABLE Compiler IF NOT EXISTS(
    name  VARCHAR  NOT NULL
);


CREATE TABLE PostCompiler IF NOT EXISTS(
    name  VARCHAR  NOT NULL
);


CREATE TABLE ToolFileFormat IF NOT EXISTS (
    name  VARCHAR  NOT NULL,
    ext   VARCHAR  NOT NULL
);


CREATE TABLE LevelEditorFormat IF NOT EXISTS (
    editor  INTEGER  NOT NULL,
    format  INTEGER  NOT NULL,
    FOREIGN KEY editor REFERENCES LevelEditor(rowid),
    FOREIGN KEY format REFERENCES ToolFileFormat(rowid)
);


CREATE TABLE CompilerFormat IF NOT EXISTS (
    compiler  INTEGER  NOT NULL,
    format    INTEGER  NOT NULL,
    FOREIGN KEY compiler REFERENCES Compiler(rowid),
    FOREIGN KEY format REFERENCES ToolFileFormat(rowid)
);


-- NOTE: PostCompilers process .bsp directly, rather than editor files


CREATE TABLE BranchLevelEditor IF NOT EXISTS (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES Editor(rowid)
);


CREATE TABLE BranchCompiler IF NOT EXISTS (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES Compiler(rowid)
);


CREATE TABLE BranchPostCompiler IF NOT EXISTS (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES PostCompiler(rowid)
);
