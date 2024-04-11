from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from datetime import datetime
from time import time

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('game', __name__)

@bp.route('/')
def index():
    """Route to index-site"""
    try:
        # gets data from db.
        db = get_db()
        games = db.execute(
            'SELECT DISTINCT g.id, arrival_time, late_person, winner_id, user.username'
            ' FROM game as g'
            ' LEFT JOIN user ON g.winner_id = user.id'
            ' ORDER BY created DESC'
        ).fetchall()
    except Exception as e:
        print("Error getting game list:", e)
        games = []
        flash("Error retrieving games from database")

    # loads index with arguments posts
    return render_template('game/index.html', games=games)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """creates new games and adds them to the database"""
    if request.method == 'POST':
        # retrieves from form
        late_person = request.form['late_person']
        arrival = request.form['arrival']

        error = None

        if not late_person:
            error = "You can't leave the field blank!"

        if error is not None:
            flash(error)
        else:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO game (late_person, arrival_time) VALUES (?, ?)',
                    (late_person, arrival)
                )
                db.commit()
                flash("New game was successfully created!")
                return redirect(url_for('game.index'))
            except Exception as e:
                print("Error when trying to submit new game to db: {}".format(e))

    return render_template('game/create.html')

@bp.route('/<int:game_id>/guess', methods=['GET', 'POST'])
@login_required
def guess(game_id):
    """Routes to page for creating a new guess"""
    if request.method == 'POST':
        # gets from form
        guess = request.form['guess']
        # gets player_id
        player_id = g.user['id']

        error = None

        if not guess:
            error = "You can't leave the field blank!"

        if error: # need to add cond: valid ts
            flash(error)
        else:
            try:
                db = get_db()
                db.execute(
                    'INSERT INTO guess (game_id, guessed_time, player_id) VALUES (?, ?, ?)',
                    (game_id, guess, player_id)
                )
                db.commit()
            except Exception as e:
                print("Error when trying to add guess to db:", e)

            return redirect(url_for('game.game', game_id = game_id))


    return render_template('game/guess.html')

@bp.route('/<int:game_id>/game', methods=['GET', 'POST'])
def game(game_id):
    try:
        db = get_db()
        current_game = db.execute(
            'SELECT DISTINCT g.id, created, arrival_time, late_person, winner_id, user.username'
            ' FROM game as g'
            ' LEFT JOIN user ON g.winner_id = user.id'
            ' WHERE g.id = ?', (game_id, )
        ).fetchone()
    except Exception as e:
        current_game = []
        print("Error when trying to get the game:", e)

    try:
        db = get_db()
        players = db.execute(
            'SELECT *'
            ' FROM guess'
            ' JOIN user ON guess.player_id = user.id'
            ' WHERE game_id = ?;', (game_id, )
        ).fetchall()
    except Exception as e:
        players = []
        print("Error when trying to get all guesses:", e)

    return render_template('game/game.html', game=current_game, players=players)


@bp.route('/<int:game_id>/win', methods=['GET', 'POST'])
def win(game_id):
    """Directs to winner site"""
    # retrieves all guesses for current game
    try:
        db = get_db()
        players = db.execute(
            'SELECT *'
            ' FROM guess'
            ' JOIN user ON guess.player_id = user.id'
            ' WHERE game_id = ?;', (game_id, )
        ).fetchall()
    except Exception as e:
        players = []
        print("Error when trying to get guesses for all players:", e)

    at = time()
    closest_time = -1
    winner_id = None
    for p in players:
        current_time = (date_to_time(p['guessed_time']) - at)**2

        if (closest_time == -1) or (current_time < closest_time):
            closest_time = current_time
            winner_id = p['player_id']

    try:
        db = get_db()
        winner = db.execute(
            'SELECT username'
            ' FROM user'
            ' WHERE id = ?', (winner_id, )
        ).fetchone()
    except Exception as e:
        winner = None
        print("Error when trying to get winner:", e)

    try:
        db = get_db()
        db.execute(
            'UPDATE game'
	        ' SET winner_id = ?'
            ' WHERE id = ?',
            (winner_id, game_id)
        )
        db.commit()
    except Exception as e:
        winner = None
        print("Error when trying commit winner:", e)

    points = 1
    try:
        db = get_db()
        db.execute(
            'UPDATE user'
            ' SET points = points + ?'
            ' where id = ?', (points, winner_id, )
        )
    except Exception as e:
        print("Error adding points:", e)

    return render_template('game/win.html', winner=winner['username'], points=points)


def date_to_time(time_string):
    """Converts a date string on form HH:MM to a datetime object"""
    # create timestamp for given time
    hour, minute = map(int, time_string.split(':'))
    now = datetime.now()
    timestamp = datetime(now.year, now.month, now.day, hour, minute)

    # create timestamp for epoch
    epoch_time = datetime(1970, 1, 1)

    # return time between epoch and current
    return (timestamp - epoch_time).total_seconds()