CREATE TABLE reported (
year INTEGER NOT NULL, metric TEXT NOT NULL, value REAL NOT NULL,
unit TEXT NOT NULL, status TEXT CHECK(status='reported'), basis TEXT NOT NULL,
source_id TEXT NOT NULL, locator TEXT NOT NULL, PRIMARY KEY(year,metric));
