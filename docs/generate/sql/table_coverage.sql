-- relies on table_branch.sql


CREATE TABLE BranchCoverage (
    branch    INTEGER  NOT NULL,
    coverage  FLOAT    NOT NULL,  -- bsp_tool coverage
    FOREIGN KEY branch REFERENCES Branch(rowid)
);


-- LumpClass coverage
-- Branch LumpClasses
-- Branch unmapped lumps

-- TODO: (UX) compare LumpClasses between branches (like current groups)
--- trace BranchFork relationships
