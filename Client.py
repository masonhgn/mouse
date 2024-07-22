class Client:
    def __init__(self, client_id, balance):
        self.client_id = client_id
        self.balance = balance
        self.portfolio = {}  # Dictionary to hold ticker and quantity

    def update_portfolio(self, ticker, quantity):
        if ticker in self.portfolio:
            self.portfolio[ticker] += quantity
        else:
            self.portfolio[ticker] = quantity

    def update_balance(self, amount):
        self.balance += amount
