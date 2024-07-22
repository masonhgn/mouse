import string
import uuid



class Order:
    def __init__(self, side: string, order_type: string, ticker: string, quantity: int, price: float = None):
        self.id = str(uuid.uuid4())
        self.side = side
        self.type = order_type
        self.price = price
        self.quantity = quantity
        self.ticker = ticker
        self.filled_quantity = 0









class OrderBook:
    def __init__(self, ticker, last_traded_price: float):
        self.ticker = ticker
        self.last_traded_price = last_traded_price
        self.orderbook = {'buy':[],'sell':[]}
        self.executed_orders = {'buy':[],'sell':[]}

    def add_buy_order(self, order: Order):

        #make sure the order matches the orderbook
        assert order.ticker == self.ticker and order.side == 'buy'
        
        if 0 in [order.quantity, order.price]: return
        
        #if market order, set limit price as either worst price in the orderbook or
        if order.type == 'market':
            if len(orderbook['sell']) == 0: order.price = self.last_traded_price
            else: order.price = self.orderbook['sell'][0]

        #add to orderbook
        self.orderbook['buy'].append(order)
        self.orderbook['buy'].sort(key=lambda x: (x.price,x.quantity), reverse=True)


    def add_sell_order(self, order: Order):

        #make sure the order matches the orderbook
        assert order.ticker == self.ticker and order.side == 'sell'
        
        if 0 in [order.quantity, order.price]: return

        #if market order, set limit price as either worst price in the orderbook or
        if order.type == 'market':
            if len(orderbook['buy']) == 0: order.price = self.last_traded_price
            else: order.price = self.orderbook['buy'][0]

        #add to orderbook
        self.orderbook['sell'].append(order)
        self.orderbook['sell'].sort(key=lambda x: (x.price, x.quantity))


    def print(self):

        #this gap var doesn't work cuz it won't work with the fprint
        gap = 60

        max_len = max(len(self.orderbook['buy']), len(self.orderbook['sell']))

        print(f"{'Buy Orders':<70} | {'Sell Orders':<70}")
        print(f"{'Price':<24} {'Quantity':<24} {'Total':<24} | {'Price':<24} {'Quantity':<24} {'Total':<24}")
        print("="*140)

        for i in range(max_len):
            if i < len(self.orderbook['buy']):
                buy_order = self.orderbook['buy'][i]
                buy_str = f"{buy_order.price:<24} {buy_order.quantity:<24} {buy_order.price * buy_order.quantity:<24}"
            else:
                buy_str = " " * 70

            if i < len(self.orderbook['sell']):
                sell_order = self.orderbook['sell'][i]
                sell_str = f"{sell_order.price:<24} {sell_order.quantity:<24} {sell_order.price * sell_order.quantity:<24}"
            else:
                sell_str = ""

            print(f"{buy_str} | {sell_str}")


        
    def match_orders(self):
        while self.orderbook['buy'] and self.orderbook['sell']:
            best_buy = self.orderbook['buy'][0]
            best_sell = self.orderbook['sell'][0]

            if best_buy.price >= best_sell.price:
                match_quantity = min(best_buy.quantity - best_buy.filled_quantity, best_sell.quantity - best_sell.filled_quantity)
                
                best_buy.filled_quantity += match_quantity
                best_sell.filled_quantity += match_quantity

                if best_buy.filled_quantity == best_buy.quantity:
                    self.executed_orders['buy'].append(best_buy.id)
                    self.orderbook['buy'].pop(0)
                    
                if best_sell.filled_quantity == best_sell.quantity:
                    self.executed_orders['sell'].append(best_sell.id)
                    self.orderbook['sell'].pop(0)
            else:
                break

        




