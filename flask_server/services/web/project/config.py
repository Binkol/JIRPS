import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_TYPE = "secret"
    SECRET_KEY = "prettysecretsecret"
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite://")
    SQLALCHEMY_TRACK_MODIFICATIONS = False