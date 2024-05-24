from flask import Flask, render_template
from flask_apscheduler import APScheduler
from pony.orm import *

class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()

db = Database()

db.bind(provider="sqlite", filename="main.db")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, use_evalex=False)