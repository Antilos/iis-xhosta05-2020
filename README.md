# ISA-2020-Project
Runs on https://iis-xhosta05-2020.herokuapp.com/

This app is build around the [Flask](https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application) framework.

This app uses PostgreSql as it's database.

# Development
Use the local python flask server for development. Push changes to gitlab. Deploy to Heroku only when neccesary, as the process is needlesly long.
```
python app.py
```
or
```
export FLASK_APP=app.py
flask run
```
While the local server is running, it will automatically detect changes in code and integrate them.

# Deploy
Login to heroku
```
heroku login
```
Push changes
```
git push heroku master
```

**Note**: If not working, contact *xkocal00*

# Database
This app uses PostgreSql database. The production database is on Heroku, but for development we'll need to use local databases.

## Tutorial
Download [Postgres 12](https://www.postgresql.org/download/). Ideally get pgAdmin. Test if you can connect to the database by running `psql`.

If you get complaints about nonexistent databases, run `createdb mydb`. I used "isa-local" as the db name, try to stick to that to simplify script sharing.

If you can't log in, create new user in pgAdmin. I used "admin4isa" as password, I think we should stick to that.
