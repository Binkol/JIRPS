from flask import Flask, jsonify, render_template, request, session
from project.models import db, User, Game


app = Flask(__name__,
            static_folder='./static',
            template_folder='./templates')
app.config.from_object("project.config.Config")

db.init_app(app)


@app.route("/")
def register():
    return render_template("register.html")

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    session["username"] = username
    try:
        user = User.query.filter_by(name=username).first()
        if user and user.active:
            return render_template("register.html", error="User is already active")
        elif user and not user.active:
            user.active = True
            db.session.commit()
        else:
            newUser = User(name=username)
            db.session.add(newUser)
            db.session.commit()
        return render_template("home.html", session=session)
    except Exception as e:
        err = "Failed to add a user: {}".format(e)
        return render_template("register.html", error=err)

@app.route("/logout", methods=['POST'])
def logout():
    try:
        username = request.form['username']
        user = User.query.filter_by(name=username).first()
        user.active = False
        db.session.commit()
        return render_template("register.html")
    except Exception as e:
        err = "Failed to logout: {}".format(e)
        return render_template("register.html", error=err)
