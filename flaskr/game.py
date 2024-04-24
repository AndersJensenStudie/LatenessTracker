from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from datetime import datetime, timedelta
from time import time

import random

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

    at = datetime.utcfromtimestamp(time())
    closest_delta = timedelta.max
    winner_id = None
    print(at)

    for p in players:
        guessed_time = get_today_time(p['guessed_time'])
        current_delta = abs(at - guessed_time)
        print("Player {}: Guessed Time: {}, Time Difference: {}".format(p['id'], guessed_time, current_delta))
        if current_delta < closest_delta:
            closest_delta = current_delta
            winner_id = p['id']

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

    # set winner
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
        print("Error when trying commit winner:", e)

    points = calculate_points()
    winner = get_winner(winner_id)
    if winner is None:
        try:
            db = get_db()
            db.execute(
                'UPDATE user'
                ' SET points = points + ?'
                ' where id = ?', (points, winner_id, )
            )
            db.commit()
        except Exception as e:
            print("Error adding points:", e)

    return render_template('game/win.html', winner=winner, points=points)


def get_today_time(time_string):
    """Converts a time string in HH:MM format to a datetime object with today's date."""
    now = datetime.now()
    hour, minute = map(int, time_string.split(':'))
    hour -= 2 # bad way of handling timezones, need to be changed when summer-time ends...
    if hour < 0:
        hour += 24

    return datetime(now.year, now.month, now.day, hour, minute)


def get_winner(winner_id):
    """ Finds the winner from a given id"""
    try:
        db = get_db()
        winner = db.execute('SELECT username'
                            ' FROM user'
                            ' WHERE id = ?', (winner_id, )).fetchone()
    except Exception as e:
        print("Error when trying to get winner:", e)
        winner = "No one lol"

    return winner['username']


def calculate_points():
    """ Calculates how many points a winner should be granted"""
    return 1
