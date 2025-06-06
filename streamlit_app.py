
import streamlit as st
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔍 Live Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Constants
USD_TO_AUD = 1.52
CRYPTO_LIST = ["BTC", "ETH", "SOL", "XRP", "ADA"]
EXCHANGES = ["Binance", "Kraken", "CoinSpot", "IndependentReserve"]

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    selected_coin = st.selectbox("Select Coin", CRYPTO_LIST)
    pair = f"{selected_coin}/USDT"
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 5, 60, 10)
    selected_exchanges = st.multiselect("Exchanges", EXCHANGES, default=EXCHANGES)

# API functions
def fetch_binance(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={symbol}USDT"
        r = requests.get(url).json()
        ask = float(r['askPrice'])
        bid = float(r['bidPrice'])
        return {'buy': ask * USD_TO_AUD, 'sell': bid * USD_TO_AUD, 'fee': 0.001}
    except:
        return None

def fetch_kraken(symbol):
    try:
        kraken_map = {"BTC": "XBT", "ETH": "ETH", "SOL": "SOL", "XRP": "XRP", "ADA": "ADA"}
        pair = f"{kraken_map[symbol]}USDT"
        r = requests.get(f"https://api.kraken.com/0/public/Ticker?pair={pair}").json()
        data = list(r["result"].values())[0]
        ask = float(data["a"][0])
        bid = float(data["b"][0])
        return {'buy': ask * USD_TO_AUD, 'sell': bid * USD_TO_AUD, 'fee': 0.0026}
    except:
        return None

def fetch_coinspot(symbol):
    try:
        r = requests.get("https://www.coinspot.com.au/pubapi/v2/latest").json()
        ask = float(r['prices'][symbol]['ask'])
        bid = float(r['prices'][symbol]['bid'])
        return {'buy': ask, 'sell': bid, 'fee': 0.01}
    except:
        return None

def fetch_independent_reserve(symbol):
    try:
        ir_map = {"BTC": "Xbt", "ETH": "Eth", "SOL": "Sol", "XRP": "Xrp", "ADA": "Ada"}
        r = requests.get(f"https://api.independentreserve.com/Public/GetMarketSummary?primaryCurrencyCode={ir_map[symbol]}&secondaryCurrencyCode=Aud").json()
        ask = float(r['CurrentHighestBidPrice'])
        bid = float(r['CurrentLowestOfferPrice'])
        return {'buy': bid, 'sell': ask, 'fee': 0.005}
    except:
        return None

api_fetchers = {
    "Binance": fetch_binance,
    "Kraken": fetch_kraken,
    "CoinSpot": fetch_coinspot,
    "IndependentReserve": fetch_independent_reserve
}

# Auto refresh using Streamlit rerun trick
st_autorefresh = st.empty()
st_autorefresh.markdown(f"<script>setTimeout(() => window.location.reload(), {refresh_rate * 1000});</script>", unsafe_allow_html=True)

# Run scan
symbol = selected_coin
data = {ex: api_fetchers[ex](symbol) for ex in selected_exchanges if api_fetchers[ex](symbol)}
valid_data = {ex: val for ex, val in data.items() if val}

if valid_data:
    best_buy = min(valid_data.items(), key=lambda x: x[1]['buy'])
    best_sell = max(valid_data.items(), key=lambda x: x[1]['sell'])
    profit_pct = round((best_sell[1]['sell'] - best_buy[1]['buy']) / best_buy[1]['buy'] * 100, 2)
    profit_aud = round(investment * (profit_pct / 100), 2)
    timestamp = datetime.now().strftime("%H:%M:%S")

    if profit_pct >= min_profit:
        st.success(f"🚀 Opportunity Found! {timestamp}")
        st.write(f"Buy {symbol} from **{best_buy[0]}** at **AUD ${best_buy[1]['buy']:.2f}**")
        st.write(f"Sell on **{best_sell[0]}** at **AUD ${best_sell[1]['sell']:.2f}**")
        st.write(f"Estimated Profit: **{profit_pct}%** | **AUD ${profit_aud}**")
    else:
        st.warning(f"No arbitrage opportunity above {min_profit}% right now.")
else:
    st.error("No valid data available from selected exchanges.")
