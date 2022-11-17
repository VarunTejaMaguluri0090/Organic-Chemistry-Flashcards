import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from forms.RegistrationForm import RegistrationForm




app = Flask(__name__)
app.config.from_object(__name__)
resultForTotalCards = 0
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db', 'project.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('CARDS_SETTINGS', silent=True)


def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.before_first_request
def init_db():
    db = get_db()
    with app.open_resource('data/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# -----------------------------------------------------------

# Uncomment and use this to initialize database, then comment it
#   You can rerun it to pave the database and start over
@app.route('/initdb')
def initdb():
    init_db()
    return 'Initialized the database.'


@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('definitions'))
    else:
        return redirect(url_for('login'))


def total_Cards():
    
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    

    db = get_db()
    query = '''
        SELECT COUNT(*) FROM cards
    '''
    if not query:
        return redirect(url_for('cards'))
    
    cur = db.execute(query)
    resultForTotalCards = cur.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    render_template('cards.html', resultForTotalCards=resultForTotalCards)


@app.route('/cards')
def cards():
    
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    query = '''
        SELECT id, type, front, back, known
        FROM cards
        ORDER BY id DESC
    '''
    
    cur = db.execute(query)
    cards = cur.fetchall()
    
    dbForTotalCardsCount = get_db()
    queryForTotalCardsCount = '''
        SELECT COUNT(*) FROM cards
    '''
    curForTotalCardsCount = dbForTotalCardsCount.execute(queryForTotalCardsCount)
    resultForTotalCards = curForTotalCardsCount.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    
    dbForTotalKnownCount = get_db()
    queryForTotalKnownCount = '''
        SELECT COUNT(*) FROM cards
        WHERE known = 1
    '''
    curForTotalKnownCount = dbForTotalKnownCount.execute(queryForTotalKnownCount)
    resultForTotalKnownCount = curForTotalKnownCount.fetchone()[0]
    print("Total known cards")
    print(resultForTotalKnownCount)
    
    return render_template('cards.html', cards=cards, filter_name="all",resultForTotalCardsCount = resultForTotalCards,resultForKnownCards= resultForTotalKnownCount)


@app.route('/filter_cards/<filter_name>')
def filter_cards(filter_name):
    total_Cards()
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    filters = {
        "all":      "where 1 = 1",
        "definitions":  "where type = 1",
        "formulae":     "where type = 2",
        "known":    "where known = 1",
        "unknown":  "where known = 0",
    }
    

    query = filters.get(filter_name)

    if not query:
        return redirect(url_for('cards'))

    db = get_db()
    fullquery = "SELECT id, type, front, back, known FROM cards " + \
        query + " ORDER BY id DESC"
    cur = db.execute(fullquery)
    cards = cur.fetchall()
    
    dbForTotalCardsCount = get_db()
    queryForTotalCardsCount = '''
        SELECT COUNT(*) FROM cards
    '''
    curForTotalCardsCount = dbForTotalCardsCount.execute(queryForTotalCardsCount)
    resultForTotalCards = curForTotalCardsCount.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    
    dbForTotalKnownCount = get_db()
    queryForTotalKnownCount = '''
        SELECT COUNT(*) FROM cards
        WHERE known = 1
    '''
    curForTotalKnownCount = dbForTotalKnownCount.execute(queryForTotalKnownCount)
    resultForTotalKnownCount = curForTotalKnownCount.fetchone()[0]
    print("Total known cards")
    print(resultForTotalKnownCount)
    return render_template('cards.html', cards=cards, filter_name=filter_name,resultForTotalCardsCount = resultForTotalCards,resultForKnownCards= resultForTotalKnownCount)


@app.route('/add', methods=['POST'])
def add_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    db.execute('INSERT INTO cards (type, front, back) VALUES (?, ?, ?)',
               [request.form['type'],
                request.form['front'],
                request.form['back']
                ])
    db.commit()
    flash('New card was added successfully')
    return redirect(url_for('cards'))


@app.route('/edit/<card_id>')
def edit(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    query = '''
        SELECT id, type, front, back, known
        FROM cards
        WHERE id = ?
    '''
    cur = db.execute(query, [card_id])
    card = cur.fetchone()
    return render_template('edit.html', card=card)


@app.route('/edit_card', methods=['POST'])
def edit_card():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    selected = request.form.getlist('known')
    known = bool(selected)
    db = get_db()
    command = '''
        UPDATE cards
        SET
          type = ?,
          front = ?,
          back = ?,
          known = ?
        WHERE id = ?
    '''
    db.execute(command,
               [request.form['type'],
                request.form['front'],
                request.form['back'],
                known,
                request.form['card_id']
                ])
    db.commit()
    flash('Card saved.')
    return redirect(url_for('cards'))


@app.route('/delete/<card_id>')
def delete(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM cards WHERE id = ?', [card_id])
    db.commit()
    flash('Card deleted.')
    return redirect(url_for('cards'))


@app.route('/definitions')
@app.route('/definitions/<card_id>')
def definitions(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return memorize("definitions", card_id)


@app.route('/formulae')
@app.route('/formulae/<card_id>')
def formulae(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return memorize("formulae", card_id)


def memorize(card_type, card_id):
    if card_type == "definitions":
        type = 1
    elif card_type == "formulae":
        type = 2
    else:
        return redirect(url_for('cards'))

    if card_id:
        card = get_card_by_id(card_id)
    else:
        card = get_card(type)
    if not card:
        flash("You've learned all the " + card_type + " flashcards")
        return redirect(url_for('cards'))
    short_answer = (len(card['back']) < 75)
    return render_template('memorize.html',
                           card=card,
                           card_type=card_type,
                           short_answer=short_answer)


def get_card(type):
    db = get_db()

    query = '''
      SELECT
        id, type, front, back, known
      FROM cards
      WHERE
        type = ?
        and known = 0
      ORDER BY RANDOM()
      LIMIT 1
    '''

    cur = db.execute(query, [type])
    return cur.fetchone()


def get_card_by_id(card_id):
    db = get_db()

    query = '''
      SELECT
        id, type, front, back, known
      FROM cards
      WHERE
        id = ?
      LIMIT 1
    '''

    cur = db.execute(query, [card_id])
    return cur.fetchone()


@app.route('/mark_known/<card_id>/<card_type>')
def mark_known(card_id, card_type):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    db.execute('UPDATE cards SET known = 1 WHERE id = ?', [card_id])
    db.commit()
    flash('Card marked as known.')
    return redirect(url_for(card_type))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username or password!'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password!'
        else:
            session['logged_in'] = True
            session.permanent = True  # stay logged in
            return redirect(url_for('cards'))
    return render_template('login.html', error=error)


@app.route("/register", methods=["GET", "POST"])
def register_user():
    #c = get_cursor()
    form = RegistrationForm()
    if form.validate_on_submit(): 
        db = get_db()
        db.execute('INSERT INTO users (username, email, description, location, password) VALUES (?, ?, ?, ?, ?)',
               [request.form['username'],
                request.form['email'],
                request.form['description'],
                request.form['location'],
                request.form['password'],
                ])
        db.commit()
        flash('You are registered. Please proceed to login.',"success")
        return redirect(url_for('login')) 
    return render_template("register.html", form=form)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You've logged out")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
    
