import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="우리 가족 FIRE", page_icon="🔥", layout="wide")

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #111827 0%, #374151 100%);
    padding: 24px;
    border-radius: 24px;
    color: white;
    margin-bottom: 18px;
}
.hero-title {font-size: 32px; font-weight: 900;}
.hero-sub {font-size: 15px; color: #d1d5db;}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 18px;
}
.metric-card {
    background: white;
    padding: 18px;
    border-radius: 20px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
    border: 1px solid #edf0f5;
}
.metric-label {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 6px;
}
.metric-value {
    color: #111827;
    font-size: 26px;
    font-weight: 900;
}
.metric-sub {
    color: #6b7280;
    font-size: 12px;
    margin-top: 6px;
}
.good {color: #059669 !important;}
.bad {color: #dc2626 !important;}

.asset-card {
    background: white;
    padding: 15px 16px;
    border-radius: 16px;
    border: 1px solid #edf0f5;
    box-shadow: 0 5px 16px rgba(0,0,0,0.045);
    margin-bottom: 10px;
}
.asset-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.asset-title {
    font-size: 16px;
    font-weight: 800;
    color: #111827;
}
.asset-value {
    font-size: 17px;
    font-weight: 900;
    color: #111827;
}
.asset-sub {
    font-size: 12px;
    color: #6b7280;
    margin-top: 6px;
}
.section-title {
    font-size: 22px;
    font-weight: 850;
    margin: 18px 0 12px 0;
}
.mobile-note {
    color: #6b7280;
    font-size: 13px;
    margin-bottom: 8px;
}

@media (max-width: 768px) {
    .hero {
        padding: 20px;
        border-radius: 20px;
    }
    .hero-title {
        font-size: 25px;
        line-height: 1.25;
    }
    .hero-sub {
        font-size: 13px;
    }
    .metric-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
    .metric-card {
        padding: 14px;
        border-radius: 16px;
    }
    .metric-label {
        font-size: 12px;
    }
    .metric-value {
        font-size: 21px;
    }
    .metric-sub {
        font-size: 11px;
    }
    .section-title {
        font-size: 19px;
    }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 기본 데이터
# -----------------------------
REAL_ESTATE_PURCHASE = 1_062_000_000
REAL_ESTATE_CURRENT = 1_500_000_000
REAL_ESTATE_DEBT = 750_000_000

MINUS_ACCOUNT_DEBT = 29_000_000

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
# 주식 계산
# -----------------------------
fx = get_fx()

stock_rows = []
for s in stocks:
    usd_price = get_stock_price(s["ticker"])
    price_krw = usd_price * fx
    amount = price_krw * s["qty"]
    invest = s["avg"] * s["qty"]
    profit = amount - invest
    rate = profit / invest * 100 if invest else 0

    stock_rows.append({
        "종목": s["name"],
        "티커": s["ticker"],
        "수량": s["qty"],
        "평단": s["avg"],
        "현재가": price_krw,
        "투자금": invest,
        "평가금액": amount,
        "평가손익": profit,
        "수익률": rate
    })

stock_df = pd.DataFrame(stock_rows)
stock_total = stock_df["평가금액"].sum()
stock_invest = stock_df["투자금"].sum()
stock_profit = stock_total - stock_invest
stock_return = stock_profit / stock_invest * 100 if stock_invest else 0

# -----------------------------
# 코인 계산
# -----------------------------
coin_rows = []
for c in coins:
    price = get_coin_price(c["ticker"])
    amount = price * c["qty"]
    invest = c["avg"] * c["qty"]
    profit = amount - invest
    rate = profit / invest * 100 if invest else 0

    coin_rows.append({
        "종목": c["name"],
        "티커": c["ticker"],
        "수량": c["qty"],
        "평단": c["avg"],
        "현재가": price,
        "투자금": invest,
        "평가금액": amount,
        "평가손익": profit,
        "수익률": rate
    })

coin_df = pd.DataFrame(coin_rows)
crypto_total = coin_df["평가금액"].sum()
crypto_invest = coin_df["투자금"].sum()
crypto_profit = crypto_total - crypto_invest
crypto_return = crypto_profit / crypto_invest * 100 if crypto_invest else 0

# -----------------------------
# 총자산 계산
# -----------------------------
total_asset = REAL_ESTATE_CURRENT + stock_total + crypto_total + CASH + OTHER
total_debt = REAL_ESTATE_DEBT + MINUS_ACCOUNT_DEBT
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
    <div class="hero-sub">총자산 · 부채 · 순자산 · 월별 성장 흐름을 한눈에 보는 가족 자산 현황판</div>
</div>
""", unsafe_allow_html=True)

tab_home, tab_growth, tab_real, tab_stock, tab_coin, tab_data = st.tabs([
    "🏠 홈", "📈 성장", "🏢 부동산", "📊 주식", "🪙 코인", "📋 데이터"
])

# -----------------------------
# 홈
# -----------------------------
with tab_home:
    change_class = "good" if mom_change >= 0 else "bad"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">총자산</div>
            <div class="metric-value">{eok(total_asset)}</div>
            <div class="metric-sub">부동산 + 주식 + 코인 + 현금</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">부채</div>
            <div class="metric-value">{eok(total_debt)}</div>
            <div class="metric-sub">주담대 + 마이너스통장</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">순자산</div>
            <div class="metric-value">{eok(net_asset)}</div>
            <div class="metric-sub">총자산 - 부채</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">전월대비</div>
            <div class="metric-value {change_class}">{eok(mom_change)}</div>
            <div class="metric-sub">{pct(mom_rate)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 자산군별 현황</div>', unsafe_allow_html=True)

    asset_table = pd.DataFrame([
        {"자산군": "부동산", "금액": REAL_ESTATE_CURRENT, "부채": REAL_ESTATE_DEBT, "순자산": REAL_ESTATE_CURRENT - REAL_ESTATE_DEBT},
        {"자산군": "주식", "금액": stock_total, "부채": 0, "순자산": stock_total},
        {"자산군": "코인", "금액": crypto_total, "부채": 0, "순자산": crypto_total},
        {"자산군": "현금", "금액": CASH, "부채": 0, "순자산": CASH},
        {"자산군": "기타", "금액": OTHER, "부채": 0, "순자산": OTHER},
        {"자산군": "마이너스통장", "금액": 0, "부채": MINUS_ACCOUNT_DEBT, "순자산": -MINUS_ACCOUNT_DEBT},
        {"자산군": "합계", "금액": total_asset, "부채": total_debt, "순자산": net_asset},
    ])

    asset_table["비중"] = asset_table["금액"] / total_asset * 100

    # 모바일용 카드 리스트
    for _, row in asset_table[asset_table["자산군"] != "합계"].iterrows():
        value_color = "bad" if row["순자산"] < 0 else ""
        st.markdown(f"""
        <div class="asset-card">
            <div class="asset-row">
                <div class="asset-title">{row["자산군"]}</div>
                <div class="asset-value {value_color}">{eok(row["순자산"])}</div>
            </div>
            <div class="asset-sub">
                금액 {won(row["금액"])} · 부채 {won(row["부채"])} · 비중 {row["비중"]:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="asset-card">
        <div class="asset-row">
            <div class="asset-title">합계</div>
            <div class="asset-value">{eok(net_asset)}</div>
        </div>
        <div class="asset-sub">
            총자산 {won(total_asset)} · 부채 {won(total_debt)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🧩 현재 자산 구성</div>', unsafe_allow_html=True)

    pie_df = asset_table[(asset_table["자산군"] != "합계") & (asset_table["금액"] > 0)]
    fig_pie = px.pie(
        pie_df,
        names="자산군",
        values="금액",
        hole=0.55,
        title="자산 구성"
    )
    fig_pie.update_layout(height=360, margin=dict(l=5, r=5, t=45, b=5), legend=dict(orientation="h"))
    st.plotly_chart(fig_pie, use_container_width=True)

    bar_df = asset_table[asset_table["자산군"] != "합계"]
    fig_bar = px.bar(
        bar_df,
        x="자산군",
        y="순자산",
        text="순자산",
        title="자산군별 순자산"
    )
    fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_bar.update_layout(height=380, margin=dict(l=5, r=5, t=45, b=5))
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# 성장 추이
# -----------------------------
with tab_growth:
    st.markdown('<div class="section-title">📈 총자산 / 순자산 성장 추이</div>', unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=history["date"],
        y=history["total_asset"],
        mode="lines+markers",
        name="총자산",
        line=dict(width=4)
    ))

    fig.add_trace(go.Scatter(
        x=history["date"],
        y=history["net_asset"],
        mode="lines+markers",
        name="순자산",
        line=dict(width=4)
    ))

    fig.update_layout(
        height=420,
        hovermode="x unified",
        yaxis_title="금액",
        xaxis_title="월",
        margin=dict(l=5, r=5, t=30, b=5),
        legend=dict(orientation="h")
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
        height=430,
        hovermode="x unified",
        margin=dict(l=5, r=5, t=45, b=5),
        legend=dict(orientation="h")
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

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">매수금액</div>
            <div class="metric-value">{eok(REAL_ESTATE_PURCHASE)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">현재시세</div>
            <div class="metric-value">{eok(REAL_ESTATE_CURRENT)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">차액</div>
            <div class="metric-value good">{eok(real_profit)}</div>
            <div class="metric-sub">{pct(real_return)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">순자산</div>
            <div class="metric-value">{eok(real_net)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    profit_class = "good" if stock_profit >= 0 else "bad"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">총 평가금액</div>
            <div class="metric-value">{eok(stock_total)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">투자금</div>
            <div class="metric-value">{eok(stock_invest)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">평가손익</div>
            <div class="metric-value {profit_class}">{eok(stock_profit)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">수익률</div>
            <div class="metric-value {profit_class}">{pct(stock_return)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    display_stock = stock_df.copy()
    display_stock["평단"] = display_stock["평단"].apply(won)
    display_stock["현재가"] = display_stock["현재가"].apply(won)
    display_stock["투자금"] = display_stock["투자금"].apply(won)
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
    fig_stock.update_layout(height=380, margin=dict(l=5, r=5, t=45, b=5))
    st.plotly_chart(fig_stock, use_container_width=True)

    st.caption(f"환율 적용: 1달러 = {fx:,.0f}원")

# -----------------------------
# 코인
# -----------------------------
with tab_coin:
    st.markdown('<div class="section-title">🪙 코인 상세</div>', unsafe_allow_html=True)

    crypto_class = "good" if crypto_profit >= 0 else "bad"

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <div class="metric-label">총 평가금액</div>
            <div class="metric-value">{eok(crypto_total)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">투자금</div>
            <div class="metric-value">{eok(crypto_invest)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">평가손익</div>
            <div class="metric-value {crypto_class}">{eok(crypto_profit)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">수익률</div>
            <div class="metric-value {crypto_class}">{pct(crypto_return)}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    display_coin = coin_df.copy()
    display_coin["평단"] = display_coin["평단"].apply(won)
    display_coin["현재가"] = display_coin["현재가"].apply(won)
    display_coin["투자금"] = display_coin["투자금"].apply(won)
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
    fig_coin.update_layout(height=380, margin=dict(l=5, r=5, t=45, b=5))
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
