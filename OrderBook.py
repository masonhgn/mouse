import string
import uuid



class Order:
    def __init__(self, client_id, side, order_type, quantity, ticker, price=None):
        self.id = str(uuid.uuid4())
        self.client_id = client_id
        self.side = side
        self.type = order_type
        self.price = price
        self.quantity = quantity
        self.ticker = ticker
        self.filled_quantity = 0
        self.executed = False


    








class OrderBook:
    def __init__(self, ticker, last_traded_price, bid=None, ask=None, volume=None):
        self.ticker = ticker
        self.last_traded_price = last_traded_price
        self.orderbook = {'buy': [], 'sell': []}
        self.order_lookup = {}
        self.bid = bid
        self.ask = ask
        self.volume = volume

    def add_order(self, order):
        assert order.ticker == self.ticker
        if 0 in [order.quantity, order.price]:
            return


        #add to order lookup table
        self.order_lookup[order.id] = order


        if order.side == 'buy':
            if order.type == 'market':
                #set limit order price to be whatever the market offers
                order.price = self.last_traded_price if len(self.orderbook['sell']) == 0 else self.order_lookup[self.orderbook['sell'][0]].price

            #add to orderbook
            self.orderbook['buy'].append(order.id)

            #sort by price in decreasing order because the best buy price is the highest
            self.orderbook['buy'].sort(key=lambda x: (self.order_lookup[x].price, self.order_lookup[x].quantity), reverse=True)
        elif order.side == 'sell':
            if order.type == 'market':
                #set limit order price to be whatever the market offers
                order.price = self.last_traded_price if len(self.orderbook['buy']) == 0 else self.order_lookup[self.orderbook['buy'][0]].price

            #add to orderbook
            self.orderbook['sell'].append(order.id)

            #sort by price in increasing order because the best sell price is the lowest
            self.orderbook['sell'].sort(key=lambda x: (self.order_lookup[x].price, self.order_lookup[x].quantity))




    def find_order(self, order_id, side):
        return self.order_lookup.get(order_id)


    def match_orders(self, clients):

        #while the orderbook is not empty
        while self.orderbook['buy'] and self.orderbook['sell']:
        
            #get top two orders
            best_buy_id = self.orderbook['buy'][0]
            best_sell_id = self.orderbook['sell'][0]

            #get orders from lookup tables
            best_buy = self.order_lookup[best_buy_id]
            best_sell = self.order_lookup[best_sell_id]    

            #update bid ask spread
            self.bid, self.ask = best_buy.price, best_sell.price
            

            #if we've found matching orders, let's execute them to some extent
            if best_buy.price >= best_sell.price:
                match_quantity = min(best_buy.quantity - best_buy.filled_quantity, best_sell.quantity - best_sell.filled_quantity)
                transaction_price = round((best_buy.price + best_sell.price) / 2,2)
                self.last_traded_price = transaction_price
                print('MATCH ' + self.ticker + ' at $' + str(transaction_price) + ' quantity=' + str(match_quantity))
                #update the filled quantity of the orders
                best_buy.filled_quantity += match_quantity
                best_sell.filled_quantity += match_quantity

                #fetch client portfolios
                buy_client = clients[best_buy.client_id]
                sell_client = clients[best_sell.client_id]

                #update client portfolios
                buy_client.update_portfolio(self.ticker, match_quantity, transaction_price)
                sell_client.update_portfolio(self.ticker, -match_quantity, transaction_price)


                #if we've filled the entire order, we want to remove the order from the queue
                if best_buy.filled_quantity == best_buy.quantity:

                    self.orderbook['buy'].pop(0)
                    best_buy.executed = True

                if best_sell.filled_quantity == best_sell.quantity:

                    self.orderbook['sell'].pop(0)
                    best_sell.executed = True
            else:
                break

    def print(self):
        max_len = max(len(self.orderbook['buy']), len(self.orderbook['sell']))

        print(f"{'Buy Orders':<50} | {'Sell Orders':<50}")
        print(f"{'Price':<15} {'Quantity':<15} {'Total':<15} | {'Price':<15} {'Quantity':<15} {'Total':<15}")
        print("="*105)

        for i in range(max_len):
            if i < len(self.orderbook['buy']):
                buy_order = self.order_lookup[self.orderbook['buy'][i]]
                buy_str = f"{buy_order.price:<15.2f} {buy_order.quantity:<15.2f} {buy_order.price * buy_order.quantity:<15.2f}"
            else:
                buy_str = " " * 50

            if i < len(self.orderbook['sell']):
                sell_order = self.order_lookup[self.orderbook['sell'][i]]
                sell_str = f"{sell_order.price:<15.2f} {sell_order.quantity:<15.2f} {sell_order.price * sell_order.quantity:<15.2f}"
            else:
                sell_str = ""

            print(f"{buy_str} | {sell_str}")
