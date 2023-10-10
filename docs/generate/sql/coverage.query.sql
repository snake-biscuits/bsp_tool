CREATE VIEW BranchCoverage IF NOT EXISTS (
    SELECT (branch, AVG(coverage))
    FROM BranchLumpClass
    GROUP BY branch
);
