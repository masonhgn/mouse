from OrderBook import OrderBook, Order
from Client import Client
import pandas as pd

class Exchange:
    def __init__(self):
        self.clients = {}  # Dictionary to hold client objects
        self.create_orderbooks_from_file('tickers.csv')

    def register_client(self, client_id, balance):
        self.clients[client_id] = Client(client_id, balance)

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

    def submit_order(self, client_id, ticker, side, type, quantity, price=None) -> None:
        order = Order(client_id, side, type, ticker, quantity, price)
        if ticker in self.orderbooks:
            self.orderbooks[ticker].add_order(order)
            self.orderbooks[ticker].match_orders(self.clients)
        else:
            print(f"Ticker {ticker} not found in the order books.")
