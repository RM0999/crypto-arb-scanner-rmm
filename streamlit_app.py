
import streamlit as st
from datetime import datetime
import requests

st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")

st.markdown("<h1 style='text-align: center;'>🔍 Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    pair = st.text_input("Trading Pair", "BTC/USDT")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 1, 60, 10)

exchanges = {
    "Binance": lambda: requests.get("https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT").json(),
    "Kraken": lambda: requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD").json(),
    "CoinSpot": lambda: requests.get("https://www.coinspot.com.au/pubapi/latest").json(),
    "CoinJar": lambda: requests.get("https://data.exchange.coinjar.com/products/BTC-AUD/ticker").json(),
    "Independent Reserve": lambda: requests.get("https://api.independentreserve.com/Public/GetMarketSummary?primaryCurrencyCode=xbt&secondaryCurrencyCode=aud").json(),
    "Crypto.com": lambda: requests.get("https://api.crypto.com/v2/public/get-ticker?instrument_name=BTC_USDT").json()
}

def get_prices():
    results = {}
    for name, fetch in exchanges.items():
        try:
            data = fetch()
            if name == "Binance":
                ask = float(data["askPrice"])
                bid = float(data["bidPrice"])
            elif name == "Kraken":
                ask = float(data["result"]["XXBTZUSD"]["a"][0])
                bid = float(data["result"]["XXBTZUSD"]["b"][0])
            elif name == "CoinSpot":
                ask = float(data["prices"]["BTC"]["ask"])
                bid = float(data["prices"]["BTC"]["bid"])
            elif name == "CoinJar":
                ask = float(data["ask"])
                bid = float(data["bid"])
            elif name == "Independent Reserve":
                ask = float(data["CurrentLowestOfferPrice"])
                bid = float(data["CurrentHighestBidPrice"])
            elif name == "Crypto.com":
                ask = float(data["result"]["data"]["a"])
                bid = float(data["result"]["data"]["b"])
            else:
                continue

            fee = 0.001  # Placeholder average fee
            results[name] = {
                "buy": round(ask * (1 + fee), 2),
                "sell": round(bid * (1 - fee), 2),
                "fee": fee
            }
        except Exception as e:
            continue
    return results

# History state
if "history" not in st.session_state:
    st.session_state.history = []

# Live scan
prices = get_prices()
if len(prices) >= 2:
    best_buy = min(prices.items(), key=lambda x: x[1]["buy"])
    best_sell = max(prices.items(), key=lambda x: x[1]["sell"])

    profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
    profit_aud = round(investment * (profit_pct / 100), 2)
    timestamp = datetime.now().strftime("%H:%M:%S")

    if profit_pct >= min_profit:
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
        st.session_state.history = st.session_state.history[-3:]  # Keep last 3

# Display
if st.session_state.history:
    current = st.session_state.history[-1]
    st.subheader("📊 Latest Opportunity")
    st.write(f"🕒 Time: {current['timestamp']}")
    st.write(f"💸 Buy from: {current['buy_exchange']} at {current['buy_price']}")
    st.write(f"💰 Sell to: {current['sell_exchange']} at {current['sell_price']}")
    st.write(f"📈 Estimated Profit: {current['profit_pct']} ({current['profit_aud']})")

    if len(st.session_state.history) > 1:
        st.subheader("📚 Last 2 Scans")
        for entry in reversed(st.session_state.history[:-1]):
            st.write(f"🕒 {entry['timestamp']} — Buy {entry['buy_exchange']} ({entry['buy_price']}), "
                     f"Sell {entry['sell_exchange']} ({entry['sell_price']}), Profit: {entry['profit_pct']} ({entry['profit_aud']})")
else:
    st.warning("No valid arbitrage opportunity found yet.")
