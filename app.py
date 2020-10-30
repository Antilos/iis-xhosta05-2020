import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

DATABASE_URL = os.environ['DATABASE_URL']

@app.route('/')
def hello_world():
    if app.config['DEVELOPMENT']:
        conn = psycopg2.connect(DATABASE_URL, password="admin4isa", sslmode='allow')
    else:
        conn = psycopg2.connect(DATABASE_URL, sslmode='allow')

    cur = conn.cursor()
    cur.execute("Select * from test_users;")

    print(cur.fetchone())
    return "Hello"

@app.route('/create-user/<username>')
def create_user(username):
    conn = psycopg2.connect(DATABASE_URL, sslmode='allow')

    cur = conn.cursor()
    print(username)
    cur.execute("INSERT INTO test_users (name) VALUES (%s)", (username,))

    conn.commit()
    cur.close()
    conn.close()

    return f"Added user {username}"

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)