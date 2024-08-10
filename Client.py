class Position:
    def __init__(self, quantity, price):
        self.quantity = quantity
        self.price = price
        self.total_value = quantity * price

class Client:
    def __init__(self, client_data):
        self.client_id = client_data['_id']
        self.balance = client_data['balance']
        self.portfolio = client_data['portfolio']

    def update_portfolio(self, ticker, quantity, price):
        if ticker in self.portfolio:
            self.portfolio[ticker]['quantity'] += quantity
            self.portfolio[ticker]['total_value'] = quantity * price
        else:
            self.portfolio[ticker] = Position(quantity, price).__dict__

        if self.portfolio[ticker]['quantity'] == 0:
            del self.portfolio[ticker]
