from email.policy import default
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    credits = db.Column(db.Integer, default=10)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, name):
        self.name = name

class Game(db.Model):
    __tablename__ = "games"

    id = db.Column(db.Integer, primary_key=True)
    room_name = db.Column(db.String(128), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    finished_at = db.Column(db.DateTime, default=None, nullable=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    user2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, default=None)
    user1_win_count = db.Column(db.Integer, default=0, nullable=False)
    user2_win_count = db.Column(db.Integer, default=0, nullable=False)
    games_played = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, room_name, created_at, user1_id):
        self.room_name = room_name
        self.created_at = created_at
        self.user1_id = user1_id