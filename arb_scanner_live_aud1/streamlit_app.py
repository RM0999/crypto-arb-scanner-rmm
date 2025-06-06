
import streamlit as st
import requests
from datetime import datetime

# Define Australian exchange APIs and spreads/fees
EXCHANGES = {
    "BTC Markets": {
        "url": "https://api.btcmarkets.net/v3/markets/BTC-AUD/ticker",
        "spread": 0.002,
        "fee": 0.001
    },
    "Independent Reserve": {
        "url": "https://api.independentreserve.com/Public/GetMarketSummary?primaryCurrencyCode=btc&secondaryCurrencyCode=aud",
        "spread": 0.0025,
        "fee": 0.001
    },
    "CoinSpot": {
        "url": "https://www.coinspot.com.au/pubapi/latest",
        "spread": 0.003,
        "fee": 0.001
    },
    "CoinJar": {
        "url": "https://data.exchange.coinjar.com/products/BTC/AUD/ticker",
        "spread": 0.002,
        "fee": 0.001
    }
}

# Streamlit setup
st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔍 Live AUD Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar config
with st.sidebar:
    st.title("⚙️ Settings")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 1, 60, 10)
    selected_exchanges = st.multiselect("Exchanges", list(EXCHANGES.keys()), default=list(EXCHANGES.keys())[:3])

def fetch_price(exchange_name, details):
    try:
        response = requests.get(details["url"])
        data = response.json()
        if exchange_name == "BTC Markets":
            price = float(data["lastPrice"])
        elif exchange_name == "Independent Reserve":
            price = float(data["LastPrice"])
        elif exchange_name == "CoinSpot":
            price = float(data["prices"]["BTC"]["last"])
        elif exchange_name == "CoinJar":
            price = float(data["last"])
        else:
            return None

        buy_price = price * (1 + details["spread"] + details["fee"])
        sell_price = price * (1 - details["spread"] - details["fee"])
        return {"buy": round(buy_price, 2), "sell": round(sell_price, 2)}
    except:
        return None

# History state
if "history" not in st.session_state:
    st.session_state.history = []

# Fetch and analyze data
prices = {ex: fetch_price(ex, EXCHANGES[ex]) for ex in selected_exchanges}
valid_prices = {k: v for k, v in prices.items() if v}

if valid_prices:
    best_buy = min(valid_prices.items(), key=lambda x: x[1]["buy"])
    best_sell = max(valid_prices.items(), key=lambda x: x[1]["sell"])
    profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
    profit_aud = round(investment * profit_pct / 100, 2)
    timestamp = datetime.now().strftime("%H:%M:%S")

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

    st.subheader("📊 Latest Opportunity")
    st.write(f"🕒 Time: {latest['timestamp']}")
    st.write(f"💸 Buy from: {latest['buy_exchange']} at {latest['buy_price']}")
    st.write(f"💰 Sell to: {latest['sell_exchange']} at {latest['sell_price']}")
    st.write(f"📈 Estimated Profit: {latest['profit_pct']} ({latest['profit_aud']})")

    if len(st.session_state.history) > 1:
        st.subheader("📚 Last 2 Scans")
        for entry in reversed(st.session_state.history[:-1]):
            st.write(f"🕒 {entry['timestamp']} — Buy {entry['buy_exchange']} ({entry['buy_price']}), "
                     f"Sell {entry['sell_exchange']} ({entry['sell_price']}), Profit: {entry['profit_pct']} ({entry['profit_aud']})")
else:
    st.error("Failed to fetch live data from selected exchanges.")
