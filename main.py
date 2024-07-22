from Exchange import Exchange
import numpy as np
if __name__ == "__main__":
    
    exchange = Exchange()
    
    for i in range(100):
        exchange.submit_order('A','buy','limit',np.random.randint(1,100),np.random.uniform(58,60))
        exchange.submit_order('A','sell','limit',np.random.randint(1,100),np.random.uniform(58,60))
    
    exchange.print_order_book('A')