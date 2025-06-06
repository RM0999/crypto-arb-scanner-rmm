import simulator

# simulator.py
if 'wallet' not in st.session_state:
    st.session_state.wallet = simulator.Wallet(balance=1000)

class Wallet:
    def __init__(self, balance=1000):
        self.balance = balance
        self.history = []

    def execute_trade(self, buy_price, sell_price, amount, fee_rate):
        gross_profit = (sell_price - buy_price) * amount
        fees = (buy_price + sell_price) * amount * fee_rate
        net_profit = gross_profit - fees
        self.balance += net_profit
        trade = Trade(buy_price, sell_price, amount, fee_rate, net_profit)
        self.history.append(trade)
        return trade

class Trade:
    def __init__(self, buy_price, sell_price, amount, fee_rate, profit):
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.amount = amount
        self.fee_rate = fee_rate
        self.profit = profit
