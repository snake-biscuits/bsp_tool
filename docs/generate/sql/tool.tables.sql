-- relies on branch.tables.sql

-- based on links etc. in "[Test Map]" GitHub Issues

-- TODO: how to represent GtKRadiant Gamepacks?
-- TODO: links to downloads & documentation (citation.tables?)
-- TODO: sort toolchains by accessibility ratings


-- TOOLS
CREATE TABLE IF NOT EXISTS LevelEditor (
    name      VARCHAR  NOT NULL,
    version   VARCHAR  NOT NULL,
    released  DATE
);


CREATE TABLE IF NOT EXISTS Compiler (
    name  VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS Utility (
    name   VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS CompilerUtility (
    compiler  INTEGER  NOT NULL,
    utility   INTEGER  NOT NULL,
    FOREIGN KEY compiler REFERENCES Compiler(rowid),
    FOREIGN KEY utility REFERENCES Utility(rowid)
);


CREATE TABLE IF NOT EXISTS PostCompiler (
    name  VARCHAR  NOT NULL
);


-- FORMATS
CREATE TABLE IF NOT EXISTS ToolFileFormat (
    name  VARCHAR  NOT NULL,
    ext   VARCHAR  NOT NULL
);


CREATE TABLE IF NOT EXISTS LevelEditorFormat (
    editor  INTEGER  NOT NULL,
    format  INTEGER  NOT NULL,
    FOREIGN KEY editor REFERENCES LevelEditor(rowid),
    FOREIGN KEY format REFERENCES ToolFileFormat(rowid)
);


CREATE TABLE IF NOT EXISTS CompilerFormat (
    compiler  INTEGER  NOT NULL,
    format    INTEGER  NOT NULL,
    FOREIGN KEY compiler REFERENCES Compiler(rowid),
    FOREIGN KEY format REFERENCES ToolFileFormat(rowid)
);


-- NOTE: PostCompilers process .bsp directly


-- BRANCHES
CREATE TABLE IF NOT EXISTS BranchLevelEditor (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES Editor(rowid)
);


CREATE TABLE IF NOT EXISTS BranchCompiler (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES Compiler(rowid)
);


CREATE TABLE IF NOT EXISTS BranchPostCompiler (
    branch  INTEGER  NOT NULL,  -- branch.tables.sql
    tool    INTEGER  NOT NULL,
    FOREIGN KEY branch REFERENCES Branch(rowid),
    FOREIGN KEY tool REFERENCES PostCompiler(rowid)
);
