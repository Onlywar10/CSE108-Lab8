from app import db, User, Class, Enrollment, app

with app.app_context():
    # Add teachers
    teacher1 = User(username="dr_hepworth", role="teacher")
    teacher1.set_password("password123")
    teacher2 = User(username="ms_walker", role="teacher")
    teacher2.set_password("password456")

    # Add students
    student1 = User(username="john_smith", role="student")
    student1.set_password("password789")
    student2 = User(username="jane_doe", role="student")
    student2.set_password("password321")
    student3 = User(username="mike_jones", role="student")
    student3.set_password("password654")

    # Commit users
    db.session.add_all([teacher1, teacher2, student1, student2, student3])
    db.session.commit()

    # Add classes
    class1 = Class(name="CS 101", teacher_id=teacher1.id, time="MWF 10:00-10:50 AM", capacity=20)
    class2 = Class(name="Physics 121", teacher_id=teacher2.id, time="TR 11:00-11:50 AM", capacity=15)

    # Commit classes
    db.session.add_all([class1, class2])
    db.session.commit()

    # Add enrollments
    enrollment1 = Enrollment(student_id=student1.id, class_id=class1.id, grade=85)
    enrollment2 = Enrollment(student_id=student2.id, class_id=class1.id, grade=92)
    enrollment3 = Enrollment(student_id=student3.id, class_id=class2.id, grade=88)
    enrollment4 = Enrollment(student_id=student2.id, class_id=class2.id, grade=91)

    # Commit enrollments
    db.session.add_all([enrollment1, enrollment2, enrollment3, enrollment4])
    db.session.commit()

    print("Dummy data inserted successfully!")
