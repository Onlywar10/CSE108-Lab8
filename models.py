from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'auth'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)  # Store plaintext password here
    role = db.Column(db.String, nullable=False)  # 'student', 'teacher', 'admin'


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('auth.id'), nullable=False)
    time = db.Column(db.String, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    teacher = db.relationship('User', backref='classes', lazy=True)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('auth.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=True)

    student = db.relationship('User', backref='enrollments', lazy=True)
    class_ = db.relationship('Class', backref='enrollments', lazy=True)
