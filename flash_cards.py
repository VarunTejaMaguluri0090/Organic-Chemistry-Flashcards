import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from forms.RegistrationForm import RegistrationForm
from forms.LoginForm import LoginForm
from data.model import db
import json



app = Flask(__name__)
app.config.from_object(__name__)
resultForTotalCards = 0
userNameToDisplay = ''
IDToPass = ''
userNameForProfile = ''
emailForProfile = ''
passwordForProfile = ''
cityForProfile = ''
stateForProfile = ''
arrayForUserData = []
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db', 'project.db'),
    SECRET_KEY='development key',
    USERNAME='',
    PASSWORD='',USERID=''
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
        return redirect(url_for('welcome'))

@app.route('/explore/<int:id>')
def explore_cards(id): 
    from data.model import db
    if id < len(db):
        card = db[id] 
    else:
        id = 0
        card = db[id]
    return render_template("explorecards.html",card = card,card_type = card['type'], next_id = id+1)


@app.route('/explore_cards/')
def explore_cards_after_login():
    with open("data/explore_cards.json", "r") as f:
        explore_cards = json.load(f)

    db = get_db()
    query = '''
        SELECT type, front, back
        FROM cards
        WHERE userid = ?
        ORDER BY id DESC'''
    
    IDToPass = str(app.config['USERID'])
    cur = db.execute(query,(IDToPass))
    db.commit()
    my_cards = cur.fetchall()
    existing_cards = set()
    for card in my_cards:
        existing_cards.add((str(card[0]), str(card[1]), str(card[2])))
    new_cards = []
    for card in explore_cards:
        find = (str(card['type']),str(card['front']),str( card['back']))
        if find in existing_cards:
           continue 
        new_cards.append(card)    
    return render_template('explorecards_after_login.html', cards = new_cards)

def total_Cards():
    
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
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
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    render_template('cards.html', resultForTotalCards=resultForTotalCards,userNameToDisplayForApp=userNameToDisplay)

@app.route('/welcome')
def welcome():
    return render_template("welcome.html",cards=db)

@app.route("/card/<int:id>")
def card_view(id): 
    try:
        card = db[index]
        return render_template("card.html",card=card,index=index,max_index=len(db)-1)
    except IndexError:
        abort(404)

@app.route('/cards')
def cards():
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    query = '''
        SELECT id, type, front, back, known,userid
        FROM cards
        WHERE userid = ?
        ORDER BY id DESC
       
    '''
    print("USERID IN CARDS")
    print(app.config['USERID'])
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    cur = db.execute(query,(IDToPass))
    cards = cur.fetchall()
    
    dbForTotalCardsCount = get_db()
    queryForTotalCardsCount = '''
        SELECT COUNT(*) FROM cards
        WHERE userid = ?
    '''
    curForTotalCardsCount = dbForTotalCardsCount.execute(queryForTotalCardsCount,(IDToPass))
    resultForTotalCards = curForTotalCardsCount.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    
    dbForTotalKnownCount = get_db()
    queryForTotalKnownCount = '''
        SELECT COUNT(*) FROM cards
        WHERE known = 1 AND userid = ?
    '''
    curForTotalKnownCount = dbForTotalKnownCount.execute(queryForTotalKnownCount,(IDToPass))
    resultForTotalKnownCount = curForTotalKnownCount.fetchone()[0]
    print("Total known cards")
    print(resultForTotalKnownCount)
    print("Printed Actuual name:")
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('cards.html', cards=cards, filter_name="all",resultForTotalCardsCount = resultForTotalCards,resultForKnownCards= resultForTotalKnownCount,userNameToDisplayForApp=userNameToDisplay)


