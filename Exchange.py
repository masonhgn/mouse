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

        self.create_orderbooks_from_db()



    def register_client(self, balance, username, password):
        hashed_password = pbkdf2_sha256.hash(password)
        client_id = str(uuid.uuid4()) 
        user_document = {
            "_id": client_id,
            "username": username,
            "password": hashed_password,
            "balance": balance,
            "portfolio": {}
        }
        self.users_collection.insert_one(user_document)
        return client_id



    def add_ticker(self, ticker, price, bid, ask, volume):
    
 
            new_orderbook = OrderBook(ticker, price, bid, ask, volume)
            

            self.tickers_collection.update_one(
                {"ticker": ticker},
                {"$set": {
                    "ticker": ticker,
                    "price": price,
                    "bid": bid,
                    "ask": ask,
                    "volume": volume
                }},
                upsert=True 
            )
            

            self.orderbooks[ticker] = new_orderbook




    def get_client(self, client_id):
        return self.users_collection.find_one({"_id": client_id})

    def get_client_by_username(self, username):
        return self.users_collection.find_one({"username": username})

    def refresh_client(self, client_id):
        client = self.get_client(client_id)
        
        for ticker, position in client['portfolio'].items():
            new_price = self.orderbooks[ticker].last_traded_price
            position['price'] = new_price
            position['total_value'] = new_price * position['quantity']

        self.users_collection.update_one(
            {"_id": client_id},
            {"$set": {"portfolio": client['portfolio']}}
        )

    def create_orderbooks_from_db(self):
        self.orderbooks = {}
        tickers = self.tickers_collection.find()
        for ticker_data in tickers:
            ticker = ticker_data['ticker']
            price = ticker_data['price']
            bid = ticker_data['bid']
            ask = ticker_data['ask']
            volume = ticker_data['volume']
            self.orderbooks[ticker] = OrderBook(ticker, price, bid, ask, volume)

    def save_orderbooks_to_db(self):
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

    def submit_order(self, client_id, side, type, quantity, ticker, price=None):
        if not self.users_collection.find_one({"_id": client_id}):
            print('Client not registered with exchange, please register first')
            return

        order = Order(client_id, side, type, quantity, ticker, price)
        if ticker in self.orderbooks:
            self.orderbooks[ticker].add_order(order)
            self.orderbooks[ticker].match_orders(self.get_all_clients())
            self.save_orderbooks_to_db()
        else:
            print(f"Ticker {ticker} not found in the order books!!!")

    def get_all_clients(self):
        return {user["_id"]: user for user in self.users_collection.find()}
