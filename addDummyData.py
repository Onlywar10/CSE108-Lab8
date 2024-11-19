from app import app, db
from models import User, Class, Enrollment

def reset_and_seed_database():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # Add admin
        admin = User(username="admin", password="password123", role="admin")
        db.session.add(admin)
        db.session.commit()

        # Add teachers
        teachers = {
            "Ralph Jenkins": User(username="rjenkins", password="password123", role="teacher"),
            "Susan Walker": User(username="swalker", password="password123", role="teacher"),
            "Ammon Hepworth": User(username="ahepworth", password="password123", role="teacher"),
        }

        db.session.add_all(teachers.values())
        db.session.commit()

        # Add students
        students = {
            "Jose Santos": User(username="jsantos", password="password123", role="student"),
            "Betty Brown": User(username="bbrown", password="password123", role="student"),
            "John Stuart": User(username="jstuart", password="password123", role="student"),
            "Li Cheng": User(username="lcheng", password="password123", role="student"),
            "Nancy Little": User(username="nlittle", password="password123", role="student"),
            "Mindy Norris": User(username="mnorris", password="password123", role="student"),
            "Aditya Ranganath": User(username="aranganath", password="password123", role="student"),
            "Yi Wen Chen": User(username="ywchen", password="password123", role="student"),
        }

        db.session.add_all(students.values())
        db.session.commit()

        # Add classes
        classes = {
            "Math 101": Class(name="Math 101", teacher_id=teachers["Ralph Jenkins"].id, time="MWF 10:00-10:50 AM", capacity=8),
            "Physics 121": Class(name="Physics 121", teacher_id=teachers["Susan Walker"].id, time="TR 11:00-11:50 AM", capacity=10),
            "CS 106": Class(name="CS 106", teacher_id=teachers["Ammon Hepworth"].id, time="MWF 2:00-2:50 PM", capacity=10),
            "CS 162": Class(name="CS 162", teacher_id=teachers["Ammon Hepworth"].id, time="TR 3:00-3:50 PM", capacity=4),
        }

        db.session.add_all(classes.values())
        db.session.commit()

        # Add enrollments
        enrollments = [
            {"student": "Jose Santos", "class": "Math 101", "grade": 92},
            {"student": "Betty Brown", "class": "Math 101", "grade": 65},
            {"student": "John Stuart", "class": "Math 101", "grade": 86},
            {"student": "Li Cheng", "class": "Math 101", "grade": 77},
            {"student": "Nancy Little", "class": "Physics 121", "grade": 53},
            {"student": "Li Cheng", "class": "Physics 121", "grade": 85},
            {"student": "Mindy Norris", "class": "Physics 121", "grade": 94},
            {"student": "John Stuart", "class": "Physics 121", "grade": 91},
            {"student": "Betty Brown", "class": "Physics 121", "grade": 88},
            {"student": "Aditya Ranganath", "class": "CS 106", "grade": 93},
            {"student": "Yi Wen Chen", "class": "CS 106", "grade": 85},
            {"student": "Nancy Little", "class": "CS 106", "grade": 57},
            {"student": "Mindy Norris", "class": "CS 106", "grade": 68},
            {"student": "Aditya Ranganath", "class": "CS 162", "grade": 99},
            {"student": "Nancy Little", "class": "CS 162", "grade": 87},
            {"student": "Yi Wen Chen", "class": "CS 162", "grade": 92},
            {"student": "John Stuart", "class": "CS 162", "grade": 67},
        ]

        for enrollment_data in enrollments:
            enrollment = Enrollment(
                student_id=students[enrollment_data["student"]].id,
                class_id=classes[enrollment_data["class"]].id,
                grade=enrollment_data["grade"],
            )
            db.session.add(enrollment)

        db.session.commit()
        print("Database reset and seeded successfully with an admin account.")

if __name__ == "__main__":
    reset_and_seed_database()