@app.route('/filter_cards/<filter_name>')
def filter_cards(filter_name):
    total_Cards()
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))

    filters = {
        "all":      "where 1 = 1 and userid = ?",
        "definitions":  "where type = 1 and userid = ?",
        "formulae":     "where type = 2 and userid = ?",
        "known":    "where known = 1 and userid = ?",
        "unknown":  "where known = 0 and userid = ?",
    }
    

    query = filters.get(filter_name)

    if not query:
        return redirect(url_for('home'))

    db = get_db()
    fullquery = "SELECT id, type, front, back, known FROM cards " + \
        query + "  ORDER BY id DESC "
    print("ID in FILTER")
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    cur = db.execute(fullquery,(IDToPass))
    cards = cur.fetchall()
    
    dbForTotalCardsCount = get_db()
    queryForTotalCardsCount = '''
        SELECT COUNT(*) FROM cards
        WHERE userid = ?
    '''
    curForTotalCardsCount = dbForTotalCardsCount.execute(queryForTotalCardsCount,(IDToPass))
    resultForTotalCards = curForTotalCardsCount.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    
    dbForTotalKnownCount = get_db()
    queryForTotalKnownCount = '''
        SELECT COUNT(*) FROM cards
        WHERE known = 1 AND userid = ?
    '''
    curForTotalKnownCount = dbForTotalKnownCount.execute(queryForTotalKnownCount,(IDToPass))
    resultForTotalKnownCount = curForTotalKnownCount.fetchone()[0]
    print("Total known cards")
    print(resultForTotalKnownCount)
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('mycards.html', cards=cards, filter_name=filter_name,resultForTotalCardsCount = resultForTotalCards,resultForKnownCards= resultForTotalKnownCount,userNameToDisplayForApp=userNameToDisplay)


@app.route('/add', methods=['POST'])
def add_card():
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    db.execute('INSERT INTO cards (userid, type, front, back) VALUES (?,?, ?, ?)',
               
               [IDToPass,request.form['type'],
                request.form['front'],
                request.form['back']
                ])
    db.commit()
    flash('New card was added successfully')
    return redirect(url_for('cards'))

@app.route('/add_card_explore/<type>/<front>/<back>')
def add_card_explore(type, front, back):
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(type, front, back)
    db.execute('INSERT INTO cards (userid, type, front, back) VALUES (?,?, ?, ?)',  
               [IDToPass,type,
                front,
                back
                ])
    db.commit()
    flash('Card is added to your MyCards portal')
    return redirect(url_for("explore_cards_after_login"))

@app.route('/edit/<card_id>')
def edit(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    query = '''
        SELECT id, type, front, back, known
        FROM cards
        WHERE id = ? AND userid = ?
    '''
    cur = db.execute(query, [card_id,IDToPass])
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    card = cur.fetchone()
    return render_template('edit.html', card=card,userNameToDisplayForApp=userNameToDisplay)


@app.route('/edit_card', methods=['POST'])
def edit_card():
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    selected = request.form.getlist('known')
    known = bool(selected)
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    command = '''
        UPDATE cards
        SET
          type = ?,
          front = ?,
          back = ?,
          known = ?
        WHERE id = ? AND userid = ?
    '''
    db.execute(command,
               [request.form['type'],
                request.form['front'],
                request.form['back'],
                known,
                request.form['card_id']
                ,IDToPass])
    db.commit()
    flash('Card saved.')
    return redirect(url_for('my_cards'))


@app.route('/delete/<card_id>')
def delete(card_id):
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    db.execute('DELETE FROM cards WHERE id = ? AND userid = ?', [card_id,IDToPass])
    db.commit()
    flash('Card deleted.')
    return redirect(url_for('my_cards'))


@app.route('/definitions')
@app.route('/definitions/<card_id>')
def definitions(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    return memorize("definitions", card_id)


@app.route('/formulae')
@app.route('/formulae/<card_id>')
def formulae(card_id=None):
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    return memorize("formulae", card_id)


def memorize(card_type, card_id):
    print("CARDID TO SHOW")
    print(card_id)
    if card_type == "definitions":
        type = 1
    elif card_type == "formulae":
        type = 2
    else:
        return redirect(url_for('my_cards'))

    if card_id:
        card = get_card_by_id(card_id)
    else:
        
        card = get_card(type)
    # if not card:
        
    #     flash("You don't have any " + card_type + " flashcards to show")
        # return redirect(url_for('cards'))
    # short_answer = (len(card['back']) < 75)
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('memorize.html',
                           card=card,
                           card_type=card_type,userNameToDisplayForApp=userNameToDisplay)
    # short_answer=short_answer



def get_card(type):
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)

    query = '''
      SELECT
        id, type, front, back, known
      FROM cards
      WHERE
        type = ?
        and known = 0 and userid = ?
      ORDER BY RANDOM()
      LIMIT 1
    '''

    cur = db.execute(query, [type,IDToPass])
    return cur.fetchone()


def get_card_by_id(card_id):
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)

    query = '''
      SELECT
        id, type, front, back, known
      FROM cards
      WHERE
        id = ? and userid = ?
      LIMIT 1
    '''

    cur = db.execute(query, [card_id,IDToPass])
    return cur.fetchone()


