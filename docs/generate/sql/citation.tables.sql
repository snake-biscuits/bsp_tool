CREATE TABLE Reference (
    label         VARCHAR,
    published     DATE,
    main_link     VARCHAR,
    archive_link  VARCHAR,  -- internet archive link
    archived      DATE
);


-- TODO: ReferenceAuthor, Author, Publication/Site


CREATE Table Citation (
    cited_table   VARCHAR  NOT NULL,  -- SELECT name FROM sqlite_master WHERE type='table'
    cited_column  VARCHAR  NOT NULL,  -- pragma_table_data(cited_table)
    reference     INTEGER  NOT NULL,
    FOREIGN KEY (reference) REFERENCES Reference(rowid)
);
