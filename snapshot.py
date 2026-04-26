import pandas as pd
import yfinance as yf
import requests
from datetime import datetime

REAL_ESTATE_CURRENT = 1_340_000_000

REAL_ESTATE_DEBT = 750_000_000
STOCK_DEBT = 34_000_000
CRYPTO_DEBT = 14_000_000

CASH = 15_000_000
OTHER = 0

stocks = [
    {"ticker": "JEPQ", "qty": 115},
    {"ticker": "QQQI", "qty": 80},
    {"ticker": "MSFT", "qty": 10},
    {"ticker": "ORCL", "qty": 15},
    {"ticker": "NFLX", "qty": 15},
]

coins = [
    {"ticker": "KRW-NEAR", "qty": 3010},
    {"ticker": "KRW-AVAX", "qty": 400},
    {"ticker": "KRW-APT", "qty": 2030},
]

def get_fx():
    try:
        return float(yf.Ticker("KRW=X").history(period="1d")["Close"].iloc[-1])
    except:
        return 1400

def get_stock_price(ticker):
    try:
        return float(yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1])
    except:
        return 0

def get_coin_price(ticker):
    try:
        url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
        data = requests.get(url).json()
        return float(data[0]["trade_price"])
    except:
        return 0

fx = get_fx()

stock_total = 0
for s in stocks:
    stock_total += get_stock_price(s["ticker"]) * fx * s["qty"]

crypto_total = 0
for c in coins:
    crypto_total += get_coin_price(c["ticker"]) * c["qty"]

debt = REAL_ESTATE_DEBT + STOCK_DEBT + CRYPTO_DEBT

new_row = {
    "date": datetime.now().strftime("%Y-%m"),
    "realestate": round(REAL_ESTATE_CURRENT),
    "stock": round(stock_total),
    "crypto": round(crypto_total),
    "cash": round(CASH),
    "other": round(OTHER),
    "debt": round(debt)
}

try:
    history = pd.read_csv("asset_history.csv")
except:
    history = pd.DataFrame(columns=["date", "realestate", "stock", "crypto", "cash", "other", "debt"])

history = history[history["date"] != new_row["date"]]
history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
history.to_csv("asset_history.csv", index=False, encoding="utf-8-sig")

print("Snapshot saved:", new_row)
