import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    SECRET_KEY = 'change-this'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    DEBUG = False

class DevelopmentConfig(Config):
    SECRET_KEY = 'dev'
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, 'app.db')
    DEVELOPMENT = True
    DEBUG = True
