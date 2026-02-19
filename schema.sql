CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    selected_language TEXT NOT NULL,
    unlocked_chapter INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS progress(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    chapter INTEGER,
    score INTEGER
);
