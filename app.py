from flask import Flask, render_template, request, redirect
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sqlalchemy.orm as so
import sqlalchemy as sa

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db") #app.db is database name
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Profile(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name:so.Mapped[str] = so.mapped_column(index=True, default="Default name") #Type hinting
    desc:so.Mapped[str] = so.mapped_column(index=True, default="Default desc")
    likes:so.Mapped[int] = so.mapped_column(default=0)
    #Constructor always looks like this
    def __init__(self):
        pass

#flask db init then flask db upgrade

p = [ Profile(), Profile(), Profile() ] #Make a list with an object in it

@app.route("/")
def home():
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
    print(postName + " " + postDesc)
    return "Post Post Posted"

