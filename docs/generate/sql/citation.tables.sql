CREATE TABLE IN NOT EXISTS Reference (
    label         VARCHAR  UNIQUE,
    published     DATE,
    main_link     VARCHAR  UNIQUE,
    archive_link  VARCHAR,  -- internet archive link
    archived      DATE
);


-- TODO: ReferenceAuthor, Author, Publication/Site


CREATE TABLE IF NOT EXISTS Citation (
    cited_table   VARCHAR  NOT NULL,  -- SELECT name FROM sqlite_master WHERE type='table'
    cited_column  VARCHAR  NOT NULL,  -- pragma_table_data(cited_table)
    reference     INTEGER  NOT NULL,
    FOREIGN KEY (reference) REFERENCES Reference(rowid)
);
