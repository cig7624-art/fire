import streamlit as st
import pandas as pd

st.set_page_config(page_title="우리 가족 자산일기", layout="wide")

st.title("🔥 우리 가족 자산일기")

pf = pd.read_csv("portfolio.csv")

latest = pf.iloc[-1]
prev = pf.iloc[-2]

total = latest["total"]
change = latest["total"] - prev["total"]
change_rate = change / prev["total"] * 100

st.subheader("📌 이번달 자산 현황")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("총자산", f"{total/100000000:.1f}억")

with col2:
    st.metric("전월 대비", f"{change/100000000:.1f}억", f"{change_rate:.1f}%")

with col3:
    top_asset = ["realestate","stock","crypto","cash"]
    top_asset_name = max(top_asset, key=lambda x: latest[x])
    st.metric("가장 큰 자산", top_asset_name)

st.divider()

st.subheader("📈 총자산 성장 추이")
st.line_chart(pf.set_index("date")["total"])

st.subheader("📊 자산별 성장 추이")
st.line_chart(pf.set_index("date")[["realestate","stock","crypto","cash"]])

st.subheader("🧠 이번달 한줄 요약")

if change > 0:
    st.success(f"이번달 우리 가족 자산은 전월보다 {change/100000000:.1f}억 증가했습니다.")
elif change < 0:
    st.error(f"이번달 우리 가족 자산은 전월보다 {abs(change)/100000000:.1f}억 감소했습니다.")
else:
    st.info("이번달 우리 가족 자산은 전월과 동일합니다.")

st.subheader("💰 자산별 전월 대비 변화")

asset_names = {
    "realestate": "부동산",
    "stock": "주식",
    "crypto": "코인",
    "cash": "현금"
}

for asset, name in asset_names.items():
    diff = latest[asset] - prev[asset]
    st.write(f"{name}: {diff/100000000:.1f}억")

st.subheader("📋 월별 데이터")
st.dataframe(pf)
