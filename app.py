import streamlit as st
import pandas as pd
import yfinance as yf
import requests

st.set_page_config(page_title="FIRE 대시보드", layout="wide")

st.title("🔥 우리 가족 FIRE 대시보드")
st.caption("총자산 · 부채 · 순자산 · 월별 성장 추이를 한눈에 보는 가족 자산 현황판")

# -----------------------------
# 기본 데이터
# -----------------------------
REAL_ESTATE_PURCHASE = 1_062_000_000
REAL_ESTATE_CURRENT = 1_340_000_000

REAL_ESTATE_DEBT = 750_000_000
STOCK_DEBT = 26_000_000
CRYPTO_DEBT = 14_000_000

CASH = 0
OTHER = 0

stocks = [
    {"name": "JEPQ", "ticker": "JEPQ", "qty": 115, "avg": 84505},
    {"name": "QQQI", "ticker": "QQQI", "qty": 80, "avg": 76525},
    {"name": "Microsoft", "ticker": "MSFT", "qty": 10, "avg": 571587},
    {"name": "Oracle", "ticker": "ORCL", "qty": 15, "avg": 226595},
    {"name": "Netflix", "ticker": "NFLX", "qty": 15, "avg": 137493},
]

coins = [
    {"name": "니어프로토콜", "ticker": "KRW-NEAR", "qty": 3010, "avg": 1775},
    {"name": "아발란체", "ticker": "KRW-AVAX", "qty": 400, "avg": 13409},
    {"name": "앱토스", "ticker": "KRW-APT", "qty": 2030, "avg": 1378},
]

def won(x):
    return f"{x:,.0f}원"

def eok(x):
    return f"{x/100000000:.2f}억"

# -----------------------------
# 현금 / 기타 수기 입력
# -----------------------------
st.subheader("💵 현금 / 기타 자산 입력")

col_cash, col_other = st.columns(2)

with col_cash:
    cash_input = st.number_input(
        "추가 현금 입력",
        min_value=0,
        value=0,
        step=1_000_000
    )

with col_other:
    other_input = st.number_input(
        "기타 자산 입력",
        min_value=0,
        value=0,
        step=1_000_000
    )

CASH = CASH + cash_input
OTHER = OTHER + other_input

st.divider()

# -----------------------------
# 주식 현재가
# -----------------------------
@st.cache_data(ttl=3600)
def get_fx():
    try:
        fx = yf.Ticker("KRW=X").history(period="1d")["Close"].iloc[-1]
        return float(fx)
    except:
        return 1400

@st.cache_data(ttl=3600)
def get_stock_price(ticker):
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        return float(price)
    except:
        return 0

fx = get_fx()

stock_rows = []

for s in stocks:
    usd_price = get_stock_price(s["ticker"])
    price_krw = usd_price * fx
    amount = price_krw * s["qty"]
    principal = s["avg"] * s["qty"]
    profit = amount - principal
    rate = profit / principal * 100 if principal else 0

    stock_rows.append({
        "종목": s["name"],
        "수량": s["qty"],
        "평단": s["avg"],
        "현재가": price_krw,
        "평가금액": amount,
        "평가손익": profit,
        "수익률": rate
    })

stock_df = pd.DataFrame(stock_rows)
stock_total = stock_df["평가금액"].sum()
stock_net = stock_total - STOCK_DEBT

# -----------------------------
# 코인 현재가
# -----------------------------
@st.cache_data(ttl=600)
def get_coin_price(ticker):
    try:
        url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
        data = requests.get(url).json()
        return float(data[0]["trade_price"])
    except:
        return 0

coin_rows = []

for c in coins:
    price = get_coin_price(c["ticker"])
    amount = price * c["qty"]
    principal = c["avg"] * c["qty"]
    profit = amount - principal
    rate = profit / principal * 100 if principal else 0

    coin_rows.append({
        "종목": c["name"],
        "수량": c["qty"],
        "평단": c["avg"],
        "현재가": price,
        "평가금액": amount,
        "평가손익": profit,
        "수익률": rate
    })

coin_df = pd.DataFrame(coin_rows)
crypto_total = coin_df["평가금액"].sum()
crypto_net = crypto_total - CRYPTO_DEBT

# -----------------------------
# 총자산 계산
# -----------------------------
total_asset = REAL_ESTATE_CURRENT + stock_total + crypto_total + CASH + OTHER
debt = REAL_ESTATE_DEBT + STOCK_DEBT + CRYPTO_DEBT
net_asset = total_asset - debt

history = pd.read_csv("asset_history.csv")
history["total_asset"] = history[["realestate", "stock", "crypto", "cash", "other"]].sum(axis=1)
history["net_asset"] = history["total_asset"] - history["debt"]

prev_net = history.iloc[-1]["net_asset"]
mom_change = net_asset - prev_net

# -----------------------------
# 1. 상단 핵심 지표
# -----------------------------
st.subheader("📌 핵심 자산 현황")

col1, col2, col3, col4 = st.columns(4)

