import sqlite3
from werkzeug.security import generate_password_hash
conn = sqlite3.connect("blog.db")
cursor = conn.cursor()
cursor.execute("""

CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY,
username TEXT UNIQUE NOT NULL,
email TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL
)

""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

conn.commit()
conn.close()