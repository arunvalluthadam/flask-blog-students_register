from flask import Flask, request, session, g, url_for, abort, render_template, flash, redirect
import sqlite3

app = Flask(__name__)

app.secret_key='flask app'

def connect_db():  # 1
    rv = sqlite3.connect('register.db')
    rv.row_factory = sqlite3.Row
    return rv

def get_db():   # 2
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.route('/delete/<int:entry_id>')
def delete(entry_id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM students WHERE id = ?", (entry_id,))
    db.commit()
    flash('The entry was deleted')
    return redirect(url_for('show_entries'))


@app.route('/')    # 5
def show_entries():
    db = get_db()
    cur = db.execute('select * from students')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)

@app.route('/add', methods=['POST'])    # 6
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute("INSERT INTO students (name, age, place, city, state, phone) VALUES (?, ?, ?, ?, ?, ?)", [request.form['name'], request.form['age'], request.form['place'], request.form['city'], request.form['state'], request.form['phone']])
    db.commit()
    flash('New entry was sucessfully posted')
    return redirect(url_for('show_entries'))

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor()
        cur.execute("select * from students where name = ?", (request.form['search'],))
        return render_template("result.html", records=cur.fetchall())
    return render_template("index.html")



@app.route('/login', methods=['GET', 'POST'])    # 7
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin':
            error = 'Invalid username'
        elif request.form['password'] != 'admin':
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You where logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')    # 8
def logout():
    session.pop('logged_in', None)
    flash('You where logged out')
    return redirect(url_for('show_entries'))


@app.teardown_appcontext   # 3
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
	app.run(debug = True)
