import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import (
    check_password_hash, generate_password_hash
)

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
@bp.before_app_request
def load_logged_in_user():
    """
    Checks if a user id is stored in the session
    and gets that user’s data from the database,
    storing it on g.user, which lasts for the length of the request.    
    """
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# @bp.route associates the URL /register with the register view function
#   When Flask receives a request to /auth/register,
#   it will call the register view and use the return value as the response.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # POST method
    if request.method == 'POST':
        
        # request.form is a special type of dict mapping submitted form keys and values.
        # The user will input their username and password.        
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Validate that username and password are not empty.
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # generate_password_hash() is used to securely hash the password, and that hash is stored.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            # db.IntegrityError occurs if the username already exists,
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # successfully registered user
                return redirect(url_for("auth.login"))
            
        # If validation fails (error is not None), the error is shown to the user.
        flash(error)
    
    # GET method: render registration page to client
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() # fetchone() returns one row from the query

        if user is None:
            error = 'Incorrect username.'
        # check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session is a dict that stores data across request
            session.clear()

            # The user’s id is stored in a new session.
            session['user_id'] = user['id']
            # The data is stored in a cookie that is sent to the browser,
            # and the browser then sends it back with subsequent requests.
            # Flask securely signs the data so that it can’t be tampered with.

            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    """
    Remove the user id from the session so that
    `load_logged_in_user` won’t load a user on subsequent requests.
    """
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    """
    This decorator returns a new view function that wraps the original view it’s applied to.
    
    - The new function checks if a user is loaded and redirects to the login page otherwise.
    - If a user is loaded the original view is called and continues normally.
    
    This decorator will be used with blog views.
    """
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # The `url_for()` function generates the URL to a view based on a name and arguments.
            return redirect(url_for('auth.login'))
            # When using a blueprint, the name of the blueprint is prepended to the name of the function,
            # so the endpoint for the login function above is 'auth.login' because it was added to the 'auth' blueprint.

        return view(**kwargs)

    return wrapped_view