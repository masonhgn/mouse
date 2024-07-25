from Exchange import Exchange
import numpy as np
from Client import Client
if __name__ == "__main__":
    
    exchange = Exchange()
    
  
    a = exchange.register_client(100000)
    b = exchange.register_client(100000)


    exchange.submit_order(a,'buy','limit',50,'A',40)
    exchange.submit_order(b,'sell','limit',50,'A',35)
    

    