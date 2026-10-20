import os
import math
from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
from supabase import create_client

import atexit
import requests
from apscheduler.schedulers.background import BackgroundScheduler


load_dotenv()

local_server = True
app = Flask(__name__)

@app.route('/hello')
def hello():
    return "Hello! Flask Blog is running.", 200





app.secret_key = os.getenv("FLASK_SECRET_KEY")



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
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY')



supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app.config['UPLOAD_FOLDER'] = UPLOAD_LOCATION




if LOCAL_SERVER == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = LOCAL_URI
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = PROD_URI

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_num = db.Column(db.String(50))
    msg = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(25), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=True)
    tagline = db.Column(db.Text, nullable=False)

    if os.getenv("local_server") == "True":
        img_file = db.Column("img_file", db.String(500), nullable=False)
    else:
        img_file = db.Column("image_url", db.String(500), nullable=False)










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
        posts=posts,
        index_bg=os.getenv('INDEX_BG', '')
        )




@app.route("/about")
def about():
    return render_template(
        'about.html',
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE,
        about_text=ABOUT_TEXT,
        about_bg=os.getenv('ABOUT_BG', '')
    )



@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == ADMIN_USER:
        posts = Posts.query.all()

        return render_template(
            'dashboard.html',
            posts=posts,
            fb_url=FB_URL,
            tw_url=TW_URL,
            gh_url=GH_URL,
            blog_name=BLOG_NAME,
            tag_line=TAG_LINE,
            about_text=ABOUT_TEXT,
            dashboard_bg=os.getenv('DASHBOARD_BG', '')
        )

    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if username == ADMIN_USER and userpass == ADMIN_PASS:
            # Set the session variable
            session['user'] = username
            posts = Posts.query.all()

            return render_template(
                'dashboard.html',
                posts=posts,
                fb_url=FB_URL,
                tw_url=TW_URL,
                gh_url=GH_URL,
                blog_name=BLOG_NAME,
                tag_line=TAG_LINE,
                about_text=ABOUT_TEXT,
                dashboard_bg=os.getenv('DASHBOARD_BG', '')
            )

    return render_template(
        'login.html',
        blog_name=BLOG_NAME,
        login_image=LOGIN_IMAGE
    )




@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == ADMIN_USER:

        if request.method == 'POST':
            box_title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            # Check whether an image file was selected
            uploaded_file = request.files.get('image_upload')

            if uploaded_file and uploaded_file.filename:
                try:
                    if not uploaded_file.content_type or not uploaded_file.content_type.startswith('image/'):
                        return "Please select a valid image file.", 400

                    # Create a unique filename to avoid duplicate names
                    original_name = secure_filename(uploaded_file.filename)

                    if not original_name:
                        return "Invalid image filename.", 400

                    filename = (
                        datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        + '_'
                        + original_name
                    )

                    # Upload image to Supabase
                    file_data = uploaded_file.read()

                    supabase.storage.from_("Images").upload(
                        filename,
                        file_data,
                        {"content-type": uploaded_file.content_type}
                    )

                    # Get the public URL
                    img_file = supabase.storage.from_("Images").get_public_url(
                        filename
                    )

                except Exception as e:
                    return f"Image upload failed: {str(e)}", 500

            # Create a new post
            if sno == '0':
                post = Posts(
                    title=box_title,
                    slug=slug,
                    content=content,
                    img_file=img_file,
                    tagline=tagline,
                    date=date
                )

                db.session.add(post)
                db.session.commit()

                session.pop('uploaded_image_url', None)

                return redirect('/dashboard')

            # Update an existing post
            else:
                post = Posts.query.filter_by(sno=int(sno)).first()

                if post is None:
                    return "Post not found", 404

                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tagline
                post.img_file = img_file
                post.date = date

                db.session.commit()

                session.pop('uploaded_image_url', None)

                return redirect('/edit/' + sno)

        # Display the form
        post = Posts.query.filter_by(sno=int(sno)).first()

        if sno != '0' and post is None:
            return "Post not found", 404

        return render_template(
            'edit.html',
            blog_name=BLOG_NAME,
            fb_url=FB_URL,
            tw_url=TW_URL,
            gh_url=GH_URL,
            post=post,
            edit_bg=os.getenv('EDIT_BG', '')
        )

    return redirect('/dashboard')







