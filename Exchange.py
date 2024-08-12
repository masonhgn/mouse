from OrderBook import OrderBook, Order
from Client import Client
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from passlib.hash import pbkdf2_sha256
import uuid


class Exchange:
    def __init__(self):
 
        uri = "mongodb+srv://cheese:12345@cluster0.rr9az.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        self.db = self.client['exchange_db'] 
        self.users_collection = self.db['users']
        self.tickers_collection = self.db['tickers'] 

        self.fetch_from_db()


    def __del__(self):
        print("saving data to database before shutdown...")
        self.save_to_db()



    def fetch_from_db(self):
        self.orderbooks = {}
        tickers = self.tickers_collection.find()
        for ticker_data in tickers:
            ticker = ticker_data['ticker']
            price = ticker_data['price']
            bid = ticker_data['bid']
            ask = ticker_data['ask']
            volume = ticker_data['volume']
            self.orderbooks[ticker] = OrderBook(ticker, price, bid, ask, volume)

        clients = {}
        for user in self.users_collection.find():
            client = Client(user)
            clients[user["_id"]] = client
        self.clients = clients
        print(self.clients)



    def save_to_db(self):
        #save orderbooks
        for ticker, orderbook in self.orderbooks.items():
                    self.tickers_collection.update_one(
                        {"ticker": ticker},
                        {
                            "$set": {
                                "price": orderbook.last_traded_price,
                                "bid": orderbook.bid,
                                "ask": orderbook.ask,
                                "volume": orderbook.volume,
                            }
                        },
                        upsert=True
                    )

        #and save clients
        for client_id, client in self.clients.items():
            self.users_collection.update_one(
                {"_id": client_id},
                {
                    "$set": {
                        "username": client.username,
                        "balance": client.balance,
                        "portfolio": client.portfolio
                    }
                },
                upsert=True
            )


    def register_client(self, balance, username, password):
        hashed_password = pbkdf2_sha256.hash(password)
        client_id = str(uuid.uuid4()) 
        client = Client({
            "_id": client_id,
            "username": username,
            "password": hashed_password,
            "balance": balance,
            "portfolio": {}
        })
        self.clients[client_id] = client
        return client_id



    def add_ticker(self, ticker, price, bid, ask, volume):
        new_orderbook = OrderBook(ticker, price, bid, ask, volume)
        self.orderbooks[ticker] = new_orderbook




    def get_client(self, client_id):
        return self.clients.get(client_id)

    def get_all_clients(self):
        return self.clients

    def get_client_by_username(self, username):
        for client in self.clients.values():
            if client.username == username:
                return client
        return None

    def get_user(self, username):
        user_data = self.users_collection.find_one({"username": username})
        return user_data


    def get_open_orders(self, client_id):
        return self.clients[client_id].orders

    def refresh_client(self, client_id):
        client = self.clients.get(client_id)
        if client:
            for ticker, position in client.portfolio.items():
                new_price = self.orderbooks[ticker].last_traded_price
                position['price'] = new_price
                position['total_value'] = new_price * position['quantity']
        else:
            print('ERROR: Client not found in refresh_client() function call!')


    def submit_order(self, client_id, side, type, quantity, ticker, price=None):
        if client_id not in self.clients:
            print('Client not registered with exchange, please register first')
            return

        order = Order(client_id, side, type, quantity, ticker, price)
        if ticker in self.orderbooks:
            self.orderbooks[ticker].add_order(order)
            self.clients[client_id].update_order(order)
            self.orderbooks[ticker].match_orders(self.clients)
        else:
            print(f"Ticker {ticker} not found in the order books!!!")
