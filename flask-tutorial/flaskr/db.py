import sqlite3

import click
from flask import current_app, g # g = global

"""
g is a special object that is unique for each request. It is used to store data that might be accessed by multiple functions during the request. The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.

current_app is another special object that points to the Flask application handling the request. Since you used an application factory, there is no application object when writing the rest of your code. get_db will be called when the application has been created and is handling a request, so current_app can be used.

sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key. This file doesn’t have to exist yet, and won’t until you initialize the database later.

"""


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row tells the connection to return rows that behave like dicts.
        g.db.row_factory = sqlite3.Row

    return g.db

# close_db checks if a connection was created by checking if g.db was set. If the connection exists, it is closed
def close_db(e=None):
    db = g.pop('db', None)
    # tell your application about the close_db function in the application factory so that it is called after each request.
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    # open_resource() opens a file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# click.command() defines a command line command called init-db that calls the init_db function and shows a success message to the user
# Command: flask --app flaskr init-db
# can either stop the server, or run this command in a new terminal (with .venv)
@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

"""
The close_db and init_db_command functions need to be registered with the application instance;
otherwise, they wont be used by the application.

However, since youre using a factory function, that instance isnt available when writing the functions.
Instead, write a function that takes an application and does the registration.
"""
# Register with the Application
# - Import and call this function from the factory.
# - Place the new code at the end of the factory function before returning the app.
def init_app(app):
    # tells Flask to call that function when cleaning up after returning the response.
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    app.cli.add_command(init_db_command)