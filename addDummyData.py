from app import db, User, app  
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# Create the admin user
admin_user = User(
    username='admin',
    password_hash=bcrypt.generate_password_hash('Admin@123').decode('utf-8'),
    role='admin'
)

# Add and commit the user to the database
with app.app_context():
    db.session.add(admin_user)
    db.session.commit()

print("Admin user created successfully!")
