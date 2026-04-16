import sqlite3

# connect to database
conn = sqlite3.connect('users.db')
c = conn.cursor()

# create table
c.execute('''
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    password TEXT
)
''')

conn.commit()
conn.close()