@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == ADMIN_USER:
        if request.method == 'POST':
            f = request.files.get('file1')

            if not f or not f.filename:
                return "Please select an image."

            filename = secure_filename(f.filename)

            try:
                # Check whether the filename already exists
                files = supabase.storage.from_("Images").list()

                existing_files = [
                    item["name"] for item in files
                ]

                if filename in existing_files:
                    return f"Image already exists: {filename}"

                # Upload image to Supabase
                file_data = f.read()

                supabase.storage.from_("Images").upload(
                    filename,
                    file_data,
                    {"content-type": f.content_type}
                )

                # Get the public image URL
                image_url = supabase.storage.from_("Images").get_public_url(
                    filename
                )

                # Store URL temporarily for the new post form
                session['uploaded_image_url'] = image_url

                # Open the New Post form
                return redirect('/edit/0')

            except Exception as e:
                return f"Upload failed: {str(e)}", 500

        return redirect('/dashboard')

    return "Unauthorized", 401





@app.route("/logout")
def logout():
   session.pop('user')
   return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
   if ('user' in session and session['user'] ==ADMIN_USER):
      post = Posts.query.filter_by(sno=int(sno)).first()
      db.session.delete(post)
      db.session.commit()
   return redirect('/dashboard')





@app.route("/contact", methods=["GET", "POST"])
def contact():
    status = None
    status_message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            status = "error"
            status_message = "Please fill in your name, email and message."
        else:
            try:
                entry = Contacts(
                    name=name,
                    phone_num=phone,
                    msg=message,
                    date=datetime.now(),
                    email=email
                )
                db.session.add(entry)
                db.session.commit()

            except Exception:
                db.session.rollback()
                app.logger.exception("Contact message could not be saved")
                status = "error"
                status_message = "Message could not be saved. Please try again later."

            if status is None:
                try:
                    email_service_url = os.getenv("EMAIL_SERVICE_URL")
                    email_service_token = os.getenv("EMAIL_SERVICE_TOKEN")

                    if not email_service_url or not email_service_token:
                        raise ValueError("Email service settings are missing")

                    response = requests.post(
                        email_service_url,
                        json={
                            "token": email_service_token,
                            "name": name,
                            "email": email,
                            "phone": phone,
                            "message": message
                        },
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()

                    if not result.get("success"):
                        raise ValueError(
                            result.get("message", "Email service failed")
                        )

                    status = "success"
                    status_message = "Your message has been sent successfully!"

                except Exception:
                    app.logger.exception("Google Apps Script email service failed")
                    status = "error"
                    status_message = (
                        "Your message was saved, but emails could not be sent. "
                        "Please try again later."
                    )

    return render_template(
        "contact.html",
        fb_url=FB_URL,
        tw_url=TW_URL,
        gh_url=GH_URL,
        blog_name=BLOG_NAME,
        tag_line=TAG_LINE,
        contact_bg=os.getenv("CONTACT_BG", ""),
        form_status=status,
        form_message=status_message
    )



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




def ping_self():
    if os.getenv("ENABLE_SELF_PING", "true").lower() in ("false", "0", "no"):
        return

    app_url = os.getenv("APP_URL") or os.getenv("SERVER_PING_URL")
    if not app_url:
        print("[self_ping] Warning: APP_URL is missing. Self-pinging disabled.")
        return

    ping_url = f"{app_url.rstrip('/')}/hello"
    try:
        response = requests.get(ping_url, timeout=10)
        if response.status_code == 200:
            print(f"[self_ping] Ping successful: {ping_url} (status: 200)")
        else:
            print(f"[self_ping] Warning: {ping_url} returned status {response.status_code}")
    except requests.RequestException as e:
        print(f"[self_ping] Connection error for {ping_url}: {e}")
    except Exception as e:
        print(f"[self_ping] Error: {e}")


def ping_supabase():
    # 1. Database check
    try:
        with app.app_context():
            db.session.execute(db.text("SELECT 1"))
            db.session.commit()

        print("Supabase database ping successful.")

    except Exception as e:
        db.session.rollback()
        print("Supabase database ping failed:", e)

    # 2. Storage bucket check
    try:
        supabase.storage.from_("Images").list()

        print("Supabase bucket ping successful.")
        print("Bucket accessible.")

    except Exception as e:
        print("Supabase bucket ping failed:", e)


scheduler = BackgroundScheduler(daemon=True)

try:
    ping_interval_minutes = int(os.getenv("PING_INTERVAL_MINUTES", "10"))
except ValueError:
    ping_interval_minutes = 10

scheduler.add_job(
    func=ping_self,
    trigger="interval",
    minutes=ping_interval_minutes,
    id="self_ping",
    max_instances=1
)

scheduler.add_job(
    func=ping_supabase,
    trigger="interval",
    days=6,
    id="supabase_ping",
    max_instances=1
)

# Avoid duplicate schedulers when running with Werkzeug development reloader
if not (__name__ == "__main__" and os.environ.get("WERKZEUG_RUN_MAIN") is None):
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown(wait=False))
# <<<<< END: SELF-PING & BACKGROUND SCHEDULER SYSTEM <<<<<




if __name__ == "__main__":
    ping_supabase()
    app.run(debug=True)