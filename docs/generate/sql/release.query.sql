-- games using nexon branches, sorted by release date
SELECT R.day, G.name, CONCAT('nexon.', B.name), P.name
FROM       ReleaseBranch AS RB
INNER JOIN Release       AS  R ON RB.release   == R.rowid
INNER JOIN Game          AS  G ON  R.game      == G.rowid  -- for G.name
INNER JOIN Platform      AS  P ON  R.platform  == P.rowid  -- for P.name
INNER JOIN Branch        AS  B ON RB.branch    == B.rowid
INNER JOIN Developer     AS  D ON  B.developer == D.rowid
WHERE D.name == 'nexon'  -- branch developer filter
ORDER BY R.day ASC


-- source engine branches sorted chronologically
SELECT X.branch_name
FROM (
    SELECT
        MIN(R.day)                   AS release_day,
        CONCAT(D.name, '.', B.name)  AS branch_name
    FROM       ReleaseBranch AS RB
    INNER JOIN Release       AS  R ON RB.release   == R.rowid
    INNER JOIN Branch        AS  B ON RB.branch    == B.rowid
    INNER JOIN Developer     AS  D ON  B.developer == D.rowid
    INNER JOIN Engine        AS  E ON  B.engine    == E.rowid
    WHERE E.name == 'Source'
    AND   R.day LIKE '%-%-%'  -- ignore dates like NULL & 'Not Yet'
    GROUP BY branch_name
) AS X
ORDER BY X.release_day ASC


-- count number of releases each month
SELECT SUBSTRING(R.day, 1, 7), COUNT(*)
FROM Release AS R
GROUP BY SUBSTRING(R.day, 1, 7)


-- view selection of releases for a given month
SELECT R.day, G.name, P.name
FROM       Release  AS R
INNER JOIN Game     AS G ON R.game     == G.rowid
INNER JOIN Platform AS P ON R.platform == P.rowid
WHERE SUBSTRING(R.day, 1, 7) == '2023-08'
ORDER BY R.day ASC
