import click
from app import db
from app import models

commands = list()

#create cli commands
@app.cli.command("fill-db")
def fill_db():
    #db.drop_all()
    #db.create_all()
    from .fillDatabase import fillWithDefaultData
    fillWithDefaultData()
    db.session.commit()

@app.cli.command("promote-to-admin")
@click.argument('username')
def promote_to_admin(username):
    user = db.User.query.filter_by(username=username).first()
    if user:
        if db.make_user_admin(user):
            print(f"Succesfully made user {username} admin.")
        else:
            print(f"User {username} is already admin.")
    else:
        print(f"[ERROR] User {username} doesn't exist.")
commands.append(promote_to_admin)

def get_user_info(username):
    user = db.User.query.filter_by(username=username).first()
    if user:
        print(f"<User {username}| is_admin={user.is_admin}>")
    else:
        print(f"[ERROR] User {username} doesn't exist.")
commands.append(get_user_info)

def init_app(app):
    for command in commands:
        app.cli.add_command(app.cli.command()(command))