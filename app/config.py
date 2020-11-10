import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    DEVELOPMENT = False
    CSRF_ENABLED = True
    LOGGING_LEVEL = logging.INFO

    SECRET_KEY = os.environ['SECRET_KEY']

    #database
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #login
    REMEMBER_COOKIE_DURATION = os.environ['REMEMBER_COOKIE_DURATION']


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    LOGGING_LEVEL = logging.INFO

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG
