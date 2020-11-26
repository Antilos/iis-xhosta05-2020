import os
import click
import logging
import subprocess
import sys
from flask import Flask, render_template, redirect, url_for
from app import config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
ckeditor = CKEditor()
bootstrap = Bootstrap()
#login.login_view = 'auth.login'

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)

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

    #configure logging
    logging.basicConfig(stream=sys.stdout, level=app.config['LOGGING_LEVEL'])

    # register with extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    ckeditor.init_app(app)
    bootstrap.init_app(app)

    @app.cli.command('ding')
    def ding():
        logging.info("DING")

    @app.cli.command('run-db-init-script')
    @click.option('-f', '--file', default='fillAppWithDefaultData.py')
    def runDbInitScript(file):
        subprocess.run(["python", file])

    # a simple hello page
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    #index page
    @app.route('/')
    @app.route('/index')
    @app.route('/home')
    def index():
        return render_template("index.html", title="Home Page")

    #register blueprints
    from .routes import auth, users, groups, threads, posts
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(threads.bp)
    app.register_blueprint(posts.bp)

    #login settings
    login.login_view='auth.login'
    from .models import AnonymousUser
    login.anonymous_user = AnonymousUser

    return app