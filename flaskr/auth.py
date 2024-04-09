import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Function for registering a new user."""
    # read from HTML-form
    if request.method == 'POST':
        username = request.form['username'].lower() # get the username, make lowercase so users "A" and "a" cant both exist
        password = request.form['password']
        db = get_db()
        error = None

        # checks if both parts of form got filled out. Should include something with illegal chars
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # if we have not gotten an error, we try to open database, and add a new user
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        # sends the error in a way that makes it accessible for the HTML
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Function for logging a user in."""
    # reads from HTML
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        db = get_db()
        error = None
        # gets user from database
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # checks if user is a registered user, and if password is correct
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # creates cookie with user id.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # flashes gotten errors
        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    """Function for loading what user is currently logged in."""
    user_id = session.get('user_id')

    # retrieve user from db
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    """Function for logging a user out"""
    session.clear()  # destroys cookie to log out
    return redirect(url_for('index'))


def login_required(view):
    """Decorator function for requiring login of user"""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
