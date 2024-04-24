import os
from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        """Return a friendly HTTP greeting."""
        return 'Hello, World!'

    # import db and init the db part of the app
    from . import db
    db.init_app(app)

    # import auth and register the blueprint in the app-object
    from . import auth
    app.register_blueprint(auth.bp)

    # import leaderboard and register blueprint
    from . import leaderboard
    app.register_blueprint(leaderboard.bp)

    # import game and register blueprint
    from . import game
    app.register_blueprint(game.bp)
    app.add_url_rule('/', endpoint='index')

    return app