@app.route('/mark_known/<card_id>/<card_type>')
def mark_known(card_id, card_type):
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    print("CARDID1")
    print(card_id)
    if card_id != 0:
        db.execute('UPDATE cards SET known = 1 WHERE id = ? and userid = ?', [card_id,IDToPass])
        db.commit()
        flash('Card marked as known.')
        return redirect(url_for(card_type))


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    error = None
    userNameToSend = ''
    passwordToSend = ''
    userIDToSend = ''
    form = LoginForm()
    if form.validate_on_submit():
        db = get_db()
        queryToGetUserName = '''
        SELECT username
        from users
        
        WHERE username = ? AND password = ?
    '''
       
       
        for row in db.execute(queryToGetUserName,[request.form['username'],
                request.form['password']]).fetchall():
            for username in row:
                print(username,end=' ')
                userNameToSend = username
                print()
        db.commit()    
           
        queryToGetPassword = '''
        SELECT password
        from users
        
        WHERE password = ? AND username = ?
    '''
       
       
        for row in db.execute(queryToGetPassword, [request.form['password'],
                request.form['username']]).fetchall():
            for passwordToCheck in row:
                print(passwordToCheck,end=' ')
                passwordToSend = passwordToCheck
                print()
        print(userNameToSend)
        print(passwordToSend)
        
        queryToGetUserID =  '''
        SELECT id
        from users
        
        WHERE username = ? AND password = ?
    '''
       
       
        for row in db.execute(queryToGetUserID, [request.form['username'],
                request.form['password']]).fetchall():
            for userIDCheck in row:
                print(userIDCheck,end=' ')
                userIDToSend = userIDCheck
                print()
        print(userNameToSend)
        print(passwordToSend)
        print(userIDToSend)
        IDToPass = userIDToSend
        # userNameToDisplay = userNameToSend
        # print("Printed the name:")
        # print(userNameToDisplay)
        
        
       
        app.config.update(dict(DATABASE=os.path.join(app.root_path, 'db', 'project.db'),
                               SECRET_KEY='development key',
                               USERNAME=userNameToSend,
                               PASSWORD=passwordToSend,USERID=userIDToSend))
        app.config.from_envvar('CARDS_SETTINGS', silent=True)
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username or password!'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password!'
        else:
            session['logged_in'] = True
            session.permanent = True  # stay logged in
            return redirect(url_for('home'))
 

    return render_template('login.html', error=error, form=form)



@app.route("/register", methods=["GET", "POST"])
def register_user():
    #c = get_cursor()
    form = RegistrationForm()
    if form.validate_on_submit():
        name = request.form['username']
        email = request.form['email']
        usernameCounter = 0
        emailCounter = 0
        db = get_db()
        query = '''
        SELECT * FROM users
        WHERE username = ?
    '''
        usernameToget = db.execute(query, [name])
        print(usernameToget)
        for row in usernameToget.fetchall():
            usernameCounter = row[0]
            print("username")
            print(usernameCounter)
            
        query2 = '''
        SELECT * FROM users
        WHERE  email = ?
    '''
        emailToget = db.execute(query2, [email])
        print(emailToget)
        for row in emailToget.fetchall():
            emailCounter = row[0]
            print("Email")
            print(emailCounter)
            
        if usernameCounter > 0:
            error = "The username " +"'" +name+ "'"+" is already taken, please choose another one"
            return render_template('register.html',error=error, form=form)
        
        if emailCounter > 0:
            error = "The email " +"'" +email+ "'"+" is already taken, please choose another one"
            return render_template('register.html',error=error, form=form)
        
        else: 
            db.execute('INSERT INTO users (username, email, description, location, password) VALUES (?, ?, ?, ?, ?)',
               [request.form['username'],
                request.form['email'],
                request.form['description'],
                request.form['location'],
                request.form['password'],
                ])
            db.commit()
            flash('You are registered. Please proceed to login.',"success")
            return redirect(url_for('user_login')) 
    return render_template("register.html", form=form)


