import os
from datetime import datetime, timedelta

from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from models import db, User, Investment, Transaction
from flask_migrate import Migrate

# ---------------- App Setup ----------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "change_this_secret_in_production")

# ✅ Use PostgreSQL, fallback to SQLite only if DATABASE_URL not set
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:mypassword123@localhost:5432/stock_sim"
)
# ✅ Make sure SQLAlchemy uses the public schema
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"options": "-c search_path=public"}}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

os.makedirs('static/charts', exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- Helpers ----------------
def fetch_current_price(symbol):
    """Return latest close price, or None if invalid ticker."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if hist.empty:
            return None
        return float(hist['Close'].iloc[-1])
    except Exception:
        return None

def make_prediction_and_chart(symbol):
    """Generate 7-day forecast using Linear Regression and save chart."""
    try:
        data = yf.download(symbol, period='180d', progress=False)
        if data.empty:
            return None, None

        close = data['Close'].dropna()
        series = close[-60:] if len(close) >= 60 else close
        X = np.arange(len(series)).reshape(-1, 1)
        y = series.values.reshape(-1, 1)

        model = LinearRegression()
        model.fit(X, y)
        future_idx = np.arange(len(series), len(series) + 7).reshape(-1, 1)
        preds = model.predict(future_idx).flatten()

        hist_plot = close[-120:] if len(close) >= 120 else close
        plt.figure(figsize=(10, 5))
        plt.plot(hist_plot.index, hist_plot.values, label='Historical Close', linewidth=2)
        pred_dates = [hist_plot.index[-1] + timedelta(days=i+1) for i in range(7)]
        plt.plot(pred_dates, preds, marker='o', linestyle='--', label='7-day Prediction')
        plt.title(f'{symbol} — Historical + 7-day Prediction')
        plt.xlabel('Date')
        plt.ylabel('Price (USD)')
        plt.legend()
        plt.grid(alpha=0.3)

        chart_filename = f'static/charts/{symbol}_chart.png'
        plt.tight_layout()
        plt.savefig(chart_filename)
        plt.close()

        return chart_filename, [round(p, 2) for p in preds]
    except Exception as e:
        print("Prediction error:", e)
        return None, None

# ---------------- Routes ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Enter username and password', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('register'))

        pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password_hash=pw_hash, balance=100000.0)
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', balance=round(current_user.balance, 2))

@app.route('/buy', methods=['GET', 'POST'])
@login_required
def buy():
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').upper().strip()
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Enter a positive amount', 'warning')
            return redirect(url_for('dashboard'))

        price = fetch_current_price(symbol)
        if price is None:
            flash('Ticker not found or no price available', 'danger')
            return redirect(url_for('dashboard'))

        if amount > current_user.balance:
            flash('Insufficient balance', 'danger')
            return redirect(url_for('dashboard'))

        shares = amount / price
        inv = Investment(user_id=current_user.id, symbol=symbol, shares=shares, buy_price=price, buy_date=datetime.utcnow())
        db.session.add(inv)
        tx = Transaction(user_id=current_user.id, symbol=symbol, shares=shares, price=price, type='BUY', date=datetime.utcnow())
        db.session.add(tx)
        current_user.balance -= amount
        db.session.commit()
        flash(f'Bought {shares:.4f} shares of {symbol} at ${price:.2f}', 'success')
        return redirect(url_for('portfolio'))
    return render_template('buy.html')

@app.route('/sell', methods=['GET', 'POST'])
@login_required
def sell():
    if request.method == 'POST':
        symbol = request.form.get('symbol', '').upper().strip()
        shares_to_sell = float(request.form.get('shares', 0))
        if shares_to_sell <= 0:
            flash('Enter positive shares to sell', 'warning')
            return redirect(url_for('portfolio'))

        holdings = Investment.query.filter_by(user_id=current_user.id, symbol=symbol).order_by(Investment.buy_date).all()
        total_shares = sum(i.shares for i in holdings)
        if shares_to_sell > total_shares:
            flash('Not enough shares to sell', 'danger')
            return redirect(url_for('portfolio'))

        price = fetch_current_price(symbol)
        if price is None:
            flash('Ticker not found or no price available', 'danger')
            return redirect(url_for('portfolio'))

        remaining = shares_to_sell
        for inv in holdings:
            if remaining <= 0:
                break
            if inv.shares <= remaining + 1e-9:
                remaining -= inv.shares
                db.session.delete(inv)
            else:
                inv.shares -= remaining
                remaining = 0.0

        proceeds = shares_to_sell * price
        tx = Transaction(user_id=current_user.id, symbol=symbol, shares=shares_to_sell, price=price, type='SELL', date=datetime.utcnow())
        db.session.add(tx)
        current_user.balance += proceeds
        db.session.commit()
        flash(f'Sold {shares_to_sell:.4f} shares of {symbol} at ${price:.2f}', 'success')
        return redirect(url_for('portfolio'))
    return render_template('sell.html')

@app.route('/portfolio')
@login_required
def portfolio():
    holdings_db = Investment.query.filter_by(user_id=current_user.id).all()
    portfolio, display, charts = {}, {}, {}
    total_cost, total_current = 0.0, 0.0

    for inv in holdings_db:
        sym = inv.symbol
        portfolio.setdefault(sym, {'shares': 0.0, 'cost': 0.0})
        portfolio[sym]['shares'] += inv.shares
        portfolio[sym]['cost'] += inv.shares * inv.buy_price
        total_cost += inv.shares * inv.buy_price

    for sym, data in portfolio.items():
        live = fetch_current_price(sym) or 0.0
        value = data['shares'] * live
        pnl = value - data['cost']
        roi = (pnl / data['cost'] * 100) if data['cost'] else 0.0
        display[sym] = {
            'shares': round(data['shares'], 6),
            'buy_cost': round(data['cost'], 2),
            'live_price': round(live, 2),
            'value': round(value, 2),
            'pnl': round(pnl, 2),
            'roi': round(roi, 2)
        }
        chart_path, preds = make_prediction_and_chart(sym)
        charts[sym] = {'chart': chart_path, 'predictions': preds}
        total_current += value

    return render_template('portfolio.html',
                           investments=display,
                           charts=charts,
                           balance=round(current_user.balance, 2),
                           total_cost=round(total_cost, 2),
                           total_current=round(total_current, 2),
                           total_pnl=round(total_current - total_cost, 2))

@app.route('/transactions')
@login_required
def transactions():
    txs = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=txs)

@app.route('/charts/<path:filename>')
def charts(filename):
    return send_from_directory('static/charts', filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
