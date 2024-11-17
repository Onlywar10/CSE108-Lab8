from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'auth'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'student', 'teacher', 'admin'

    def set_password(self, password):
        """Hashes and sets the password."""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifies the password against the hash."""
        return bcrypt.check_password_hash(self.password_hash, password)


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    teacher_id = db.Column(db.Integer, db.ForeignKey('auth.id'))  # Fixed foreign key
    time = db.Column(db.String)
    capacity = db.Column(db.Integer)

    # Set the relationship between the Teac her and the Class
    teacher = db.relationship('User', backref='classes', lazy=True)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('auth.id'), nullable=False)  # Fixed foreign key
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    grade = db.Column(db.Integer, nullable=True)

    student = db.relationship('User', backref='enrollments', lazy=True)
    class_ = db.relationship('Class', backref='enrollments', lazy=True)
