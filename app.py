import streamlit as st
import random
import datetime

# Simulate a market scan result
def simulate_arbitrage_scan():
    buy_exchange = random.choice(["Binance", "KuCoin", "Bybit"])
    sell_exchange = random.choice(["OKX", "Bitget", "Binance"])
    buy_price = round(random.uniform(73000, 75000), 2)
    sell_price = round(buy_price * random.uniform(1.01, 1.03), 2)
    profit_pct = round((sell_price - buy_price) / buy_price * 100, 2)
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    return {
        "timestamp": timestamp,
        "buy_exchange": buy_exchange,
        "sell_exchange": sell_exchange,
        "buy_price": f"AUD {buy_price:,.2f}",
        "sell_price": f"AUD {sell_price:,.2f}",
        "profit_pct": f"{profit_pct}%",
    }

# Persistent history using Streamlit's session state
if 'history' not in st.session_state:
    st.session_state.history = []

# Title
st.title("🔁 Live Crypto Arbitrage Scanner (Auto-Refreshing)")

# Simulate a new scan every refresh
latest = simulate_arbitrage_scan()
st.session_state.history.append(latest)
st.session_state.history = st.session_state.history[-3:]

# Show latest
st.subheader("📊 Latest Opportunity")
st.write(f"🕒 Time: {latest['timestamp']}")
st.write(f"💸 Buy from: {latest['buy_exchange']} at {latest['buy_price']}")
st.write(f"💰 Sell to: {latest['sell_exchange']} at {latest['sell_price']}")
st.write(f"📈 Estimated Profit: {latest['profit_pct']}")

# Show history
if len(st.session_state.history) > 1:
    st.subheader("📚 Last 2 Scans")
    for entry in reversed(st.session_state.history[:-1]):
        st.write(f"🕒 {entry['timestamp']} — Buy {entry['buy_exchange']} ({entry['buy_price']}), "
                 f"Sell {entry['sell_exchange']} ({entry['sell_price']}), Profit: {entry['profit_pct']}")
