from flask import Flask, render_template, request, redirect, session
import sqlite3
from helpers import login_required
from werkzeug.security import check_password_hash, generate_password_hash
from ticket import Ticket,generate_qr_code
import time
app = Flask(__name__)

app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#export FLASK_APP=hello.py
# Home page
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        start=request.form["start_location"]
        end=request.form["end_location"]
        username = session['username']
        ticket=generate_qr_code(start_location=start,destination=end,qr_code_file=f'static/tickets/{username}.png')       
         # Insert new user into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO history (hash,start,destination,userid,time) VALUES (?,?,?,?,?)', (ticket.id,ticket.start_location,ticket.destination,session["id"],ticket.creation_time))
        conn.commit()
        return redirect("/generate_ticket")
    return render_template('home.html', username=session['username'])

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            return render_template('register.html', error='Username already exists')
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        return redirect('/')
    
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user from the database
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user and check_password_hash( user['password'], password):
            session['username'] = username
            session['id'] = user["id"]
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect('/login')

# Generate ticket route
@app.route('/generate_ticket')
@login_required
def generate_ticket():
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE userid = ?', (session['id'],))
    data = cursor.fetchone()
    if not data:
        return render_template("no_display.html")
    t=Ticket(data['hash'],data['time'],data['start'],data['destination'],f'static/tickets/{session["username"]}.png')    
    return render_template('tickets.html', username=username,start=t.start_location,destination=t.destination,time_remaining=t.valid_upto())
@app.route('/myrfid')
@login_required
def rfid():
    return render_template('myrfid.html')
if __name__ == '__main__':
    app.run(debug=True)