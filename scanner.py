import streamlit as st
from datetime import datetime
import random

st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")

st.markdown("<h1 style='text-align: center;'>🔍 Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    pair = st.text_input("Trading Pair", "BTC/USDT")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment ($)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 1, 60, 10)
    exchanges = st.multiselect("Exchanges", ["Binance", "KuCoin", "OKX", "Bybit", "Bitget"], default=["Binance", "Bybit", "Bitget"])

placeholder = st.empty()

def get_mock_data(exchange):
    base = 50000 * random.uniform(0.985, 1.015)
    spread = {
        "Binance": 1.002,
        "KuCoin": 1.005,
        "OKX": 1.003,
        "Bybit": 1.004,
        "Bitget": 1.006
    }[exchange]
    return {
        "buy": round(base * spread, 2),
        "sell": round(base * random.uniform(0.998, 0.999), 2),
        "fee": 0.001
    }

if st.button("Start Scanning"):
    with placeholder.container():
        st.info(f"🔄 Scanning {pair} every {refresh_rate} seconds...")
        all_data = {}
        for ex in exchanges:
            data = get_mock_data(ex)
            all_data[ex] = data

        best_buy = min(all_data.items(), key=lambda x: x[1]["buy"])
        best_sell = max(all_data.items(), key=lambda x: x[1]["sell"])
        profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
        profit_usd = round(investment * (profit_pct / 100), 2)

        if profit_pct >= min_profit:
            st.success(f"🚀 Opportunity Found! {datetime.now().strftime('%H:%M:%S')}")
            st.write(f"Buy from **{best_buy[0]}** at **${best_buy[1]['buy']}**")
            st.write(f"Sell on **{best_sell[0]}** at **${best_sell[1]['sell']}**")
            st.write(f"Estimated Profit: **{profit_pct}%** | **${profit_usd}**")
        else:
            st.warning(f"No arbitrage opportunity above {min_profit}% right now.")
