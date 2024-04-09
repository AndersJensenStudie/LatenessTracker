import sqlite3

import click
from flask import current_app, g

def get_db():
    """Opens a new database connection if there is none yet"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Closes the database again at the end of the function"""
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """Initializes the database"""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Construct the Database port of the Flask app"""
    app.teardown_appcontext(close_db) # tells flask to call close_db when cleaning up
    app.cli.add_command(init_db_command) # adds init_db_command as a command that can be called with the ´flask´-command