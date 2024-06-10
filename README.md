# Custom made CTF website

![wakapi](https://wakapi.dev/api/badge/minejerik/interval:any/project:ctf_website)

Is in development and will be used for my unnamed CTF in september


# How to run:
Install Requirements:
```
pip install -r requirements.txt
```

Add the dates to the database:

1. Edit add_dates.py to have the dates you want
2. Run add_dates.py

Running the CTF:

THESE ARE BOTH IN DEBUG MODE! DO NOT USE IN PRODUCTION!
```
flask --app main:app run --debug
```
or 
```
python3 main.py
```
