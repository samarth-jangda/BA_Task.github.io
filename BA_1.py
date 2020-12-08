import os
import sys
from functools import wraps

import requests
from flask import render_template, request, Flask, session, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_socketio import SocketIO
from flask_ngrok import run_with_ngrok
from sqlalchemy.testing import db
from werkzeug.utils import secure_filename
import pandas as pd
from pandas import DataFrame
from flask import send_from_directory
from IPython.display import HTML
import unicodedata as ud
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.config["Secret_Key"] = "6a79852e71abd3dc5e4d#"
#run_with_ngrok(app)
app.debug = True
app.secret_key = "AsdHahD12@!#@3@#@#554"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSORD'] = ''
app.config["MYSQL_DB"] = 'bookbank'
app.config["SQLALCHEMY_DATABASE_URL"] = "http://localhost/phpmyadmin/tbl_structure.php?db=register&table=register"
app.config["MYSQL CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
socketio = SocketIO(app)

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "logged in" in session:
            return f(*args,*kwargs)
        else:
            flash("Unauthorized, Please log in","Danger")
            return redirect(url_for("index"))
    return wrap

def not_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if "logged in" in session:
            return f(*args,*kwargs)
        else:
            flash("Unauthorized", "danger")
            return redirect(url_for("index"))
    return wrap

@app.route("/", methods=(["GET", "POST"]))
def index():
    # form = loginform()
    try:
        con = mysql.connection.cursor()
        print("Connected to database")
    except Exception as e:

        sys.exit(e)
    # cur = con.cursor()
    con.execute("SELECT * FROM logins")
    data = DataFrame(data=con.fetchall())

    if request.method == "POST":

        username = request.form['username']
        password = request.form["password"]

        cur = mysql.connection.cursor()

        if username in list(data[0]):
            if password == '#Admin123':
                return render_template('admin.html')
            if password not in list(data[1]):
                flash("You need to log in")
                return render_template("login.html")

            flash('Wrong password enter again')
            return render_template('index.html')

        else:
            cur.execute("INSERT INTO logins(username,password) VALUES (%s,%s)",
                         (username, password))
            mysql.connection.commit()
            cur.close()

            # if cur.username != username:
            # flash("you writtern wrong evoc_id")

            flash("Submission-Successful")
            return render_template("index.html")
    return render_template("login.html")
@app.route("/abc",methods = (["Get","Post"]))
def login():
    # form = loginform()
    try:
        con = mysql.connection.cursor()
        print("Connected to database")
    except Exception as e:
        sys.exit(e)
    #cur = con.cursor()
    con.execute("SELECT * FROM logins")
    data = DataFrame(data=con.fetchall())

    if request.method == "POST":

        username = request.form['username']
        password = request.form['password']
        #c_password = request.form['confirm_evoc_id']
        cur = mysql.connection.cursor()

        if username in list(data[0]):
            if int(password) not in list(data[1]):
                flash("the following evoc_id is wrong")
                return render_template("logins.html")
            else:
                return render_template('index.html')
        else:
            flash("You need to sign up ")
            return render_template("logins.html")

    return render_template('index.html')
@app.route('/page2')
def page():
    return render_template("subpage.html")

@app.route('/lib',methods=(["GET","POST"]))
def library():

    if request.method == "POST":
        bookname = request.form["bookname"]
        author = request.form["author"]
        genre = request.form["genre"]
        published_yr = request.form["published_yr"]
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO library(bookname,author,genre,published_yr) VALUES(%s,%s,%s,%s)",(bookname,author,genre,published_yr))
        mysql.connection.commit()
        cur.close()
        return render_template("admin.html")
    return render_template("admin.html")

#Upload images here
UPLOAD_FOLDER = "C:/BA_task1/static/images"
ALLOWED_EXTENSIONS = {'txt','png','gif'}
def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
#Providing the route to an html

@app.route('/upload',methods=["GET","POST"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No Flash Apart")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == '':
            flash("No File Selected")
            return redirect(request.url)
        else:
        #if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"],filename))
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO images(img_dir) VALUES(%s)", (filename,))
            cur.connection.commit()
            cur.close()
            return redirect(url_for('uploaded_file',filename=filename))

    return render_template("admin.html")



@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route("/display/<filename>",methods=["GET","POST"])
def display_image(filename):
    print(filename)
    return redirect(url_for('images.html',img_name ='uploads/' + filename),code=301)

#books are being searched bu user

@app.route("/books",methods = ["GET","POST"])
def search_books():
    cur = mysql.connection.cursor()
    cur.execute("SELECT bookname FROM LIBRARY")
    data_0 = DataFrame(data=cur.fetchall())
    #print(data_0)
    List_1 = data_0[0]
    cur.execute("SELECT bookname FROM LIBRARY")
    a = DataFrame(data=cur.fetchall())
    cur.execute("SELECT * FROM IMAGES")
    b = DataFrame(data=cur.fetchall())
    frame = [a, b]
    New_data = pd.concat(frame, axis=1)
    print(New_data)


    if request.method == "POST":
        books = request.form.get("books", None)
        if books not in list(New_data[0]):
            #here match the correspondng pic of book chosen by user
            pic = New_data[1]
            print(pic)
    cur.close()


    #return render_template(url_for("pic.html",img_name = 'uploads/' + filename),code=301)

    return render_template("books.html",lst_items = List_1)


#basically joining the databases table for finding image according to user search

from werkzeug.middleware.shared_data import SharedDataMiddleware
app.add_url_rule("/uploads/<filename>",'uploaded_file',build_only=True)
#app.wsgi_app = SharedDataMiddleware(app.wsgi_app,{'/uploads': app.config["UPLOAD_FOLDER"]})

if __name__ == '__main__':
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.run()