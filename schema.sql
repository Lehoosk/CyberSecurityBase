CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    default_public INTEGER,
    created TEXT,
    user_exercise_count INTEGER,
    user_comment_count INTEGER
);

CREATE TABLE exercises (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    exercise_type_id INTEGER REFERENCES exercise_types ON DELETE CASCADE,
    exercise_class_id INTEGER REFERENCES classes,
    exercise_weight REAL,
    exercise_date TEXT,
    public INTEGER,
    note TEXT,
    comment_count INTEGER
);

CREATE TABLE exercise_types (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    exercise_type_name TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    label TEXT,
    reps  INTEGER
);

INSERT INTO classes
VALUES
 (1, '3 series of 2 reps', 2),
 (2, '5 series of 5 reps', 5),
 (3, '3 series of 10 reps', 10);

CREATE TABLE pr_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    exercise_type_id INTEGER REFERENCES exercise_types ON DELETE CASCADE,
    exercise_class_id INTEGER REFERENCES classes,
    e1rm_epley REAL,
    e1rm_lombardi REAL,
    e1rm_brzycki REAL,
    ex_weight REAL,
    pr_date TEXT
);

 CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    exercise_id INTEGER REFERENCES exercises ON DELETE CASCADE,
    user_id INTEGER REFERENCES users ON DELETE CASCADE,
    comment_text TEXT,
    created_date TEXT
);
