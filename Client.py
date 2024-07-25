import uuid


class Client:
    def __init__(self, balance):
        self.client_id = str(uuid.uuid4())
        self.balance = balance
        self.portfolio = {}
    


    def update_portfolio(self, ticker, quantity):
        if ticker in self.portfolio:
            self.portfolio[ticker] += quantity
        else:
            self.portfolio[ticker] = quantity

        #if we sold all of a security, let's make sure we remove it from our portfolio
        if self.portfolio[ticker] == 0: del self.portfolio[ticker]


    def update_balance(self, amount):
        self.balance += amount
