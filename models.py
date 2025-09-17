from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    balance = db.Column(db.Float, default=100000.0)  # fake starting balance

    def __repr__(self):
        return f"<User {self.username}>"

class Investment(db.Model):
    __tablename__ = 'investment'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    buy_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Investment {self.symbol} shares={self.shares}>"

class Transaction(db.Model):
    __tablename__ = 'transaction'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # BUY or SELL
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Transaction {self.type} {self.symbol} {self.shares}>"
