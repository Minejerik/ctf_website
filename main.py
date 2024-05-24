from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
from pony.orm import *
from pony.flask import Pony
from flask_login import LoginManager, UserMixin, login_user
from uuid import UUID, uuid4
from flask_bcrypt import Bcrypt


class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

app.config["SECRET_KEY"] = "upouuoiuo89279798723kjhskldfhfbccvhauiy89ywuyoi;wjdfl;jasdldfkasuiou27SAGGASJDGAHlkjf"

scheduler = APScheduler()

db = Database()

login_manager = LoginManager()
login_manager.init_app(app)

Pony(app)

## DB models



class User(db.Entity, UserMixin):
    id = PrimaryKey(int, auto=True)
    solves = Set('Solve')
    points = Required(int, default=0)
    username = Required(str)
    password = Required(str)
    user_id = Required(str)

    def get_id(self):
        return self.user_id



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

db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

set_sql_debug(True)

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



@app.route('/register', methods=["GET", "POST"])
def register():
  # If the user made a POST request, create a new user
    if request.method == "POST":
        user = User(username=request.form.get("username"),
                     password=request.form.get("password"),
                     user_id=str(uuid4()))
        # Add the user to the database
        commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("index"))
    # Renders sign_up template if user made a GET request
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by 
    # filtering for the username
    if request.method == "POST":
        # user = User.query.filter_by(
        #     username=request.form.get("username")).first()
        user = User.get(username = request.form.get("username"))
        # Check if the password entered is the 
        # same as the user's password
        if user.password == request.form.get("password"):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("index"))
        # Redirect the user back to the home
        # (we'll create the home route in a moment)
    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True, use_evalex=False)