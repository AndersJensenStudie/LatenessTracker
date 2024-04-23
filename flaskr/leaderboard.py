from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from datetime import datetime
from time import time

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('leaderboard', __name__)

@bp.route('/pointsboard')
def pointsboard():
    """route to leaderboard"""
    try:
      db = get_db()
      players = db.execute(
          'SELECT username, points'
          ' FROM user'
          ' ORDER BY points DESC'
      )
    except Exception as e:
        players = []
        print("Error getting players for pointsboard:", e)

    return render_template('leaderboard/pointsboard.html', players=players)