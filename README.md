# 📈 AI Stock Market Simulator

> **Live Demo:** [ai-stock-trading-simulator.vercel.app](https://ai-stock-trading-simulator.vercel.app)

An AI-powered stock market simulator built with **Flask**, **Python**, **SQLAlchemy**, and **Machine Learning**. Register, log in, buy/sell stocks with real-time data, and track your portfolio with AI-driven price predictions.

---

## 🚀 Features

- 🔑 **User Authentication** — Register & Login with Flask-Login + bcrypt
- 💰 **Buy & Sell Stocks** — Trade with real-time price data via yfinance
- 📊 **Portfolio Dashboard** — Live P/L, ROI, and equity tracking
- 🤖 **AI Prediction** — 7-day stock price forecasting using Linear Regression
- 📈 **Interactive Charts** — ApexCharts-powered visualizations with trendlines
- 🗄️ **Database** — SQLite (local) / PostgreSQL (production)
- 🌐 **Deployed** — Hosted on Vercel with serverless Python

---

## 🛠️ Tech Stack

| Layer          | Technology                              |
|----------------|----------------------------------------|
| Backend        | Flask, Python 3.12                     |
| Database       | SQLite / PostgreSQL + SQLAlchemy ORM   |
| Auth           | Flask-Login, Flask-Bcrypt              |
| Frontend       | HTML, CSS, Bootstrap 5, ApexCharts     |
| AI/ML          | scikit-learn, pandas, numpy            |
| Stock Data     | yfinance API                           |
| Deployment     | Vercel (Serverless Python)             |

---

## ⚡ Quick Start

```bash
# Clone the repo
git clone https://github.com/Deepnarayan70/ai-stock-trading-simulator.git
cd ai-stock-trading-simulator

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux


# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 📂 Project Structure

```
├── app.py              # Main Flask application & routes
├── models.py           # SQLAlchemy database models
├── requirements.txt    # Python dependencies
├── vercel.json         # Vercel deployment config
├── static/
│   └── style.css       # Custom CSS styling
└── templates/
    ├── base.html       # Base layout template
    ├── index.html      # Landing page
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── dashboard.html  # Trading dashboard
    ├── portfolio.html  # Portfolio with AI charts
    ├── buy.html        # Buy stocks form
    ├── sell.html       # Sell stocks form
    └── transactions.html # Transaction history
```

---

## 📄 License

This project is for **educational purposes only**. Not financial advice.

Built with ❤️ by [Deep Narayan](https://github.com/Deepnarayan70)
