from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        # Add user to database
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('dashboard', role=user.role))

        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard/<role>')
def dashboard(role):
    return render_template('dashboard.html', role=role)

if __name__ == '__main__':
    app.run(debug=True)
