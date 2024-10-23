import sqlite3
import prep

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

"""
cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

cur.execute("INSERT INTO todos (title, descr) VALUES (?, ?)",
            ('First Todo', 'Finish UCLA secondary')
            )

cur.execute("INSERT INTO todos (title, descr) VALUES (?, ?)",
            ('Second Todo', 'Work on Website')
            )

cur.execute("INSERT INTO exercises (title) VALUES (?)",
            ('Pushups',)
            )

cur.execute("INSERT INTO workouts (ex, reps, dat) VALUES (?, ?, ?)",
            ('Pushups', 5, "10/18")
            )

cur.execute("INSERT INTO workouts (ex, reps, dat) VALUES (?, ?, ?)",
            ('Pushups', 7, "10/19")
            )

cur.execute("INSERT INTO workouts (ex, reps, dat) VALUES (?, ?, ?)",
            ('Pushups', 10, "10/20")
            ) """


connection.commit()
connection.close()

#prep.main()