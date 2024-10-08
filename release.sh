#!/bin/sh

sqlite3 /workspace/api.db <<'END_SQL'
.timeout 2000
CREATE TABLE if not exists Users(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, password TEXT NOT NULL, role CHAR(10) NOT NULL, disabled BOOL NOT NULL);
END_SQL
