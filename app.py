from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import current_user, login_user
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, logout_user

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db") #app.db is database name
app.secret_key = "shhhhhhhhhh"
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)

class Profile(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True) #a:int = 5 <- type hinting
    name:so.Mapped[str] = so.mapped_column(index=True, default="Default name")
    desc:so.Mapped[str] = so.mapped_column(index=True, default="Default desc")
    likes:so.Mapped[int] = so.mapped_column(default=0)

    #Constructor always looks like this
    def __init__(self):
        pass

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256), default="")
    posts: so.Mapped[list["Post"]] = so.relationship(back_populates="author")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return self.username

class Post(db.Model):
    __tablename__ = "posts"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(index=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(256), default="")
    likes: so.Mapped[int] = so.mapped_column(nullable=True)

    user_id:so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"))

    author:so.Mapped["User"] = so.relationship(back_populates="posts")

    tags:so.Mapped[str] = so.mapped_column(sa.String(250), default="")

    def tag_names(self) -> list:
         return self.tags.split()

#flask db init then flask db upgrade

#p = [ Profile(), Profile(), Profile() ] #Make a list with an object in it

@app.route("/", methods=['GET'])
def home():
    #query = sa.select(Post)

    tags = request.args.get("tags", "")
    sort = request.args.get("post-sort", "option1")
    search = request.args.get("search", "")

    query = sa.select(Post)

    if search:
        query = query.where(sa.or_(
            Post.title.ilike(f"%{search}%"),
            Post.body.ilike(f"%{search}%"),
            Post.author.has(User.username.ilike(f"%{search}%"))
        ))

    if tags:
        query = query.where(Post.tags.ilike(f"%{tags}%")) #Not a hack but certainly cheap

    if sort == "option1":
        query = query.order_by(Post.likes.desc())
    elif sort == "option2":
        query = query.order_by(Post.id.asc())
    elif sort == "option3":
        query = query.order_by(Post.likes.asc())
    elif sort == "option4":
        query = query.order_by(Post.id.desc())

    posts = db.session.scalars(query).all()

    return render_template("index.html", posts=posts)

@app.route("/create-post", methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create.html')
    elif request.method == 'POST':
        if current_user.is_authenticated == False:
            flash("You must be logged in to post :/")
            return redirect(url_for('login_view'))
        else:
            #user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"])) 
            post = Post(title=request.form["postName"], body=request.form["postDesc"], tags=request.form["tags"], author=current_user, likes=0)
            db.session.add(post)
            
            db.session.commit()
            flash("Post Created! Congrats! :)")
            return redirect(url_for('home'))


@app.route("/profile/<int:post_id>")
def profile(post_id):
    post = db.session.get(Post, post_id)

    #return render_template("post.html", post=post)
    return render_template("profile.html", post=post)

@app.post("/post/<int:post_id>/like")
def like_post(post_id):
    post = db.session.get(Post, post_id)

    post.likes += 1
    db.session.commit()

    return redirect(url_for("profile", post_id=post_id))

@app.route("/submit", methods=["POST"])
def postSubmit():
    postName = request.form["postName"]
    postDesc = request.form["postDesc"]

    obj = Profile(name=postName, desc=postDesc)
    db.session.add(obj)

    db.session.commit() #Commit database changes

    #print(postName + " " + postDesc)
    #return "Post Post Posted"

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        else:
            user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"])) 
            if user is None or not user.check_password(request.form["userPassword"]):
                flash('Login failed', 'failure')
                return redirect(url_for('home'))
                #return 'Login Failed'
            login_user(user)
            flash("Welcome back! :D")
            return redirect(url_for('home'))
    
@app.route('/logout')
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if current_user.is_authenticated:
            flash("You must be logged out to create another account :/")
            return redirect(url_for('home'))
        else:
            #user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"])) 
            user = User(username=request.form["userName"])
            #user = User(username=form.username.data, email=form.email.data)
            #user.set_password(form.password.data)
            user.set_password(request.form["userPassword"])
            db.session.add(user)
            db.session.commit()
            flash("Account Created! :D")
            return redirect(url_for('home'))

@app.route('/remove')
def remove():
    if current_user.is_authenticated:   
        db.session.delete(current_user)
        db.session.commit()
        logout_user() 
        flash("Bye!")
        return redirect(url_for('home'))
    else:
        flash('You must be logged in to delete an account, silly')
        return redirect(url_for('home'))
