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
App is automatically deployed after a change in the github/main branch.

# Database
This app uses PostgreSql database. The production database is on Heroku, but for development we'll need to use local databases.
This is ok, as the app uses SQLAlchemy to abstract database operations. The correct database will be chosen using local variables

Database is generated from sql-alchemy ORM in app/models.py using Alembic migration tool.
```
flask db migrate #creates a migration
flask db upgrade #upgrades the database
```

Heroku's ephemeral file system makes it so the migration has to be created before pushing, and upgraded during the build process.

## Tutorial
Use SQLite for local development. Set SQLALCHEMY_DATABASE_URI configuration option to "sqlite:///path/to/db"