col1.metric("총자산", eok(total_asset))
col2.metric("부채", eok(debt))
col3.metric("순자산", eok(net_asset))
col4.metric("전월대비", eok(mom_change))

st.divider()

# -----------------------------
# 2. 자산군별 표
# -----------------------------
st.subheader("📊 자산군별 현황")

asset_table = pd.DataFrame([
    {"자산군": "부동산", "총자산": REAL_ESTATE_CURRENT, "부채": REAL_ESTATE_DEBT, "순자산": REAL_ESTATE_CURRENT - REAL_ESTATE_DEBT},
    {"자산군": "주식", "총자산": stock_total, "부채": STOCK_DEBT, "순자산": stock_net},
    {"자산군": "코인", "총자산": crypto_total, "부채": CRYPTO_DEBT, "순자산": crypto_net},
    {"자산군": "현금", "총자산": CASH, "부채": 0, "순자산": CASH},
    {"자산군": "기타", "총자산": OTHER, "부채": 0, "순자산": OTHER},
    {"자산군": "합계", "총자산": total_asset, "부채": debt, "순자산": net_asset},
])

asset_table["비중"] = asset_table["총자산"] / total_asset * 100

st.dataframe(
    asset_table.assign(
        총자산=asset_table["총자산"].apply(won),
        부채=asset_table["부채"].apply(won),
        순자산=asset_table["순자산"].apply(won),
        비중=asset_table["비중"].apply(lambda x: f"{x:.1f}%")
    ),
    hide_index=True,
    use_container_width=True
)

st.divider()

# -----------------------------
# 3. 성장 추이
# -----------------------------
st.subheader("📈 총자산 성장 추이")
st.line_chart(history.set_index("date")["total_asset"])

st.subheader("📊 자산별 성장 추이")
asset_growth = history.set_index("date")[["realestate", "stock", "crypto", "cash", "other"]]
asset_growth = asset_growth.rename(columns={
    "realestate": "부동산",
    "stock": "주식",
    "crypto": "코인",
    "cash": "현금",
    "other": "기타"
})
st.line_chart(asset_growth)

st.divider()

# -----------------------------
# 4. 부동산 상세
# -----------------------------
st.subheader("🏠 부동산 상세")

real_estate_profit = REAL_ESTATE_CURRENT - REAL_ESTATE_PURCHASE
real_estate_net = REAL_ESTATE_CURRENT - REAL_ESTATE_DEBT

real_df = pd.DataFrame([
    {"항목": "매수금액", "금액": REAL_ESTATE_PURCHASE},
    {"항목": "현재시세", "금액": REAL_ESTATE_CURRENT},
    {"항목": "차액", "금액": real_estate_profit},
    {"항목": "부채", "금액": REAL_ESTATE_DEBT},
    {"항목": "순자산", "금액": real_estate_net},
])

st.dataframe(
    real_df.assign(금액=real_df["금액"].apply(won)),
    hide_index=True,
    use_container_width=True
)

st.info("※ 부동산 현재시세는 우선 월 1회 직접 업데이트하는 방식입니다.")

st.divider()

# -----------------------------
# 5. 주식 상세
# -----------------------------
st.subheader("📈 주식 상세")

st.dataframe(
    stock_df.assign(
        평단=stock_df["평단"].apply(won),
        현재가=stock_df["현재가"].apply(won),
        평가금액=stock_df["평가금액"].apply(won),
        평가손익=stock_df["평가손익"].apply(won),
        수익률=stock_df["수익률"].apply(lambda x: f"{x:.1f}%")
    ),
    hide_index=True,
    use_container_width=True
)

st.caption(f"환율 적용: 1달러 = {fx:,.0f}원")

stock_summary = pd.DataFrame([
    {"항목": "총 평가금액", "금액": stock_total},
    {"항목": "부채", "금액": STOCK_DEBT},
    {"항목": "순자산", "금액": stock_net},
])

st.markdown("### 📊 주식 요약")

st.dataframe(
    stock_summary.assign(금액=stock_summary["금액"].apply(won)),
    hide_index=True,
    use_container_width=True
)

st.divider()

# -----------------------------
# 6. 코인 상세
# -----------------------------
st.subheader("🪙 코인 상세")

st.dataframe(
    coin_df.assign(
        평단=coin_df["평단"].apply(won),
        현재가=coin_df["현재가"].apply(won),
        평가금액=coin_df["평가금액"].apply(won),
        평가손익=coin_df["평가손익"].apply(won),
        수익률=coin_df["수익률"].apply(lambda x: f"{x:.1f}%")
    ),
    hide_index=True,
    use_container_width=True
)

crypto_summary = pd.DataFrame([
    {"항목": "총 평가금액", "금액": crypto_total},
    {"항목": "부채", "금액": CRYPTO_DEBT},
    {"항목": "순자산", "금액": crypto_net},
])

st.markdown("### 📊 코인 요약")

st.dataframe(
    crypto_summary.assign(금액=crypto_summary["금액"].apply(won)),
    hide_index=True,
    use_container_width=True
)
