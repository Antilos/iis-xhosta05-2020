import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.urls import url_parse

from flask_login import current_user, login_user, logout_user, login_required

from app.models import User
from app.forms import LoginForm, RegisterForm
from app import db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# @bp.route('/register', methods=('GET', 'POST'))
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         cur = db.cursor()
#         error = None

#         if not username:
#             error = 'Username is required.'
#         elif not password:
#             error = 'Password is required.'
#         else:
#             cur.execute('SELECT id FROM users WHERE username = %s', (username,))
#             if cur.fetchone() is not None:
#                 error = f"User {username} is already registered."
        
#         if error is None:
#             db.cursor().execute(
#                 'INSERT INTO users (username, password) VALUES (%s, %s)', (username, generate_password_hash(password))
#             )
#             db.commit()
#             return redirect(url_for('auth.login'))

#         flash(error)
    
#     return render_template('auth/register.html')

# @bp.route('/login', methods=('GET', 'POST'))
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         db = get_db()
#         error = None

#         passwdHash = db.cursor().execute('SELECT (password) FROM users WHERE username = %s', (username,)).fetchone()
#         if user is None:
#             error = 'Incorrect username.'
#         elif not check_password_hash(passwdHash, password):
#             error = 'Incorrect password.'

#         if error is None:
#             session.clear()
#             session['user_id'] = user['id']
#             return redirect(url_for('index'))

#         flash(error)

#     return render_template('auth/login.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    #if form is submited, attempt to log user in
    if form.validate_on_submit():
        #validate login data
        print(form.username.data)
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        
        #log user in
        login_user(user, remember=form.remember_me.data)

        #redirect user to the page they were logging in from
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(url_for('auth.login'))
    
    #if method was GET, render login template
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('You are now a registered user.')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))