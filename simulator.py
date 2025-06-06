
class Wallet:
    def __init__(self, initial_balance):
        self.balance = initial_balance
        self.history = []

    def execute_trade(self, exchange_buy, exchange_sell, buy_price, sell_price, fee_buy, fee_sell, investment):
        total_cost = investment * (1 + fee_buy)
        total_gain = investment * (sell_price / buy_price) * (1 - fee_sell)

        if self.balance >= total_cost:
            self.balance -= total_cost
            self.balance += total_gain
            profit = total_gain - total_cost
            trade_record = {
                "buy_from": exchange_buy,
                "sell_to": exchange_sell,
                "buy_price": buy_price,
                "sell_price": sell_price,
                "investment": investment,
                "profit": profit
            }
            self.history.append(trade_record)
            return trade_record
        else:
            return None

    def get_balance(self):
        return round(self.balance, 2)

    def get_history(self):
        return self.history[-5:]
