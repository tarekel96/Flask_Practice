# Flask_Practice

Following the Official Flask Blog Tutorial (v 3.0.x):
- https://flask.palletsprojects.com/en/3.0.x/tutorial/

## Running the Application

Step 1:
```
cd /path/to/flask-tutorial
```

Step 2:
```
flask --app flaskr run --debug
```

Should see the application running under:
* http://127.0.0.1:5000

Flask Tutorial folders & files:
```
flask-tutorial
├── dist
│   └── flaskr-1.0.0-py2.py3-none-any.whl
├── flaskr
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-311.pyc
│   │   ├── auth.cpython-311.pyc
│   │   ├── blog.cpython-311.pyc
│   │   └── db.cpython-311.pyc
│   ├── auth.py
│   ├── blog.py
│   ├── db.py
│   ├── schema.sql
│   ├── static
│   │   └── style.css
│   └── templates
│       ├── auth
│       │   ├── login.html
│       │   └── register.html
│       ├── base.html
│       └── blog
│           ├── create.html
│           ├── index.html
│           └── update.html
├── instance
│   └── flaskr.sqlite
└── pyproject.toml
```