from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from ticket import Ticket, generate_qr_code

app = Flask(__name__)

app.secret_key = "your_secret_key"

# Database connection
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM history WHERE userid = ? and status=0", (session["id"],)
        )
        data = cursor.fetchone()
        if data:
            flash("You Already have a ticket can use one at a time")
            return redirect("/")
        start = request.form["start_location"]
        end = request.form["end_location"]
        username = session["username"]
        ticket = generate_qr_code(
            start_location=start,
            destination=end,
            qr_code_file=f"static/tickets/{username}.png",
        )
        # Insert new user into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO history (hash,start,destination,userid,time) VALUES (?,?,?,?,?)",
            (
                ticket.id,
                ticket.start_location,
                ticket.destination,
                session["id"],
                ticket.creation_time,
            ),
        )
        conn.commit()
        return redirect("/generate_ticket")
    return render_template("home.html", username=session["username"])


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            return render_template("register.html", error="Username already exists")
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        return redirect("/")

    return render_template("register.html")


# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user from the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["id"] = user["id"]
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


# Logout route
@app.route("/logout")
@login_required
def logout():
    session.pop("username", None)
    session.pop("id", None)
    return redirect("/login")


# Generate ticket route
@app.route("/generate_ticket", methods=["GET", "POST"])
@login_required
def generate_ticket():
    if request.method == "POST":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM history WHERE userid = ? and status=0", (session["id"],)
        )
        conn.commit()
    username = session["username"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM history WHERE userid = ? and status=0", (session["id"],)
    )
    data = cursor.fetchone()
    if not data:
        return render_template("no_display.html")
    t = Ticket(
        data["hash"],
        data["time"],
        data["start"],
        data["destination"],
        f'static/tickets/{session["username"]}.png',
    )
    return render_template(
        "tickets.html",
        username=username,
        start=t.start_location,
        destination=t.destination,
        time_remaining=t.valid_upto(),
    )


@app.route("/myrfid")
@login_required
def rfid():
    username = session["username"]
    return render_template("myrfid.html", username=username)


@app.route("/myhistory")
@login_required
def history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM history WHERE userid = ? and status=1", (session["id"],)
    )
    data = cursor.fetchall()
    if not data:
        return render_template("no_display.html")
    return render_template("history.html", data=data)


@app.route("/scan_qr_code")
def scan_qr_code():
    return render_template("scanner.html")


@app.route("/process_qr_code", methods=["POST"])
def process_qr_code():
    qr_code_data = request.form["qr_code_data"]

    # Handle the scanned QR code data
    # ...
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history WHERE  hash=?", (qr_code_data,))
    data = cursor.fetchone()
    if not data:
        return render_template("no_display.html")
    cursor.execute("SELECT * FROM users WHERE id = ?", (data["userid"],))
    user = cursor.fetchone()
    t = Ticket(
        data["hash"],
        data["time"],
        data["start"],
        data["destination"],
        f'static/tickets/{user["username"]}.png',
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE history SET status=1 where hash=?", (qr_code_data,))
    conn.commit()
    t.remove()
    return render_template("no_display.html")


def start_ngrok():
    from pyngrok import ngrok


if __name__ == "__main__":
    app.run(debug=True)
