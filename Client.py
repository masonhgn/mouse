import uuid


class Position:
    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price
        self.total_value = quantity*price



class Client:
    def __init__(self, balance):
        self.client_id = str(uuid.uuid4())
        self.balance = balance
        self.portfolio = {}
    


    def update_portfolio(self, ticker, quantity, price):
        if ticker in self.portfolio:
            self.portfolio[ticker].quantity += quantity
            self.portfolio[ticker].total_value = quantity*price
        else:
            self.portfolio[ticker] = Position(quantity, price)

        #if we sold all of a security, let's make sure we remove it from our portfolio
        if self.portfolio[ticker].quantity == 0: del self.portfolio[ticker]

