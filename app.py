from collections import UserString
from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


# Create a Flask Instance
app = Flask(__name__)

# Add ckeditor
ckeditor = CKEditor(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True
# Secret Key!
app.config['SECRET_KEY'] = ",XCzD!TX7f#CEFA3b9H&}K@[$/D&b8R'caTf9]A){uw`!;UnE.y5"
# Add Database
# SQLite
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:password@localhost/our_users"

# Saving Pictures
UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize The Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Create Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    about_author = db.Column(db.Text(500), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    # User Can Have Many Posts
    posts = db.relationship('Posts', backref='poster')

    # Hashing passwords
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name
    
# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Foreign Key To Link Users (refer to primary key of the user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Create Search Function
@app.route('/search', methods=['POST', 'GET'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        # Get data from submitted form
        searched_for = form.searched.data
        # Query the database
        posts = Posts.query.filter(Posts.content.like('%' + searched_for + '%')).order_by(Posts.title).all()
        return render_template("search.html", form=form, searched_for=searched_for, posts=posts)
    else:
        return render_template("type_something.html")

# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create Admin Page
@app.route('/admin')
@login_required
def admin():
    if current_user.id == 37:
        return render_template("admin.html")
    else:
        flash("You Must Be The Admin To Access The Page!")
        return render_template("unauthorized_action.html")


# # Adding Cache Control
# def add_cache_control(response):
#     if current_user.is_authenticated:
#         response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
#     return response


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check The Hash
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login Successfull!!")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!")
        else:
            flash("User Doesn't Exist!")

    return render_template('login.html', form=form)

# Create Logout Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out")
    return redirect('login')


# Create Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    update = Users.query.get_or_404(id)
    if request.method == 'POST':
        update.name = request.form['name']
        update.username = request.form['username']
        update.email = request.form['email']
        update.favorite_color = request.form['favorite_color']
        update.about_author = request.form['about_author']
        
        # Check For Profile Pic
        if request.files['profile_pic']:
            update.profile_pic = request.files['profile_pic']

            # Grab Image Name
            pic_filename = secure_filename(update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            # Save That Image
            update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
            # change it to string to save to db 
            update.profile_pic = pic_name
            try:
                db.session.add(update)
                db.session.commit()
                flash(f"User {update.name.capitalize()} Updated Successfully!!")
                return render_template("dashboard.html", form=form, update=update)
            except:
                flash("Looks like there was a problem try again!")
                return render_template("dashboard.html", form=form, update=update)
        
        else:
            db.session.commit()
            flash(f"User {update.name.capitalize()} Updated Successfully!!")
            return render_template("dashboard.html", form=form, update=update)
        
    else:
        return render_template("dashboard.html", form=form, update=update)
        

# Deleting Post
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id or id == 37:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Blog Got deleted")
            return redirect('/posts')
        except:
            flash("Whoops there was a problem deleting post, try again")
            return redirect('/posts')
    else:
        flash("You Aren't Authorized To Delete This Post")
        return render_template("unauthorized_action.html")

# Post Edit or updating post
@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        # post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
        # Update Database
        db.session.add(post)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('post', id=post.id))
    
    if current_user.id == post.poster_id or current_user.id == 37:
        form.title.data = post.title
        # form.author.data = post.author
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_post.html', form=form)
    else:
        flash("You Aren't Authorized To Edit This Post")
        return render_template("unauthorized_action.html")

# Grab a post
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template("post.html", post=post)

# Show all posts from the database
@app.route('/posts')
def posts():
    # Grab all the posts from database
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
# @login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, poster_id = poster, slug=form.slug.data)
        # Clearing The Form
        form.title.data = ''
        form.content.data = ''
        ##### form.author.data = ''
        form.slug.data = ''
        # Add Post Data To The DataBase
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully!")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)

@app.route('/')
def index():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("index.html", posts=posts)

# @app.route('/')
# def index():
#     first_name = "John"
#     stuff = "This is Bold Text"

#     favorite_pizza = ["Pepparoni", "Cheese", "Mashrooms", 41]
#     return render_template("index.html", first_name=first_name, stuff=stuff, 
#                            favorite_pizza=favorite_pizza)

# Adding users
@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username = form.username.data, name = form.name.data, email = form.email.data, favorite_color = form.favorite_color.data, password_hash = hashed_pw)
            db.session.add(user)
            db.session.commit()
            flash(f"User {form.name.data} Added Successfully!")
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        return redirect('/login')

    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form)

# Update Database Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.username = request.form['username']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash(f"User {name_to_update.name.capitalize()} Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Looks like there was a problem... try again!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    

# delete user
@app.route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f"User {user_to_delete.name} Deleted Successfully!!")
            return redirect('/user/add')
        except:
            flash("Whoops! There was a problem deleting user, try again")
    else:
        flash("You Can't Delete Another User")
        return render_template("unauthorized_action.html")

# localhost:5000/user/nameoftheuser
@app.route('/user/<name>')
def user(name):
    return render_template("user.html", name=name)

# Create Custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 400
 
# Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # Validating Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash(f"Welcome {name.capitalize()}, Form Submitted Successfully!")
    return render_template("name.html", name=name, form=form)

# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # Validating Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup User By Email Address
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)

    return render_template("test_pw.html", email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)

# Json
@app.route('/date')
def get_current_date():
    favorite_meal = {
        "John": "Pepparoni",
        "Mary": "Cheese",
        "Tim": "meat"
    }

    # return {"Date": date.today()}
    return favorite_meal


# Register the cache control function using after_request decorator
# app.after_request(add_cache_control)
