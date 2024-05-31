## used to setup dates for the ctf
## run before the first run of the ctf

from pony.orm import *
from datetime import datetime

db = Database()

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    solves = Set('Solve')
    points = Required(int, default=0)
    username = Required(str)
    password = Required(bytes)
    user_id = Required(str)
    admin = Required(bool, default=False)
    hidden = Required(bool, default=False)

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
    desc = Required(str)
    hidden = Required(bool, default=True)

db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

set_sql_debug(True)


with db_session:

    dates = []
    for i in range(0, 150):
        dates.append(Challenge(flag="B@RACKOBAMA", solve_count=140, points=150, name=f"TEST CHALLENGE {i}", desc="very long testing datastring we must test and balls", hidden=False))

    commit()