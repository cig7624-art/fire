st.header("📈 자산 성장")

pf = pd.read_csv("portfolio.csv")

st.subheader("총자산 추이")
st.line_chart(pf.set_index("date")["total"])

st.subheader("자산별 변화")
st.line_chart(pf.set_index("date")[["realestate","stock","crypto","cash"]])

# 이번달 변화 계산
latest = pf.iloc[-1]
prev = pf.iloc[-2]

change = latest["total"] - prev["total"]

st.subheader("🧠 이번달 요약")

if change > 0:
    st.success(f"이번달 자산 +{int(change/10000000)}천만원 증가")
else:
    st.error(f"이번달 자산 {int(change/10000000)}천만원 감소")

# 자산별 변화
st.subheader("자산별 증가")

for col in ["realestate","stock","crypto","cash"]:
    diff = latest[col] - prev[col]
    st.write(f"{col}: {int(diff/10000000)}천만원")
