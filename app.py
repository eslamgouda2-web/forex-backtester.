import streamlit as st

st.set_page_config(

    page_title="Forex Backtester",

    page_icon="📊",

    layout="wide"

)

st.title("📊 Forex Backtester")

st.subheader("ZigZag Break & Retest")

st.write("أول نسخة من برنامج الباك تيست")

st.divider()

col1, col2 = st.columns(2)

with col1:

    symbol = st.selectbox(

        "الزوج",

        ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD"]

    )

    timeframe = st.selectbox(

        "الفريم",

        ["5 Minutes", "15 Minutes", "1 Hour", "4 Hours"]

    )

with col2:

    start_date = st.date_input("من", value=None)

    end_date = st.date_input("إلى", value=None)

st.divider()

st.subheader("⚙️ إعدادات ZigZag")

col1, col2, col3 = st.columns(3)

with col1:

    depth = st.number_input(

        "Period / Depth",

        min_value=1,

        value=12

    )

with col2:

    deviation = st.number_input(

        "Deviation",

        min_value=0.0,

        value=5.0

    )

with col3:

    backstep = st.number_input(

        "Backstep",

        min_value=1,

        value=3

    )

st.divider()

st.subheader("🎯 إعدادات الاستراتيجية")

retest = st.checkbox(

    "تفعيل Retest",

    value=True

)

trail_start = st.number_input(

    "بدء Trailing عند R",

    min_value=0.1,

    value=1.0,

    step=0.1

)

swing_trailing = st.checkbox(

    "Trailing خلف كل Swing",

    value=True

)

st.divider()

if st.button("🚀 RUN BACKTEST", use_container_width=True):

    st.success("تم تشغيل الاختبار — محرك الباك تيست سيتم إضافته في الخطوة التالية.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Trades", "—")

    col2.metric("Win Rate", "—")

    col3.metric("Profit Factor", "—")

    col4.metric("Net R", "—")
