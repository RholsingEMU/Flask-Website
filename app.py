from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from flask_login import current_user, login_user
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa
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
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(unique=True, index=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

#flask db init then flask db upgrade

#p = [ Profile(), Profile(), Profile() ] #Make a list with an object in it

@app.route("/")
def home():
    query = sa.select(Profile)
    p = db.session.scalars(query).all()

    #db.session.commit()

    return render_template("index.html", profiles=p)

@app.route("/create-post")
def create():
    return render_template("create.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/submit", methods=["POST"])
def postSubmit():
    postName = request.form["postName"]
    postDesc = request.form["postDesc"]

    obj = Profile(name=postName, desc=postDesc)
    db.session.add(obj)

    db.session.commit() #Commit database changes

    print(postName + " " + postDesc)
    return "Post Post Posted"

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))

'''@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # request.form = LoginForm()
        user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"]))
        if user is None or not user.check_password(request.form["userPassword"]):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In')'''

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
                #return redirect(url_for('home'))
                #return 'Login Failed'
                flash('Login failed. Idiot.')
            login_user(user)
            return redirect(url_for('home'))
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

'''@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    #form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        #user = User(username=request.form["userName"], userPassword=form.request["userPassword"])
        #user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"])) 
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)'''

@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        else:
            #user = db.session.scalar(sa.select(User).where(User.username == request.form["userName"])) 
            user = User(username=request.form["userName"])
            #user = User(username=form.username.data, email=form.email.data)
            #user.set_password(form.password.data)
            user.set_password(request.form["userPassword"])
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))

