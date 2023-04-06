DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS tagAssignments;

CREATE TABLE models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE tagAssignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tagId INTEGER,
    modelId INTEGER,
    FOREIGN KEY(tagId) REFERENCES tags(id),
    FOREIGN KEY (modelId) REFERENCES models(id),
    CONSTRAINT Unique_Tag UNIQUE (tagId,modelId)
);