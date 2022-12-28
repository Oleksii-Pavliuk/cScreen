##
## cScreen is a web app which gives you ability to control your assets from one place 
##
##
##
##
##
from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from api import info1, info
from cs50 import SQL
from flask_apscheduler import APScheduler   


#Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
#Configure bcript
bcrypt = Bcrypt(app)
#Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
#Configure mail
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '6db3fdcdeaa784'
app.config['MAIL_PASSWORD'] = 'c8abd219513ca3'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#Scheduller config
app.config["SCHEDULER_API_ENABLED"] = True
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()   

#Connect databases
db = SQL("sqlite:///screen.db")

db_values = SQL("sqlite:///values.db")

#Setting up counter of login attempts

#Homepage
@app.route('/', methods = ['POST', 'GET'])
def index():
     return render_template('index.html')


#Registration
@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html', code = 0)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            return render_template('register.html',code = 1 ,alert = 'Insert username')
        if not password:
            return render_template('register.html',code = 1 ,alert = 'Insert password')
        if password != confirmation:
            return render_template('register.html',code = 1 ,alert = 'Passwords dont match')
        if len(db.execute('SELECT * FROM users WHERE username = ?',username)) > 0:
            return render_template('register.html',code = 1 ,alert = 'Username already exists')
        else:
            db.execute('INSERT INTO users (username,hash) VALUES (?,?)',username,bcrypt.generate_password_hash(password).decode('utf-8'))
            db_values.execute('CREATE TABLE ? (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,value INTEGER NOT NULL,date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)',username)
            return redirect('/login')

#Login function 
@app.route('/login', methods=["GET", "POST"])
def login():
    #Rendering login page or getting username and password from page
    if request.method == 'GET':
        return render_template('login.html',code = 0)
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    #Checking for correct input
        if not username:
            return render_template('login.html',code = 1 , alert= 'You need to input your username')

        if not password:
            return render_template('login.html',code = 1 , alert= 'You need to input your password')

        hash = db.execute('SELECT * FROM users WHERE username = ?', username)
        print(hash)
        if len(hash) != 1:
            return render_template('login.html',code = 1 , alert = 'Wrong username')
        else:
            #Checking password if user inputted wrong password 3 times redirecting him to reset password page
            if bcrypt.check_password_hash(hash[0]['hash'], password):
                session['user_id'] = username
                return redirect('/')
            else:
                return render_template('login.html',code = 1 , alert = 'Wrong password')

#Logout function
@app.route('/logout')
def logout():
    session.clear()

    return redirect("/")

#Requesting email from user to reset password 
@app.route('/email_reset',  methods=["GET", "POST"])
def email_reset():
    if request.method == 'GET':
        return render_template('reset_send_email.html', code = 0)
    else:
        email = request.form.get('email')
        rows = db.execute('SELECT * FROM users WHERE username = ?',email)
        if len(rows) != 1:
            return render_template('reset_send_email.html',code =1, alert='Wrong email')
        else:
            msg = Message('cScreen account password reset',sender =   'capetruha@gmail.com', recipients=[email])
            msg.body = 'http://127.0.0.1:5000/password_reset.html'            
            mail.send(msg)
            return render_template('reset.html')


#Password reset function
@app.route('/password_reset', methods=["GET", "POST"])
def password_reset():
    if request.method == 'GET':
        return render_template('password_reset.html',code = 0)
    else:
        password = request.form.get('password')
        confirmation  = request.form.get('confirmation')
        if not password:
            return render_template('password_reset.html',code = 1 , alert = 'Insert password')
        if password != confirmation:
            return render_template('password_reset.html',code = 1 , alert = 'Passwords dont match')






@app.route('/search', methods=['POST','GET'])
def search():
    return render_template('search.html')

@app.route('/coin')
def coin():
        coin = request.args.get("q")

        token = info1(coin)
        if token == 1:
            print('error 1 ')
            data = 1
            return jsonify(data)
        else:
            id = token['data']['id']
            symbol= token['data']['symbol']
            name = token['data']['name']
            price = token['data']['quote']['USD']['price']
            data = {'id': id,
                    'symbol':symbol,
                    'name': name , 
                    'price': price}
            return jsonify(data)


