import json
import re
from flask_mail import Mail, Message 
from flask import Flask, jsonify, render_template, request, redirect, session, flash
import sqlite3
from helpers import login_required,apology,list_otp
from werkzeug.security import check_password_hash, generate_password_hash
from ticket import Ticket, generate_qr_code
from random import randint
app = Flask(__name__)

app.secret_key = "your_secret_key"
# Ensure mail Api
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ctftechnoverse@gmail.com'#to be filled
app.config['MAIL_PASSWORD'] = 'qkow rxpo bxds fgud'#to be filled
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


mail = Mail(app) 

# Database connection
def get_db_connection():
    #conn = sqlite3.connect("database.db")
    conn = sqlite3.connect("DB.db")
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
    if session["username"]=="admin":
        flash("T3chn0v3rs3{Kira_is_L}",category="success")
    return render_template("home.html", username=session["username"])

@app.route("/otp",methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        if not request.form.get("otp"):
            flash('must provide otp')
            return apology("must provide otp", 403)
        if int(request.form.get("otp")) not in list_otp:
            flash('invalid otp')
            return apology("invalid otp", 403)
        list_otp.remove(int(request.form.get("otp")))
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user from the database with email
        cursor.execute("SELECT * FROM users WHERE email = ?", (session["email"],))
        user = cursor.fetchone()
        session["id"]=user["id"]
        session["username"]=user["username"]
        #user will be redirected to change password
        flash('otp verified now you can change password')
        return redirect('/change_password')
    else:
        return render_template("otp.html",email=session["email"])

@app.route("/forgot",methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        if not request.form.get("email"):
            flash('must provide email')
            return apology("must provide email", 403)
        
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
        if not re.match(pattern,request.form.get("email")):
            return render_template("forgot.html", error="Invalid Email")
        conn = get_db_connection()
        cursor = conn.cursor()
        rows=cursor.execute("SELECT * FROM users WHERE email=?", (request.form.get("email"),)).fetchall()
        
        if len(rows) != 1:
            flash('invalid email')
            return render_template("forgot.html")
        
        #genrate an otp and send it to user
        
        #8 digit otp 
        otp=randint(10000000,99999999)
        msg = Message('OTp for new password', sender = 'ctftechnoverse@gmail.com', recipients = [request.form.get("email")])

        msg.body = f"otp is {otp}"
        mail.send(msg)

        session["email"]=request.form.get("email")
        list_otp.append(otp)
        print(list_otp)
        return redirect("/otp")
        #otp=randint(1000,9999)
        #send email to user with new password
        #generate new password
        new_pass="".join([chr(randint(65,90)) for i in range(8)])
        msg = Message('New Password', sender = 'ctftechnoverse@gmail.com', recipients = [request.form.get("email")])
        msg.body = f"new password is {new_pass}"
        mail.send(msg)
        

        hash=generate_password_hash(new_pass)
        cursor.execute("UPDATE users SET password=? WHERE email=?", (hash,request.form.get("email")))
        conn.commit()
        #update database with new password
        flash('new password sent to your email')
        return redirect("/")
    else:
        return render_template("forgot.html")


# Registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        email = request.form["email"]   
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        #email validation
        if not email:
            return render_template("register.html", error="Email is required")
        pattern = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
        if not re.match(pattern,request.form.get("email")):
            return render_template("register.html", error="Invalid Email")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            return render_template("register.html", error="Username already exists")
        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
            return render_template("register.html", error="Email already exists")
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute(
            "INSERT INTO users (username, password,email) VALUES (?, ?, ?)",
            (username, hashed_password, email),
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

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        if new_password != confirm_password:
            return render_template("change_password.html", error="Passwords do not match")

        conn = get_db_connection()
        cursor = conn.cursor()
        # Hash the new password
        hashed_password = generate_password_hash(new_password)

        # Update the password in the database
        cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hashed_password, session["id"]))
        conn.commit()
        flash("Password changed successfully",category="success")
        return redirect("/")
    
    return render_template("change_password.html")




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
        id= request.form["id"]
        conn = get_db_connection()
        cursor = conn.cursor()
        if not id:
            return render_template("generate_ticket.html", error="Invalid id")
        #check if id is of admin
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        user = cursor.fetchone()
        print(user["username"])
        if session['username']=="admin" :
            #no flag for admin
            flash("no flag for admin :)",category="idea")
            return redirect("/generate_ticket")

        if user and user["username"]=="admin" and session["username"]!="admin":
            #they hacked and rewareded a flag
            flash("T3chn0v3rs3{h4ck3r_0f_4dm1n}",category="success")
            print("T3chn0v3rs3{h4ck3r_0f_4dm1n}")
            return redirect("/")

        cursor.execute(
            "DELETE FROM history WHERE userid = ? and status=0", (session["id"],)
        )
        conn.commit()
        return redirect("/")
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
        id=session["id"],
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
    # if user is admin then ask a key they formed from site
    if user and user["username"]=="admin":
        
        return jsonify({"status": "admin",'url':"/key"}), 302
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

@app.route("/key",methods=["POST","GET"])
def key():
    if request.method == "POST":
        if not request.form.get("key"):
            flash('must provide key')
            return render_template("key.html", error="must provide key")
        if request.form.get("key")!="T3chn0v3rs3{Kira_is_L}":
            flash('invalid key')
            return render_template("key.html", error="invalid key")
        if request.form.get("key")=="T3chn0v3rs3{Kira_is_L}":
            flash('T3chn0v3rs3{$4m3er_$ury4_S41ki_Ku$uo}',category="success")
            return redirect("/key")
    else:
        return render_template("key.html")
def start_ngrok():
    from pyngrok import ngrok


if __name__ == "__main__":
    app.run(debug=True)
