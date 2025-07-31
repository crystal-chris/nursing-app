from flask import Flask, request, redirect, url_for, render_template_string, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    name TEXT,
                    email TEXT,
                    password TEXT,
                    contact TEXT,
                    sex TEXT,
                    location TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template_string('''
        <h1>Welcome to Nursing App</h1>
        <a href="{{ url_for('register', role='patient') }}">Register as Patient</a><br>
        <a href="{{ url_for('register', role='nurse') }}">Register as Nurse</a><br><br>
        <a href="{{ url_for('login') }}">Login</a>
    ''')

# ---------------- REGISTER PAGE ----------------
@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        contact = request.form['contact']
        sex = request.form['sex']
        location = request.form['location']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (role, name, email, password, contact, sex, location) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (role, name, email, password, contact, sex, location))
        conn.commit()
        conn.close()

        return render_template_string('''
            <h2>Registration Successful!</h2>
            <p>Name: {{ name }}</p>
            <p>Email: {{ email }}</p>
            <p>Contact: {{ contact }}</p>
            <p>Sex: {{ sex }}</p>
            <p>Location: {{ location }}</p>
            <a href="{{ url_for('login') }}">Go to Login</a>
        ''', name=name, email=email, contact=contact, sex=sex, location=location)

    return render_template_string('''
        <h2>Register as {{ role.title() }}</h2>
        <form method="POST">
            Full Name: <input type="text" name="name" required><br>
            Email: <input type="email" name="email" required><br>
            Password: <input type="password" name="password" required><br>
            Contact: <input type="text" name="contact"><br>
            Sex: <select name="sex">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                </select><br>
            Location: <input type="text" name="location"><br>
            <button type="submit">Register</button>
        </form>
    ''', role=role)

# ---------------- LOGIN PAGE ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[0]  # user[0] is ID
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template_string('''
        <h2>Login</h2>
        <form method="POST">
            Email: <input type="email" name="email" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Login</button>
        </form>
        <p style="color:red;">{{ error }}</p>
    ''', error=error)

# ---------------- DASHBOARD PAGE ----------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT name, email, role, contact, sex, location FROM users")
    users = c.fetchall()
    conn.close()

    return render_template_string('''
        <h2>Dashboard - All Registered Users</h2>
        <table border="1">
            <tr>
                <th>Name</th><th>Email</th><th>Role</th><th>Contact</th><th>Sex</th><th>Location</th>
            </tr>
            {% for user in users %}
            <tr>
                <td>{{ user[0] }}</td><td>{{ user[1] }}</td><td>{{ user[2] }}</td>
                <td>{{ user[3] }}</td><td>{{ user[4] }}</td><td>{{ user[5] }}</td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="{{ url_for('logout') }}">Logout</a>
    ''', users=users)

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)
