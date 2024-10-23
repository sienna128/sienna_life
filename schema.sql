DROP TABLE IF EXISTS posts;

/* CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
); */

DROP TABLE IF EXISTS todos;

/*
CREATE TABLE todos (
    todo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    descr TEXT
    
); */

DROP TABLE IF EXISTS exercises;

/*
CREATE TABLE exercises (
    exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    nam TEXT NOT NULL
    
);*/

DROP TABLE IF EXISTS workouts;

/*
CREATE TABLE workouts (
    workout_id INTEGER PRIMARY KEY AUTOINCREMENT,
    --exercise_id FOREIGN KEY REFERENCES exercises(exercise_id),
    --date_id FOREIGN KEY REFERENCES dates(date_id),
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ex TEXT NOT NULL,
    reps INTEGER,
    num_sets INTEGER, 
    dat TEXT
    
);*/

DROP TABLE IF EXISTS dates;

/*
CREATE TABLE dates (
    date_id INTEGER PRIMARY KEY AUTOINCREMENT,
    mon TEXT,
    da TEXT,
    str_dat TEXT
);*/

DROP TABLE IF EXISTS weeks;

/*
CREATE TABLE weeks (
    week_id INTEGER PRIMARY KEY AUTOINCREMENT,
    day1 TEXT, 
    day2 TEXT, 
    day3 TEXT, 
    day4 TEXT,
    day5 TEXT,
    day6 TEXT,
    day7 TEXT
); */

DROP TABLE IF EXISTS today;

/*
CREATE TABLE today (
    week_id INTEGER,
    str_dat TEXT
);*/