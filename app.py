from flask import Flask, render_template
from random import randint

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")
    #return f"<p>WAGA my BAGA please. The number {str(randint(0, 20))}</p><a href=localhost:5000/waga>waga</a>"

@app.route("/create-post")
def waga():
    return render_template("create.html")

@app.route("/profile")
def bobo():
    return render_template("profile.html")
