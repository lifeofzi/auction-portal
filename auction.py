from flask import Flask,request
app = Flask(__name__)
import os

@app.route('/')
def index():
    
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'



if __name__ == '__main__': # Start the flask server when running this script.
   app.run('0.0.0.0',int(os.environ.get('PORT',8080)),debug = True)
