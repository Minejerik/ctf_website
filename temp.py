## do not use this file, it is for testing purposes only

from pony.orm import *
from datetime import datetime

from random import choice
from slugify import slugify

db = Database()

class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    solves = Set('Solve')
    points = Required(int, default=0)
    username = Required(str)
    email = Required(str)
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
    solve_count = Optional(int, default=0)
    solves = Set(Solve)
    points = Optional(int)
    name = Required(str)
    slug = Required(str)
    desc = Required(str)
    hidden = Required(bool, default=True)
    category = Optional('Category')
    downloadables = Set('Downloadable')
    
class Category(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    desc = Optional(str)
    challenges = Set(Challenge)
    
class Downloadable(db.Entity):
    id = PrimaryKey(int, auto=True)
    file_name = Required(str)
    challenge = Required(Challenge)

db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

set_sql_debug(True)

cats = []

with db_session:
    cats.append(Category(name="test_cat_1", desc="cat 1 desc"))
    cats.append(Category(name="test_cat_2", desc="cat 2 desc"))
    cats.append(Category(name="test_cat_3", desc="cat 3 desc"))
    commit()

with db_session:
    cats = list(Category.select())
    dates = []
    for i in range(0, 15):
        
        ch = Challenge(flag=f"flag_{i}", name=f"test_challenge_{i}", desc=f"desc_{i}", category=choice(cats), points=100, hidden=False, slug=slugify(f"test_challenge_{i}"))
        for i2 in range(0, 5):
            ch.downloadables.create(file_name=f"file_{i}_{i2}")
            
        
        dates.append(ch)

    commit()