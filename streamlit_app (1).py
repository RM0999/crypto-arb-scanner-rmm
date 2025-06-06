
import streamlit as st
import requests
from datetime import datetime

# Set page config
st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")

# Title
st.markdown("<h1 style='text-align: center;'>🔍 Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.title("⚙️ Settings")
    pair = st.text_input("Trading Pair", "BTC/USDT")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 5, 60, 10)
    exchanges = st.multiselect("Exchanges", ["Binance", "KuCoin", "Bybit", "OKX", "Bitget", "Kraken", "Coinstash", "Crypto.com"],
                               default=["Binance", "Bybit", "Kraken"])

# Fees by exchange (realistic approximations)
exchange_fees = {
    "Binance": 0.001,
    "KuCoin": 0.001,
    "Bybit": 0.001,
    "OKX": 0.001,
    "Bitget": 0.001,
    "Kraken": 0.0026,
    "Coinstash": 0.008,
    "Crypto.com": 0.003
}

# Fetch BTC/USDT prices in AUD
def get_price(exchange):
    try:
        if exchange == "Kraken":
            # Kraken gives USD values; convert to AUD
            btc_usdt = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSDT").json()
            usd_price = float(btc_usdt["result"]["XXBTZUSD"]["c"][0])
            fx = requests.get("https://api.exchangerate.host/convert?from=USD&to=AUD").json()
            rate = fx["result"]
            price = usd_price * rate
        elif exchange == "Binance":
            price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT").json()["price"])
            price *= requests.get("https://api.exchangerate.host/convert?from=USD&to=AUD").json()["result"]
        else:
            # Use a mock value if no real API available
            price = 73000
        return round(price, 2)
    except:
        return None

# Run scan
data = {}
for ex in exchanges:
    price = get_price(ex)
    if price:
        fee = exchange_fees.get(ex, 0.001)
        data[ex] = {
            "buy": price * (1 + fee),
            "sell": price * (1 - fee),
            "fee": fee
        }

if len(data) < 2:
    st.error("❌ Not enough exchange data available.")
else:
    best_buy = min(data.items(), key=lambda x: x[1]["buy"])
    best_sell = max(data.items(), key=lambda x: x[1]["sell"])
    profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
    profit_aud = round(investment * (profit_pct / 100), 2)

    if profit_pct >= min_profit:
        st.success(f"🚀 Opportunity Found! {datetime.now().strftime('%H:%M:%S')}")
        st.write(f"💸 Buy from **{best_buy[0]}** at **AUD ${best_buy[1]['buy']:,.2f}**")
        st.write(f"💰 Sell on **{best_sell[0]}** at **AUD ${best_sell[1]['sell']:,.2f}**")
        st.write(f"📈 Estimated Profit: **{profit_pct}%** | **AUD ${profit_aud:,.2f}**")
    else:
        st.warning(f"No arbitrage opportunity above {min_profit}% at the moment.")
