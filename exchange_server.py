from flask import Flask, request, jsonify, render_template, redirect, url_for
from Exchange import Exchange

app = Flask(__name__)
exchange = Exchange()

@app.route('/register_client', methods=['POST'])
def register_client():
    data = request.get_json()
    balance = data['balance']
    client_id = exchange.register_client(balance)
    print('registered client '+client_id)
    return jsonify({"client_id": client_id})

@app.route('/submit_order', methods=['POST'])
def submit_order():
    data = request.get_json()
    client_id = data['client_id']
    ticker = data['ticker']
    side = data['side']
    order_type = data['type']
    quantity = data['quantity']
    price = data.get('price')
    
    exchange.submit_order(client_id, side, order_type, quantity, ticker, price)
    return jsonify({"success": True, "message": "Order submitted successfully"})

@app.route('/order_book/<ticker>', methods=['GET'])
def get_order_book(ticker):
    orderbook = exchange.orderbooks.get(ticker)
    if not orderbook:
        return jsonify({"buy_orders": [], "sell_orders": []})

    buy_orders = [{"client_id": o.client_id, "side": o.side, "type": o.type, "quantity": o.quantity, "price": o.price} for o in orderbook.orderbook['buy']]
    sell_orders = [{"client_id": o.client_id, "side": o.side, "type": o.type, "quantity": o.quantity, "price": o.price} for o in orderbook.orderbook['sell']]
    
    return jsonify({"buy_orders": buy_orders, "sell_orders": sell_orders})

@app.route('/orderbook_page/<ticker>', methods=['GET', 'POST'])
def orderbook_page(ticker):
    if request.method == 'POST':
        client_id = request.form['client_id']
        side = request.form['side']
        order_type = request.form['type']
        quantity = int(request.form['quantity'])
        price = float(request.form['price']) if request.form['price'] else None
        
        exchange.submit_order(client_id, side, order_type, quantity, ticker, price)
        return redirect(url_for('orderbook_page', ticker=ticker))

    return render_template('orderbook.html', ticker=ticker)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
