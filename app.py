import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="우리 가족 FIRE 대시보드",
    page_icon="🔥",
    layout="wide"
)

# -----------------------------
# 디자인 CSS
# -----------------------------
st.markdown("""
<style>
.main {
    background-color: #f7f8fb;
}

.hero {
    background: linear-gradient(135deg, #111827 0%, #374151 100%);
    padding: 34px;
    border-radius: 28px;
    color: white;
    margin-bottom: 24px;
}

.hero-title {
    font-size: 36px;
    font-weight: 900;
    margin-bottom: 6px;
}

.hero-sub {
    font-size: 16px;
    color: #d1d5db;
}

.card {
    background: white;
    padding: 22px;
    border-radius: 22px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border: 1px solid #edf0f5;
    margin-bottom: 16px;
}

.card-label {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 8px;
}

.card-value {
    color: #111827;
    font-size: 30px;
    font-weight: 900;
}

.card-sub {
    color: #6b7280;
    font-size: 13px;
    margin-top: 6px;
}

.section-title {
    font-size: 22px;
    font-weight: 850;
    margin: 12px 0 14px 0;
}

.good {
    color: #059669;
    font-weight: 800;
}

.bad {
    color: #dc2626;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 기본 데이터
# -----------------------------
REAL_ESTATE_PURCHASE = 1_062_000_000
REAL_ESTATE_CURRENT = 1_500_000_000

REAL_ESTATE_DEBT = 750_000_000
STOCK_DEBT = 15_000_000
CRYPTO_DEBT = 14_000_000

BASE_CASH = 3_500_000
BASE_OTHER = 0

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

def pct(x):
    return f"{x:.1f}%"

@st.cache_data(ttl=3600)
def get_fx():
    try:
        return float(yf.Ticker("KRW=X").history(period="1d")["Close"].iloc[-1])
    except:
        return 1400

@st.cache_data(ttl=3600)
def get_stock_price(ticker):
    try:
        return float(yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1])
    except:
        return 0

@st.cache_data(ttl=600)
def get_coin_price(ticker):
    try:
        url = f"https://api.upbit.com/v1/ticker?markets={ticker}"
        data = requests.get(url, timeout=5).json()
        return float(data[0]["trade_price"])
    except:
        return 0

# -----------------------------
# 입력 사이드바
# -----------------------------
st.sidebar.title("⚙️ 입력 / 설정")
cash_input = st.sidebar.number_input("추가 현금 입력", min_value=0, value=0, step=1_000_000)
other_input = st.sidebar.number_input("기타 자산 입력", min_value=0, value=0, step=1_000_000)

CASH = BASE_CASH + cash_input
OTHER = BASE_OTHER + other_input

# -----------------------------
# 가격 계산
# -----------------------------
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
        "티커": s["ticker"],
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

coin_rows = []
for c in coins:
    price = get_coin_price(c["ticker"])
    amount = price * c["qty"]
    principal = c["avg"] * c["qty"]
    profit = amount - principal
    rate = profit / principal * 100 if principal else 0

    coin_rows.append({
        "종목": c["name"],
        "티커": c["ticker"],
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

total_asset = REAL_ESTATE_CURRENT + stock_total + crypto_total + CASH + OTHER
total_debt = REAL_ESTATE_DEBT + STOCK_DEBT + CRYPTO_DEBT
net_asset = total_asset - total_debt

history = pd.read_csv("asset_history.csv")
history["total_asset"] = history[["realestate", "stock", "crypto", "cash", "other"]].sum(axis=1)
history["net_asset"] = history["total_asset"] - history["debt"]

prev_net = history.iloc[-1]["net_asset"]
mom_change = net_asset - prev_net
mom_rate = mom_change / prev_net * 100 if prev_net else 0

# -----------------------------
# 헤더
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-title">🔥 우리 가족 FIRE 대시보드</div>
    <div class="hero-sub">총자산 · 부채 · 순자산 · 자산 성장 흐름을 한눈에 보는 가족 자산 현황판</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# 탭
# -----------------------------
tab_home, tab_growth, tab_real, tab_stock, tab_coin, tab_data = st.tabs([
    "🏠 홈",
    "📈 성장 추이",
    "🏢 부동산",
    "📊 주식",
    "🪙 코인",
    "📋 데이터"
])

# -----------------------------
# 홈
# -----------------------------
with tab_home:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">총자산</div>
            <div class="card-value">{eok(total_asset)}</div>
            <div class="card-sub">부동산 + 주식 + 코인 + 현금 + 기타</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">부채</div>
            <div class="card-value">{eok(total_debt)}</div>
            <div class="card-sub">부동산·주식·코인 부채 합산</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="card">
            <div class="card-label">순자산</div>
            <div class="card-value">{eok(net_asset)}</div>
            <div class="card-sub">총자산 - 부채</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        change_class = "good" if mom_change >= 0 else "bad"
        st.markdown(f"""
        <div class="card">
            <div class="card-label">전월대비</div>
            <div class="card-value {change_class}">{eok(mom_change)}</div>
            <div class="card-sub">{pct(mom_rate)}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 자산군별 현황</div>', unsafe_allow_html=True)

    asset_table = pd.DataFrame([
        {"자산군": "부동산", "금액": REAL_ESTATE_CURRENT, "부채": REAL_ESTATE_DEBT, "순자산": REAL_ESTATE_CURRENT - REAL_ESTATE_DEBT},
        {"자산군": "주식", "금액": stock_total, "부채": STOCK_DEBT, "순자산": stock_net},
        {"자산군": "코인", "금액": crypto_total, "부채": CRYPTO_DEBT, "순자산": crypto_net},
        {"자산군": "현금", "금액": CASH, "부채": 0, "순자산": CASH},
        {"자산군": "기타", "금액": OTHER, "부채": 0, "순자산": OTHER},
        {"자산군": "합계", "금액": total_asset, "부채": total_debt, "순자산": net_asset},
    ])

    asset_table["비중"] = asset_table["금액"] / total_asset * 100

    show_asset = asset_table.copy()
    show_asset["금액"] = show_asset["금액"].apply(won)
    show_asset["부채"] = show_asset["부채"].apply(won)
    show_asset["순자산"] = show_asset["순자산"].apply(won)
    show_asset["비중"] = show_asset["비중"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(show_asset, hide_index=True, use_container_width=True)

    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig_pie = px.pie(
            asset_table[asset_table["자산군"] != "합계"],
            names="자산군",
            values="금액",
            hole=0.55,
            title="현재 자산 구성"
        )
        fig_pie.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        fig_bar = px.bar(
            asset_table[asset_table["자산군"] != "합계"],
            x="자산군",
            y="순자산",
            text="순자산",
            title="자산군별 순자산"
        )
        fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig_bar.update_layout(height=420, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# 성장 추이
# -----------------------------
with tab_growth:
    st.markdown('<div class="section-title">📈 총자산 / 순자산 성장 추이</div>', unsafe_allow_html=True)

    chart_history = history.copy()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=chart_history["date"],
        y=chart_history["total_asset"],
        mode="lines+markers",
        name="총자산",
        line=dict(width=4)
    ))

    fig.add_trace(go.Scatter(
        x=chart_history["date"],
        y=chart_history["net_asset"],
        mode="lines+markers",
        name="순자산",
        line=dict(width=4)
    ))

    fig.update_layout(
        height=500,
        hovermode="x unified",
        yaxis_title="금액",
        xaxis_title="월",
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">📊 자산별 성장 추이</div>', unsafe_allow_html=True)

    growth_df = history[["date", "realestate", "stock", "crypto", "cash", "other"]].copy()
    growth_df = growth_df.rename(columns={
        "realestate": "부동산",
        "stock": "주식",
        "crypto": "코인",
        "cash": "현금",
        "other": "기타"
    })

    long_df = growth_df.melt(id_vars="date", var_name="자산군", value_name="금액")

    fig2 = px.line(
        long_df,
        x="date",
        y="금액",
        color="자산군",
        markers=True,
        title="자산군별 월별 변화"
    )

    fig2.update_traces(line=dict(width=3))
    fig2.update_layout(
        height=520,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 부동산
# -----------------------------
with tab_real:
    st.markdown('<div class="section-title">🏢 부동산 상세</div>', unsafe_allow_html=True)

    real_profit = REAL_ESTATE_CURRENT - REAL_ESTATE_PURCHASE
    real_net = REAL_ESTATE_CURRENT - REAL_ESTATE_DEBT
    real_return = real_profit / REAL_ESTATE_PURCHASE * 100

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("매수금액", eok(REAL_ESTATE_PURCHASE))
    c2.metric("현재시세", eok(REAL_ESTATE_CURRENT))
    c3.metric("차액", eok(real_profit), pct(real_return))
    c4.metric("순자산", eok(real_net))

    real_df = pd.DataFrame([
        {"항목": "매수금액", "금액": REAL_ESTATE_PURCHASE},
        {"항목": "현재시세", "금액": REAL_ESTATE_CURRENT},
        {"항목": "차액", "금액": real_profit},
        {"항목": "부채", "금액": REAL_ESTATE_DEBT},
        {"항목": "순자산", "금액": real_net},
    ])

    st.dataframe(
        real_df.assign(금액=real_df["금액"].apply(won)),
        hide_index=True,
        use_container_width=True
    )

    st.info("부동산 현재시세는 우선 월 1회 직접 업데이트하는 방식입니다.")

# -----------------------------
# 주식
# -----------------------------
with tab_stock:
    st.markdown('<div class="section-title">📊 주식 상세</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("총 평가금액", eok(stock_total))
    c2.metric("주식 부채", eok(STOCK_DEBT))
    c3.metric("주식 순자산", eok(stock_net))

    display_stock = stock_df.copy()
    display_stock["평단"] = display_stock["평단"].apply(won)
    display_stock["현재가"] = display_stock["현재가"].apply(won)
    display_stock["평가금액"] = display_stock["평가금액"].apply(won)
    display_stock["평가손익"] = display_stock["평가손익"].apply(won)
    display_stock["수익률"] = display_stock["수익률"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_stock, hide_index=True, use_container_width=True)

    fig_stock = px.bar(
        stock_df,
        x="종목",
        y="평가금액",
        text="평가금액",
        title="종목별 평가금액"
    )
    fig_stock.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_stock.update_layout(height=450)
    st.plotly_chart(fig_stock, use_container_width=True)

    st.caption(f"환율 적용: 1달러 = {fx:,.0f}원")

# -----------------------------
# 코인
# -----------------------------
with tab_coin:
    st.markdown('<div class="section-title">🪙 코인 상세</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("총 평가금액", eok(crypto_total))
    c2.metric("코인 부채", eok(CRYPTO_DEBT))
    c3.metric("코인 순자산", eok(crypto_net))

    display_coin = coin_df.copy()
    display_coin["평단"] = display_coin["평단"].apply(won)
    display_coin["현재가"] = display_coin["현재가"].apply(won)
    display_coin["평가금액"] = display_coin["평가금액"].apply(won)
    display_coin["평가손익"] = display_coin["평가손익"].apply(won)
    display_coin["수익률"] = display_coin["수익률"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(display_coin, hide_index=True, use_container_width=True)

    fig_coin = px.bar(
        coin_df,
        x="종목",
        y="평가금액",
        text="평가금액",
        title="코인별 평가금액"
    )
    fig_coin.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_coin.update_layout(height=450)
    st.plotly_chart(fig_coin, use_container_width=True)

# -----------------------------
# 데이터
# -----------------------------
with tab_data:
    st.markdown('<div class="section-title">📋 월별 스냅샷 데이터</div>', unsafe_allow_html=True)
    st.dataframe(history, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">⚙️ 현재 입력값</div>', unsafe_allow_html=True)
    st.write(f"추가 현금 입력: {won(cash_input)}")
    st.write(f"기타 자산 입력: {won(other_input)}")
