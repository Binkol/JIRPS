from flask import Flask, jsonify, render_template, request, session
from project.models import db, User, Game
from flask_socketio import SocketIO, join_room, leave_room, emit
import datetime

app = Flask(__name__,
            static_folder='./static',
            template_folder='./templates')
app.config.from_object("project.config.Config")

db.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*")

games_statuses = {}

def getWinner(game_status):
    keys = list(game_status)
    values = list(game_status.values())

    if values[0] == values[1]:
        return None
    
    if values[0] == "rock" and values[1] == "scissors":
        return keys[0]
    elif values[0] == "paper" and values[1] == "rock":
        return keys[0]
    elif values[0] == "scissors" and values[1] == "paper":
        return keys[0]
    else:
        return keys[1]

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


@app.route("/game_room", methods=['GET', 'POST'])
def game_room():
    session["room"] = request.form["room"]
    user = User.query.filter_by(name=session.get('username')).first()
    game = Game.query.filter_by(room_name=request.form["room"]).first()
    
    if not game:
        new_game = Game(
                room_name = request.form["room"],
                created_at = datetime.datetime.now(),
                user1_id = user.id
                )
        db.session.add(new_game)
        db.session.commit()

        session["player1"] = user.name
    else:
        game.user2_id = user.id
        db.session.commit()

        session["player2"] = user.name
    
    games_statuses[request.form["room"]] = {}

    return render_template("game_room.html", session=session)


@socketio.on("join", namespace="/game_room")
def join(message):
    room = session.get("room")
    join_room(room)
    emit("status", {"msg": session.get("username") + "has entered"}, room=room)

@socketio.on("text", namespace="/game_room")
def text(message):
    room = session.get("room")
    print("message send", message["msg"], "from ", session.get("username"))
    emit("message", {"msg": session.get("username") + message["msg"]}, room=room)

@socketio.on("left", namespace="/game_room")
def left(message):
    room = session.get("room")
    username = session.get("username")
    leave_room(room)
    session.clear()
    emit("status", {"msg": "username " + username + " left."})

@socketio.on("selected_option", namespace="/game_room")
def choose_rock(message):
    room = session.get("room")
    username = session.get("username")

    games_statuses[room][username] = message["msg"]
    emit("message", {"msg": username + " is ready."}, room=room)
    
    if len(games_statuses[room]) == 2:
        winner = getWinner(games_statuses[room])
        if winner is not None:
            msg = "{} won with {}".format(winner, games_statuses[room][winner])
        else:
            msg = "Draw, {0} against {0}".format(games_statuses[room][username])
        emit("message", {"msg": msg}, room=room)
        games_statuses[room] = {}


    

