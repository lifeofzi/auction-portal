from flask import Flask, request, render_template , session, redirect , url_for
from flaskext.mysql import MySQL
import os
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
    return render_template('index.html')

@app.route('/home')
def home():
    if session.get('logged_in',False)== True :
        return render_template('home.html',username=session['user_ID'])
    else: 
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email',' ')
        password = request.form.get('password',' ')
        cursor = mysql.connect().cursor()
        cursor.execute("SELECT * from users where email='" + email + "' and password='" + password + "'") #Correct here
        data = cursor.fetchone()
        if data is None:
            return "Username or Password is wrong"
        else:
            print data
            session['logged_in'] = True
            session['user_ID'] = data[0]
            #print session
            print  "Logged in successfully"
            return redirect(url_for('home'))
    else:
        return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print request.form.get('user','assd')
        return 'Hello'
    else:
        return render_template('signup.html')


if __name__ == '__main__': # Start the flask server when running this script.
   app.run('0.0.0.0',int(os.environ.get('PORT',8082)) , debug = True)