#Adds coins to acount from search page
@app.route('/add_coins', methods=['POST', 'GET'])
def add_coins():
    text = 'ok'
    try:
        name = request.form.get('name')
        amount = float(request.form.get('amount'))
        symbol = request.form.get('symbol')
        price = float(request.form.get('price'))
        db.execute('INSERT INTO transactions (userid,symbol,name,price,amount) VALUES((SELECT id FROM users WHERE username = ?),?,?,?,?)',session['user_id'],symbol,name,price,amount)
        return jsonify(text)
    except:
        text = 'eror'
        return jsonify(text)
#Adds transaction with amoun less than 0 to transactions from portfolio page
@app.route('/del_coins', methods=['POST', 'GET'])
def del_coin():
    text = 'ok'
    try:
        name = request.form.get('name')
        amount = 0 - float(request.form.get('amount'))
        symbol = request.form.get('symbol')
        price = float(request.form.get('price'))
        db.execute('INSERT INTO transactions (userid,symbol,name,price,amount) VALUES((SELECT id FROM users WHERE username = ?),?,?,?,?)',session['user_id'],symbol,name,price,amount)
        return jsonify(text)
    except:
        text = 'eror'
        return jsonify(text)


#Portfolio page
@app.route('/portfolio', methods=['POST','GET'])
def portfolio():
        #Getting all assets that user have and quantity of each asset 
        username = session['user_id']
        assets = db.execute('SELECT symbol,name,SUM(amount) FROM transactions WHERE userid = (SELECT id FROM users WHERE username = ?)  GROUP BY symbol HAVING SUM(amount) > 0 ORDER BY SUM(amount)*price DESC', username)
        #Assigning total value to zero 
        value = 0
        #Creating empy list for symbols to make request for all assets
        syms = []
        symbols = ''
        #Calculating total portfolio value
        for asset in assets:
            if asset['SUM(amount)'] > 0:
                #Getting actual price from Coinmarcetcap API for each coin
                token = info1(asset['symbol'])
                asset['id']= token['data']['id']
                asset['price'] = round(token['data']['quote']['USD']['price'],4)
                #Calculating total value
                value += (token['data']['quote']['USD']['price']*asset['SUM(amount)'])
                #Adding symbols to empty list
                symbols += ','+token['data']['symbol']
                syms.append(token['data']['symbol'])
        value = round(value, 2)
        #Making request to API for all of the assets s
        responce = info(symbols)
        #Empty list
        coins = []
        i = 0
        for asset in assets:
            coins.append({
                'x': responce['data'][syms[i]][0]['symbol'],
                'y': responce['data'][syms[i]][0]['quote']['USD']['percent_change_24h'],
                'z': responce['data'][syms[i]][0]['quote']['USD']['price']
            })
            i += 1
        return render_template('portfolio.html', username = username, value = value,assets = assets,tokens = coins)
    
#History page 
@app.route('/history')
def history():
    transactions = db.execute('SELECT * FROM transactions WHERE userid = (SELECT id FROM users WHERE username = ?) ORDER BY time',session['user_id'])
    values = db_values.execute('SELECT value,date FROM ? ORDER BY date ASC',session['user_id'])
    print(values)
    return render_template('history.html', transactions = transactions,values = values)



#Daily portfolios value writer
@scheduler.task('cron', id='value_writer',hour=10, minute = 0)
def value_execution():
    users = db.execute('SELECT username FROM users')

    for user in users:
        assets = db.execute('SELECT symbol,name,SUM(amount) FROM transactions WHERE userid = (SELECT id FROM users WHERE username = ?)  GROUP BY symbol HAVING SUM(amount) > 0 ORDER BY SUM(amount)*price DESC', user['username'])
        value = 0
        #Calculating total portfolio value
        for asset in assets:
            if asset['SUM(amount)'] > 0:
                #Getting actual price from Coinmarcetcap API for each coin
                token = info1(asset['symbol'])
                #Calculating total value
                value += (token['data']['quote']['USD']['price']*asset['SUM(amount)'])
        value = round(value, 2)
        db_values.execute('INSERT INTO ? (value) VALUES (?)',user['username'],value)

