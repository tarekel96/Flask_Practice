from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

# Note: The blog blueprint does not have a url_prefix
# So the index view will be at /, the create view at /create, and so on.
bp = Blueprint('blog', __name__)

# The index will show all of the posts, most recent first
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

# The create view works the same as the auth register view.
# Either the form is displayed, or the posted data is validated and the post is added to the database or an error is shown.
@bp.route('/create', methods=('GET', 'POST'))
# The login_required decorator you wrote earlier is used on the blog views.
# A user must be logged in to visit these views, otherwise they will be redirected to the login page.
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# Both the update and delete views will need to fetch a post by id and check if the author matches the logged in user.
# To avoid duplicating code, you can write a function to get the post and call it from each view.
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # abort() will raise a special exception that returns an HTTP status code.
    # It takes an optional message to show with the error, otherwise a default message is used.
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# Unlike the views you’ve written so far, the update function takes an argument, id.
# That corresponds to the <int:id> in the route. A real URL will look like /1/update.
# Flask will capture the 1, ensure it’s an int, and pass it as the id argument.
# If you don’t specify int: and instead do <id>, it will be a string. 
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            # To generate a URL to the update page, url_for() needs to be passed the id
            # so it knows what to fill in: url_for('blog.update', id=post['id']).
            # This is also in the `index.html` file above.
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# The delete view doesn’t have its own template, the delete button is part of update.html and posts to the /<id>/delete URL.
# Since there is no template, it will only handle the POST method and then redirect to the index view.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))