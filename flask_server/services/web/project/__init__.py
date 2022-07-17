from flask import Flask, jsonify, render_template, request, session
from project.models import db, User, Game
from flask_socketio import SocketIO, join_room, leave_room, emit
from project import utils
import datetime

app = Flask(__name__,
            static_folder='./static',
            template_folder='./templates')
app.config.from_object("project.config.Config")

db.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*")

games_statuses = {}


@app.route("/")
def register():
    return render_template("register.html")

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    session["username"] = username
    session['error'] = ""

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
    user = User.query.filter_by(name=session.get('username')).first()
    game = Game.query.filter_by(room_name=request.form["room"]).first()
    session["room"] = request.form["room"]
    session["credits"] = user.credits

    if not game:
        new_game = Game(
                room_name = request.form["room"],
                created_at = datetime.datetime.now(),
                user1_id = user.id
                )
        db.session.add(new_game)
        db.session.commit()

        session["player1"] = user.name
        games_statuses[request.form["room"]] = {}
    else:
        if game.user2_id is None:
            game.user2_id = user.id
            db.session.commit()
            session["player2"] = user.name
        else:
            session['error'] = "Room is full or Game is finished"
            return render_template("home.html", session=session)

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
    emit("message", {"msg": session.get("username") + ": " + message["msg"]}, room=room)


@socketio.on("left", namespace="/game_room")
def left(message):
    room = session.get("room")
    username = session.get("username")
    leave_room(room)
    session.clear()

    game = Game.query.filter_by(room_name=room).first()
    game.finished_at = datetime.datetime.now()
    games_statuses.pop(room, None)

    user = User.query.filter_by(name=username).first()
    user.active = False

    db.session.commit()
    emit("status", {"msg": "username " + username + " left."})


@socketio.on("selected_option", namespace="/game_room")#select rock paper or scissors
def selected_option(message):
    room = session.get("room")
    username = session.get("username")

    games_statuses[room][username] = message["msg"]
    emit("message", {"msg": username + " is ready."}, room=room)

    if len(games_statuses[room]) == 2: #if two players are connected to a game sessions
        winner = utils.getWinner(games_statuses[room])
        if winner is not None:
            utils.calculate_and_commit_players_credits(list(games_statuses[room]), winner)
            utils.emit_updated_score(room, list(games_statuses[room]))
            utils.update_winnings_count(room, winner)
            msg = "{} won with {}".format(winner, games_statuses[room][winner])
        else:
            msg = "Draw, {0} against {0}".format(games_statuses[room][username])
        emit("message", {"msg": msg}, room=room)
        games_statuses[room] = {}


@socketio.on("credits_request", namespace="/game_room")
def add_credits(message):
    room = session.get("room")
    username = session.get("username")

    user = User.query.filter_by(name=username).first()
    user.credits += 10
    db.session.commit()

    utils.emit_updated_score(room, [username])


    

