from app import app
from models import db

# Run once to create database tables
with app.app_context():
    db.create_all()
    print("Database created / updated")
