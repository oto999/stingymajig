from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update
from random import randint
import csv
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = str(randint(1000000,9999999))
app.config["SQLALCHEMY_DATABASE_URI"] ="sqlite:///stuff.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db = SQLAlchemy(app)



class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.String(40), nullable = False)
    password = db.Column(db.String(40), nullable = False)
    cash = db.Column(db.INTEGER, nullable = False)

    def __str__(self):
        return f"ID: {self.id}, Username: {self.username}, Password: {self.password},Cash: {self.cash}"

    # @staticmethod
    # def update_user(_username, **kwargs):
    #     username = User.query.filter_by(username=_username).first()
    #     print(kwargs)
    #     username.__dict__.update(kwargs)
    #     print(username.__dict__)
    #     db.session.commit()

db.create_all()



@app.route('/')
def Home_Page():
    session["cash"] = 0
    session["items"] = 0
    return render_template("Main.html")


@app.route('/login', methods= ["GET","POST"])
def Login():
    mob = User.query.all()
    if request.method == "POST":
        for person in mob:
            if request.form["username"] == person.username:
                if request.form["password"] == person.password:
                    session["username"] = person.username
                    session["cash"] = person.cash
                    session["items"] = 0
                    return render_template("Main.html")
        flash("Strangers aren't welcome here!, Go register!")
    return render_template("Login.html")


@app.route('/register', methods= ["GET","POST"])
def Register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cash = request.form["cash"]
        session["username"] = username
        session["password"] = password
        session["cash"] = cash
        session["items"] = 0
        if ((session["cash"] == None) or (session["username"] == None) or (session["password"] == None)):
            flash('Fill all the fields')
            return render_template("register.html")

        newbie = User(username = session["username"],password = session["password"],cash = session["cash"])
        db.session.add(newbie)
        db.session.commit()
        return render_template("Main.html")

    return render_template("register.html")
    #return redirect(url_for("Home_Page", ))


@app.route('/logout')
def Logout():
    session.pop("username", None)
    session.pop("password", None)
    session["cash"] = 0
    session["items"] = 0
    return render_template("Main.html")

@app.route('/deposit', methods= ["GET","POST"])
def GimmeSomeCash():
    if request.method == "POST":
        if session["username"] != None:
            newCash = int(session["cash"]) + 50
            # person = User.query.filter_by(username=session["username"]).update(dict(cash=newCash))
            # person.cash = newCash
            # db.session.commit()

            #User.update_user(session["username"], cash=newCash)

            cashData = sqlite3.connect("user.sqlite")
            c = cashData.cursor()
            dict = {"newcash":newCash,"name":session["username"]}
            c.execute('''UPDATE user
                         SET cash = :newcash
                         WHERE username = :name
            ''', dict)
            session["cash"] = newCash
        return render_template("Main.html")
    return render_template("Main.html")

@app.route('/shop', methods= ["GET","POST"])
def Shop():
    csv_file = open('random_stuff.csv', "r", encoding='UTF-8')
    file = csv_file.readlines()
    random_stuff = csv.reader(file)
    return render_template("Shop.html", random_stuff=random_stuff)

@app.route('/buy')
def Buy():
    session["items"] += 1
    return render_template("Bought.html")

if __name__ == "__main__": app.run(debug=True)
db.create_all()


