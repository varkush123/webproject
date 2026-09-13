import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

local_server = True
app = Flask(__name__)
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

LOCAL_SERVER = os.getenv('local_server')
LOCAL_URI = os.getenv('local_uri')
PROD_URI = os.getenv('prod_uri')

FB_URL = os.getenv('fb_url')
TW_URL = os.getenv('tw_url')
GH_URL = os.getenv('gh_url')

BLOG_NAME = os.getenv('blog_name')
TAG_LINE = os.getenv('tag_line')

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL_USER
app.config['MAIL_PASSWORD'] = EMAIL_PASS

mail = Mail(app) 

if LOCAL_SERVER == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = LOCAL_URI
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = PROD_URI
db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12))
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def home ():
   return render_template('index.html', 
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE)

@app.route("/about")
def about ():
   return render_template('about.html', 
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE)

@app.route("/contact", methods = ['GET', 'POST'])
def contact ():
   if(request.method== 'POST'):
      # add entry to the database
      name = request.form.get('name')
      email   = request.form.get('email')
      phone   = request.form.get('phone')
      message   = request.form.get('message')
      
      entry = Contacts(name=name, phone_num= phone, msg= message, date= datetime.now(), email= email)
      db.session.add(entry)
      db.session.commit()
      mail.send_message('New Message from ' + name,
                        sender=email, 
                        recipients=[EMAIL_USER],
                        body = message + "\n" + phone
                        )     
   
   return render_template('contact.html', 
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE)

@app.route("/post")
def post ():
   return render_template('post.html',
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE)

app.run(debug = True)