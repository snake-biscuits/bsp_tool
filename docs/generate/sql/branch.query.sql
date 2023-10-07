-- example queries


-- list all branches of a given engine
SELECT D.name, B.name  -- ("Developer", "Branch")
FROM Branch AS B
INNER JOIN Developer as D
ON D.rowid=B.developer  -- match FK
WHERE B.engine=9;  -- Source Engine
