from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2

app = Flask(__name__)
app.secret_key = '1234' # Needed for user login sessions

# --- Database Connection Helper ---
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="tourismdb",
        user="postgres",
        password="root" 
    )
    return conn

# --- Routes ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form.get('phone', '') # Only used during registration

        conn = get_db_connection()
        cur = conn.cursor()

        if 'register' in request.form:
            # Register new user
            try:
                cur.execute("INSERT INTO users (username, password, phone) VALUES (%s, %s, %s)", 
                            (username, password, phone))
                conn.commit()
            except psycopg2.IntegrityError:
                conn.rollback()
                return "Username already exists. Go back and try another."
        else:
            # Login existing user
            cur.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            if user:
                session['user_id'] = user[0]
                session['username'] = username
                conn.close()
                return redirect(url_for('book'))
            else:
                return "Invalid credentials."

        conn.close()
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        package_id = int(request.form['package_id'])
        travel_date = request.form['travel_date']
        travel_time = request.form['travel_time']
        people = int(request.form['people'])
        
        # Recalculate cost on server to prevent frontend tampering
        cur.execute("SELECT price_per_person FROM packages WHERE id = %s", (package_id,))
        price = cur.fetchone()[0]
        total_cost = price * people

        # Save booking to Postgres
        cur.execute("""
            INSERT INTO bookings (user_id, package_id, travel_date, travel_time, num_people, total_cost) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], package_id, travel_date, travel_time, people, total_cost))
        conn.commit()
        conn.close()
        
        return redirect(url_for('success'))

    # GET request: Load packages for the interactive UI
    cur.execute("SELECT id, name, price_per_person, image_url FROM packages")
    packages = cur.fetchall()
    conn.close()
    
    return render_template('book.html', packages=packages, username=session['username'])

@app.route('/success')
def success():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('success.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