@app.route("/get_profile")
def get_profile():
    #c = get_cursor()
    arrayForUserData.clear()
    form = RegistrationForm()
    print(app.config['USERID'])
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    db = get_db()
    query = '''
        SELECT *
        FROM users
        WHERE id = ?
        ORDER BY id DESC
       
    '''
    
    for row in db.execute(query, (IDToPass,)).fetchall():
        for userInfo in row:
            print(userInfo,end=' ')
            arrayForUserData.append(userInfo)
            
            print()
        print(arrayForUserData)
        usernameForProfile = arrayForUserData[1]
        emailForProfile = arrayForUserData[2]
        stateForProfile = arrayForUserData[3]
        cityForProfile = arrayForUserData[4]
        passwordForProfile = arrayForUserData[5]
        
    return render_template("profile.html", form=form,  usernameInProfile = usernameForProfile,emailInProfile = emailForProfile,stateInProfile = stateForProfile,cityInProfile = cityForProfile,passwordInProfile = passwordForProfile)




@app.route("/updateProfile", methods=["POST"])
def update_profile():
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    form = RegistrationForm()
    print("Update Started")
    command = '''
        UPDATE users
        SET
          email = ?,
          location = ?,
          password = ?,
          description = ?
        WHERE id = ?
    '''
    db.execute(command,[request.form['email'],request.form['location'],request.form['password'],request.form['description'],IDToPass])
    db.commit()
    
    
    print("Update Ended")
    flash('Your profile has been updated.',"success")
    
    db = get_db()
    query = '''
        SELECT *
        FROM users
        WHERE id = ?
        ORDER BY id DESC
       
    '''
    
    for row in db.execute(query, (IDToPass,)).fetchall():
        for userInfo in row:
            print(userInfo,end=' ')
            arrayForUserData.append(userInfo)
            
            print()
        print(arrayForUserData)
        usernameForProfile = arrayForUserData[1]
        emailForProfile = arrayForUserData[2]
        stateForProfile = arrayForUserData[3]
        cityForProfile = arrayForUserData[4]
        passwordForProfile = arrayForUserData[5]
    return render_template("homepage.html",form=form)

    


@app.route('/home')
def home():
    
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('homepage.html',userNameToDisplayForApp=userNameToDisplay)


@app.route('/add_card_Nav')
def add_card_Nav():
    
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('cards.html',userNameToDisplayForApp=userNameToDisplay)

@app.route('/my_cards')
def my_cards():
    
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    query = '''
        SELECT id, type, front, back, known,userid
        FROM cards
        WHERE userid = ?
        ORDER BY id DESC
       
    '''
    print("USERID IN CARDS")
    print(app.config['USERID'])
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    cur = db.execute(query,(IDToPass))
    cards = cur.fetchall()
    
    dbForTotalCardsCount = get_db()
    queryForTotalCardsCount = '''
        SELECT COUNT(*) FROM cards
        WHERE userid = ?
    '''
    curForTotalCardsCount = dbForTotalCardsCount.execute(queryForTotalCardsCount,(IDToPass))
    resultForTotalCards = curForTotalCardsCount.fetchone()[0]
    print("Total cards")
    print(resultForTotalCards)
    
    dbForTotalKnownCount = get_db()
    queryForTotalKnownCount = '''
        SELECT COUNT(*) FROM cards
        WHERE known = 1 AND userid = ?
    '''
    curForTotalKnownCount = dbForTotalKnownCount.execute(queryForTotalKnownCount,(IDToPass))
    resultForTotalKnownCount = curForTotalKnownCount.fetchone()[0]
    print("Total known cards")
    print(resultForTotalKnownCount)
    print("Printed Actuual name:")
    userNameToDisplay = app.config['USERNAME']
    print(userNameToDisplay)
    return render_template('mycards.html', cards=cards, filter_name="all",resultForTotalCardsCount = resultForTotalCards,resultForKnownCards= resultForTotalKnownCount,userNameToDisplayForApp=userNameToDisplay)

@app.route('/reser_cards')
def reser_cards():
    if not session.get('logged_in'):
        return redirect(url_for('user_login'))
    db = get_db()
    IDToPass = str(app.config['USERID'])
    print(IDToPass)
    db.execute('UPDATE cards SET known = 0 WHERE  userid = ?', [IDToPass])
    db.commit()
    flash('Cards has been reset.')
    return redirect(url_for('my_cards'))

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You've logged out")
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run()
    
