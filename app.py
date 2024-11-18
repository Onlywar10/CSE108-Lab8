from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Class, Enrollment
from config import Config

# Initialize app, database, bcrypt
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
bcrypt = Bcrypt(app)

# --- Flask-Admin Setup ---
# Custom ModelView for admin access control
class AdminModelView(ModelView):
    def is_accessible(self):
        # Only allow access to admin users
        return session.get('role') == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access the admin page.", "danger")
        return redirect(url_for('login'))


# Custom Enrollment View for Admin
class EnrollmentAdminView(AdminModelView):
    column_list = ['id', 'student_name', 'class_name', 'grade']
    column_labels = {
        'id': 'Enrollment ID',
        'student_name': 'Student Name',
        'class_name': 'Class Name',
        'grade': 'Grade'
    }

    # Custom columns for student and class names
    def _student_name_formatter(view, context, model, name):
        return model.student.username if model.student else "Unknown"

    def _class_name_formatter(view, context, model, name):
        return model.class_.name if model.class_ else "Unknown"

    column_formatters = {
        'student_name': _student_name_formatter,
        'class_name': _class_name_formatter
    }

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Class, db.session))
admin.add_view(EnrollmentAdminView(Enrollment, db.session))

# --- Flask Routes (Keep Your Existing Routes) ---
@app.route('/')
def home():
    return render_template('base.html')

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

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['id'] = user.id
            session['role'] = user.role
            session['username'] = user.username

            flash(f'Welcome, {user.username}!', 'success')
            if user.role == 'admin':
                return redirect('/admin')
            return redirect(url_for('dashboard', role=user.role))

        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/dashboard/<role>')
def dashboard(role):
    # Handle different roles (Teacher, Student)
    if role == 'teacher':
        teacher_id = session.get('id')
        if not teacher_id:
            flash("Unauthorized access! Please log in.", "danger")
            return redirect(url_for("login"))

        classes = Class.query.filter_by(teacher_id=teacher_id).all()
        class_info = [
            {
                'id': class_.id,
                'name': class_.name,
                'teacher': User.query.get(teacher_id).username,
                'time': class_.time,
                'capacity': class_.capacity,
                'enrolled': Enrollment.query.filter_by(class_id=class_.id).count()
            }
            for class_ in classes
        ]

        return render_template('teacherDashboard.html', classes=class_info)

    return render_template('dashboard.html', role=role)

@app.route('/class/<int:class_id>', methods=['GET'])
def view_class(class_id):
    class_ = Class.query.get_or_404(class_id)
    teacher = User.query.get_or_404(class_.teacher_id)
    enrollments = Enrollment.query.filter_by(class_id=class_.id).all()

    students = [
        {
            'id': enrollment.student_id,
            'name': User.query.get(enrollment.student_id).username,
            'grade': enrollment.grade
        }
        for enrollment in enrollments
    ]

    return render_template('class_detail.html', class_=class_, teacher=teacher, students=students)

@app.route('/class/<int:class_id>/update_grade', methods=['POST'])
def update_grade(class_id):
    data = request.get_json()
    student_id = data.get('student_id')
    new_grade = data.get('new_grade')

    enrollment = Enrollment.query.filter_by(class_id=class_id, student_id=student_id).first()
    if enrollment:
        enrollment.grade = new_grade
        db.session.commit()
        return {'message': 'Grade updated successfully'}, 200
    else:
        return {'message': 'Enrollment not found'}, 404

if __name__ == '__main__':
    app.run(debug=True)
