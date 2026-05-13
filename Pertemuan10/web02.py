# -*- coding: utf-8 -*-
import os
import sqlite3

from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import render_template

app = Flask(__name__)

app.secret_key = 'virus_lucu'

DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    'database.db'
)

# trigger virus setelah submit
INFECTED = False


# =========================
# DATABASE
# =========================
def connect_db():
    return sqlite3.connect(DATABASE_PATH)


def create_tables():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(32),
            password VARCHAR(32)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS timeline(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT
        )
    ''')

    conn.commit()
    conn.close()


def init_data():

    conn = connect_db()
    cur = conn.cursor()

    users = [
        ('user1', '123456'),
        ('user2', '123456')
    ]

    cur.executemany(
        'INSERT INTO user VALUES(NULL, ?, ?)',
        users
    )

    conn.commit()
    conn.close()


def init():

    create_tables()

    conn = connect_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM user')

    if len(cur.fetchall()) == 0:
        init_data()

    conn.close()


# =========================
# LOGIN
# =========================
def login_user(username, password):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        'SELECT id, username FROM user '
        'WHERE username=? AND password=?',
        (username, password)
    )

    row = cur.fetchone()

    conn.close()

    if row:
        return {
            'id': row[0],
            'username': row[1]
        }

    return None


def get_user(uid):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        'SELECT id, username FROM user WHERE id=?',
        (uid,)
    )

    row = cur.fetchone()

    conn.close()

    return {
        'id': row[0],
        'username': row[1]
    }


# =========================
# TIMELINE
# =========================
def create_post(uid, content):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        'INSERT INTO timeline VALUES(NULL, ?, ?)',
        (uid, content)
    )

    conn.commit()
    conn.close()


def get_posts():

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        'SELECT id, user_id, content '
        'FROM timeline ORDER BY id DESC'
    )

    rows = cur.fetchall()

    conn.close()

    return rows


# =========================
# ROUTES
# =========================
@app.route('/init')
def initialize():

    init()

    return redirect('/login')


@app.route('/')
def home():

    global INFECTED

    if 'uid' not in session:
        return redirect('/login')

    user = get_user(session['uid'])

    posts = get_posts()

    html = render_template(
        'dashboard.html',
        user=user,
        posts=posts,
        infected=INFECTED
    )

    # reset virus setelah tampil
    INFECTED = False

    return html


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']

    user = login_user(username, password)

    if user:

        session['uid'] = user['id']

        return redirect('/')

    return redirect('/login')


@app.route('/create', methods=['POST'])
def create():

    global INFECTED

    if 'uid' in session:

        create_post(
            session['uid'],
            request.form['content']
        )

        # trigger virus setelah submit
        INFECTED = True

    return redirect('/')


@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


if __name__ == '__main__':

    init()

    app.run(debug=True)