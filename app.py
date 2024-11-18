from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Class, Enrollment
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


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
    # Clear all session data to log the user out
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Login attempt with username: {username}")  # Debug

        # Fetch the user from the database
        user = User.query.filter_by(username=username).first()

        # Validate user credentials
        if user and user.check_password(password):
            # Store the user's ID, role, and username in the session
            session['id'] = user.id
            session['role'] = user.role
            session['username'] = user.username
            print(f"Session set for user: {session}")  # Debug: Log session

            flash(f'Welcome, {user.username}!', 'success')
            return redirect(url_for('dashboard', role=user.role))

        # Handle invalid credentials
        print("Invalid credentials provided.")  # Debug
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/dashboard/<role>')
def dashboard(role):
    print(f"Dashboard route accessed with role: {role}")  # Debug print

    # Check if the role is "teacher"
    if role == "teacher":
        print("Teacher dashboard requested.")  # Debug print

        # Fetch the teacher's ID from the session
        teacher_name = session.get('username')  # Corrected key
        print(f"Teacher Name from session: {teacher_name}")  # Debug print
        teacher_id = session.get('id')  # Corrected key
        print(f"Teacher ID from session: {teacher_id}")  # Debug print

        if not teacher_id:
            print("Unauthorized access: No id in session.")  # Debug print
            flash("Unauthorized access! Please log in.", "danger")
            return redirect(url_for("login"))

        # Fetch classes taught by the teacher
        classes = Class.query.filter_by(teacher_id=teacher_id).all()
        print(f"Classes found: {len(classes)}")  # Debug print

        # Add enrollment information for each class
        class_info = []
        for class_ in classes:
            enrolled_students = Enrollment.query.filter_by(
                class_id=class_.id).count()
            # Debug print
            print(f"Class ID: {class_.id}, Enrolled: {enrolled_students}")

            class_info.append({
                'id': class_.id,
                'name': class_.name,
                # Get teacher's name
                'teacher': User.query.get(teacher_id).username,
                'time': class_.time,
                'capacity': class_.capacity,
                'enrolled': enrolled_students
            })

        print(f"Final class info: {class_info}")  # Debug print

        # Render the teacher dashboard template
        return render_template('teacherDashboard.html', classes=class_info)
    # Handle other roles here (e.g., student, admin)

    # Check if the role is "student"
    if role == "student":
        print("Student Dashboard requested.")

        # Fetch the students's ID from the session
        student_name = session.get('username')  # Corrected key
        print(f"Student Name from session: {student_name}")  # Debug print
        student_id = session.get('id')  # Corrected key
        print(f"Student ID from session: {student_id}")  # Debug print

        # Fetch data on all available classes
        result = Class.query.all()

        # All classes list
        classes = []
        for class_ in result:
            # Getting the teacher's name for the course
            teacherName = User.query.filter_by(id=class_.teacher_id).first()

            # Check to see if student is already enrolled in the course
            enrollmentCheck = Enrollment.query.filter_by(
                student_id=student_id)

            enrolled = "+"
            for enrollment in enrollmentCheck:
                if (class_.id == enrollment.class_id):
                    print("Student is enrolled in", class_.name)
                    enrolled = "-"
                else:
                    print("Student is not enrolled in", class_.name)

            # Updating the capacity
            # First get the count of students already enrolled in the class
            studentsEnrolled = Enrollment.query.filter_by(
                class_id=class_.id).count()
            availableCapacity = str(studentsEnrolled) + \
                "/" + str(class_.capacity)

            # Class data dictionary to send to front end
            classData = {"id": class_.id, "name": class_.name,
                         "teacher_id": teacherName.username, "time": class_.time, "capacity": availableCapacity, "enrolled": enrolled}

            classes.append(classData)

        # Fetching all classes that current student is enrolled in
        enrollmentCheck = Enrollment.query.filter_by(
            student_id=student_id)
        enrolledList = []

        for class_ in enrollmentCheck:
            # Get the class data from the class id
            classData = Class.query.filter_by(id=class_.class_id).first()

            # Getting the teacher's name for the course
            teacherName = User.query.filter_by(id=classData.teacher_id).first()

            # Updating the capacity
            # First get the count of students already enrolled in the class
            studentsEnrolled = Enrollment.query.filter_by(
                class_id=classData.id).count()
            availableCapacity = str(studentsEnrolled) + \
                "/" + str(classData.capacity)

            enrollmentData = {"id": classData.id, "name": classData.name,
                              "teacher_id": teacherName.username, "time": classData.time, "capacity": availableCapacity}
            enrolledList.append(enrollmentData)

        return render_template('studentDashboard.html', classes=classes, enrolledList=enrolledList)
    else:
        return render_template('dashboard.html', role=role)


@ app.route("/enroll", methods=["POST"])
def enroll():
    data = request.get_json()
    print(data["enrolled"])

    if (data["enrolled"] == "+"):
        newEnrollment = Enrollment(
            student_id=session.get('id'), class_id=data["id"], grade=0)
        db.session.add(newEnrollment)
        db.session.commit()
        print("Added class")
        return "Enrolled successfully!"
    else:
        enrollment = Enrollment.query.filter_by(
            student_id=session.get("id"), class_id=data["id"]).first()

        db.session.delete(enrollment)
        db.session.commit()
        print("Remove class button pressed")
        return "Removed classes successfully!"


@ app.route('/class/<int:class_id>', methods=['GET'])
def view_class(class_id):
    # Fetch class and associated details for the GET request
    class_ = Class.query.get_or_404(class_id)
    teacher = User.query.get_or_404(class_.teacher_id)

    # Fetch all enrollments for the class
    enrollments = Enrollment.query.filter_by(class_id=class_.id).all()

    # Fetch student details for each enrollment
    students = [
        {
            'id': enrollment.student_id,
            'name': User.query.get(enrollment.student_id).username,
            'grade': enrollment.grade
        }
        for enrollment in enrollments
    ]

    # Render the class detail template
    return render_template('class_detail.html', class_=class_, teacher=teacher, students=students)


@ app.route('/class/<int:class_id>/update_grade', methods=['POST'])
def update_grade(class_id):
    # Parse JSON data from the request
    data = request.get_json()
    student_id = data.get('student_id')
    new_grade = data.get('new_grade')

    # Find the enrollment record and update the grade
    enrollment = Enrollment.query.filter_by(
        class_id=class_id, student_id=student_id).first()
    if enrollment:
        enrollment.grade = new_grade
        db.session.commit()
        return {'message': 'Grade updated successfully'}, 200
    else:
        return {'message': 'Enrollment not found'}, 404

    # Render the class detail template
    return render_template('class_detail.html', class_=class_, teacher=teacher, students=students)


if __name__ == '__main__':
    app.run(debug=True)
