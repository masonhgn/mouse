from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from Exchange import Exchange
from passlib.hash import pbkdf2_sha256
import threading
import time
import signal
import sys


app = Flask(__name__)
app.secret_key = '1234'

exchange = Exchange()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



# Register a signal handler for SIGINT (Ctrl+C)
def handle_shutdown(signal, frame):
    print("SIGINT, SAVING TO DATABASE")
    exchange.save_to_db()
    sys.exit(0)

# Set up the signal handler
signal.signal(signal.SIGINT, handle_shutdown)




@app.route('/')
def home():
    tickers = exchange.tickers_collection.find({}, {"_id": 0, "ticker": 1, "price": 1}) 
    tickers = list(tickers) 
    return render_template('home.html', tickers=tickers)



class User(UserMixin):
    def __init__(self, id, balance, username):
        self.id = id
        self.balance = balance
        self.username = username



def display_orderbook_passive():

    def printob():
        while True:
            orderbook = exchange.orderbooks.get('GOOG')
            orderbook.print()
            time.sleep(1)
    
    thread = threading.Thread(target=printob)
    thread.daemon = True  # This makes sure the thread will exit when the main program does
    thread.start()

display_orderbook_passive()

@login_manager.user_loader
def load_user(user_id):
    client = exchange.get_client(user_id)
    if client:
        return User(client.client_id, client.balance, client.username)
    return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_data = exchange.get_user(username)

        if user_data and pbkdf2_sha256.verify(password, user_data['password']):
            user = User(str(user_data['_id']), user_data['balance'], username)
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('order_submission'))
        flash('Invalid username or password', 'danger')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        balance = 100000  
        
        if exchange.get_client_by_username(username):
            flash('Username already taken', 'danger')
            return render_template('register.html')

        client_id = exchange.register_client(balance, username, password)
        new_user = User(client_id, balance, username)
        login_user(new_user)
        flash('Registration successful!', 'success')
        return redirect(url_for('order_submission'))

    return render_template('register.html')



@app.route('/add_ticker', methods=['POST'])
def add_ticker():
    data = request.get_json()
    ticker = data['ticker']
    price = data['price']
    bid = data['bid']
    ask = data['ask']
    volume = data['volume']
    
 
    exchange.add_ticker(ticker, price, bid, ask, volume)
    
    return jsonify({"success": True, "message": f"Ticker {ticker} added successfully"})


@app.route('/submit_order', methods=['POST'])
@login_required
def submit_order():
    try:
        data = request.get_json()


        required_fields = ['ticker', 'side', 'type', 'quantity']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            flash(f"Missing fields: {', '.join(missing_fields)}", 'danger')
            return jsonify({"success": False, "message": "Missing required fields"}), 400

        client_id = current_user.id  
        ticker = data['ticker']
        side = data['side']
        order_type = data['type']
        quantity = data['quantity']
        price = data.get('price')

      
        if ticker not in exchange.orderbooks:
            flash(f"Ticker {ticker} not found in the order books!", 'danger')
            return jsonify({"success": False, "message": f"Ticker {ticker} not found"}), 404

     
        if order_type == 'limit' and price is None:
            flash("Limit orders require a price", 'danger')
            return jsonify({"success": False, "message": "Limit orders require a price"}), 400

        exchange.submit_order(client_id, side, order_type, quantity, ticker, price)
        flash("Order submitted successfully", 'success')
        return jsonify({"success": True, "message": "Order submitted successfully"})

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
        return jsonify({"success": False, "message": "An error occurred"}), 500


@app.route('/order_book/<ticker>', methods=['GET'])
@login_required
def get_order_book(ticker):
    orderbook = exchange.orderbooks.get(ticker)
    if not orderbook:
        return jsonify({"buy_orders": [], "sell_orders": []})


    buy_orders = [
        {
            "client_id": orderbook.order_lookup[order_id].client_id,
            "quantity": orderbook.order_lookup[order_id].quantity,
            "price": orderbook.order_lookup[order_id].price
        }
        for order_id in orderbook.orderbook['buy']
    ]

    sell_orders = [
        {
            "client_id": orderbook.order_lookup[order_id].client_id,
            "quantity": orderbook.order_lookup[order_id].quantity,
            "price": orderbook.order_lookup[order_id].price
        }
        for order_id in orderbook.orderbook['sell']
    ]

    return jsonify({"buy_orders": buy_orders, "sell_orders": sell_orders})


@app.route('/order_submission', methods=['GET', 'POST'])
@login_required
def order_submission():
    if request.method == 'POST':
        client_id = current_user.id
        ticker = request.form['ticker'].upper()
        side = request.form['side']
        order_type = request.form['type']
        quantity = int(request.form['quantity'])
        
        price = None
        if order_type == 'limit':
            price = float(request.form['price'])
        
        if ticker not in exchange.orderbooks:
            flash(f"Ticker {ticker} not found!", 'danger')
            return redirect(url_for('order_submission'))
        
        exchange.submit_order(client_id, side, order_type, quantity, ticker, price)
        flash("Order submitted successfully", 'success')
        return redirect(url_for('order_submission'))
    
    open_orders = exchange.get_open_orders(current_user.id)
    return render_template('order_submission.html', open_orders=open_orders)


def get_open_orders(self, client_id):
    open_orders = []
    for ticker, orderbook in self.orderbooks.items():
        for order_id in orderbook.orderbook['buy'] + orderbook.orderbook['sell']:
            order = orderbook.order_lookup[order_id]
            if order.client_id == client_id and order.filled_quantity < order.quantity:
                open_orders.append({
                    'ticker': ticker,
                    'side': order.side,
                    'quantity': order.quantity,
                    'filled_quantity': order.filled_quantity,
                    'price': order.price
                })
    return open_orders


@app.route('/open_orders', methods=['GET'])
@login_required
def fetch_open_orders():
    orders, open_orders = exchange.get_open_orders(current_user.id), []
    for order_id, order in orders.items():
        open_orders.append({
                    'ticker': order.ticker,
                    'side': order.side,
                    'quantity': order.quantity,
                    'filled_quantity': order.filled_quantity,
                    'price': order.price,
                    'executed': order.executed
                })

    return jsonify(open_orders)