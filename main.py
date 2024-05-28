from flask import Flask, render_template, request, redirect, url_for, abort
from functools import wraps
from flask_apscheduler import APScheduler
from datetime import datetime
from pony.orm import *
from pony.flask import Pony
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, AnonymousUserMixin, logout_user
from uuid import UUID, uuid4
from flask_bcrypt import Bcrypt
import nh3



class Config:
    SCHEDULER_API_ENABLED = True

app = Flask(__name__)
app.config.from_object(Config())

app.config["SECRET_KEY"] = "upouuoiuo89279798723kjhskldfhfbccvhauiy89ywuyoi;wjdfl;jasdldfkasuiou27SAGGASJDGAHlkjf"


scheduler = APScheduler()

db = Database()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.anonymous_user = AnonymousUserMixin
login_manager.login_view = "/login"

Pony(app)

## DB models

class User(db.Entity, UserMixin):
    id = PrimaryKey(int, auto=True)
    solves = Set('Solve')
    points = Required(int, default=0)
    username = Required(str)
    password = Required(bytes)
    user_id = Required(str)
    admin = Required(bool, default=False)
    hidden = Required(bool, default=False)

    def get_id(self):
        return self.user_id

class Solve(db.Entity):
    id = PrimaryKey(int, auto=True)
    solver = Required(User)
    challenge = Required('Challenge')
    solvetime = Required(datetime)

class Challenge(db.Entity):
    id = PrimaryKey(int, auto=True)
    flag = Required(str)
    solve_count = Optional(int)
    solves = Set(Solve)
    points = Optional(int)
    name = Required(str)

class Date(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    date = Required(datetime)

db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

# set_sql_debug(True)

## START DATE
## MAKE SURE TO RUN add_dates.py otherwise this won't work!!!
with db_session:
    START_DATE = list(Date.select(name="start"))[0].date
    END_DATE = list(Date.select(name="end"))[0].date

STARTED = (datetime.now() >= START_DATE)

@scheduler.task('interval', id='do_job_1', seconds=10)
def check_if_started():
    global STARTED
    STARTED = (datetime.now() >= START_DATE)

@app.context_processor
def inject_data():
    return dict(
        start=START_DATE,
        end=END_DATE,
        started=STARTED
    )   


## User Functions

# Used by flask login to get the user
@login_manager.user_loader
def load_user(user_id):
    with db_session:
        return User.get(user_id=user_id)
    
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if isinstance(current_user, AnonymousUserMixin) or not current_user.admin:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function

@app.template_filter('pluralize')
def pluralize(number, singular = '', plural = 's'):
    if number == 1:
        return singular
    else:
        return plural


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
@admin_only
def adminindex():
    users = list(User.select())
    return render_template("admin/index.html", users=users)

@app.route("/admin/etc", methods=["POST", "GET"])
@admin_only
def adminetc():
    if request.method == "post":
        print(request.form())
    users = list(User.select())
    return render_template("admin/etc.html", users=users)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        print(current_user)
        print(request.form)
        if not bcrypt.check_password_hash(current_user.password, request.form.get("currentPassword")):
            return render_template("settings.html", error="Incorrect Password!")
        if current_user.username != request.form.get("username"):
            temp = User.get(username=request.form.get("username"))
            if temp:
                return render_template("settings.html", error="Username already taken!")
            else:
                if nh3.is_html(request.form.get("username")):
                    return render_template("settings.html", error="Username contains HTML!")
                current_user.username = request.form.get("username")
        if request.form.get('newPassword1') != "":
            if request.form.get("newPassword1") != request.form.get("newPassword2"):
                return render_template("settings.html", error="Passwords do not match!")
            else:
                password = bcrypt.generate_password_hash(request.form.get("newPassword1"))
                current_user.password = password
    return render_template("settings.html")

@app.route('/register', methods=["GET", "POST"])
def register():
  # If the user made a POST request, create a new user
    if request.method == "POST":
        name = request.form.get("username")
        if nh3.is_html(name):
            return render_template("register.html", error="Username contains HTML!")
        user = User(username=request.form.get("username"),
                     password=bcrypt.generate_password_hash(request.form.get("password")),
                     user_id=str(uuid4()))
        # Add the user to the database
        commit()
        # Once user account created, redirect them
        # to login route (created later on)
        return redirect(url_for("index"))
    # Renders sign_up template if user made a GET request
    return render_template("register.html")

@app.route('/users')
def users():
    users = User.select(hidden=False)[0:50]
    return render_template('users.html', users=users)

@app.route('/users/<page>')
def userpage(page):
    users = select(hidden=False)[0*page:50*page]
    return render_template('users.html', users=users)

@app.route('/user/<id>')
def userbyid(id):
    user = User[int(id)]
    if not user:
        abort(404)
    solves = list(user.solves)
    return render_template('usertag.html', user=user, solves=solves)

@app.route("/login", methods=["GET", "POST"])
def login():
    # If a post request was made, find the user by 
    # filtering for the username
    if request.method == "POST":
        # user = User.query.filter_by(
        #     username=request.form.get("username")).first()
        user = User.get(username = request.form.get("username"))
        if not user:
            return render_template("login.html", error="Incorrect user or password")
        # Check if the password entered is the 
        # same as the user's password
        if bcrypt.check_password_hash(user.password, request.form.get("password")):
            # Use the login_user method to log in the user
            login_user(user)
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Incorrect user or password")
        # Redirect the user back to the home
        # (we'll create the home route in a moment)
    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True, use_evalex=False)