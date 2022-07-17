from project.models import db, User, Game
from flask_socketio import SocketIO, emit

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

def calculate_and_commit_players_credits(players, winning_player):
    for player in players:
        if player == winning_player:
            winner = User.query.filter_by(name=player).first()
        else:
            loser = User.query.filter_by(name=player).first()
    
    winner.credits += 1
    loser.credits -= 3
    db.session.commit()

def update_winnings_count(room, player):
    game = Game.query.filter_by(room_name=room).first()
    winner = User.query.filter_by(name=player).first()
    user1 = User.query.filter_by(id=game.user1_id).first()

    if winner == user1:
        game.user1_win_count += 1
    else:
        game.user2_win_count +=1
    
    db.session.commit()

def emit_updated_score(room, players):
    for player in players:
        user = User.query.filter_by(name=player).first()
        emit("score_update", {"username": user.name, "score": user.credits}, room=room)
