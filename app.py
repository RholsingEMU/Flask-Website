from flask import Flask, render_template, request, redirect
from random import randint

class Profile:
    name="Default"
    desc="Default"
    likes=0
    #Constructor always looks like this
    def __init__(self):
        pass

p = [ Profile(), Profile(), Profile() ] #Make a list with an object in it

app = Flask(__name__)

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

