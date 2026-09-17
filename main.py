import os
from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

local_server = True
app = Flask(__name__)


app.secret_key = 'momos'

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
ABOUT_TEXT = os.getenv('about_text')
NO_OF_POSTS = int(os.getenv('no_of_posts'))
LOGIN_IMAGE = os.getenv('login_image')
ADMIN_USER = os.getenv('admin_user')
ADMIN_PASS = os.getenv('admin_password')


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

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)
    tagline = db.Column(db.String(12), nullable=True)
    
    


@app.route("/")
def home ():
   posts = Posts.query.filter_by().all() [0:NO_OF_POSTS]
   return render_template('index.html', 
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE,
        posts=posts)

@app.route("/about")
def about ():
   return render_template('about.html', 
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE,
        about_text=ABOUT_TEXT)

@app.route("/dashboard", methods=['GET','POST'])
def dashboard ():
   if ('user' in session and session['user'] ==ADMIN_USER):
      posts = Posts.query.all()
      return render_template('dashboard.html', posts = posts,fb_url=FB_URL,
              tw_url=TW_URL,
              gh_url=GH_URL,
              blog_name=BLOG_NAME,
              tag_line=TAG_LINE,
              about_text=ABOUT_TEXT)

   
   if(request.method== 'POST'):
      username = request.form.get('uname')
      userpass = request.form.get('pass')
      if(username == ADMIN_USER and userpass == ADMIN_PASS):
         #set the session variable
         session['user'] = username
         posts = Posts.query.all()
         return render_template('dashboard.html', posts = posts, fb_url=FB_URL,
                 tw_url=TW_URL,
                 gh_url=GH_URL,
                 blog_name=BLOG_NAME,
                 tag_line=TAG_LINE,
                 about_text=ABOUT_TEXT)
    
   return render_template('login.html',blog_name=BLOG_NAME, login_image=LOGIN_IMAGE)

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

@app.route("/post/<string:post_slug>", methods = ['GET'])
def post (post_slug):
   post = Posts.query.filter_by(slug=post_slug).first()
   
   return render_template('post.html',
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE,
        post=post)

app.run(debug = True)