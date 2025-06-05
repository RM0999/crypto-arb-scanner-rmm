
import streamlit as st
import random
from datetime import datetime

# Page config
st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")

st.markdown("<h1 style='text-align: center;'>🔍 Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    pair = st.text_input("Trading Pair", "BTC/USDT")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 1, 60, 10)
    exchanges = st.multiselect("Exchanges", ["Binance", "KuCoin", "OKX", "Bybit", "Bitget"], default=["Binance", "Bybit", "Bitget"])

# Simulate exchange data
def get_mock_data(exchange):
    base = 73000 * random.uniform(0.985, 1.015)
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

# Initialize session history
if "history" not in st.session_state:
    st.session_state.history = []

# Run scan on load
all_data = {ex: get_mock_data(ex) for ex in exchanges}
best_buy = min(all_data.items(), key=lambda x: x[1]["buy"])
best_sell = max(all_data.items(), key=lambda x: x[1]["sell"])
profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
profit_aud = round(investment * (profit_pct / 100), 2)
timestamp = datetime.now().strftime("%H:%M:%S")

# Store latest result
latest = {
    "timestamp": timestamp,
    "buy_exchange": best_buy[0],
    "sell_exchange": best_sell[0],
    "buy_price": f"AUD ${best_buy[1]['buy']:,.2f}",
    "sell_price": f"AUD ${best_sell[1]['sell']:,.2f}",
    "profit_pct": f"{profit_pct}%",
    "profit_aud": f"AUD ${profit_aud:,.2f}"
}
st.session_state.history.append(latest)
st.session_state.history = st.session_state.history[-3:]

# Show most recent
st.subheader("📊 Latest Opportunity")
st.write(f"🕒 Time: {latest['timestamp']}")
st.write(f"💸 Buy from: {latest['buy_exchange']} at {latest['buy_price']}")
st.write(f"💰 Sell to: {latest['sell_exchange']} at {latest['sell_price']}")
st.write(f"📈 Estimated Profit: {latest['profit_pct']} ({latest['profit_aud']})")

# Show past 2
if len(st.session_state.history) > 1:
    st.subheader("📚 Last 2 Scans")
    for entry in reversed(st.session_state.history[:-1]):
        st.write(f"🕒 {entry['timestamp']} — Buy {entry['buy_exchange']} ({entry['buy_price']}), "
                 f"Sell {entry['sell_exchange']} ({entry['sell_price']}), Profit: {entry['profit_pct']} ({entry['profit_aud']})")
