-- list all Source Engine branches
SELECT CONCAT(D.name, ".", B.name)
FROM       Branch    AS B
INNER JOIN Developer AS D ON B.developer == D.rowid
WHERE E.name == "Source"


-- list all branch forks INSIDE Source Engine (no forks in or out)
-- NOTE: could concat developers, but I'm lazy
SELECT B.name, F.name
FROM       BranchFork AS BF
INNER JOIN Branch     AS  B ON BF.base == B.rowid
INNER JOIN Branch     AS  F ON BF.fork == F.rowid
INNER JOIN Engine     AS  E ON B.engine == E.rowid AND F.engine == E.rowid
WHERE E.name == "Source"
