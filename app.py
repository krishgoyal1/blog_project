from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="Templates")

app.secret_key = "your_secret_key"

def get_db_connection():
    conn = sqlite3.connect("blog.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute ("INSERT INTO users (username, email, password_hash) VALUES (?,?,?)", (username, email, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username or Email already exists!"

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"],password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials!"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT posts.title, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", posts=posts)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/post", methods = ["GET","POST"])
def post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        user_id = session["user_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content), )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("post.html")

if __name__ == "__main__":
    app.run(debug=True)
