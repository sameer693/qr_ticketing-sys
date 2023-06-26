from flask import Flask, render_template, request, redirect, session
import sqlite3
import qrcode
from helpers import login_required
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


# Home page
@app.route('/')
@login_required
def home():
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

        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()

        session['username'] = username

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

        if user and user['password'] == password:
            session['username'] = username
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

    # Generate QR code for the ticket
    ticket_data = f'Ticket for {username}'
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(ticket_data)
    qr.make(fit=True)
    qr_image = qr.make_image(fill='black', back_color='white')

    # Save the QR code image
    qr_image.save(f'static/tickets/{username}.png')

    return render_template('ticket.html', username=username)

if __name__ == '__main__':
    app.run(debug=True)