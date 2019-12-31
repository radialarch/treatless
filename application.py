import time
import requests
import os

from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from urllib.request import urlopen
from bs4 import BeautifulSoup

from helpers import first_names, get_names, get_gifts

app = Flask(__name__)
 
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        challenge = request.form.get("collection")

        # check if participants have already been scraped
        check = db.execute("SELECT * FROM challenges WHERE name = :challenge", 
                    {"challenge": challenge}).fetchone()
        if not check:
            db.execute("INSERT INTO challenges (name) VALUES (:challenge)",
                       {"challenge": challenge})
            db.commit()
        
        challenge_id = db.execute("SELECT id FROM challenges WHERE name = :challenge", 
                                  {"challenge": challenge}).fetchone()
        
        if not check:
            names = get_names(challenge)
            for name in names:
                db.execute("INSERT INTO participants (name, challenge) VALUES (:name, :id)",
                           {"name": name, "id": challenge_id})
            db.commit()
            
        names = db.execute("SELECT name FROM participants WHERE challenge = :id",
                           {"id": challenge_id})

        for name in names:
            gifts = get_gifts(name, challenge)
            db.execute("UPDATE participants SET gifts = :gifts WHERE name = :name",
                       {"name": name, "gifts": gifts})

        # get all treatless participants from challenge
        treatless = db.execute("SELECT name FROM participants WHERE challenge = :challenge AND (gifts = 0 OR gifts = 1)",
                               {"challenge": challenge_id})
        return render_template("treatless.html", treatless=treatless)
    else:
        return redirect("/")
