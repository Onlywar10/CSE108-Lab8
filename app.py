from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from models import db, User, Class, Enrollment
from config import Config
from wtforms.fields import StringField
from wtforms.fields import SelectField

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# --- Flask-Admin Setup ---
class AdminModelView(ModelView):
    def is_accessible(self):
        # Only allow access to admin users
        return session.get('role') == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have permission to access the admin page.", "danger")
        return redirect(url_for('login'))
class ClassAdminView(ModelView):
    def delete_model(self, model):
        # Delete related enrollments first
        Enrollment.query.filter_by(class_id=model.id).delete()
        db.session.commit()
        # Then delete the class
        super().delete_model(model)

class UserAdminView(ModelView):
    column_list = ['id', 'username', 'role', 'password']

    def on_model_delete(self, model):
        """
        Custom behavior before deleting a User.
        Remove or reassign classes if the user is a teacher.
        """
        if model.role == 'teacher':
            # Delete or reassign all classes taught by this teacher
            classes = Class.query.filter_by(teacher_id=model.id).all()
            for class_ in classes:
                db.session.delete(class_)
            db.session.commit()

        super().on_model_delete(model)

from wtforms.fields import SelectField

class EnrollmentAdminView(ModelView):
    # Specify the columns to display in the list view
    column_list = ['id', 'student_id', 'class_id', 'grade']
    column_labels = {
        'id': 'Enrollment ID',
        'student_id': 'Student Name',
        'class_id': 'Class Name',
        'grade': 'Grade'
    }

    # Override the form fields for student_id and class_id
    form_overrides = {
        'student_id': SelectField,
        'class_id': SelectField
    }

    # Arguments for form fields
    form_args = {
        'student_id': {
            'label': 'Student Name',
            'choices': lambda: [(s.id, s.username) for s in User.query.filter_by(role='student').all()]
        },
        'class_id': {
            'label': 'Class Name',
            'choices': lambda: [(c.id, c.name) for c in Class.query.all()]
        }
    }

    # Optional: Formatters for displaying student and class names in the table
    def _student_name_formatter(view, context, model, name):
        return model.student.username if model.student else "Unknown"

    def _class_name_formatter(view, context, model, name):
        return model.class_.name if model.class_ else "Unknown"

    column_formatters = {
        'student_id': _student_name_formatter,
        'class_id': _class_name_formatter
    }

admin = Admin(app, name='Admin Panel', template_mode='bootstrap4')
admin.add_view(UserAdminView(User, db.session))
admin.add_view(ClassAdminView(Class, db.session))
admin.add_view(EnrollmentAdminView(Enrollment, db.session))



# --- Flask Routes ---
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
        new_user = User(username=username, role=role, password=password)
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

        user = User.query.filter_by(username=username, password=password).first()

        if user:
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

    if role == 'student':
        student_id = session.get('id')
        if not student_id:
            flash("Unauthorized access! Please log in.", "danger")
            return redirect(url_for("login"))

        # Fetch all available classes
        result = Class.query.all()
        classes = [
            {
                'id': class_.id,
                'name': class_.name,
                'teacher': User.query.get(class_.teacher_id).username,
                'time': class_.time,
                'capacity': f"{Enrollment.query.filter_by(class_id=class_.id).count()}/{class_.capacity}",
                'enrolled': '+' if not Enrollment.query.filter_by(student_id=student_id, class_id=class_.id).first() else '-'
            }
            for class_ in result
        ]

        enrolled_classes = Enrollment.query.filter_by(student_id=student_id).all()
        enrolled_list = [
            {
                'id': class_.class_id,
                'name': class_.class_.name,
                'teacher': User.query.get(class_.class_.teacher_id).username,
                'time': class_.class_.time,
                'capacity': f"{Enrollment.query.filter_by(class_id=class_.class_id).count()}/{class_.class_.capacity}"
            }
            for class_ in enrolled_classes
        ]

        return render_template('studentDashboard.html', classes=classes, enrolledList=enrolled_list)

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


@app.route('/enroll', methods=['POST'])
def enroll():
    data = request.get_json()

    if data["enrolled"] == "+":
        new_enrollment = Enrollment(student_id=session.get('id'), class_id=data["id"], grade=0)
        db.session.add(new_enrollment)
        db.session.commit()
        return "Enrolled successfully!"
    else:
        enrollment = Enrollment.query.filter_by(student_id=session.get("id"), class_id=data["id"]).first()
        db.session.delete(enrollment)
        db.session.commit()
        return "Removed classes successfully!"


if __name__ == '__main__':
    app.run(debug=True)
