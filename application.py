import os
import matplotlib.pyplot as pl
import numpy as np

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# this database has a table for club information and a table for user information
clubdb = SQL("sqlite:///clubinfo.db")

# this database has one club per table, every row of a table is one review
reviewdb = SQL("sqlite:///clubreview.db")

@app.route("/")
def index():
    """Show the list of clubs"""

    clubs = clubdb.execute("SELECT name FROM clublist")
    for row in clubs:
        row['link'] = "/club/" + row['name']
    return render_template("index.html", data = clubs)




@app.route("/club/<name>")
def club(name):
    """Show the info for a given club"""

    # get the information of the club from clubinfo.db
    info = clubdb.execute("SELECT description, email, site FROM clublist WHERE name = :name", name = name )

    # get the reviews of the club from clubreview.db and make a table of reviews if none exists
    reviewdb.execute("CREATE TABLE IF NOT EXISTS :club_name ('experience' integer, 'leadership' integer, 'culture' integer, 'social' integer, 'workload' integer, 'meetings' text, 'recommend' text, 'comments' text)",club_name=name)
    reviews = reviewdb.execute("SELECT experience, leadership, culture, social, workload, meetings, recommend, comments FROM :club_name", club_name = name)

    # get the review link
    review_link = "/review/" + name

    # plot experiences
    experiences = []
    for review in reviews:
        experiences.append(review['experience'])
    experiences = [i for i in experiences if i]
    temp = {}
    for i in range(1,6):
        temp[i] = experiences.count(i)
    experiences = temp
    X = np.arange(len(experiences))
    pl.bar(X, list(experiences.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, experiences.keys(), rotation = 90)
    pl.title('Experience')
    pl.savefig('static/experience.png', dpi = 300)
    pl.clf()

    # plot leadership
    leaderships = []
    for review in reviews:
        leaderships.append(review['leadership'])
    leaderships = [i for i in leaderships if i]
    temp = {}
    for i in range(1,6):
        temp[i] = leaderships.count(i)
    leaderships = temp
    X = np.arange(len(leaderships))
    pl.bar(X, list(leaderships.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, leaderships.keys(), rotation = 90)
    pl.title('Leadership')
    pl.savefig('static/leadership.png', dpi = 300)
    pl.clf()

    # plot culture
    cultures = []
    for review in reviews:
        cultures.append(review['culture'])
    cultures = [i for i in cultures if i]
    temp = {}
    for i in range(1,6):
        temp[i] = cultures.count(i)
    cultures = temp
    X = np.arange(len(cultures))
    pl.bar(X, list(cultures.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, cultures.keys(), rotation = 90)
    pl.title('Culture')
    pl.savefig('static/culture.png', dpi = 300)
    pl.clf()

    # plot social
    socials = []
    for review in reviews:
        socials.append(review['social'])
    socials = [i for i in socials if i]
    temp = {}
    for i in range(1,6):
        temp[i] = socials.count(i)
    socials = temp
    X = np.arange(len(socials))
    pl.bar(X, list(socials.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, socials.keys(), rotation = 90)
    pl.title('Social')
    pl.savefig('static/social.png', dpi = 300)
    pl.clf()

    # plot meetings
    meetings = []
    for review in reviews:
        meetings.append(review['meetings'])
    meetings = [i for i in meetings if i]
    meetings = {i:meetings.count(i) for i in meetings}
    X = np.arange(len(meetings))
    pl.bar(X, list(meetings.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, meetings.keys(), rotation = 90)
    pl.title('Meetings')
    pl.savefig('static/meetings.png', dpi = 300)
    pl.clf()

    # plot how recommended the club is
    recommend = []
    for review in reviews:
        recommend.append(review['recommend'])
    recommend = [i for i in recommend if i]
    recommend = {i:recommend.count(i) for i in recommend}
    X = np.arange(len(recommend))
    pl.bar(X, list(recommend.values()), align='center', width=0.5, color = 'b', bottom = 0.0)
    pl.xticks(X, list(recommend.keys()))
    pl.title('Recommend')
    pl.savefig('static/recommend.png', dpi = 300)
    pl.clf()

    # get the average workload
    workload = []
    for review in reviews:
        workload.append(review['workload'])
    workload = [i for i in workload if i]
    if workload:
        avg_workload = sum(workload)/len(workload)
    else:
        avg_workload = 0

    # send the information to the webpage in order to dynamically generate the page
    return render_template("club.html", name = name, info = info[0], review_link = review_link, reviews = reviews, avg_workload = avg_workload)

@app.route("/review/<name>", methods=["GET", "POST"])
@login_required
def review(name):
    """Review a given club"""

    if request.method == "POST":
        experience = request.form.get("Experience")
        leadership = request.form.get("Leadership")
        culture = request.form.get("Culture")
        social = request.form.get("Social")
        workload = request.form.get("Workload")
        meetings = request.form.get("Meetings")
        recommend = request.form.get("Recommend")
        comments = request.form.get("Comments")

        # make a table of reviews for the club if none exists
        reviewdb.execute("CREATE TABLE IF NOT EXISTS :club_name ('experience' integer, 'leadership' integer, 'culture' integer, 'social' integer, 'workload' integer, 'meetings' text, 'recommend' text, 'comments' text)",club_name=name)

        # insert information into table
        reviewdb.execute("INSERT INTO :club_name ('experience' , 'leadership' , 'culture' , 'social', 'workload', 'meetings', 'recommend', 'comments' ) VALUES (:my_experience, :my_leadership, :my_culture, :my_social, :my_workload, :my_meetings, :my_recommend, :my_comments)",
                   club_name = name, my_experience = experience, my_leadership = leadership, my_culture = culture, my_social = social, my_workload = workload, my_meetings = meetings, my_recommend = recommend, my_comments = comments )

        #redirect to the club page
        club_link = "/club/" + name
        return redirect(club_link)

    else:
        review_link = "/review/" + name
        return render_template("review.html", review_link = review_link)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password again", 400)

        if request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords must match", 400)

        if clubdb.execute("SELECT * FROM users WHERE username = :name", name=request.form.get("username")):
            return apology("username already exists", 400)
        clubdb.execute("INSERT INTO users ( username, hash) VALUES ( :username , :the_hash)",
                   username=request.form.get("username"), the_hash=generate_password_hash(request.form.get("password")))

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = clubdb.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/search", methods=["GET"])
def search():
    """Search for a given club"""
    searchitem = request.args.get("searched").lower()
    searched = list()
    for i in range(len(searchitem) - 2):
        searched.append(searchitem[i: i+3])

    compareto = list()

    # predefines nothing as the most similar, sets similarity to 0
    mostsimilar = ""
    highestSimilarity = 0


    # looks through clubs and seeks a club name thats similar enough
    clubs = clubdb.execute("SELECT name FROM clublist")
    for club in clubs:
        name = club['name']
        if name.lower() == searchitem:
            info = clubdb.execute("SELECT description, email, site FROM clublist WHERE name = :name", name = name)
            return render_template("club.html", name = name, info=info[0])
        localSimilarity = 0

        # populates a list to use for comparison to the searchitem
        for k in range(len(name) - 2):
            compareto.append(name[k: k+3])

        # compares substrings in both lists, only compares neighboring substrings
        if len(compareto)>=2:
            for i in range(len(searched) - 1):
                    if i>len(compareto)-2:
                        break
                    if searched[i]==compareto[i] or searched[abs(i-1)]==compareto[abs(i-1)] or searched[i+1]==compareto[i+1]:
                        localSimilarity = localSimilarity + 1

        if localSimilarity>highestSimilarity:
            mostsimilar = name
            highestSimilarity = localSimilarity

        del compareto[:]

    options = list()
    if highestSimilarity!=0:
        options.append(mostsimilar)
    else:
        for club in clubs:
            if searchitem[0] == club['name'].lower()[0]:
                options.append(club['name'])
    return render_template("options.html", searched=searchitem.upper(), options=options)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
