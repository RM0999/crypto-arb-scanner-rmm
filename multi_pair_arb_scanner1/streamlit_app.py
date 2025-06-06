
import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Multi-Pair Crypto Arbitrage Scanner", layout="wide")
st.title("🔍 Multi-Pair Crypto Arbitrage Scanner")

# Settings
with st.sidebar:
    st.header("⚙️ Settings")
    trading_pairs = st.multiselect("Select Trading Pairs", ["BTC/USDT", "ETH/USDT", "XRP/USDT", "SOL/USDT", "LTC/USDT"], default=["BTC/USDT"])
    min_profit = st.slider("Minimum Profit (%)", 0.1, 5.0, 0.5)
    investment = st.number_input("Investment (AUD)", min_value=10.0, value=1000.0)
    st.caption("Live prices fetched from Binance, Kraken, and more (AUD converted).")

# Mock AUD conversion rate
usd_to_aud = 1.48

# Exchange API endpoints
api_endpoints = {
    "Binance": lambda pair: f"https://api.binance.com/api/v3/ticker/bookTicker?symbol={pair.replace('/', '')}",
    "KuCoin": lambda pair: f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={pair.replace('/', '-')}",
    "OKX": lambda pair: f"https://www.okx.com/api/v5/market/ticker?instId={pair.replace('/', '-')}",
    "Bybit": lambda pair: f"https://api.bybit.com/v2/public/tickers?symbol={pair.replace('/', '')}",
    "Bitget": lambda pair: f"https://api.bitget.com/api/v2/spot/market/ticker?symbol={pair.replace('/', '')}",
    "Kraken": lambda pair: f"https://api.kraken.com/0/public/Ticker?pair={pair.replace('/', '')}",
    "Crypto.com": lambda pair: f"https://api.crypto.com/v2/public/get-ticker?instrument_name={pair.replace('/', '_')}",
}

def fetch_prices(pair):
    prices = {}
    for name, url_func in api_endpoints.items():
        try:
            url = url_func(pair)
            r = requests.get(url, timeout=5)
            data = r.json()
            if name == "Binance":
                bid, ask = float(data["bidPrice"]), float(data["askPrice"])
            elif name == "KuCoin":
                bid, ask = float(data["data"]["bestBid"]), float(data["data"]["bestAsk"])
            elif name == "OKX":
                item = data["data"][0]
                bid, ask = float(item["bidPx"]), float(item["askPx"])
            elif name == "Bybit":
                item = data["result"][0]
                bid, ask = float(item["bid_price"]), float(item["ask_price"])
            elif name == "Bitget":
                bid, ask = float(data["data"]["buyPri"]), float(data["data"]["sellPri"])
            elif name == "Kraken":
                key = list(data["result"].keys())[0]
                bid, ask = float(data["result"][key]["b"][0]), float(data["result"][key]["a"][0])
            elif name == "Crypto.com":
                ticker = data["result"]["data"]
                bid, ask = float(ticker["b"]), float(ticker["k"])
            else:
                continue
            prices[name] = {
                "buy": round(ask * usd_to_aud, 2),
                "sell": round(bid * usd_to_aud, 2),
            }
        except:
            continue
    return prices

# Display arbitrage for each selected trading pair
for pair in trading_pairs:
    st.subheader(f"📈 {pair} Arbitrage Opportunities")
    price_data = fetch_prices(pair)
    if not price_data or len(price_data) < 2:
        st.warning(f"❌ Not enough data for {pair}")
        continue

    best_buy = min(price_data.items(), key=lambda x: x[1]["buy"])
    best_sell = max(price_data.items(), key=lambda x: x[1]["sell"])

    profit_pct = round((best_sell[1]["sell"] - best_buy[1]["buy"]) / best_buy[1]["buy"] * 100, 2)
    profit_aud = round(investment * (profit_pct / 100), 2)

    if profit_pct >= min_profit:
        st.success(f"💰 {datetime.now().strftime('%H:%M:%S')} — Buy on {best_buy[0]} at AUD ${best_buy[1]['buy']}, "
                   f"Sell on {best_sell[0]} at AUD ${best_sell[1]['sell']} → Profit: {profit_pct}% (AUD ${profit_aud})")
    else:
        st.info(f"⏱️ No arbitrage over {min_profit}% for {pair}. Best spread: {profit_pct}%")
