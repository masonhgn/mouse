from OrderBook import OrderBook, Order
from Client import Client
import pandas as pd

class Exchange:
    def __init__(self):
        self.clients = {} 
        self.create_orderbooks_from_file('tickers.csv')

    def register_client(self, balance):

        #create new client object
        new_client = Client(balance)

        #register it in the exchange so we can keep track of it
        self.clients[new_client.client_id] = Client(balance)

        #return the id
        return new_client.client_id


    def refresh_client(client_id):
        '''refreshes all of the positions of a single client based on latest prices'''
        client = self.clients[client_id]
        
        for ticker, position in client.portfolio.items():
            new_price = self.orderbooks[ticker].last_traded_price
            position.price = new_price
            position.total_value = new_price * position.quantity



    def print_order_book(self, ticker) -> None:
        self.orderbooks[ticker].print()



    def create_orderbooks_from_file(self, filename: str) -> None:
        orderbooks = {}

        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            ticker = row['ticker']
            price = row['price']
            bid = row['bid']
            ask = row['ask']
            volume = row['volume']
            orderbooks[ticker] = OrderBook(ticker, price, bid, ask, volume)

        self.orderbooks = orderbooks

    def save_orderbooks_to_file(self, filename: str) -> None:
        data = []

        for ticker, orderbook in self.orderbooks.items():
            data.append({
                'ticker': ticker,
                'price': orderbook.price,
                'bid': orderbook.bid,
                'ask': orderbook.ask,
                'volume': orderbook.volume,
            })

        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)




    def submit_order(self, client_id, side, type, quantity, ticker, price=None) -> None:
        
        #client has to be registered with exchange so we can keep track of and refresh its portfolio value
        if not client_id in self.clients:
            print('client not registered with exchange, please register first')
            return

        order = Order(client_id, side, type, quantity,ticker, price)
        if ticker in self.orderbooks:
            self.orderbooks[ticker].add_order(order)
            self.orderbooks[ticker].match_orders(self.clients)
        else:
            print(f"ticker {ticker} not found in the order books!!!")
