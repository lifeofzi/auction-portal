from flask import Flask, request, render_template , session, redirect , url_for , flash, jsonify,json
from flaskext.mysql import MySQL
import os
import pymysql

app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'AuctionPortal'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SECRET_KEY'] = '12345'

mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def index():
    return redirect(url_for('home'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in',False) == True:
        return redirect(url_for('home'))
    if request.method == 'POST':
        error = None
        email = request.form.get('email',' ')
        password = request.form.get('password',' ')
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        login_querry = "SELECT * from users where email=%s and password=%s"
        cursor.execute(login_querry , (email , password ))
        data = cursor.fetchone()
        if data is None:
            error = 'Invalid credentials'
            return render_template('login.html', error=error)
            #return "Username or Password is wrong"
        else:
            print data
            session['logged_in'] = True
            session['user_ID'] = data['id']
            session['user_name'] = data['name']
            session['user_balance'] = data['account_balance']
            #print session
            flash('You were successfully logged in, ' + session['user_name'],'success')
            return redirect(url_for('home'))
    else:
        
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('logged_in',False) == True:
        flash('Login first!' , 'danger')
        return redirect(url_for('home'))
    if request.method == 'POST':
        error = None
        name =  request.form.get('name',' ')
        email=  request.form.get('email',' ')
        password =  request.form.get('password',' ')
        signup_querry = "Insert INTO users (name,email,password,dateofjoin) VALUES (%s , %s, %s, CURDATE())"
        conn = mysql.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(signup_querry , (name, email, password))
            conn.commit()
            flash(u'Account Created Successfully! Login Now.', 'success')
            return redirect(url_for('login'))
        except:
            error = 'User with this email already exists!'
            return render_template('signup.html',error=error)
    else:
        return render_template('signup.html')



@app.route('/create', methods=['GET', 'POST'])
def create():
    if session.get('logged_in',False) == False :
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            error = None
            name =  request.form.get('name',' ')
            desc=  request.form.get('description',' ')
            startprice = float(request.form.get('startprice',1))
            hours = int(request.form.get('hours', 0))
            minutes = int(request.form.get('minutes', 2))
            increment = float(request.form.get('increment',1))
            picture1 = request.form.get('picture1',' ')
            picture2 = request.form.get('picture2',' ')
            picture3 =request.form.get('picture3',' ')
            category = int(request.form.get('category',1))
            auction_create_querry = "Insert INTO auctions (name,description,admin_id,start_time,end_time,start_price,increment_price,picture1,picture2,picture3,category_id) VALUES (%s , %s ,%s, NOW(), NOW() + INTERVAL %s HOUR + INTERVAL %s MINUTE, %s , %s, %s, %s, %s , %s)"
            conn = mysql.connect()
            cursor = conn.cursor()
            print (name, desc, session['user_ID'] , hours, minutes, startprice, increment, picture1, picture2 ,picture3, category)
            cursor.execute(auction_create_querry , (name, desc, session['user_ID'] , hours, minutes, startprice, increment, picture1, picture2 ,picture3, category))
            conn.commit()
            flash(u'Auction Started!', 'success')
            return redirect(url_for('home'))
        except Exception as e: 
            print(e)
            error = 'Could Not Create Auction!'
            return render_template('create.html',error=error)
    else:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        categories_querry = "SELECT * from categories"
        cursor.execute(categories_querry)
        data = cursor.fetchall()
        return render_template('create.html' , get = data)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it's there
    session['user_ID']=None
    session['logged_in']=False
    session['user_name']=None
    session['user_balance']=None
    return redirect(url_for('login'))


@app.route('/home' , methods=['GET'])
def home():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        
        #Updating Balance
        new_balance_querry = "SELECT U.account_balance FROM users U WHERE U.id= %s"
        new_balance_cursor= conn.cursor(pymysql.cursors.Cursor)
        new_balance_cursor.execute(new_balance_querry, session['user_ID'])
        balance = new_balance_cursor.fetchone()
        session['user_balance'] = balance[0]
        
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        get_auctions_querry = "SELECT * FROM auctions WHERE end_time > NOW()"
        cursor.execute(get_auctions_querry)
        data = cursor.fetchall()
        for d in data:
            # print d
            auction_id = d['auction_id']
            bid_cursor = conn.cursor(pymysql.cursors.Cursor)
            bid_querry = "SELECT MAX(B.bid_amount) , COUNT(B.bid_id) from auctions A , bids B WHERE A.end_time > NOW() AND A.auction_id = B.auction_id AND A.auction_id = %s"
            bid_cursor.execute(bid_querry, auction_id)
            bid_result=bid_cursor.fetchone()

            d['max_bid']=bid_result[0]
            d['no_bids']=bid_result[1]
            
            #Getting Max-Bidder
            max_bidder_cursor = conn.cursor(pymysql.cursors.Cursor)
            max_bidder_querry = "SELECT U.name , U.avatar FROM users U, auctions A , bids B WHERE B.user_id = U.id AND B.auction_id = A.auction_id AND A.auction_id = %s AND B.bid_amount IN ( SELECT MAX(B.bid_amount) from auctions A , bids B WHERE A.auction_id = B.auction_id AND A.auction_id = %s )"
            max_bidder_cursor.execute(max_bidder_querry, (auction_id, auction_id))
            max_bidder_result=max_bidder_cursor.fetchone()
            if (max_bidder_result):
                d['max_bidder_name']=max_bidder_result[0]
                d['max_bidder_avatar']=max_bidder_result[1]
            else:
                d['max_bidder_name']=' '
                d['max_bidder_avatar']=' '
                
            # Getting Admin
            admin_info_querry = "SELECT U.name , U.avatar FROM users U, auctions A WHERE A.admin_id = U.id AND A.auction_id = %s"
            admin_info_cursor = conn.cursor(pymysql.cursors.Cursor)
            admin_info_cursor.execute(admin_info_querry, auction_id)
            admin_info_result = admin_info_cursor.fetchone()
            d['admin_name'] = admin_info_result[0]
            d['admin_avatar'] = admin_info_result[1]
            
        now_querry  = "Select DATE_FORMAT( NOW() , '%Y-%m-%d %H:%i:%S') "
        now_cursor = conn.cursor(pymysql.cursors.Cursor)
        now_cursor.execute(now_querry)
        now = now_cursor.fetchone()
        print "-----------------"
        print now
                                 # Has active auctions 
        return render_template('home.html', auctions = data, now = now[0])

@app.route('/bid' , methods=['POST'])
def place_bid():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = session['user_ID']
        auction_id = int(request.form.get('auction_id'))
        
        bid_amount = float(request.form.get('bid_amount'))
        #Finding User
        conn = mysql.connect()
        finding_user_querry = "SELECT B.user_id FROM bids B WHERE B.user_id= %s AND B.auction_id = %s"
        finding_user_cursor= conn.cursor(pymysql.cursors.Cursor)
        finding_user_cursor.execute(finding_user_querry,( user_id , auction_id))
        if(not finding_user_cursor.fetchone()):
            auction_create_querry = "Insert INTO bids (bid_amount,bid_time,user_id,auction_id) VALUES (%s , NOW() ,%s, %s)"
            try:
                cursor = conn.cursor()
                cursor.execute(auction_create_querry , (bid_amount, user_id, auction_id))
                conn.commit()
                flash(u'Bid Placed Successfully!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                print "--------------------------------------------------------------------"
                error = 'Could not place bid!'
                print error
                print e
                print "--------------------------------------------------------------------"
                flash(u'Bid Could not be placed! - 1', 'danger')
                return redirect(url_for('home'))
        else:
            conn = mysql.connect()
            auction_create_querry = "Update bids set bid_amount = %s WHERE user_id = %s AND auction_id = %s"
            
            #get existing bid placed
            get_existing_user_querry = "Select max(bid_amount) FROM bids WHERE user_id = %s AND auction_id = %s"
            get_existing_user_cursor = conn.cursor()
            get_existing_user_cursor.execute(get_existing_user_querry , ( user_id, auction_id))
            get_user_result = get_existing_user_cursor.fetchone()
            existing_bid = get_user_result[0]
            
            #get present account balance
            get_user_balance_querry = "Select account_balance FROM users WHERE id = %s"
            get_user_balance_cursor = conn.cursor()
            get_user_balance_cursor.execute(get_user_balance_querry , ( user_id))
            get_user_balance_result = get_user_balance_cursor.fetchone()
            user_balance = get_user_balance_result[0]
            
            
            try:
                cursor = conn.cursor()
                cursor.execute(auction_create_querry , (bid_amount, user_id, auction_id))
                conn.commit()
                flash(u'Bid Placed Successfully!', 'success')
                return redirect(url_for('home'))
            except Exception as e:
                print "--------------------------------------------------------------------"
                print e
                print "--------------------------------------------------------------------"
                flash(u'Bid Could not be placed! -2', 'danger')
                return redirect(url_for('home'))
        


@app.route('/dashboard' , methods=['GET'])
def dashboard():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        user_id = session['user_ID']
        conn = mysql.connect()
        querry = "Select B.bid_amount , B.bid_time, A.name FROM auctions A, bids B  WHERE user_id = %s AND B.auction_id = A.auction_id"
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(querry , (user_id))
        data = cursor.fetchall()

        
        #return jsonify(data)
        return render_template('dashboard.html', auctions = data)
        
@app.route('/mypurchases' , methods=['GET'])
def mypurchases():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        user_id = session['user_ID']
        conn = mysql.connect()
        querry = "Select P.price , A.name FROM auctions A, purchases P  WHERE user_id = %s AND P.auction_id = A.auction_id"
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(querry , (user_id))
        data = cursor.fetchall()
        #return jsonify(data)
        return render_template('mypurchases.html', auctions = data)
        
@app.route('/categories' , methods=['GET'])
def categories():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        #Updating Balance
        new_balance_querry = "SELECT U.account_balance FROM users U WHERE U.id= %s"
        new_balance_cursor= conn.cursor(pymysql.cursors.Cursor)
        new_balance_cursor.execute(new_balance_querry, session['user_ID'])
        balance = new_balance_cursor.fetchone()
        session['user_balance'] = balance[0]
        
        
        user_id = session['user_ID']
        querry = "Select category_id, name from categories"
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(querry)
        cat_data = cursor.fetchall()
    
        for f in cat_data:
            print "------------------------------------"
            print f['category_id']
            print "------------------------------------"
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            get_auctions_querry = "SELECT * FROM auctions WHERE end_time > NOW() AND category_id = %s"
            cursor.execute(get_auctions_querry, (f['category_id']))
            data = cursor.fetchall()
            for d in data:
                auction_id = d['auction_id']
                bid_cursor = conn.cursor(pymysql.cursors.Cursor)
                bid_querry = "SELECT MAX(B.bid_amount) , COUNT(B.bid_id) from auctions A , bids B WHERE A.end_time > NOW() AND A.auction_id = B.auction_id AND A.auction_id = %s"
                bid_cursor.execute(bid_querry, auction_id)
                bid_result=bid_cursor.fetchone()

                d['max_bid']=bid_result[0]
                d['no_bids']=bid_result[1]
            
                #Getting Max-Bidder
                max_bidder_cursor = conn.cursor(pymysql.cursors.Cursor)
                max_bidder_querry = "SELECT U.name , U.avatar FROM users U, auctions A , bids B WHERE B.user_id = U.id AND B.auction_id = A.auction_id AND A.auction_id = %s AND B.bid_amount IN ( SELECT MAX(B.bid_amount) from auctions A , bids B WHERE A.auction_id = B.auction_id AND A.auction_id = %s )"
                max_bidder_cursor.execute(max_bidder_querry, (auction_id, auction_id))
                max_bidder_result=max_bidder_cursor.fetchone()
                if (max_bidder_result):
                    d['max_bidder_name']=max_bidder_result[0]
                    d['max_bidder_avatar']=max_bidder_result[1]
                else:
                    d['max_bidder_name']=' '
                    d['max_bidder_avatar']=' '
                
                # Getting Admin
                admin_info_querry = "SELECT U.name , U.avatar FROM users U, auctions A WHERE A.admin_id = U.id AND A.auction_id = %s"
                admin_info_cursor = conn.cursor(pymysql.cursors.Cursor)
                admin_info_cursor.execute(admin_info_querry, auction_id)
                admin_info_result = admin_info_cursor.fetchone()
                d['admin_name'] = admin_info_result[0]
                d['admin_avatar'] = admin_info_result[1]
            f['data'] = data
        #return jsonify(cat_data)
        return render_template('categories.html', data = cat_data)




@app.route('/history' , methods=['GET'])
def history():
    if session.get('logged_in',False) == False:
        flash('Login first!' , 'danger')
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        get_auctions_querry = "SELECT * FROM auctions WHERE end_time < NOW()"
        cursor.execute(get_auctions_querry)
        data = cursor.fetchall()
        for d in data:
            # print d
            auction_id = d['auction_id']
            bid_cursor = conn.cursor(pymysql.cursors.Cursor)
            bid_querry = "SELECT MAX(B.bid_amount) , COUNT(B.bid_id) from auctions A , bids B WHERE A.end_time < NOW() AND A.auction_id = B.auction_id AND A.auction_id = %s"
            bid_cursor.execute(bid_querry, auction_id)
            bid_result=bid_cursor.fetchone()

            d['max_bid']=bid_result[0]
            d['no_bids']=bid_result[1]
            
            #Getting Max-Bidder
            max_bidder_cursor = conn.cursor(pymysql.cursors.Cursor)
            max_bidder_querry = "SELECT U.name , U.avatar FROM users U, auctions A , bids B WHERE B.user_id = U.id AND B.auction_id = A.auction_id AND A.auction_id = %s AND B.bid_amount IN ( SELECT MAX(B.bid_amount) from auctions A , bids B WHERE A.auction_id = B.auction_id AND A.auction_id = %s )"
            max_bidder_cursor.execute(max_bidder_querry, (auction_id, auction_id))
            max_bidder_result=max_bidder_cursor.fetchone()
            if (max_bidder_result):
                d['max_bidder_name']=max_bidder_result[0]
                d['max_bidder_avatar']=max_bidder_result[1]
            else:
                d['max_bidder_name']=' '
                d['max_bidder_avatar']=' '
                
            # Getting Admin
            admin_info_querry = "SELECT U.name , U.avatar FROM users U, auctions A WHERE A.admin_id = U.id AND A.auction_id = %s"
            admin_info_cursor = conn.cursor(pymysql.cursors.Cursor)
            admin_info_cursor.execute(admin_info_querry, auction_id)
            admin_info_result = admin_info_cursor.fetchone()
            d['admin_name'] = admin_info_result[0]
            d['admin_avatar'] = admin_info_result[1]
            
        print "-----------------"
        print data
                                 # Has active auctions 
        return render_template('history.html', auctions = data)










if __name__ == '__main__': # Start the flask server when running this script.
   #app.run('0.0.0.0',int(os.environ.get('PORT',8082))  , debug = True)
   app.run('0.0.0.0',int(8082)  , debug = True)
