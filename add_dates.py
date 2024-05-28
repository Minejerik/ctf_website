## used to setup dates for the ctf
## run before the first run of the ctf

from pony.orm import *
from datetime import datetime

db = Database()

class Date(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    date = Required(datetime)

db.bind(provider="sqlite", filename="main.db", create_db=True)

db.generate_mapping(create_tables=True)

set_sql_debug(True)


with db_session:
    dates = []

    dates.append(Date(name="start", date=datetime.fromisoformat('2024-09-20T20:00:00.0')))
    dates.append(Date(name="end", date=datetime.fromisoformat('2024-09-22T20:00:00.0')))

    commit()