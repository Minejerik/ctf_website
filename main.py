from flask import Flask, render_template
from flask_apscheduler import APScheduler
from pony.orm import *
from flask_login import LoginManager, UserMixin


class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()

db = Database()

login_manager = LoginManager()
login_manager.init_app(app)


db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

set_sql_debug(True)

## DB models


class User(db.Entity, UserMixin):
    id = PrimaryKey(int, auto=True)
    user_id = Required(str)
    solves = Set('Solve')
    points = Required(int)
    username = Required(str)


class Solve(db.Entity):
    id = PrimaryKey(int, auto=True)
    solver = Required(User)
    challenge = Required('Challenge')


class Challenge(db.Entity):
    id = PrimaryKey(int, auto=True)
    flag = Required(str)
    solve_count = Optional(int)
    solves = Set(Solve)
    points = Optional(int)


## User Functions

# Used by flask login to get the user
@login_manager.user_loader
def load_user(user_id):
    with db_session:
        return User.get(user_id=user_id)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, use_evalex=False)