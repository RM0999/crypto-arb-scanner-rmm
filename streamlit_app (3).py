
import streamlit as st
import requests
from datetime import datetime
import time
import simulator  # Import the simulator module

USD_TO_AUD = 1.52

# Initialize wallet and history
if 'wallet' not in st.session_state:
    st.session_state.wallet = simulator.Wallet(balance=10000)
if 'history' not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title="Crypto Arbitrage Scanner", layout="wide")
st.markdown("<h1 style='text-align: center;'>🔍 Live Crypto Arbitrage Scanner</h1>", unsafe_allow_html=True)

# Sidebar settings
with st.sidebar:
    st.title("⚙️ Settings")
    pair = st.text_input("Trading Pair", "BTC/USDT")
    min_profit = st.slider("Minimum Profit (%)", 0.5, 10.0, 2.0)
    investment = st.number_input("Investment (AUD)", min_value=10, value=1000)
    refresh_rate = st.slider("Refresh Interval (sec)", 5, 60, 10)
    selected_exchanges = st.multiselect("Exchanges", ["Binance", "Kraken", "CoinSpot", "IndependentReserve"],
                                        default=["Binance", "Kraken", "CoinSpot", "IndependentReserve"])

# API functions
def fetch_binance():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT").json()
        ask = float(r['askPrice'])
        bid = float(r['bidPrice'])
        return {'buy': ask * USD_TO_AUD, 'sell': bid * USD_TO_AUD, 'fee': 0.001}
    except:
        return None

def fetch_kraken():
    try:
        r = requests.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSDT").json()
        data = r["result"]["XXBTZUSD"]
        ask = float(data["a"][0])
        bid = float(data["b"][0])
        return {'buy': ask * USD_TO_AUD, 'sell': bid * USD_TO_AUD, 'fee': 0.0026}
    except:
        return None

def fetch_coinspot():
    try:
        r = requests.get("https://www.coinspot.com.au/pubapi/v2/latest").json()
        ask = float(r['prices']['BTC']['ask'])
        bid = float(r['prices']['BTC']['bid'])
        return {'buy': ask, 'sell': bid, 'fee': 0.01}
    except:
        return None

def fetch_independent_reserve():
    try:
        r = requests.get("https://api.independentreserve.com/Public/GetMarketSummary?primaryCurrencyCode=Xbt&secondaryCurrencyCode=Aud").json()
        ask = float(r['CurrentHighestBidPrice'])
        bid = float(r['CurrentLowestOfferPrice'])
        return {'buy': bid, 'sell': ask, 'fee': 0.005}
    except:
        return None

api_fetchers = {
    "Binance": fetch_binance,
    "Kraken": fetch_kraken,
    "CoinSpot": fetch_coinspot,
    "IndependentReserve": fetch_independent_reserve,
}

placeholder = st.empty()

# Auto-refresh loop
while True:
    with placeholder.container():
        st.markdown(f"<h3>Scanning {pair} at {datetime.now().strftime('%H:%M:%S')}</h3>", unsafe_allow_html=True)
        data = {ex: api_fetchers[ex]() for ex in selected_exchanges if api_fetchers[ex]()}
        valid_data = {ex: val for ex, val in data.items() if val}

        if valid_data:
            best_buy = min(valid_data.items(), key=lambda x: x[1]['buy'])
            best_sell = max(valid_data.items(), key=lambda x: x[1]['sell'])
            profit_pct = round((best_sell[1]['sell'] - best_buy[1]['buy']) / best_buy[1]['buy'] * 100, 2)
            profit_aud = round(investment * (profit_pct / 100), 2)
            timestamp = datetime.now().strftime("%H:%M:%S")

            if profit_pct >= min_profit:
                st.success(f"🚀 Opportunity Found! {timestamp}")
                st.write(f"Buy from **{best_buy[0]}** at **AUD ${best_buy[1]['buy']:.2f}**")
                st.write(f"Sell on **{best_sell[0]}** at **AUD ${best_sell[1]['sell']:.2f}**")
                st.write(f"Estimated Profit: **{profit_pct}%** | **AUD ${profit_aud}**")

                trade = simulator.execute_trade(
                    wallet=st.session_state.wallet,
                    buy_price=best_buy[1]['buy'],
                    sell_price=best_sell[1]['sell'],
                    investment=investment,
                    buy_fee=best_buy[1]['fee'],
                    sell_fee=best_sell[1]['fee'],
                    buy_exchange=best_buy[0],
                    sell_exchange=best_sell[0],
                    timestamp=timestamp
                )

                st.session_state.history.insert(0, trade)
                st.session_state.history = st.session_state.history[:5]
            else:
                st.warning(f"No arbitrage opportunity above {min_profit}% right now.")
        else:
            st.error("No valid data available from selected exchanges.")

        # Show trade history
        if st.session_state.history:
            st.subheader("📚 Last 5 Trades")
            for t in st.session_state.history:
                st.write(f"🕒 {t['timestamp']} | Buy {t['buy_exchange']} (${t['buy_price']}) → "
                         f"Sell {t['sell_exchange']} (${t['sell_price']}) | Profit: ${t['net_profit']:.2f}")

        # Wallet info
        st.subheader("💼 Wallet Status")
        st.write(f"Balance: **AUD ${st.session_state.wallet.balance:.2f}**")

    time.sleep(refresh_rate)
