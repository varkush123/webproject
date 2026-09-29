import os
import math
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
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
UPLOAD_LOCATION = os.getenv('upload_location')

app.config['UPLOAD_FOLDER'] = UPLOAD_LOCATION
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
    img_file = db.Column(db.String(15), nullable=True)
    tagline = db.Column(db.String(12), nullable=True)
    
    


@app.route("/")
def home ():
   posts = Posts.query.filter_by().all() 
   last = math.ceil(len(posts)/NO_OF_POSTS)
   #[0:NO_OF_POSTS]
   #posts = posts[]
   page = request.args.get('page')
   if(not str(page).isnumeric()):
      page = 1
   page=int(page)
   posts = posts[(page-1)*NO_OF_POSTS: (page-1)*NO_OF_POSTS+ NO_OF_POSTS]
   #pagination logic
   #first
   if (page==1):
      prev = "#"
      next = "/?page="+ str(page+1)
   elif(page==last):
      prev = "/?page="+ str(page-1)
      next = "#"
   else:
      prev = "/?page="+ str(page-1)
      next = "/?page="+ str(page+1)

  

   return render_template('index.html', prev=prev, next=next,
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


@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
   if ('user' in session and session['user'] ==ADMIN_USER):
      if request.method == 'POST':
         box_title = request.form.get('title')
         tagline = request.form.get('tagline')
         slug = request.form.get('slug')
         content = request.form.get('content')
         img_file = request.form.get('img_file')
         date = datetime.now()

         if sno == '0':
            post = Posts(title=box_title, slug=slug, content=content, img_file=img_file, tagline=tagline, date=date)
            db.session.add(post)
            db.session.commit()

         else:
            post = Posts.query.filter_by(sno=sno).first()
            post.title = box_title
            post.slug = slug
            post.content = content
            post.tagline = tagline
            post.img_file = img_file
            post.date = date
            db.session.commit()
            return redirect('/edit/'+sno)
      post = Posts.query.filter_by(sno=sno).first() 
      return render_template('edit.html', blog_name=BLOG_NAME, fb_url=FB_URL, tw_url=TW_URL, gh_url=GH_URL, post=post)


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
   if ('user' in session and session['user'] ==ADMIN_USER):
      if(request.method== 'POST'):
         f= request.files['file1']
         f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
         return "Uploaded successfully"



@app.route("/logout")
def logout():
   session.pop('user')
   return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
   if ('user' in session and session['user'] ==ADMIN_USER):
      post = Posts.query.filter_by(sno=sno).first()
      db.session.delete(post)
      db.session.commit()
   return redirect('/dashboard')


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