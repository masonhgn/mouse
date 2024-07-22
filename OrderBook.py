import string
import uuid



class Order:
    def __init__(self, client_id, side, order_type, ticker, quantity, price=None):
        self.id = str(uuid.uuid4())
        self.client_id = client_id
        self.side = side
        self.type = order_type
        self.price = price
        self.quantity = quantity
        self.ticker = ticker
        self.filled_quantity = 0


    








class OrderBook:
    def __init__(self, ticker, last_traded_price, bid=None, ask=None, volume=None):
        self.ticker = ticker
        self.last_traded_price = last_traded_price
        self.orderbook = {'buy': [], 'sell': []}
        self.executed_orders = {'buy': [], 'sell': []}
        self.bid = bid
        self.ask = ask
        self.volume = volume

    def add_order(self, order):
        assert order.ticker == self.ticker
        if 0 in [order.quantity, order.price]:
            return

        if order.side == 'buy':
            if order.type == 'market':
                order.price = self.last_traded_price if len(self.orderbook['sell']) == 0 else self.orderbook['sell'][0].price
            self.orderbook['buy'].append(order)
            self.orderbook['buy'].sort(key=lambda x: (x.price, x.quantity), reverse=True)
        elif order.side == 'sell':
            if order.type == 'market':
                order.price = self.last_traded_price if len(self.orderbook['buy']) == 0 else self.orderbook['buy'][0].price
            self.orderbook['sell'].append(order)
            self.orderbook['sell'].sort(key=lambda x: (x.price, x.quantity))

    def match_orders(self, clients):
        while self.orderbook['buy'] and self.orderbook['sell']:
            best_buy = self.orderbook['buy'][0]
            best_sell = self.orderbook['sell'][0]
            self.bid, self.ask = best_buy.price, best_sell.price

            if best_buy.price >= best_sell.price:
                match_quantity = min(best_buy.quantity - best_buy.filled_quantity, best_sell.quantity - best_sell.filled_quantity)
                transaction_price = (best_buy.price + best_sell.price) / 2

                # Update filled quantities
                best_buy.filled_quantity += match_quantity
                best_sell.filled_quantity += match_quantity

                # Update client portfolios and balances
                buy_client = clients[best_buy.client_id]
                sell_client = clients[best_sell.client_id]

                buy_client.update_portfolio(self.ticker, match_quantity)
                buy_client.update_balance(-transaction_price * match_quantity)

                sell_client.update_portfolio(self.ticker, -match_quantity)
                sell_client.update_balance(transaction_price * match_quantity)

                if best_buy.filled_quantity == best_buy.quantity:
                    self.executed_orders['buy'].append(best_buy.id)
                    self.orderbook['buy'].pop(0)

                if best_sell.filled_quantity == best_sell.quantity:
                    self.executed_orders['sell'].append(best_sell.id)
                    self.orderbook['sell'].pop(0)
            else:
                break

    def print(self):
        max_len = max(len(self.orderbook['buy']), len(self.orderbook['sell']))

        print(f"{'Buy Orders':<50} | {'Sell Orders':<50}")
        print(f"{'Price':<15} {'Quantity':<15} {'Total':<15} | {'Price':<15} {'Quantity':<15} {'Total':<15}")
        print("="*105)

        for i in range(max_len):
            if i < len(self.orderbook['buy']):
                buy_order = self.orderbook['buy'][i]
                buy_str = f"{buy_order.price:<15.2f} {buy_order.quantity:<15.2f} {buy_order.price * buy_order.quantity:<15.2f}"
            else:
                buy_str = " " * 50

            if i < len(self.orderbook['sell']):
                sell_order = self.orderbook['sell'][i]
                sell_str = f"{sell_order.price:<15.2f} {sell_order.quantity:<15.2f} {sell_order.price * sell_order.quantity:<15.2f}"
            else:
                sell_str = ""

            print(f"{buy_str} | {sell_str}")
