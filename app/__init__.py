import os
from flask import Flask, render_template, redirect, url_for
from app import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    #set config
    try:
        environment = os.environ["APP_ENVIRONMENT"]
    except KeyError:
        environment = "default"
    
    if environment == "development":
        app.config.from_object(config.DevelopmentConfig)
    elif environment == "production":
        app.config.from_object(config.ProductionConfig)
    elif environment == "default":
        app.config.from_object(config.Config)

    if test_config is None:
        # load instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        #laod the test config if passed in
        app.config.from_mapping(test_config)

    #ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register with extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # a simple hello page
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #index page
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template("index.html", title="Home Page")

    #register blueprints
    from .routes import auth, users
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)

    return app