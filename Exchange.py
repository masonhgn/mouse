from OrderBook import OrderBook

class Exchange:

    def __init__(self):

        self.tickers = [
            'A',
            'B',
            'C',
        ]
        self.create_orderbooks_from_file('tickers.txt')
            

    def create_orderbooks_from_file(filename: str) -> dict:
        orderbooks = {}
        
        with open(filename, 'r') as file:
            for line in file:
                ticker, price = line.strip().split()
                price = float(price)
                orderbooks[ticker] = OrderBook(ticker, price)
        
        self.orderbooks = orderbooks


    def submit_order(self, )

    