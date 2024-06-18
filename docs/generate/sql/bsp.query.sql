-- BspClass (branch, fork) pairings
SELECT B.name, F.name
FROM       BspClassFork AS BF
INNER JOIN BspClass     AS  B ON BF.base == B.rowid
INNER JOIN BspClass     AS  F ON BF.fork == F.rowid

-- developer.BspClass
SELECT CONCAT(D.name, ".", BC.name)
FROM       BspClass  AS BC
INNER JOIN Developer AS  D ON BC.developer == D.rowid

-- (BspClass, branch) pairings
SELECT BC.name, B.name
FROM       BspClassBranch AS BCB
INNER JOIN BspClass       AS  BC ON BCB.bsp_class == BC.rowid
INNER JOIN Branch         AS   B ON BCB.branch    ==  B.rowid
