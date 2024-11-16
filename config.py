import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Use SQLite for simplicity
    SQLALCHEMY_TRACK_MODIFICATIONS = False
