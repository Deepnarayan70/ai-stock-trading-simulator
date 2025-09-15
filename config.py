import os

class Config:
    # Use PostgreSQL instead of SQLite
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:@Deep6375@localhost:5432/stock_sim"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
